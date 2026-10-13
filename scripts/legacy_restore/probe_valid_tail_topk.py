import os
import types
import sys
import csv
import json
import math
import time
import math
import pprint
import random

import torch
import numpy as np
from torchdrug import core
from torchdrug.utils import comm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from biopathnet import dataset, layer, model, task, util  # noqa: F401

logger = None

def solver_load_bound(solver, checkpoint, load_optimizer=False):
    global logger
    logger.warning("Load checkpoint from %s" % checkpoint)
    checkpoint = os.path.expanduser(checkpoint)
    state = torch.load(checkpoint, map_location=solver.device)

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

    if load_optimizer and "optimizer" in state:
        solver.optimizer.load_state_dict(state["optimizer"])
        for opt_state in solver.optimizer.state.values():
            for k, v in opt_state.items():
                if isinstance(v, torch.Tensor):
                    opt_state[k] = v.to(solver.device)

    comm.synchronize()

def _to_triplet(x):
    if isinstance(x, torch.Tensor):
        return x.long()
    return torch.tensor(x, dtype=torch.long)

def _get_original_index(valid_set, i):
    if hasattr(valid_set, "indices"):
        return int(valid_set.indices[i])
    return int(i)

def _safe_vocab(vocab, idx):
    try:
        return str(vocab[int(idx)])
    except Exception:
        return str(int(idx))

@torch.no_grad()
def exact_tail_probe(solver, triplet, topk=20, chunk_size=2048, query_tag="q0"):
    task_obj = solver.model
    task_obj.eval()

    triplet = _to_triplet(triplet).to(solver.device)
    h, t, r = triplet.tolist()
    h = torch.tensor(h, device=solver.device, dtype=torch.long)
    t = torch.tensor(t, device=solver.device, dtype=torch.long)
    r = torch.tensor(r, device=solver.device, dtype=torch.long)

    # filtered mask for tail side, aligned to task.target() logic
    any_idx = -torch.ones(1, dtype=torch.long, device=solver.device)
    pattern = torch.stack([h.view(1), any_idx, r.view(1)], dim=-1)
    edge_index, num_t_truth = task_obj.graph.match(pattern)
    t_truth_index = task_obj.graph.edge_list[edge_index, 1]

    mask = torch.ones(task_obj.num_entity, dtype=torch.bool, device=solver.device)
    if getattr(task_obj, "remove_pos", True):
        mask[t_truth_index] = False

    if getattr(task_obj, "heterogeneous_evaluation", False):
        node_type = task_obj.fact_graph.node_type
        mask[node_type != node_type[t]] = False

    # exact positive score
    pos_score = task_obj.model(
        task_obj.fact_graph,
        h.view(1, 1),
        t.view(1, 1),
        r.view(1, 1),
        all_loss=None,
        metric=None,
    ).view(-1)[0].detach().cpu().item()
    family_ctx_gold_aux = _router_debug_to_jsonable(getattr(task_obj.model, "_last_family_ctx_aux", None))
    family_ctx_gold_debug = _router_debug_to_jsonable(getattr(task_obj.model, "_last_family_ctx_debug", None))

    num_entity = int(task_obj.num_entity)
    total_chunks = math.ceil(num_entity / chunk_size)
    logger.warning("[%s] tail-only exact probe: num_entity=%d chunk_size=%d total_chunks=%d",
                   query_tag, num_entity, chunk_size, total_chunks)

    parts = []
    tic = time.time()
    last_log = 0
    for chunk_id, start in enumerate(range(0, num_entity, chunk_size), start=1):
        end = min(start + chunk_size, num_entity)
        neg_index = torch.arange(start, end, device=solver.device)

        h_index = h.view(1, 1).expand(1, len(neg_index))
        t_index = neg_index.view(1, -1)
        r_index = r.view(1, 1).expand(1, len(neg_index))

        part = task_obj.model(
            task_obj.fact_graph,
            h_index,
            t_index,
            r_index,
            all_loss=None,
            metric=None,
        ).view(-1).detach().cpu()

        parts.append(part)

        # log every ~5% or last chunk
        pct = int(chunk_id * 100 / total_chunks)
        if pct >= last_log + 5 or chunk_id == total_chunks:
            elapsed = time.time() - tic
            logger.warning("[%s] chunks %d/%d (%d%%) elapsed=%.1fs",
                           query_tag, chunk_id, total_chunks, pct, elapsed)
            last_log = pct

    scores = torch.cat(parts, dim=0)
    mask_cpu = mask.detach().cpu()
    truth_cpu = t_truth_index.detach().cpu().tolist()

    # exact filtered rank aligned to task.evaluate()
    rank = int((((pos_score <= scores) & mask_cpu).sum().item()) + 1)

    # filtered topk candidates
    filtered_scores = scores.clone()
    filtered_scores[~mask_cpu] = float("-inf")
    k = min(int(topk), int(mask_cpu.sum().item()))
    if k > 0:
        top_scores, top_idx = torch.topk(filtered_scores, k=k)
        top_idx = top_idx.tolist()
        top_scores = [float(x) for x in top_scores.tolist()]
    else:
        top_idx, top_scores = [], []
    top20_idx = top_idx[:20]
    top20_scores = top_scores[:20]
    if top20_idx:
        probe_top20_index = torch.tensor(top20_idx, device=solver.device, dtype=torch.long)
        _ = task_obj.model(
            task_obj.fact_graph,
            h.view(1, 1).expand(1, len(probe_top20_index)),
            probe_top20_index.view(1, -1),
            r.view(1, 1).expand(1, len(probe_top20_index)),
            all_loss=None,
            metric=None,
        )
        family_ctx_top20_aux = _router_debug_to_jsonable(getattr(task_obj.model, "_last_family_ctx_aux", None))
        family_ctx_top20_debug = _router_debug_to_jsonable(getattr(task_obj.model, "_last_family_ctx_debug", None))
    else:
        family_ctx_top20_aux = None
        family_ctx_top20_debug = None

    result = {
        "head_id": int(h.item()),
        "tail_id": int(t.item()),
        "relation_id": int(r.item()),
        "gold_tail_score": float(pos_score),
        "gold_tail_filtered_rank": int(rank),
        "filtered_candidate_n": int(mask_cpu.sum().item()),
        "all_true_tail_ids_for_query": [int(x) for x in truth_cpu],
        "topk_filtered_tail_ids": [int(x) for x in top_idx],
        "topk_filtered_tail_scores": top_scores,
        "top20_tail_ids": [int(x) for x in top20_idx],
        "top20_tail_scores": top20_scores,
        "family_ctx_gold_aux": family_ctx_gold_aux,
        "family_ctx_gold_debug": family_ctx_gold_debug,
        "family_ctx_top20_aux": family_ctx_top20_aux,
        "family_ctx_top20_debug": family_ctx_top20_debug,
        "elapsed_sec": round(time.time() - tic, 3),
    }
    return result



