import torch
from torch import nn
import torch.nn.functional as F


class MoKGRLengthRouter(nn.Module):
    def __init__(self, query_dim, num_hops, min_hop=2, max_hop=None, num_experts=3, temperature=1.1):
        super().__init__()
        self.query_dim = int(query_dim)
        self.num_hops = int(num_hops)
        self.min_hop = int(min_hop)
        self.max_hop = int(num_hops if max_hop is None else max_hop)
        self.num_experts = int(num_experts)
        self.temperature = float(temperature)

        if not (1 <= self.min_hop <= self.max_hop <= self.num_hops):
            raise ValueError(
                f"invalid hop range: min_hop={self.min_hop}, max_hop={self.max_hop}, num_hops={self.num_hops}"
            )

        self.hop_range = self.max_hop - self.min_hop + 1
        self.context_proj = nn.Linear(self.query_dim, self.query_dim)
        self.hop_embedding = nn.Embedding(self.hop_range, self.query_dim)
        self.noise_proj = nn.Linear(self.query_dim, 1)
        self.softplus = nn.Softplus()

    def forward(self, query):
        context = self.context_proj(query)                              # [B, D]
        hop_ids = torch.arange(self.hop_range, device=query.device)     # [H]
        hop_embed = self.hop_embedding(hop_ids)                         # [H, D]

        logits = torch.matmul(context, hop_embed.t())                   # [B, H]
        if self.training:
            noise_scale = self.softplus(self.noise_proj(context))       # [B, 1]
            logits = logits + torch.randn_like(logits) * noise_scale

        k = min(self.num_experts, self.hop_range)
        topk_values, topk_indices = torch.topk(logits, k, dim=-1)       # [B, K], [B, K]
        topk_weights = F.softmax(topk_values / self.temperature, dim=-1) # [B, K]

        full_weight = torch.zeros_like(logits)                          # [B, H]
        full_weight.scatter_(1, topk_indices, topk_weights)

        debug = {
            "hop_logits": logits,
            "hop_weight": full_weight,
            "topk_indices": topk_indices,
        }
        return full_weight, debug
