import os
import torch
from torch import nn


def _rg_alpha_max():
    return float(os.environ.get("RG_MIN_ALPHA_MAX", "0.35"))


class RelationGuidedEvidenceRouter(nn.Module):
    """
    Minimal M1 + M3a hook:
      - hop experts: each hop hidden is one expert
      - type-compatibility expert: query-conditioned type gate over last-hop hidden
      - meta fusion: route between hop_mix and type_mix
      - residual blend with last-hop hidden for warm-start stability

    M3a 当前只做一件事:
      - optional local_context is concatenated ONLY into the gate-like type branch
      - not into hop_router / meta_router yet
    """

    def __init__(
        self,
        query_dim,
        hop_dims,
        expert_dim,
        type_vocab_cap=64,
        router_hidden_dim=64,
        router_temperature=1.0,
        residual_init=-2.0,
        local_context_enable=False,
        local_context_dim=64,
    ):
        super().__init__()
        self.num_hop = len(hop_dims)
        self.expert_dim = int(expert_dim)
        self.router_temperature = float(router_temperature)
        self.type_vocab_cap = int(type_vocab_cap)
        self.local_context_enable = bool(local_context_enable)
        self.local_context_dim = int(local_context_dim)

        self.hop_projs = nn.ModuleList([
            nn.Identity() if d == self.expert_dim else nn.Linear(d, self.expert_dim)
            for d in hop_dims
        ])
        self.last_proj = (
            nn.Identity() if hop_dims[-1] == self.expert_dim else nn.Linear(hop_dims[-1], self.expert_dim)
        )

        router_in_dim = query_dim + self.expert_dim

        self.hop_router = nn.Sequential(
            nn.Linear(router_in_dim, router_hidden_dim),
            nn.ReLU(),
            nn.Linear(router_hidden_dim, self.num_hop),
        )

        self.type_emb = nn.Embedding(self.type_vocab_cap, self.expert_dim)
        self.type_query_proj = nn.Linear(query_dim, self.expert_dim)

        type_gate_input_dim = self.expert_dim * 3
        if self.local_context_enable:
            type_gate_input_dim += self.local_context_dim

        self.type_gate = nn.Sequential(
            nn.Linear(type_gate_input_dim, router_hidden_dim),
            nn.ReLU(),
            nn.Linear(router_hidden_dim, self.expert_dim),
        )

        self.local_context_selector = None
        if self.local_context_enable:
            self.local_context_selector = nn.Sequential(
                nn.Linear(query_dim + self.local_context_dim, router_hidden_dim),
                nn.ReLU(),
                nn.Linear(router_hidden_dim, 1),
            )

        self.meta_router = nn.Sequential(
            nn.Linear(router_in_dim, router_hidden_dim),
            nn.ReLU(),
            nn.Linear(router_hidden_dim, 2),
        )

        self.out_norm = nn.LayerNorm(self.expert_dim)
        self.trust_head = nn.Sequential(
            nn.Linear(router_in_dim, router_hidden_dim),
            nn.ReLU(),
            nn.Linear(router_hidden_dim, 1),
        )
        nn.init.constant_(
            self.trust_head[-1].bias,
            float(os.environ.get("RG_MIN_TRUST_BIAS_INIT", "-2.2"))
        )
        self.residual_logit = nn.Parameter(torch.tensor(float(residual_init)))

    def _safe_node_type(self, node_type):
        return node_type.clamp(min=0, max=self.type_vocab_cap - 1)

    def forward(self, hiddens, query, node_type, h_index, local_context=None, collect_debug=False):
        """
        hiddens: list of [num_nodes, batch_size, d_l]
        query:   [batch_size, query_dim]
        node_type: [num_nodes]
        h_index: [batch_size]
        local_context: [batch_size, C] or None
        """
        proj_hiddens = [proj(h) for proj, h in zip(self.hop_projs, hiddens)]
        hop_stack = torch.stack(proj_hiddens, dim=0)  # [L, N, B, D]

        base_last = self.last_proj(hiddens[-1])  # [N, B, D]
        batch_size = query.size(0)
        batch_index = torch.arange(batch_size, device=query.device)
        head_feat = base_last[h_index, batch_index]   # [B, D]
        router_input = torch.cat([query, head_feat], dim=-1)  # [B, query_dim + D]

        hop_logits = self.hop_router(router_input) / self.router_temperature
        hop_weight = torch.softmax(hop_logits, dim=-1)  # [B, L]
        hop_mix = (
            hop_stack * hop_weight.t().unsqueeze(1).unsqueeze(-1)
        ).sum(dim=0)  # [N, B, D]

        safe_node_type = self._safe_node_type(node_type)
        type_base = self.type_emb(safe_node_type).unsqueeze(1).expand(-1, batch_size, -1)   # [N, B, D]
        type_query = self.type_query_proj(query).unsqueeze(0).expand(base_last.size(0), -1, -1)  # [N, B, D]
        if os.getenv("ROUTER_ZERO_TYPE_BASE", "0") == "1":
            type_base = torch.zeros_like(type_base)
        if os.getenv("ROUTER_ZERO_TYPE_QUERY", "0") == "1":
            type_query = torch.zeros_like(type_query)
        if os.getenv("ROUTER_ZERO_TYPE_LAST", "0") == "1":
            base_last = torch.zeros_like(base_last)

        type_pieces = [type_base, type_query, base_last]
        local_context_gate = None
        local_context_selected = local_context
        if self.local_context_enable and local_context is not None:
            selector_input = torch.cat([query, local_context], dim=-1)  # [B, query_dim + C]
            local_context_gate = torch.sigmoid(self.local_context_selector(selector_input))  # [B, 1]
            local_context_selected = local_context_gate * local_context
            local_expand = local_context_selected.unsqueeze(0).expand(base_last.size(0), -1, -1)  # [N, B, C]
            type_pieces.append(local_expand)

        type_input = torch.cat(type_pieces, dim=-1)
        type_gate = torch.sigmoid(self.type_gate(type_input))  # [N, B, D]
        type_mix = type_gate * base_last  # [N, B, D]

        meta_logits = self.meta_router(router_input) / self.router_temperature
        meta_weight = torch.softmax(meta_logits, dim=-1)  # [B, 2]

        fused = (
            meta_weight[:, 0].unsqueeze(0).unsqueeze(-1) * hop_mix
            + meta_weight[:, 1].unsqueeze(0).unsqueeze(-1) * type_mix
        )

        residual_alpha = _rg_alpha_max() * torch.sigmoid(self.trust_head(router_input))  # [B, 1]
        residual_alpha_broadcast = residual_alpha.unsqueeze(0)  # [1, B, 1]
        selected_hidden = self.out_norm(
            (1.0 - residual_alpha_broadcast) * fused + residual_alpha_broadcast * base_last
        )

        router_debug = {}
        if collect_debug:
            hop_weight_cpu = hop_weight.detach().cpu()
            meta_weight_cpu = meta_weight.detach().cpu()
            residual_alpha_cpu = residual_alpha.detach().cpu()
            head_feat_norm_cpu = head_feat.norm(dim=-1).detach().cpu()

            type_gate_mean_cpu = type_gate.mean(dim=(0, 2)).detach().cpu()
            selected_hidden_norm_cpu = selected_hidden.norm(dim=-1).mean(dim=0).detach().cpu()

            router_debug = {
                "ROUTER_HOP_WEIGHT": hop_weight_cpu,
                "ROUTER_META_WEIGHT": meta_weight_cpu,
                "ROUTER_RESIDUAL_ALPHA": residual_alpha_cpu,
                "ROUTER_HEAD_FEAT_NORM": head_feat_norm_cpu,
                "hop_weight": hop_weight_cpu,
                "meta_weight": meta_weight_cpu,
                "residual_alpha": residual_alpha_cpu,
                "head_feat_norm": head_feat_norm_cpu,
                "type_gate_mean": type_gate_mean_cpu,
                "selected_hidden_norm": selected_hidden_norm_cpu,
            }

            if local_context is not None:
                router_debug["local_context_norm"] = local_context.norm(dim=-1).detach().cpu()
            if local_context_gate is not None:
                router_debug["local_context_gate_mean"] = local_context_gate.mean(dim=-1).detach().cpu()

        return selected_hidden, router_debug
