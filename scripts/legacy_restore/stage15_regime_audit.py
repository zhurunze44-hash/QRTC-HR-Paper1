from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path("<REDACTED_SERVER_PATH>")
EXP_ROOT = ROOT / "paper1_b1lite_gate_ultralowmem_lnctardppi_20260324_192443"

ALIASES = {
    "head_name": ["head_name", "query_node", "query_head", "query_head_name", "head"],
    "head_id": ["head_id", "query_head_id", "query_node_id", "query_id"],
    "relation_name": ["relation_name", "query_relation", "relation"],
    "relation_id": ["relation_id", "query_relation_id", "rel_id"],
    "gold_tail_name": ["gold_tail_name", "gold_tail", "tail_name", "gold_name"],
    "gold_tail_id": ["gold_tail_id", "tail_id", "gold_id"],
    "pred_name": ["pred_tail_name", "pred_node_name", "pred_tail", "pred_node"],
    "pred_id": ["pred_tail_id", "pred_node_id"],
    "score": ["pred_score", "prediction_score", "score"],
    "rank": ["topk_rank", "rank", "pred_rank"],
    "filtered_candidate_n": ["filtered_candidate_n", "candidate_n", "filtered_n", "num_candidates"],
}
LABEL_CANDS = ["query_bucket", "bucket", "regime_bucket", "query_regime", "regime", "stability_bucket"]