def _router_debug_to_jsonable(obj):
    if obj is None:
        return None

    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[k] = _router_debug_to_jsonable(v)
        return out

    if isinstance(obj, (list, tuple)):
        return [_router_debug_to_jsonable(v) for v in obj]

    if isinstance(obj, torch.Tensor):
        x = obj.detach().cpu()
        if x.numel() == 0:
            return {
                "_kind": "tensor_summary",
                "shape": list(x.shape),
                "numel": 0,
            }
        if x.numel() == 1:
            v = x.item()
            if isinstance(v, bool):
                return bool(v)
            if isinstance(v, int):
                return int(v)
            return float(v)
        if x.ndim == 1 and x.numel() <= 32:
            vals = x.tolist()
            out = []
            for v in vals:
                if isinstance(v, bool):
                    out.append(bool(v))
                elif isinstance(v, int):
                    out.append(int(v))
                else:
                    out.append(float(v))
            return out
        xf = x.float()
        return {
            "_kind": "tensor_summary",
            "shape": list(x.shape),
            "mean": float(xf.mean().item()),
            "min": float(xf.min().item()),
            "max": float(xf.max().item()),
        }

    if isinstance(obj, (bool, int, float, str)):
        return obj

    return str(obj)

def _dump_router_debug_if_any(solver, logger):
    import json
    import os

    model = getattr(solver, "model", None)

    visited = set()
    found_with_attr = []
    found_nonnull = []
    router_like = []

    def walk(obj, path, depth):
        if obj is None or depth < 0:
            return
        oid = id(obj)
        if oid in visited:
            return
        visited.add(oid)

        cls = type(obj).__name__

        if hasattr(obj, "_last_router_debug"):
            val = getattr(obj, "_last_router_debug", None)
            found_with_attr.append({"path": path, "class": cls, "is_nonnull": val is not None})
            if val is not None:
                found_nonnull.append((path, val))

        if "router" in cls.lower() or "debug" in cls.lower():
            router_like.append({"path": path, "class": cls})

        # named_children for nn.Module
        if hasattr(obj, "named_children"):
            try:
                for name, child in obj.named_children():
                    walk(child, f"{path}.{name}", depth - 1)
            except Exception:
                pass

        # common wrapper attrs
        for name in ["model", "encoder", "decoder", "predictor", "network", "task", "backbone"]:
            try:
                child = getattr(obj, name, None)
            except Exception:
                child = None
            if child is not None:
                walk(child, f"{path}.{name}", depth - 1)

    walk(model, "solver.model", 4)

    out_dir = getattr(solver, "working_dir", None) or getattr(solver, "output_dir", None) or os.getcwd()

    probe_state = {
        "env_BIOPATHNET_COLLECT_ROUTER_DEBUG": os.environ.get("BIOPATHNET_COLLECT_ROUTER_DEBUG"),
        "solver_model_class": type(model).__name__ if model is not None else None,
        "found_with__last_router_debug": found_with_attr,
        "router_like_objects": router_like,
        "chosen_debug_source": found_nonnull[0][0] if found_nonnull else None,
        "debug_found": bool(found_nonnull),
    }

    state_path = os.path.join(out_dir, "router_debug_probe_state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(probe_state, f, ensure_ascii=False, indent=2)
    logger.warning(f"WROTE {state_path}")

    if not found_nonnull:
        logger.warning("ROUTER_DEBUG_MISSING")
        return

    dbg = found_nonnull[0][1]
    out_path = os.path.join(out_dir, "router_debug.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(_router_debug_to_jsonable(dbg), f, ensure_ascii=False, indent=2)
    logger.warning(f"WROTE {out_path}")


def _maybe_override_router_residual_alpha(solver, logger):
    alpha_str = os.environ.get("ROUTER_FORCE_RESIDUAL_ALPHA", "").strip()
    if not alpha_str:
        return
    alpha = float(alpha_str)
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"ROUTER_FORCE_RESIDUAL_ALPHA must be in (0,1), got {alpha}")
    logit = math.log(alpha / (1.0 - alpha))

    target = None
    for mod in solver.model.modules():
        if mod.__class__.__name__ == "RelationGuidedEvidenceRouter" and hasattr(mod, "residual_logit"):
            target = mod
            break

    if target is None:
        raise RuntimeError("RelationGuidedEvidenceRouter with residual_logit not found in solver.model")

    with torch.no_grad():
        target.residual_logit.fill_(float(logit))

    logger.warning(
        "ROUTER_RESIDUAL_OVERRIDE_APPLIED alpha=%.6f logit=%.6f",
        alpha, logit
    )



def _resolve_evidence_router(obj):
    seen = set()
    queue = [obj]
    while queue:
        cur = queue.pop(0)
        if cur is None:
            continue
        cid = id(cur)
        if cid in seen:
            continue
        seen.add(cid)
        if hasattr(cur, "evidence_router") and getattr(cur, "evidence_router") is not None:
            return getattr(cur, "evidence_router")
        for name in ("model", "module", "predictor", "task", "net"):
            if hasattr(cur, name):
                queue.append(getattr(cur, name))
    raise RuntimeError("probe meta override: evidence_router not found after solver_load_bound(...)")

def _apply_probe_meta_override(owner, mode):
    mode = (mode or "").strip().lower()
    if not mode:
        return

    if mode in ("hop", "hop_only", "1,0", "[1,0]", "[1, 0]"):
        keep_idx = 0
        tag = "hop_only"
    elif mode in ("type", "type_only", "0,1", "[0,1]", "[0, 1]"):
        keep_idx = 1
        tag = "type_only"
    else:
        raise ValueError(f"unsupported ROUTER_FORCE_META={mode!r}; use hop or type")

    router = _resolve_evidence_router(owner)
    if not hasattr(router, "meta_router") or router.meta_router is None:
        raise RuntimeError("probe meta override: meta_router not found on evidence_router")

    meta_router = router.meta_router
    if not hasattr(meta_router, "_probe_meta_orig_forward"):
        meta_router._probe_meta_orig_forward = meta_router.forward

    def _forced_meta_forward(self, x):
        ref = self._probe_meta_orig_forward(x)
        if ref.ndim != 2 or ref.shape[1] != 2:
            raise RuntimeError(
                f"probe meta override expects meta_router output shape [B,2], got {tuple(ref.shape)}"
            )
        out = ref.new_full(ref.shape, -1e9)
        out[:, keep_idx] = 0.0
        return out

    meta_router.forward = types.MethodType(_forced_meta_forward, meta_router)
    print(f"[probe meta override] ROUTER_FORCE_META={tag} -> fixed meta weights = {[1,0] if keep_idx == 0 else [0,1]}")

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
    probe_checkpoint = cfg.checkpoint
    cfg.checkpoint = None
    if isinstance(cfg.engine.gpus, int):
        cfg.engine.gpus = [cfg.engine.gpus]
    _orig_solver_load = util.solver_load
    def _probe_solver_load_passthrough(solver, checkpoint, *args, **kwargs):
        if checkpoint is None:
            logger.warning('Probe bypass: skip util.solver_load because checkpoint is None')
            return
        return _orig_solver_load(solver, checkpoint, *args, **kwargs)
    util.solver_load = _probe_solver_load_passthrough
    try:
        solver = util.build_solver(cfg, ds)
    finally:
        util.solver_load = _orig_solver_load
    cfg.checkpoint = probe_checkpoint
    solver_load_bound(solver, probe_checkpoint, load_optimizer=False)

    if not hasattr(cfg, "checkpoint"):
        raise ValueError("cfg.checkpoint is required")

    solver_load_bound(solver, cfg.checkpoint, load_optimizer=False)
    forced_meta_env = os.getenv('ROUTER_FORCE_META', '').strip()
    if forced_meta_env:
        _apply_probe_meta_override(solver, forced_meta_env)
    _maybe_override_router_residual_alpha(solver, logger)

    valid_offset = int(os.environ.get("VALID_OFFSET", "0"))
    query_limit = int(os.environ.get("QUERY_LIMIT", "1"))
    tail_chunk = int(os.environ.get("TAIL_CHUNK", "2048"))
    topk = int(os.environ.get("TOPK", "20"))

    entity_vocab = getattr(ds, "entity_vocab", None)
    relation_vocab = getattr(ds, "relation_vocab", None)

    valid_len = len(solver.valid_set)
    end = min(valid_offset + query_limit, valid_len)
    if valid_offset >= valid_len:
        raise ValueError(f"VALID_OFFSET={valid_offset} >= len(valid_set)={valid_len}")

    valid_offset = int(os.getenv("PROBE_VALID_OFFSET", str(valid_offset)))
    query_limit = int(os.getenv("PROBE_QUERY_LIMIT", str(query_limit)))
    topk = int(os.getenv("PROBE_TOPK", str(topk)))
    end = min(valid_offset + query_limit, valid_len)
    if valid_offset >= valid_len:
        raise ValueError(f"PROBE_VALID_OFFSET={valid_offset} >= len(valid_set)={valid_len}")
    logger.warning("PROBE_CONFIG = %s", json.dumps({
        "valid_len": valid_len,
        "valid_offset": valid_offset,
        "query_limit": query_limit,
        "tail_chunk": tail_chunk,
        "topk": topk,
    }, ensure_ascii=False))

    summary_rows = []
    detail_path = os.path.join(working_dir, "valid_tail_probe_details.jsonl")
    topk_path = os.path.join(working_dir, "valid_tail_probe_topk.tsv")
    summary_path = os.path.join(working_dir, "valid_tail_probe_summary.tsv")

    with open(detail_path, "w", encoding="utf-8") as f_detail, \
         open(topk_path, "w", encoding="utf-8", newline="") as f_topk:
        topk_writer = csv.writer(f_topk, delimiter="\t")
        topk_writer.writerow([
            "valid_local_index", "valid_original_index",
            "head_id", "head_name", "relation_id", "relation_name",
            "gold_tail_id", "gold_tail_name", "gold_tail_filtered_rank", "gold_tail_score",
            "row_type", "topk_rank", "pred_tail_id", "pred_tail_name", "pred_score"
        ])

        for local_i in range(valid_offset, end):
            original_i = _get_original_index(solver.valid_set, local_i)
            triplet = _to_triplet(solver.valid_set[local_i])
            h, t, r = [int(x) for x in triplet.tolist()]

            query_tag = f"valid[{local_i}]"
            logger.warning("[%s] original_index=%d head=%s relation=%s tail=%s",
                           query_tag,
                           original_i,
                           _safe_vocab(entity_vocab, h) if entity_vocab is not None else h,
                           _safe_vocab(relation_vocab, r) if relation_vocab is not None else r,
                           _safe_vocab(entity_vocab, t) if entity_vocab is not None else t)

            res = exact_tail_probe(
                solver=solver,
                triplet=triplet,
                topk=topk,
                chunk_size=tail_chunk,
                query_tag=query_tag,
            )

            enriched = {
                "valid_local_index": int(local_i),
                "valid_original_index": int(original_i),
                "head_name": _safe_vocab(entity_vocab, h) if entity_vocab is not None else str(h),
                "relation_name": _safe_vocab(relation_vocab, r) if relation_vocab is not None else str(r),
                "gold_tail_name": _safe_vocab(entity_vocab, t) if entity_vocab is not None else str(t),
                **res,
                "all_true_tail_names_for_query": [
                    _safe_vocab(entity_vocab, x) if entity_vocab is not None else str(x)
                    for x in res["all_true_tail_ids_for_query"]
                ],
                "topk_filtered_tail_names": [
                    _safe_vocab(entity_vocab, x) if entity_vocab is not None else str(x)
                    for x in res["topk_filtered_tail_ids"]
                ],
            }

            f_detail.write(json.dumps(enriched, ensure_ascii=False) + "\n")
            f_detail.flush()

            topk_writer.writerow([
                local_i, original_i,
                h, enriched["head_name"],
                r, enriched["relation_name"],
                t, enriched["gold_tail_name"],
                res["gold_tail_filtered_rank"], res["gold_tail_score"],
                "gold", "",
                t,
                enriched["gold_tail_name"],
                res["gold_tail_score"],
            ])
            f_topk.flush()

            for rank_i, (pred_id, pred_score) in enumerate(
                zip(res["topk_filtered_tail_ids"], res["topk_filtered_tail_scores"]), start=1
            ):
                topk_writer.writerow([
                    local_i, original_i,
                    h, enriched["head_name"],
                    r, enriched["relation_name"],
                    t, enriched["gold_tail_name"],
                    res["gold_tail_filtered_rank"], res["gold_tail_score"],
                    "topk", rank_i,
                    pred_id,
                    _safe_vocab(entity_vocab, pred_id) if entity_vocab is not None else str(pred_id),
                    pred_score,
                ])
                f_topk.flush()

            summary_rows.append({
                "valid_local_index": local_i,
                "valid_original_index": original_i,
                "head_id": h,
                "head_name": enriched["head_name"],
                "relation_id": r,
                "relation_name": enriched["relation_name"],
                "gold_tail_id": t,
                "gold_tail_name": enriched["gold_tail_name"],
                "gold_tail_filtered_rank": res["gold_tail_filtered_rank"],
                "hit_at_1": int(res["gold_tail_filtered_rank"] <= 1),
                "hit_at_10": int(res["gold_tail_filtered_rank"] <= 10),
                "hit_at_100": int(res["gold_tail_filtered_rank"] <= 100),
                "filtered_candidate_n": res["filtered_candidate_n"],
                "gold_tail_score": res["gold_tail_score"],
                "elapsed_sec": res["elapsed_sec"],
            })

            logger.warning("[%s] DONE rank=%d hit@10=%d hit@100=%d elapsed=%.1fs",
                           query_tag,
                           res["gold_tail_filtered_rank"],
                           int(res["gold_tail_filtered_rank"] <= 10),
                           int(res["gold_tail_filtered_rank"] <= 100),
                           res["elapsed_sec"])
            if solver.device.type == "cuda":
                torch.cuda.empty_cache()

    with open(summary_path, "w", encoding="utf-8", newline="") as f_sum:
        logger.warning("SUMMARY_ROWS_N = %d", len(summary_rows))
        _dump_router_debug_if_any(solver, logger)
        if not summary_rows:
            logger.warning("NO_SUMMARY_ROWS; skip summary TSV write")
            return
        writer = csv.DictWriter(f_sum, fieldnames=list(summary_rows[0].keys()), delimiter="\t")
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)

    logger.warning("WROTE %s", detail_path)
    logger.warning("WROTE %s", topk_path)
    logger.warning("WROTE %s", summary_path)

    print(summary_path)
    print(topk_path)
    print(detail_path)

if __name__ == "__main__":
    main()
