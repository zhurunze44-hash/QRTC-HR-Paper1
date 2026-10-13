import torch
from torch import nn
from torch.nn import functional as F


class RelationGuidedEvidenceRouterMinPost(nn.Module):
    def __init__(self, query_dim, hop_dims, residual_gamma=0.1, router_hidden_dim=64):
        super().__init__()
        if not hop_dims:
            raise ValueError("hop_dims must be non-empty")

        self.query_dim = int(query_dim)
        self.hop_dims = [int(x) for x in hop_dims]
        self.expert_dim = int(self.hop_dims[-1])
        self.num_hops = len(self.hop_dims)
        self.residual_gamma = float(residual_gamma)

        self.expert_router = nn.Sequential(
            nn.Linear(self.query_dim, int(router_hidden_dim)),
            nn.ReLU(),
            nn.Linear(int(router_hidden_dim), 2),
        )
        self.hop_router = nn.Sequential(
            nn.Linear(self.query_dim, int(router_hidden_dim)),
            nn.ReLU(),
            nn.Linear(int(router_hidden_dim), self.num_hops),
        )

        self.hop_projs = nn.ModuleList()
        for dim in self.hop_dims:
            if dim == self.expert_dim:
                self.hop_projs.append(nn.Identity())
            else:
                self.hop_projs.append(nn.Linear(dim, self.expert_dim, bias=False))

        self._compat_cache_key = None
        self._compat_cache_tensor = None

    def _build_relation_tail_type_compat(self, graph, node_type, device):
        if node_type is None or node_type.numel() == 0:
            compat = torch.zeros(int(graph.num_relation), 1, device=device)
            self._compat_cache_key = (int(graph.num_relation), int(graph.num_node), 1, str(device))
            self._compat_cache_tensor = compat
            return compat

        node_type = node_type.to(device=device, dtype=torch.long)
        num_type = int(node_type.max().item()) + 1 if node_type.numel() else 1
        cache_key = (int(graph.num_relation), int(graph.num_node), int(num_type), str(device))

        if self._compat_cache_key == cache_key and self._compat_cache_tensor is not None:
            return self._compat_cache_tensor

        edge_list = getattr(graph, "edge_list", None)
        if edge_list is None or edge_list.size(-1) < 3:
            compat = torch.zeros(int(graph.num_relation), int(num_type), device=device)
            self._compat_cache_key = cache_key
            self._compat_cache_tensor = compat
            return compat

        edge_list = edge_list.to(device)
        rel = edge_list[:, 2].long()
        tail = edge_list[:, 1].long()
        tail_type = node_type[tail].long().clamp(min=0)

        counts = torch.zeros(int(graph.num_relation), int(num_type), dtype=torch.float, device=device)
        ones = torch.ones_like(rel, dtype=torch.float, device=device)
        counts.index_put_((rel, tail_type), ones, accumulate=True)

        probs = (counts + 1.0) / (counts.sum(dim=-1, keepdim=True) + float(num_type))
        compat = torch.log(probs + 1e-12)
        compat = compat - compat.mean(dim=-1, keepdim=True)

        self._compat_cache_key = cache_key
        self._compat_cache_tensor = compat
        return compat

    def forward(
        self,
        graph,
        relation_query,     # [B, Q]
        relation_index,     # [B]
        hop_hidden_states,  # list of [N, B, D_i]
        t_index,            # [B, K]
        base_feature,       # [B, K, D_last + Q]
        collect_debug=False,
    ):
        device = base_feature.device
        if t_index.dim() == 1:
            t_index = t_index.unsqueeze(1)

        batch_size, num_candidate, base_dim = base_feature.shape
        expected_dim = self.expert_dim + self.query_dim
        if base_dim != expected_dim:
            raise ValueError(
                f"base_feature dim mismatch: got {base_dim}, expected {expected_dim} "
                f"(expert_dim={self.expert_dim}, query_dim={self.query_dim})"
            )

        if len(hop_hidden_states) != self.num_hops:
            raise ValueError(
                f"hop_hidden_states length mismatch: got {len(hop_hidden_states)}, expected {self.num_hops}"
            )

        relation_query = relation_query.to(device)
        relation_index = relation_index.to(device=device, dtype=torch.long)

        hop_tail_features = []
        for hidden, proj in zip(hop_hidden_states, self.hop_projs):
            hidden_bt = hidden.transpose(0, 1)  # [B, N, D]
            gather_index = t_index.unsqueeze(-1).expand(-1, -1, hidden_bt.size(-1))
            tail_hidden = hidden_bt.gather(1, gather_index)
            tail_hidden = proj(tail_hidden)
            hop_tail_features.append(tail_hidden)

        last_hidden = hop_tail_features[-1]
        expert_weight = F.softmax(self.expert_router(relation_query), dim=-1)  # [B, 2]
        hop_weight = F.softmax(self.hop_router(relation_query), dim=-1)        # [B, L]

        hop_stack = torch.stack(hop_tail_features, dim=1)                       # [B, L, K, D]
        hop_mix = (hop_stack * hop_weight.view(batch_size, self.num_hops, 1, 1)).sum(dim=1)

        node_type = getattr(graph, "node_type", None)
        if node_type is None:
            type_bias = torch.zeros(batch_size, num_candidate, device=device)
        else:
            node_type = node_type.to(device=device, dtype=torch.long)
            compat = self._build_relation_tail_type_compat(graph, node_type, device=device)
            tail_type = node_type[t_index].long().clamp(min=0, max=compat.size(1) - 1)
            type_bias = compat[relation_index].gather(1, tail_type)

        type_hidden = last_hidden * type_bias.unsqueeze(-1)

        hop_expert_weight = expert_weight[:, 0].view(batch_size, 1, 1)
        type_expert_weight = expert_weight[:, 1].view(batch_size, 1, 1)
        fused_hidden = hop_expert_weight * hop_mix + type_expert_weight * type_hidden

        node_query = relation_query.unsqueeze(1).expand(batch_size, num_candidate, self.query_dim)
        routed_hidden = last_hidden + self.residual_gamma * fused_hidden
        routed_feature = torch.cat([routed_hidden, node_query], dim=-1)

        type_bias_stats = torch.stack(
            [
                type_bias.min(dim=-1).values,
                type_bias.mean(dim=-1),
                type_bias.max(dim=-1).values,
            ],
            dim=-1,
        )

        debug = {
            "expert_weight": expert_weight.detach(),
            "hop_weight": hop_weight.detach(),
            "type_bias_stats": type_bias_stats.detach(),
        }
        if collect_debug:
            debug["type_bias"] = type_bias.detach()

        return routed_feature, debug
