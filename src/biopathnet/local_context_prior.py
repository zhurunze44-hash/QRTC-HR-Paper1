import torch
import torch.nn as nn
import torch.nn.functional as F


class HeadLocalContextEncoder(nn.Module):
    """
    第一版只做:
    1) head 的 in/out relation histogram
    2) relation-aware neighbor relation summary

    不做:
    - tail-specific context
    - type branch
    - text branch
    """

    def __init__(
        self,
        num_relation: int,
        relation_dim: int,
        context_dim: int,
        hidden_dim: int = 64,
        use_relation_hist: bool = True,
    ):
        super().__init__()
        self.num_relation = int(num_relation)
        self.relation_dim = int(relation_dim)
        self.context_dim = int(context_dim)
        self.hidden_dim = int(hidden_dim)
        self.use_relation_hist = bool(use_relation_hist)

        if self.use_relation_hist:
            self.rel_hist_proj = nn.Sequential(
                nn.Linear(self.num_relation * 2, self.hidden_dim),
                nn.ReLU(),
                nn.Linear(self.hidden_dim, self.context_dim),
            )

        self.query_proj = nn.Linear(self.relation_dim, self.hidden_dim)
        self.neigh_rel_proj = nn.Linear(self.relation_dim + 2, self.hidden_dim)  # relation emb + dir onehot(2)
        self.attn_score = nn.Linear(self.hidden_dim, 1)

        self.fuse = nn.Sequential(
            nn.Linear(self.context_dim + self.hidden_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.context_dim),
        )

    def forward(
        self,
        relation_emb,        # [B, Dr]
        rel_hist_in,         # [B, R]
        rel_hist_out,        # [B, R]
        neighbor_rel_emb,    # [B, N, Dr]
        neighbor_dir_onehot, # [B, N, 2]
        neighbor_mask,       # [B, N]
    ):
        B = relation_emb.size(0)

        if self.use_relation_hist:
            rel_hist_feat = torch.cat([rel_hist_in, rel_hist_out], dim=-1)   # [B, 2R]
            hist_ctx = self.rel_hist_proj(rel_hist_feat)                      # [B, C]
        else:
            hist_ctx = relation_emb.new_zeros(B, self.context_dim)

        q = self.query_proj(relation_emb).unsqueeze(1)                        # [B, 1, H]
        neigh_feat = torch.cat([neighbor_rel_emb, neighbor_dir_onehot], dim=-1)  # [B, N, Dr+2]
        neigh_h = self.neigh_rel_proj(neigh_feat)                             # [B, N, H]

        attn_h = torch.tanh(q + neigh_h)                                      # [B, N, H]
        attn_logit = self.attn_score(attn_h).squeeze(-1)                      # [B, N]

        if neighbor_mask.dtype != torch.bool:
            neighbor_mask = neighbor_mask.bool()

        # 防止全空邻居时 softmax 出 nan
        all_invalid = (~neighbor_mask).all(dim=-1, keepdim=True)              # [B, 1]
        safe_mask = neighbor_mask.clone()
        safe_mask[all_invalid.expand_as(safe_mask)] = True

        attn_logit = attn_logit.masked_fill(~safe_mask, float("-inf"))
        attn = torch.softmax(attn_logit, dim=-1)                              # [B, N]
        attn = attn * neighbor_mask.float()
        attn = attn / (attn.sum(dim=-1, keepdim=True) + 1e-12)

        neigh_ctx = torch.sum(attn.unsqueeze(-1) * neigh_h, dim=1)            # [B, H]
        local_context = self.fuse(torch.cat([hist_ctx, neigh_ctx], dim=-1))   # [B, C]

        aux = {
            "local_context": local_context,
            "local_attn": attn,
            "hist_ctx": hist_ctx,
            "neigh_ctx": neigh_ctx,
        }
        return local_context, aux


class HeadLocalContextCacheProvider:
    """
    第一版最小 cache provider

    只缓存:
    1) 每个 head 的 in/out relation histogram
    2) 每个 head 的一跳邻边 relation ids
    3) 每个 head 的一跳邻边 direction ids
    4) mask

    约定:
    - direction_id = 0 表示该邻边对当前节点是 in-edge
    - direction_id = 1 表示该邻边对当前节点是 out-edge
    """

    def __init__(
        self,
        num_node: int,
        num_relation: int,
        max_neighbor: int = 16,
        hist_dtype=torch.float32,
    ):
        self.num_node = int(num_node)
        self.num_relation = int(num_relation)
        self.max_neighbor = int(max_neighbor)
        self.hist_dtype = hist_dtype

        self.rel_hist_in = None
        self.rel_hist_out = None
        self.neighbor_rel_ids = None
        self.neighbor_dir_ids = None
        self.neighbor_mask = None
        self._built = False

    def build_from_edge_list(self, edge_list: torch.Tensor):
        """
        edge_list: [E, 3] with columns [head, tail, relation]
        """
        if edge_list.dim() != 2 or edge_list.size(-1) < 3:
            raise ValueError(f"edge_list shape must be [E, 3+] but got {tuple(edge_list.shape)}")

        edge_list = edge_list.detach().to("cpu")
        head = edge_list[:, 0].long()
        tail = edge_list[:, 1].long()
        rel = edge_list[:, 2].long()

        rel_hist_in = torch.zeros(self.num_node, self.num_relation, dtype=self.hist_dtype)
        rel_hist_out = torch.zeros(self.num_node, self.num_relation, dtype=self.hist_dtype)

        neighbor_rel_ids = torch.zeros(self.num_node, self.max_neighbor, dtype=torch.long)
        neighbor_dir_ids = torch.zeros(self.num_node, self.max_neighbor, dtype=torch.long)
        neighbor_mask = torch.zeros(self.num_node, self.max_neighbor, dtype=torch.bool)

        cursor = torch.zeros(self.num_node, dtype=torch.long)

        E = edge_list.size(0)
        for i in range(E):
            h = int(head[i])
            t = int(tail[i])
            r = int(rel[i])

            rel_hist_out[h, r] += 1.0
            rel_hist_in[t, r] += 1.0

            pos_h = int(cursor[h].item())
            if pos_h < self.max_neighbor:
                neighbor_rel_ids[h, pos_h] = r
                neighbor_dir_ids[h, pos_h] = 1
                neighbor_mask[h, pos_h] = True
                cursor[h] += 1

            pos_t = int(cursor[t].item())
            if pos_t < self.max_neighbor:
                neighbor_rel_ids[t, pos_t] = r
                neighbor_dir_ids[t, pos_t] = 0
                neighbor_mask[t, pos_t] = True
                cursor[t] += 1

        self.rel_hist_in = rel_hist_in
        self.rel_hist_out = rel_hist_out
        self.neighbor_rel_ids = neighbor_rel_ids
        self.neighbor_dir_ids = neighbor_dir_ids
        self.neighbor_mask = neighbor_mask
        self._built = True

    def get_batch(self, head_index: torch.Tensor, device=None):
        if not self._built:
            raise RuntimeError("HeadLocalContextCacheProvider is not built yet")

        head_index = head_index.long().detach().to("cpu")
        batch = {
            "rel_hist_in": self.rel_hist_in[head_index],
            "rel_hist_out": self.rel_hist_out[head_index],
            "neighbor_rel_ids": self.neighbor_rel_ids[head_index],
            "neighbor_dir_ids": self.neighbor_dir_ids[head_index],
            "neighbor_mask": self.neighbor_mask[head_index],
        }

        if device is not None:
            for k in batch:
                batch[k] = batch[k].to(device, non_blocking=True)

        return batch
