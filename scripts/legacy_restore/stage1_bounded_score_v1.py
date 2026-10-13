import argparse
import json
from pathlib import Path

import pandas as pd
import torch
import yaml


def normalize_columns(df, mapping):
    cols = {c.lower(): c for c in df.columns}
    out = {}
    for target, aliases in mapping.items():
        found = None
        for a in aliases:
            if a.lower() in cols:
                found = cols[a.lower()]
                break
        if found is None:
            raise KeyError(
                f"missing required column for {target}; "
                f"candidates={aliases}; actual={list(df.columns)}"
            )
        out[target] = df[found]
    return pd.DataFrame(out)


def build_solver(cfg):
    from torchdrug import core

    dataset = core.Configurable.load_config_dict(cfg["dataset"])

    train_set = valid_set = test_set = None
    for name in ["split", "get_split", "split_dataset"]:
        fn = getattr(dataset, name, None)
        if callable(fn):
            out = fn()
            if isinstance(out, (list, tuple)) and len(out) >= 3:
                train_set, valid_set, test_set = out[:3]
                break

    if train_set is None:
        for names in [("train_set", "valid_set", "test_set"), ("train", "valid", "test")]:
            if all(hasattr(dataset, n) for n in names):
                train_set, valid_set, test_set = [getattr(dataset, n) for n in names]
                break

    if train_set is None:
        raise RuntimeError("cannot recover dataset splits automatically")

    task = core.Configurable.load_config_dict(cfg["task"])
    solver = core.Engine(
        task,
        train_set,
        valid_set,
        test_set,
        **cfg["engine"],
    )
    return dataset, solver


def load_checkpoint(solver, ckpt):
    if hasattr(solver, "load"):
        solver.load(ckpt)
        return
    state = torch.load(ckpt, map_location="cpu")
    if isinstance(state, dict) and "model" in state:
        solver.model.load_state_dict(state["model"], strict=False)
    else:
        solver.model.load_state_dict(state, strict=False)


def get_graph(task, model):
    for obj in [task, model]:
        for name in ["fact_graph", "graph"]:
            if hasattr(obj, name):
                g = getattr(obj, name)
                if g is not None:
                    return g
    raise RuntimeError("cannot find fact_graph / graph on task or model")


def get_device(model):
    try:
        return next(model.parameters()).device
    except StopIteration:
        return torch.device("cpu")


