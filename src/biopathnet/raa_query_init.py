
import torch

def load_raa_anchor_cache(cache_pt_path, device=None):
    pack = torch.load(cache_pt_path, map_location="cpu")
    if device is not None:
        for k in ["head_ids", "rel_ids", "anchor_ids", "anchor_scores", "anchor_mask"]:
            pack[k] = pack[k].to(device)
    return pack

def batch_lookup_rows(batch_head_ids, batch_rel_ids, pair_to_row):
    rows = []
    for h, r in zip(batch_head_ids.tolist(), batch_rel_ids.tolist()):
        rows.append(pair_to_row.get(f"{int(h)}\t{int(r)}", -1))
    return torch.tensor(rows, device=batch_head_ids.device, dtype=torch.long)

def _single_query_anchor_context(anchor_ids, anchor_scores, edge_src, edge_dst, edge_rel, relation_weight):
    device = relation_weight.device
    dtype = relation_weight.dtype
    dim = relation_weight.shape[1]

    ctx = torch.zeros(dim, device=device, dtype=dtype)
    total_w = torch.zeros((), device=device, dtype=dtype)

    used_anchor_n = 0
    used_edge_n = 0

    for aid, score in zip(anchor_ids.tolist(), anchor_scores.tolist()):
        if aid < 0:
            continue
        score = float(score)
        if score == 0.0:
            continue

        mask = (edge_src == aid) | (edge_dst == aid)
        if not mask.any():
            continue

        rel_ids = edge_rel[mask].long()
        rel_vec = relation_weight[rel_ids].mean(dim=0)

        ctx = ctx + score * rel_vec
        total_w = total_w + score
        used_anchor_n += 1
        used_edge_n += int(mask.sum().item())

    if total_w.item() > 0:
        ctx = ctx / total_w

    return ctx, used_anchor_n, used_edge_n

def build_anchor_context(batch_head_ids, batch_rel_ids, graph, relation_weight, pack):
    rows = batch_lookup_rows(batch_head_ids, batch_rel_ids, pack["pair_to_row"])
    valid = rows >= 0

    device = relation_weight.device
    dtype = relation_weight.dtype
    B = batch_head_ids.shape[0]
    D = relation_weight.shape[1]

    ctx = torch.zeros(B, D, device=device, dtype=dtype)

    edge_list = graph.edge_list.to(device)
    edge_src = edge_list[:, 0].long()
    edge_dst = edge_list[:, 1].long()
    edge_rel = edge_list[:, 2].long()

    cache_hit_n = int(valid.sum().item())
    nonzero_ctx_n = 0
    edge_hit_query_n = 0
    edge_hit_anchor_n = 0
    edge_hit_total_n = 0

    for bi, row in enumerate(rows.tolist()):
        if row < 0:
            continue

        a_ids = pack["anchor_ids"][row].to(device)
        a_scores = pack["anchor_scores"][row].to(device)
        a_mask = pack["anchor_mask"][row].to(device)

        a_ids = a_ids[a_mask]
        a_scores = a_scores[a_mask]

        if a_ids.numel() == 0:
            continue

        one_ctx, used_anchor_n, used_edge_n = _single_query_anchor_context(
            anchor_ids=a_ids,
            anchor_scores=a_scores,
            edge_src=edge_src,
            edge_dst=edge_dst,
            edge_rel=edge_rel,
            relation_weight=relation_weight,
        )
        ctx[bi] = one_ctx

        if used_anchor_n > 0:
            edge_hit_query_n += 1
            edge_hit_anchor_n += used_anchor_n
            edge_hit_total_n += used_edge_n
        if one_ctx.norm().item() > 0:
            nonzero_ctx_n += 1

    stats = {
        "batch_n": int(B),
        "cache_hit_n": cache_hit_n,
        "cache_hit_rate": float(valid.float().mean().item()),
        "nonzero_ctx_n": int(nonzero_ctx_n),
        "edge_hit_query_n": int(edge_hit_query_n),
        "edge_hit_anchor_n": int(edge_hit_anchor_n),
        "edge_hit_total_n": int(edge_hit_total_n),
    }
    return ctx, valid, stats

def fuse_query_init(q0, batch_head_ids, batch_rel_ids, graph, relation_weight, pack, alpha=0.1):
    ctx, valid, stats = build_anchor_context(
        batch_head_ids=batch_head_ids,
        batch_rel_ids=batch_rel_ids,
        graph=graph,
        relation_weight=relation_weight,
        pack=pack,
    )
    q0_prime = q0 + float(alpha) * ctx
    stats = dict(stats)
    stats["alpha"] = float(alpha)
    stats["q0_mean_norm"] = float(q0.norm(dim=1).mean().item())
    stats["ctx_mean_norm"] = float(ctx.norm(dim=1).mean().item())
    stats["q0_prime_mean_norm"] = float(q0_prime.norm(dim=1).mean().item())
    return q0_prime, ctx, valid, stats
