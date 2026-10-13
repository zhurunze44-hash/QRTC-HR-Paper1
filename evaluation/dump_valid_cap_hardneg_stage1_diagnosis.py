import os
import sys
import json
import random
import pprint
from collections import Counter, defaultdict, deque

import torch
import numpy as np
from torch.utils import data as torch_data

from torchdrug import core, utils
from torchdrug.utils import comm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from biopathnet import dataset, layer, model, task, util  # noqa: F401

logger = None


REL_NAMES = {
    0: "interacts-with",
    1: "controls-state-change-of",
    2: "in-complex-with",
    3: "controls-transport-of",
    4: "catalysis-precedes",
    5: "controls-expression-of",
    6: "controls-phosphorylation-of",
    7: "ceRNA or sponge",
    8: "expression association",
    9: "epigenetic regulation",
    10: "interact with protein",
    11: "interact with mRNA",
    12: "transcriptional regulation",
}


def solver_load_bound(solver, checkpoint):
    global logger
    logger.warning("Load checkpoint from %s" % checkpoint)
    state = torch.load(os.path.expanduser(checkpoint), map_location=solver.device)
    if "model" not in state:
        raise KeyError("checkpoint missing 'model' key")

    for k in [
        "fact_graph",
        "fact_graph_supervision",
        "graph",
        "train_graph",
        "valid_graph",
        "test_graph",
        "full_valid_graph",
        "full_test_graph",
    ]:
        state["model"].pop(k, None)

    incompatible = solver.model.load_state_dict(state["model"], strict=False)
    logger.warning("missing_keys = %s", list(incompatible.missing_keys))
    logger.warning("unexpected_keys = %s", list(incompatible.unexpected_keys))
    comm.synchronize()


def build_undirected_adj(edge_list):
    adj = defaultdict(list)
    edge_cpu = edge_list[:, :2].detach().cpu().tolist()
    for h, t in edge_cpu:
        h = int(h)
        t = int(t)
        adj[h].append(t)
        adj[t].append(h)
    return adj


def bounded_hop_distance(adj, source, target, max_hop=3):
    source = int(source)
    target = int(target)
    if source == target:
        return 0
    seen = {source}
    q = deque([(source, 0)])
    while q:
        node, dist = q.popleft()
        if dist >= max_hop:
            continue
        nd = dist + 1
        for nb in adj.get(node, []):
            if nb == target:
                return nd
            if nb not in seen:
                seen.add(nb)
                q.append((nb, nd))
    return max_hop + 1


def safe_mean(xs):
    return float(sum(xs) / len(xs)) if xs else None


def summarize_records(records):
    n = len(records)
    if n == 0:
        return {}

    deltas = [r["delta_pos_minus_neg"] for r in records]
    neg_above = [d < 0 for d in deltas]
    hop_counter = Counter(r["hop_bucket"] for r in records)
    type_ok = [bool(r["type_compatible"]) for r in records]

    return {
        "n_hardneg": n,
        "delta_pos_minus_neg_mean": safe_mean(deltas),
        "delta_pos_minus_neg_median": float(np.median(deltas)) if deltas else None,
        "delta_pos_minus_neg_min": float(min(deltas)) if deltas else None,
        "delta_pos_minus_neg_max": float(max(deltas)) if deltas else None,
        "neg_score_ge_pos_count": int(sum(neg_above)),
        "neg_score_ge_pos_rate": float(sum(neg_above) / n),
        "type_compatible_count": int(sum(type_ok)),
        "type_compatible_rate": float(sum(type_ok) / n),
        "hop_bucket_counts": dict(hop_counter),
        "hop_le_1_rate": float(sum(1 for r in records if r["hop_distance"] <= 1) / n),
        "hop_le_2_rate": float(sum(1 for r in records if r["hop_distance"] <= 2) / n),
        "hop_le_3_rate": float(sum(1 for r in records if r["hop_distance"] <= 3) / n),
    }