def call_model(model, graph, h_id, r_id, cand_ids, device):
    model.eval()
    cand_ids = list(map(int, cand_ids))

    h = torch.tensor([int(h_id)], dtype=torch.long, device=device)
    r = torch.tensor([int(r_id)], dtype=torch.long, device=device)
    t_mat = torch.tensor([cand_ids], dtype=torch.long, device=device)

    h_vec = torch.full((len(cand_ids),), int(h_id), dtype=torch.long, device=device)
    r_vec = torch.full((len(cand_ids),), int(r_id), dtype=torch.long, device=device)
    t_vec = torch.tensor(cand_ids, dtype=torch.long, device=device)

    tries = [
        ("call_h_tmat_r", lambda: model(graph, h, t_mat, r)),
        ("forward_h_tmat_r", lambda: model.forward(graph, h, t_mat, r)),
        ("call_hvec_tvec_rvec", lambda: model(graph, h_vec, t_vec, r_vec)),
        ("forward_hvec_tvec_rvec", lambda: model.forward(graph, h_vec, t_vec, r_vec)),
    ]

    last_err = None
    with torch.no_grad():
        for tag, fn in tries:
            try:
                out = fn()
                if isinstance(out, tuple):
                    out = out[0]
                out = torch.as_tensor(out).detach().float().cpu().reshape(-1)
                if out.numel() != len(cand_ids):
                    raise RuntimeError(
                        f"{tag} returned numel={out.numel()} expected={len(cand_ids)}"
                    )
                return out.numpy(), tag
            except Exception as e:
                last_err = f"{tag}: {repr(e)}"
    raise RuntimeError(f"all model call attempts failed; last_err={last_err}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--query_pool", required=True)
    parser.add_argument("--candidate_pool", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    qraw = pd.read_csv(args.query_pool, sep="\t")
    craw = pd.read_csv(args.candidate_pool, sep="\t")

    q = normalize_columns(
        qraw,
        {
            "query_id": ["query_id", "qid", "query_idx", "case_id"],
            "head_id": ["head_id", "h_id", "head", "query_head_id"],
            "relation_id": ["relation_id", "r_id", "relation", "query_relation_id"],
            "gold_tail_id": ["gold_tail_id", "tail_id", "t_id", "gold_id", "gold_entity_id"],
            "relation_name": ["relation_name", "r_name", "relation_text", "relation_str"],
        },
    ).copy()

    c = normalize_columns(
        craw,
        {
            "query_id": ["query_id", "qid", "query_idx", "case_id"],
            "cand_id": ["cand_id", "candidate_id", "entity_id", "tail_id", "neg_id", "target_id"],
        },
    ).copy()

    q["query_id"] = q["query_id"].astype(str)
    c["query_id"] = c["query_id"].astype(str)
    q["head_id"] = q["head_id"].astype(int)
    q["relation_id"] = q["relation_id"].astype(int)
    q["gold_tail_id"] = q["gold_tail_id"].astype(int)
    c["cand_id"] = c["cand_id"].astype(int)

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    _, solver = build_solver(cfg)
    ckpt = cfg["checkpoint"]
    load_checkpoint(solver, ckpt)

    task = solver.task
    model = getattr(solver, "model", None)
    if model is None:
        model = task.model

    graph = get_graph(task, model)
    device = get_device(model)

    rows = []
    call_tags = {}

    for _, row in q.iterrows():
        qid = row["query_id"]
        cand_ids = c.loc[c["query_id"] == qid, "cand_id"].tolist()
        if not cand_ids:
            raise RuntimeError(f"query_id={qid} has no candidates")

        gold = int(row["gold_tail_id"])
        if gold not in cand_ids:
            raise RuntimeError(f"query_id={qid} gold_tail_id={gold} not in candidate pool")

        scores, call_tag = call_model(
            model=model,
            graph=graph,
            h_id=int(row["head_id"]),
            r_id=int(row["relation_id"]),
            cand_ids=cand_ids,
            device=device,
        )
        call_tags[qid] = call_tag

        cand_df = pd.DataFrame(
            {
                "query_id": qid,
                "cand_id": cand_ids,
                "score": scores,
            }
        ).sort_values(["score", "cand_id"], ascending=[False, True]).reset_index(drop=True)

        gold_row = cand_df[cand_df["cand_id"] == gold]
        gold_score = float(gold_row["score"].iloc[0])
        gold_rank = 1 + int((cand_df["score"] > gold_score).sum())

        rows.append(
            {
                "query_id": qid,
                "head_id": int(row["head_id"]),
                "relation_id": int(row["relation_id"]),
                "relation_name": str(row["relation_name"]),
                "gold_tail_id": gold,
                "candidate_n": int(len(cand_ids)),
                "gold_score": gold_score,
                "gold_rank": int(gold_rank),
                "hit_at_1": int(gold_rank <= 1),
                "hit_at_10": int(gold_rank <= 10),
                "reciprocal_rank": 1.0 / float(gold_rank),
                "model_call_tag": call_tag,
            }
        )

        cand_df.to_csv(outdir / f"{args.label}.query_{qid}.candidates.tsv", sep="\t", index=False)

    perq = pd.DataFrame(rows).sort_values("query_id").reset_index(drop=True)
    perq.to_csv(outdir / f"{args.label}.per_query.tsv", sep="\t", index=False)

    metrics = {
        "label": args.label,
        "query_n": int(len(perq)),
        "bounded_mrr": float(perq["reciprocal_rank"].mean()),
        "bounded_hits_at_1": float(perq["hit_at_1"].mean()),
        "bounded_hits_at_10": float(perq["hit_at_10"].mean()),
        "mean_gold_rank": float(perq["gold_rank"].mean()),
        "median_gold_rank": float(perq["gold_rank"].median()),
        "checkpoint": ckpt,
        "config": args.config,
        "query_pool": args.query_pool,
        "candidate_pool": args.candidate_pool,
        "call_tags": call_tags,
    }
    (outdir / f"{args.label}.metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
