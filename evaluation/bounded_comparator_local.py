#!/usr/bin/env python
import os
import sys
import json
import copy
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torchdrug import core

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from biopathnet import dataset, layer, model, task, util  # noqa: F401


def resolve_col(df, candidates, label):
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(f"missing {label}; available columns = {list(df.columns)}")


def unique_keep_order(xs):
    out, seen = [], set()
    for x in xs:
        x = int(x)
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def hit_at(ranks, k):
    if len(ranks) == 0:
        return 0.0
    return float(np.mean(np.array(ranks) <= k))


def build_solver_official(config_path, checkpoint, output_dir, gpus="[0]"):
    cfg = util.load_config(config_path, context={"gpus": gpus})
    cfg = copy.deepcopy(cfg)
    cfg.output_dir = str(output_dir)
    cfg.checkpoint = str(checkpoint)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    util.create_working_directory(cfg)
    logger = util.get_root_logger()
    logger.warning("BOUNDED_COMPARATOR_ON")
    logger.warning("CONFIG=%s", config_path)
    logger.warning("CHECKPOINT=%s", checkpoint)
    logger.warning("RG_MIN_ENABLE=%s", os.environ.get("RG_MIN_ENABLE", "0"))
    logger.warning("RG_MIN_GAMMA=%s", os.environ.get("RG_MIN_GAMMA", "NA"))
    logger.warning("RG_MIN_ROUTER_HIDDEN_DIM=%s", os.environ.get("RG_MIN_ROUTER_HIDDEN_DIM", "NA"))

    ds = core.Configurable.load_config_dict(cfg.dataset)
    solver = util.build_solver(cfg, ds)
    solver.model.split = "valid"
    solver.model.eval()

    return cfg, ds, solver, logger