def main():
    global logger
    args, vars = util.parse_args()
    cfg = util.load_config(args.config, context=vars)
    working_dir = util.create_working_directory(cfg)

    seed_rank = int(args.seed) + int(comm.get_rank())
    random.seed(int(args.seed))
    np.random.seed(int(args.seed))
    torch.manual_seed(seed_rank)

    logger = util.get_root_logger()
    logger.warning("Working directory: %s", working_dir)
    logger.warning("Config file: %s", args.config)
    logger.warning("Seed: %d", seed_rank)
    logger.warning(pprint.pformat(cfg))

    ds = core.Configurable.load_config_dict(cfg.dataset)
    solver = util.build_solver(cfg, ds)

    if not hasattr(cfg, "checkpoint"):
        raise ValueError("cfg.checkpoint is required")

    solver_load_bound(solver, cfg.checkpoint)

    valid_cap = int(os.environ.get("VALID_CAP", "32"))
    eval_bs = int(os.environ.get("EVAL_BATCH_SIZE", "1"))
    topk = int(os.environ.get("HARDNEG_TOPK", "50"))
    random_neg_samples = int(os.environ.get("RANDOM_NEG_SAMPLES", "2048"))

    original_valid = solver.valid_set
    cap = min(valid_cap, len(original_valid))
    solver.valid_set = torch_data.Subset(original_valid, list(range(cap)))
    solver.batch_size = eval_bs

    model_obj = solver.model
    model_obj.eval()
    if hasattr(model_obj, "split"):
        model_obj.split = "valid"

    fact_graph = model_obj.fact_graph
    node_type = fact_graph.node_type.detach().cpu()
    num_entity = int(model_obj.num_entity)

    logger.warning("Build undirected adjacency from fact_graph")
    adj = build_undirected_adj(fact_graph.edge_list)
    logger.warning("Adjacency built: source_nodes=%d", len(adj))

    out_jsonl = os.path.join(working_dir, "valid_cap_hardneg_stage1.jsonl")
    out_summary = os.path.join(working_dir, "valid_cap_hardneg_stage1_summary.json")

    dataloader = torch_data.DataLoader(
        solver.valid_set,
        batch_size=solver.batch_size,
        shuffle=False,
        num_workers=solver.num_worker,
    )

    all_hardneg_records = []
    relation_hardneg_records = defaultdict(list)
    query_summaries = []
    rel_counter = Counter()
    random_type_stats = defaultdict(lambda: {"ok": 0, "total": 0})

    with open(out_jsonl, "w", encoding="utf-8") as f:
        with torch.no_grad():
            row_offset = 0
            for batch in dataloader:
                if solver.device.type == "cuda":
                    batch = utils.cuda(batch, device=solver.device)

                pred = model_obj.predict(batch, all_loss=None, metric={})
                mask, target = model_obj.target(batch)

                pos_pred = pred.gather(-1, target.unsqueeze(-1))
                if model_obj.filtered_ranking:
                    ranking = torch.sum((pos_pred <= pred) & mask, dim=-1) + 1
                else:
                    ranking = torch.sum(pos_pred <= pred, dim=-1) + 1

                pred_cpu = pred.detach().cpu()
                mask_cpu = mask.detach().cpu()
                target_cpu = target.detach().cpu()
                pos_score_cpu = pos_pred.squeeze(-1).detach().cpu()
                rank_cpu = ranking.detach().cpu()
                batch_cpu = batch.detach().cpu()

                bs = len(batch_cpu)
                for i in range(bs):
                    cap_row = row_offset + i
                    try:
                        global_index = int(original_valid.indices[cap_row])
                    except Exception:
                        global_index = cap_row

                    h, t, r = [int(x) for x in batch_cpu[i].tolist()]
                    rel_name = REL_NAMES.get(r, f"rel_{r}")
                    rel_counter[rel_name] += 1

                    rec = {
                        "cap_row": cap_row,
                        "global_index": global_index,
                        "head": h,
                        "tail": t,
                        "relation": r,
                        "relation_name": rel_name,
                        "tail_positive_id": int(target_cpu[i, 0]),
                        "head_positive_id": int(target_cpu[i, 1]),
                        "tail_positive_score": float(pos_score_cpu[i, 0]),
                        "head_positive_score": float(pos_score_cpu[i, 1]),
                        "tail_positive_rank": int(rank_cpu[i, 0]),
                        "head_positive_rank": int(rank_cpu[i, 1]),
                        "topk": topk,
                    }

                    query_hard_records = []

                    for side_idx, side in [(0, "tail"), (1, "head")]:
                        score = pred_cpu[i, side_idx].clone()
                        valid_mask = mask_cpu[i, side_idx].bool()

                        positive_id = int(target_cpu[i, side_idx])
                        positive_type = int(node_type[positive_id])
                        pos_score = float(pos_score_cpu[i, side_idx])

                        # Random baseline: type compatibility among random all-entity negatives.
                        rand_ids = torch.randint(0, num_entity, (random_neg_samples,))
                        rand_ok = int((node_type[rand_ids] == positive_type).sum().item())
                        random_type_stats[side]["ok"] += rand_ok
                        random_type_stats[side]["total"] += random_neg_samples

                        # Hard negatives are selected from filtered valid candidates.
                        score[~valid_mask] = float("-inf")
                        k = min(topk, int(valid_mask.sum().item()))
                        vals, ids = torch.topk(score, k=k)

                        hard_negs = []
                        for rank_pos, (cid, val) in enumerate(zip(ids.tolist(), vals.tolist()), start=1):
                            cid = int(cid)
                            val = float(val)
                            cand_type = int(node_type[cid])
                            type_compatible = cand_type == positive_type
                            source = h if side == "tail" else t
                            hop = bounded_hop_distance(adj, source, cid, max_hop=3)
                            hop_bucket = str(hop) if hop <= 3 else ">3"
                            delta = pos_score - val

                            hn = {
                                "side": side,
                                "hardneg_rank_within_topk": rank_pos,
                                "candidate_id": cid,
                                "score": val,
                                "positive_score": pos_score,
                                "delta_pos_minus_neg": float(delta),
                                "neg_score_ge_pos": bool(delta < 0),
                                "source_id_for_hop": int(source),
                                "hop_distance": int(hop),
                                "hop_bucket": hop_bucket,
                                "candidate_type": cand_type,
                                "positive_type": positive_type,
                                "type_compatible": bool(type_compatible),
                            }
                            hard_negs.append(hn)

                            flat_hn = {
                                "cap_row": cap_row,
                                "global_index": global_index,
                                "relation": r,
                                "relation_name": rel_name,
                                **hn,
                            }
                            all_hardneg_records.append(flat_hn)
                            relation_hardneg_records[rel_name].append(flat_hn)
                            query_hard_records.append(flat_hn)

                        rec[f"{side}_hard_negatives"] = hard_negs

                    rec["query_hardneg_summary"] = summarize_records(query_hard_records)
                    query_summaries.append(rec["query_hardneg_summary"])
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    f.flush()

                row_offset += bs

    global_summary = summarize_records(all_hardneg_records)
    relation_summary = {
        rel: summarize_records(records)
        for rel, records in sorted(relation_hardneg_records.items())
    }

    random_type_summary = {}
    for side, d in sorted(random_type_stats.items()):
        total = max(1, d["total"])
        random_type_summary[side] = {
            "random_type_compatible_count": int(d["ok"]),
            "random_type_sample_count": int(d["total"]),
            "random_type_compatible_rate": float(d["ok"] / total),
        }

    summary = {
        "valid_cap_requested": valid_cap,
        "valid_cap_used": cap,
        "eval_batch_size": eval_bs,
        "topk": topk,
        "random_neg_samples_per_query_side": random_neg_samples,
        "n_query": cap,
        "relation_query_counts": dict(rel_counter),
        "global_hardneg_summary": global_summary,
        "relation_hardneg_summary": relation_summary,
        "random_type_compatibility_baseline": random_type_summary,
        "config": args.config,
        "checkpoint": cfg.checkpoint,
        "hardneg_stage1_jsonl": out_jsonl,
    }

    with open(out_summary, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    logger.warning("WROTE %s", out_jsonl)
    logger.warning("WROTE %s", out_summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