def latest_dir(prefix: str) -> Path:
    ds = [p for p in ROOT.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not ds:
        raise FileNotFoundError(f"missing dir prefix={prefix}")
    return sorted(ds, key=lambda p: p.name)[-1]


def pick_col(df: pd.DataFrame, names: list[str]) -> str | None:
    lower = {str(c).strip().lower(): c for c in df.columns}
    for n in names:
        if n.lower() in lower:
            return lower[n.lower()]
    for n in names:
        for c in df.columns:
            if n.lower() in str(c).strip().lower():
                return c
    return None


def canon(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for k, names in ALIASES.items():
        c = pick_col(out, names)
        if c is not None and k not in out.columns:
            out[k] = out[c]
    return out


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def jkey(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    if not cols:
        return pd.Series([""] * len(df), index=df.index)
    x = df[cols[0]].fillna("").astype(str).str.strip()
    for c in cols[1:]:
        x = x + "||" + df[c].fillna("").astype(str).str.strip()
    return x


def qbin(s: pd.Series, q: int = 4) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    if x.notna().sum() < max(q, 4):
        return pd.Series(["NA" if pd.isna(v) else "ALL" for v in x], index=s.index)
    try:
        return pd.qcut(x, q=q, duplicates="drop").astype(str)
    except Exception:
        return pd.Series(["NA" if pd.isna(v) else "ALL" for v in x], index=s.index)


def entropy_top3(vals: list[float]) -> tuple[float, float]:
    arr = np.asarray([v for v in vals if pd.notna(v)], dtype=float)
    if arr.size == 0:
        return np.nan, np.nan
    z = arr - np.max(arr)
    p = np.exp(z)
    p = p / p.sum()
    ent = float(-(p * np.log(p + 1e-12)).sum())
    return ent, float(p[0])


def find_pairs() -> list[tuple[Path, Path, Path]]:
    topks = sorted(EXP_ROOT.rglob("*valid_tail_probe_topk*.tsv"))
    sums = sorted(EXP_ROOT.rglob("*valid_tail_probe_summary*.tsv"))
    by_parent: dict[Path, dict[str, list[Path]]] = {}
    for p in topks:
        by_parent.setdefault(p.parent, {}).setdefault("topk", []).append(p)
    for p in sums:
        by_parent.setdefault(p.parent, {}).setdefault("summary", []).append(p)
    out = []
    for parent, d in by_parent.items():
        if "topk" not in d or "summary" not in d:
            continue
        out.append((parent, sorted(d["topk"])[0], sorted(d["summary"])[0]))
    return sorted(out, key=lambda x: str(x[0]))


def best_qcols(df: pd.DataFrame) -> list[str]:
    cols = []
    for c in ["relation_id", "relation_name", "head_id", "head_name", "gold_tail_id", "gold_tail_name"]:
        if c in df.columns and df[c].notna().any():
            cols.append(c)
    return cols


def collect_pair(parent: Path, topk_path: Path, sum_path: Path) -> pd.DataFrame:
    try:
        if (not topk_path.exists()) or topk_path.stat().st_size == 0:
            return pd.DataFrame()
        topk = canon(pd.read_csv(topk_path, sep="\t", dtype=str))
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    try:
        if sum_path.exists() and sum_path.stat().st_size > 0:
            summ = canon(pd.read_csv(sum_path, sep="\t", dtype=str))
        else:
            summ = pd.DataFrame()
    except pd.errors.EmptyDataError:
        summ = pd.DataFrame()

    if "score" not in topk.columns:
        return pd.DataFrame()

    qcols = best_qcols(topk)
    if len(qcols) < 2:
        qcols = [c for c in ["relation_id", "relation_name", "head_id", "head_name"] if c in topk.columns]
    if len(qcols) < 2:
        return pd.DataFrame()

    topk["__score"] = num(topk["score"])
    topk["__rank"] = num(topk["rank"]) if "rank" in topk.columns else np.nan

    rows = []
    for qkey, g in topk.groupby(qcols, dropna=False):
        g2 = g.sort_values(["__rank", "__score"], ascending=[True, False], na_position="last")
        scores = list(g2["__score"].head(3).values)
        pred_ids = list(g2["pred_id"].head(3).astype(str).values) if "pred_id" in g2.columns else []
        pred_names = list(g2["pred_name"].head(3).astype(str).values) if "pred_name" in g2.columns else []

        top1 = scores[0] if len(scores) >= 1 else np.nan
        top2 = scores[1] if len(scores) >= 2 else np.nan
        top3 = scores[2] if len(scores) >= 3 else np.nan
        margin = top1 - top2 if pd.notna(top1) and pd.notna(top2) else np.nan
        ent, p1 = entropy_top3([top1, top2, top3])

        sig_items = pred_ids[:3] if pred_ids and any(str(x) != "nan" for x in pred_ids[:3]) else pred_names[:3]
        sig = "|".join([str(x) for x in sig_items if str(x) != "nan"])

        base = {}
        if isinstance(qkey, tuple):
            for i, c in enumerate(qcols):
                base[c] = qkey[i]
        else:
            base[qcols[0]] = qkey

        base.update({
            "run_dir": str(parent),
            "top1_score": top1,
            "top2_score": top2,
            "top3_score": top3,
            "margin_12": margin,
            "top3_entropy": ent,
            "top3_p1": p1,
            "top1_pred_id": pred_ids[0] if len(pred_ids) >= 1 else np.nan,
            "top1_pred_name": pred_names[0] if len(pred_names) >= 1 else np.nan,
            "top3_signature": sig if sig else np.nan,
        })
        rows.append(base)

    feat = pd.DataFrame(rows)
    if len(feat) == 0:
        return feat

    sum_qcols = [c for c in qcols if c in summ.columns]
    keep = list(dict.fromkeys(sum_qcols + [c for c in ["filtered_candidate_n"] if c in summ.columns]))
    if len(sum_qcols) >= 2 and keep:
        s2 = summ[keep].copy()
        feat["__k"] = jkey(feat, sum_qcols)
        s2["__k"] = jkey(s2, sum_qcols)
        vc = s2["__k"].value_counts(dropna=False)
        s2 = s2[s2["__k"].map(vc) == 1]
        feat = feat.merge(s2.drop(columns=sum_qcols), on="__k", how="left").drop(columns="__k")

    return feat


def purity(df: pd.DataFrame, label_col: str, group_cols: list[str]) -> dict:
    work = df.copy()
    for c in group_cols:
        work[c] = work[c].fillna("NA").astype(str)
    g = work.groupby(group_cols + [label_col], dropna=False).size().rename("n").reset_index()
    total = g.groupby(group_cols, dropna=False)["n"].sum().rename("group_n").reset_index()
    top = g.groupby(group_cols, dropna=False)["n"].max().rename("top_n").reset_index()
    m = total.merge(top, on=group_cols, how="left")
    m["group_purity"] = m["top_n"] / m["group_n"]
    return {
        "row_n": int(len(work)),
        "group_n": int(len(m)),
        "weighted_majority_accuracy": float(m["top_n"].sum() / len(work)) if len(work) else np.nan,
        "mean_group_purity": float(m["group_purity"].mean()) if len(m) else np.nan,
        "median_group_purity": float(m["group_purity"].median()) if len(m) else np.nan,
    }


def main() -> None:
    outdir = ROOT / f"stage15_regime_predictability_audit_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    outdir.mkdir(parents=True, exist_ok=True)

    bucket_dir = latest_dir("round1_query_bucket_summary_")
    bucket = canon(pd.read_csv(bucket_dir / "QUERY_BUCKET_SUMMARY.tsv", sep="\t", dtype=str))
    label_col = pick_col(bucket, LABEL_CANDS)
    if label_col is None:
        raise RuntimeError("missing regime bucket column in QUERY_BUCKET_SUMMARY.tsv")
    if "regime_bucket" not in bucket.columns:
        bucket["regime_bucket"] = bucket[label_col]

    pairs = find_pairs()
    frames = []
    for parent, topk_path, sum_path in pairs:
        df = collect_pair(parent, topk_path, sum_path)
        if len(df) > 0:
            frames.append(df)
    if not frames:
        raise RuntimeError("no valid paired probe rows collected")

    local_df = pd.concat(frames, ignore_index=True, sort=False)
    local_df = canon(local_df)

    join_orders = [
        ["relation_id", "head_id", "gold_tail_id"],
        ["relation_name", "head_name", "gold_tail_name"],
        ["relation_id", "head_id"],
        ["relation_name", "head_name"],
    ]
    join_cols = None
    for cols in join_orders:
        if all(c in local_df.columns for c in cols) and all(c in bucket.columns for c in cols):
            join_cols = cols
            break
    if join_cols is None:
        raise RuntimeError("cannot find stable join cols with QUERY_BUCKET_SUMMARY.tsv")

    b2 = bucket[join_cols + ["regime_bucket"]].copy()
    dup = b2.groupby(join_cols, dropna=False).size().rename("dup_n").reset_index()
    b2 = b2.merge(dup, on=join_cols, how="left")
    b2 = b2[b2["dup_n"] == 1].drop(columns="dup_n")

    df = local_df.merge(b2, on=join_cols, how="left")
    df = df[df["regime_bucket"].notna()].copy()
    if len(df) == 0:
        raise RuntimeError("zero labeled rows after join to QUERY_BUCKET_SUMMARY.tsv")

    relation_col = "relation_id" if "relation_id" in df.columns else "relation_name"

    for c in ["filtered_candidate_n", "top1_score", "margin_12", "top3_entropy", "top3_p1"]:
        if c not in df.columns:
            df[c] = np.nan
        df[c] = num(df[c])

    fam = []
    for _, g in df.groupby(relation_col, dropna=False):
        vc = g["top3_signature"].fillna("NA").astype(str).value_counts()
        keep = set(vc[vc >= 3].index.tolist())
        fam.extend([x if x in keep else "__OTHER__" for x in g["top3_signature"].fillna("NA").astype(str)])
    df["top3_proto_family"] = fam

    df["cand_bin"] = qbin(df["filtered_candidate_n"])
    df["top1_bin"] = qbin(df["top1_score"])
    df["margin_bin"] = qbin(df["margin_12"])
    df["entropy_bin"] = qbin(df["top3_entropy"])
    df["p1_bin"] = qbin(df["top3_p1"])
    df["local_signal_bin"] = (
        "cand=" + df["cand_bin"].astype(str) +
        "|top1=" + df["top1_bin"].astype(str) +
        "|margin=" + df["margin_bin"].astype(str) +
        "|ent=" + df["entropy_bin"].astype(str) +
        "|p1=" + df["p1_bin"].astype(str)
    )

    df.to_csv(outdir / "LOCAL_SIGNAL_TABLE.tsv", sep="\t", index=False)

    schemes = [
        ("relation_only", [relation_col]),
        ("relation_top1_pred_id", [relation_col, "top1_pred_id"]),
        ("relation_top3_proto_family", [relation_col, "top3_proto_family"]),
        ("relation_local_signal_bin", [relation_col, "local_signal_bin"]),
        ("relation_proto_plus_local", [relation_col, "top3_proto_family", "local_signal_bin"]),
    ]

    global_rows = []
    for name, cols in schemes:
        stat = purity(df, "regime_bucket", cols)
        stat["scheme"] = name
        stat["group_cols"] = "|".join(cols)
        global_rows.append(stat)
    global_df = pd.DataFrame(global_rows).sort_values("weighted_majority_accuracy", ascending=False)
    global_df.to_csv(outdir / "PREDICTABILITY_GLOBAL.tsv", sep="\t", index=False)

    by_rel_rows = []
    for rel, g in df.groupby(relation_col, dropna=False):
        for name, cols in [
            ("top1_pred_id", ["top1_pred_id"]),
            ("top3_proto_family", ["top3_proto_family"]),
            ("local_signal_bin", ["local_signal_bin"]),
            ("proto_plus_local", ["top3_proto_family", "local_signal_bin"]),
        ]:
            stat = purity(g, "regime_bucket", cols)
            stat[relation_col] = rel
            stat["scheme"] = name
            by_rel_rows.append(stat)
    by_rel_df = pd.DataFrame(by_rel_rows).sort_values([relation_col, "weighted_majority_accuracy"], ascending=[True, False])
    by_rel_df.to_csv(outdir / "PREDICTABILITY_BY_RELATION.tsv", sep="\t", index=False)

    rel7 = df[df[relation_col].astype(str) == "7"].copy()
    if len(rel7) > 0:
        rel7.groupby(["top3_proto_family", "local_signal_bin", "regime_bucket"], dropna=False).size().rename("n").reset_index().to_csv(
            outdir / "REL7_DETAIL.tsv", sep="\t", index=False
        )

    summary = {
        "status": "ok",
        "outdir": str(outdir),
        "bucket_dir": str(bucket_dir),
        "pair_count": len(pairs),
        "join_cols": join_cols,
        "labeled_row_n": int(len(df)),
        "relation_col": relation_col,
        "best_scheme": str(global_df.iloc[0]["scheme"]),
        "best_weighted_majority_accuracy": float(global_df.iloc[0]["weighted_majority_accuracy"]),
    }
    (outdir / "RECEIPT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append(f"outdir\t{outdir}")
    lines.append(f"pair_count\t{len(pairs)}")
    lines.append(f"labeled_row_n\t{len(df)}")
    base = global_df.loc[global_df["scheme"] == "relation_only", "weighted_majority_accuracy"]
    if len(base):
        lines.append(f"relation_only_weighted_majority_accuracy\t{float(base.iloc[0]):.6f}")
    lines.append(f"best_scheme\t{summary['best_scheme']}")
    lines.append(f"best_weighted_majority_accuracy\t{summary['best_weighted_majority_accuracy']:.6f}")
    (outdir / "SUMMARY.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