@torch.no_grad()
def bounded_score_query(solver, head_id, relation_id, gold_tail_id, cand_ids, chunk_size=256):
    task_obj = solver.model           # task wrapper
    net = task_obj.model              # underlying NBFNet / BF backbone
    graph = task_obj.fact_graph       # official fact graph used by task
    device = solver.device

    gold_tail_id = int(gold_tail_id)
    cand_ids = unique_keep_order([x for x in cand_ids if int(x) != gold_tail_id])
    ordered_ids = [gold_tail_id] + cand_ids

    rows = []
    for st in range(0, len(ordered_ids), chunk_size):
        tails = ordered_ids[st: st + chunk_size]
        h = torch.tensor([[int(head_id)] * len(tails)], dtype=torch.long, device=device)
        t = torch.tensor([tails], dtype=torch.long, device=device)
        r = torch.tensor([[int(relation_id)] * len(tails)], dtype=torch.long, device=device)

        score = net(graph, h, t, r).view(-1).detach().float().cpu().numpy()
        for cand_id, s in zip(tails, score.tolist()):
            rows.append({
                "cand_id": int(cand_id),
                "score": float(s),
                "is_gold": int(int(cand_id) == gold_tail_id),
            })

    df = pd.DataFrame(rows).drop_duplicates(subset=["cand_id"], keep="first")
    df = df.sort_values(["score", "cand_id"], ascending=[False, True], kind="mergesort").reset_index(drop=True)
    df["bounded_rank"] = np.arange(1, len(df) + 1)

    gold_rank = int(df.loc[df["is_gold"] == 1, "bounded_rank"].iloc[0])
    return df, gold_rank


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--query-pool", required=True)
    ap.add_argument("--candidate-pool", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--query-id", default=None)
    ap.add_argument("--query-limit", type=int, default=None)
    ap.add_argument("--chunk-size", type=int, default=256)
    ap.add_argument("--gpus", default="[0]")
    args = ap.parse_args()

    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    qdf = pd.read_csv(args.query_pool, sep="\t")
    cdf = pd.read_csv(args.candidate_pool, sep="\t")

    qid_col = resolve_col(qdf, ["query_id", "id"], "query_id")
    head_col = resolve_col(qdf, ["head_id", "query_head_id", "h_id"], "head_id")
    rel_col = resolve_col(qdf, ["relation_id", "query_relation_id", "r_id"], "relation_id")
    gold_col = resolve_col(qdf, ["gold_tail_id", "gold_id", "tail_id", "target_id"], "gold_tail_id")

    cand_qid_col = resolve_col(cdf, ["query_id", "id"], "candidate.query_id")
    cand_id_col = resolve_col(cdf, ["cand_id", "candidate_id", "tail_id", "entity_id"], "candidate.cand_id")

    qdf[qid_col] = qdf[qid_col].astype(str)
    cdf[cand_qid_col] = cdf[cand_qid_col].astype(str)

    if args.query_id is not None:
        qdf = qdf[qdf[qid_col] == str(args.query_id)].copy()

    qdf = qdf.sort_values(qid_col, kind="mergesort").reset_index(drop=True)
    if args.query_limit is not None:
        qdf = qdf.head(int(args.query_limit)).copy()

    cfg, ds, solver, logger = build_solver_official(
        config_path=args.config,
        checkpoint=args.checkpoint,
        output_dir=out_dir,
        gpus=args.gpus,
    )

    entity_vocab = list(ds.entity_vocab)
    relation_vocab = list(ds.relation_vocab)

    per_candidate = []
    per_query = []

    for _, row in qdf.iterrows():
        query_id = str(row[qid_col])
        head_id = int(row[head_col])
        relation_id = int(row[rel_col])
        gold_tail_id = int(row[gold_col])

        cand_ids = cdf.loc[cdf[cand_qid_col] == query_id, cand_id_col].astype(int).tolist()
        if len(cand_ids) == 0:
            raise ValueError(f"query_id={query_id} has no candidates in shared candidate pool")

        score_df, gold_rank = bounded_score_query(
            solver=solver,
            head_id=head_id,
            relation_id=relation_id,
            gold_tail_id=gold_tail_id,
            cand_ids=cand_ids,
            chunk_size=args.chunk_size,
        )

        score_df.insert(0, "query_id", query_id)
        score_df.insert(1, "head_id", head_id)
        score_df.insert(2, "relation_id", relation_id)
        score_df.insert(3, "gold_tail_id", gold_tail_id)

        if head_id < len(entity_vocab):
            score_df["head_name"] = entity_vocab[head_id]
        if relation_id < len(relation_vocab):
            score_df["relation_name"] = relation_vocab[relation_id]
        score_df["gold_tail_name"] = entity_vocab[gold_tail_id] if gold_tail_id < len(entity_vocab) else None
        score_df["cand_name"] = score_df["cand_id"].map(lambda x: entity_vocab[x] if int(x) < len(entity_vocab) else None)

        per_candidate.append(score_df)

        per_query.append({
            "query_id": query_id,
            "head_id": head_id,
            "relation_id": relation_id,
            "gold_tail_id": gold_tail_id,
            "candidate_n_in_bounded_pool": int(len(score_df)),
            "gold_rank": int(gold_rank),
            "mrr": float(1.0 / gold_rank),
            "hit@1": int(gold_rank <= 1),
            "hit@3": int(gold_rank <= 3),
            "hit@10": int(gold_rank <= 10),
            "hit@20": int(gold_rank <= 20),
            "hit@50": int(gold_rank <= 50),
            "hit@100": int(gold_rank <= 100),
            "head_name": entity_vocab[head_id] if head_id < len(entity_vocab) else None,
            "relation_name": relation_vocab[relation_id] if relation_id < len(relation_vocab) else None,
            "gold_tail_name": entity_vocab[gold_tail_id] if gold_tail_id < len(entity_vocab) else None,
        })

        logger.warning(
            "[bounded] query_id=%s head=%s rel=%s gold=%s gold_rank=%d pool_n=%d",
            query_id, head_id, relation_id, gold_tail_id, gold_rank, len(score_df)
        )

    cand_df = pd.concat(per_candidate, ignore_index=True) if per_candidate else pd.DataFrame()
    pq_df = pd.DataFrame(per_query)

    cand_path = out_dir / "per_candidate_scores.tsv"
    pq_path = out_dir / "per_query_summary.tsv"
    summary_path = out_dir / "bounded_summary.json"

    cand_df.to_csv(cand_path, sep="\t", index=False)
    pq_df.to_csv(pq_path, sep="\t", index=False)

    ranks = pq_df["gold_rank"].tolist() if len(pq_df) else []
    summary = {
        "checkpoint": str(args.checkpoint),
        "query_n": int(len(pq_df)),
        "mean_mrr": float(np.mean([1.0 / r for r in ranks])) if ranks else None,
        "mean_rank": float(np.mean(ranks)) if ranks else None,
        "median_rank": float(np.median(ranks)) if ranks else None,
        "hit@1": hit_at(ranks, 1),
        "hit@3": hit_at(ranks, 3),
        "hit@10": hit_at(ranks, 10),
        "hit@20": hit_at(ranks, 20),
        "hit@50": hit_at(ranks, 50),
        "hit@100": hit_at(ranks, 100),
        "candidate_n_per_query_min": int(pq_df["candidate_n_in_bounded_pool"].min()) if len(pq_df) else None,
        "candidate_n_per_query_max": int(pq_df["candidate_n_in_bounded_pool"].max()) if len(pq_df) else None,
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("DONE")
    print(f"PER_CANDIDATE={cand_path}")
    print(f"PER_QUERY={pq_path}")
    print(f"SUMMARY={summary_path}")


if __name__ == "__main__":
    main()
