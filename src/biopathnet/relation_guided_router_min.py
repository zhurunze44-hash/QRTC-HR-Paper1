import torch
import torch.nn as nn
import torch.nn.functional as F


def gather_candidate_repr(node_repr, index):
    """
    node_repr: [B, N, D]
    index: [B] or [B, K]
    return: [B, 1, D] or [B, K, D]
    """
    if index.dim() == 1:
        index = index.unsqueeze(1)

    batch_size, num_nodes, dim = node_repr.shape
    k = index.size(1)
    gather_index = index.unsqueeze(-1).expand(batch_size, k, dim)
    return node_repr.gather(dim=1, index=gather_index)


class StaticTypeCompatibility(nn.Module):
    def __init__(self, compat_table, entity_type_pad=-1):
        super().__init__()
        self.register_buffer("compat_table", compat_table)
        self.entity_type_pad = entity_type_pad

    def forward(self, r_index, tail_type_ids):
        """
        r_index: [B]
        tail_type_ids: [B, K, M]
        return: [B, K]
        """
        batch_size, k, m = tail_type_ids.shape
        rel_table = self.compat_table[r_index]                # [B, T]
        num_types = rel_table.size(-1)

        safe_type_ids = tail_type_ids.clamp_min(0)            # [B, K, M]
        rel_table = rel_table.unsqueeze(1).expand(batch_size, k, num_types)
        gathered = rel_table.gather(dim=-1, index=safe_type_ids)

        mask = (tail_type_ids != self.entity_type_pad).float()
        denom = mask.sum(dim=-1).clamp_min(1.0)
        type_bias = (gathered * mask).sum(dim=-1) / denom     # [B, K]
        return type_bias


class RelationGuidedEvidenceRouterMin(nn.Module):
    def __init__(
        self,
        hidden_dim,
        num_hops,
        type_compat_module,
        gamma=0.1,
        router_hidden_dim=None,
    ):
        super().__init__()
        router_hidden_dim = router_hidden_dim or hidden_dim

        self.expert_router = nn.Sequential(
            nn.Linear(hidden_dim, router_hidden_dim),
            nn.ReLU(),
            nn.Linear(router_hidden_dim, 2),
        )
        self.hop_router = nn.Sequential(
            nn.Linear(hidden_dim, router_hidden_dim),
            nn.ReLU(),
            nn.Linear(router_hidden_dim, num_hops),
        )

        self.type_compat = type_compat_module
        self.gamma = gamma

    def forward(
        self,
        rel_emb,          # [B, D]
        r_index,          # [B]
        base_repr,        # [B, K, D]
        hop_repr_list,    # list of [B, K, D]
        tail_type_ids,    # [B, K, M]
    ):
        batch_size, k, dim = base_repr.shape
        num_hops = len(hop_repr_list)

        expert_logits = self.expert_router(rel_emb)                 # [B, 2]
        expert_weights = F.softmax(expert_logits, dim=-1)           # [B, 2]
        hop_expert_w = expert_weights[:, 0].view(batch_size, 1, 1)
        type_expert_w = expert_weights[:, 1].view(batch_size, 1, 1)

        hop_logits = self.hop_router(rel_emb)                       # [B, L]
        hop_weights = F.softmax(hop_logits, dim=-1)                 # [B, L]

        hop_stack = torch.stack(hop_repr_list, dim=1)               # [B, L, K, D]
        hop_mix_repr = (hop_stack * hop_weights.view(batch_size, num_hops, 1, 1)).sum(dim=1)

        type_bias = self.type_compat(r_index, tail_type_ids)        # [B, K]
        type_repr = base_repr * type_bias.unsqueeze(-1)

        fused_repr = hop_expert_w * hop_mix_repr + type_expert_w * type_repr
        final_repr = base_repr + self.gamma * fused_repr

        aux = {
            "expert_weights": expert_weights,
            "hop_weights": hop_weights,
            "type_bias": type_bias,
        }
        return final_repr, aux


def build_relation_tail_type_table(
    train_triples,
    entity_type_ids,
    num_relations,
    num_types,
    alpha=1.0,
):
    """
    train_triples: iterable of (h, r, t)
    entity_type_ids: list-like, entity_type_ids[t] -> iterable[type_id]
    return: compat_table [R, T]
    """
    counts = torch.zeros(num_relations, num_types, dtype=torch.float)

    for _, r, t in train_triples:
        tail_types = entity_type_ids[t]
        if isinstance(tail_types, torch.Tensor):
            tail_types = tail_types.tolist()
        for tp in tail_types:
            if tp is None:
                continue
            tp = int(tp)
            if tp >= 0:
                counts[int(r), tp] += 1.0

    probs = (counts + alpha) / (counts.sum(dim=-1, keepdim=True) + alpha * num_types)
    compat = torch.log(probs + 1e-8)
    compat = compat - compat.mean(dim=-1, keepdim=True)
    return compat
