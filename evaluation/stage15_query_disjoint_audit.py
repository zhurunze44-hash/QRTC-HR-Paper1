from __future__ import annotations
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd


ROOT = Path("<REDACTED_SERVER_PATH>")


def latest_dir(prefix: str) -> Path:
    ds = [p for p in ROOT.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not ds:
        raise FileNotFoundError(f"missing dir prefix={prefix}")
    return sorted(ds, key=lambda p: p.name)[-1]


def majority_label(vals) -> str | None:
    s = pd.Series(list(vals)).dropna().astype(str)
    if len(s) == 0:
        return None
    vc = s.value_counts()
    top_n = vc.iloc[0]
    tops = sorted(vc[vc == top_n].index.tolist())
    return tops[0]


def make_key(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    x = df[cols[0]].fillna("NA").astype(str).str.strip()
    for c in cols[1:]:
        x = x + "||" + df[c].fillna("NA").astype(str).str.strip()
    return x


def pick_query_cols(df: pd.DataFrame) -> list[str]:
    pref = [
        ["relation_id", "head_id", "gold_tail_id"],
        ["relation_name", "head_name", "gold_tail_name"],
        ["relation_id", "head_id"],
        ["relation_name", "head_name"],
    ]
    for cols in pref:
        if all(c in df.columns for c in cols):
            return cols
    raise RuntimeError("cannot find stable query key columns")


def pick_relation_col(df: pd.DataFrame) -> str:
    if "relation_id" in df.columns:
        return "relation_id"
    if "relation_name" in df.columns:
        return "relation_name"
    raise RuntimeError("missing relation column")


def fit_edges(series: pd.Series, q: int = 4):
    x = pd.to_numeric(series, errors="coerce").dropna()
    if len(x) < q or x.nunique() < 2:
        return None
    edges = np.quantile(x, np.linspace(0, 1, q + 1))
    edges = np.unique(edges)
    if len(edges) < 2:
        return None
    edges = edges.astype(float)
    edges[0] = -np.inf
    edges[-1] = np.inf
    return edges.tolist()


def apply_edges(series: pd.Series, edges):
    x = pd.to_numeric(series, errors="coerce")
    if edges is None:
        return pd.Series(
            ["NA" if pd.isna(v) else "ALL" for v in x],
            index=series.index,
            dtype="object",
        )
    out = pd.cut(x, bins=edges, include_lowest=True, duplicates="drop")
    out = out.astype(str)
    out[x.isna()] = "NA"
    return out


def build_majority_map(df: pd.DataFrame, key_cols: list[str], label_col: str) -> dict:
    tmp = df[key_cols + [label_col]].copy()
    for c in key_cols + [label_col]:
        tmp[c] = tmp[c].fillna("NA").astype(str)
    g = tmp.groupby(key_cols + [label_col], dropna=False).size().rename("n").reset_index()
    g = g.sort_values(key_cols + ["n", label_col], ascending=[True] * len(key_cols) + [False, True])
    best = g.drop_duplicates(subset=key_cols, keep="first")
    out = {}
    for _, r in best.iterrows():
        k = tuple(r[c] for c in key_cols)
        out[k] = r[label_col]
    return out


def query_level_accuracy(df: pd.DataFrame, query_col: str, true_col: str, pred_col: str) -> float:
    rows = []
    for q, g in df.groupby(query_col, dropna=False):
        true_lab = majority_label(g[true_col])
        pred_lab = majority_label(g[pred_col])
        rows.append(int(true_lab == pred_lab))
    if not rows:
        return 0.0
    return float(sum(rows) / len(rows))


def main() -> None:
    input_dir = latest_dir("stage15_regime_predictability_audit_")
    outdir = ROOT / f"stage15_query_disjoint_audit_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_dir / "LOCAL_SIGNAL_TABLE.tsv", sep="\t")
    if "regime_bucket" not in df.columns:
        raise RuntimeError("LOCAL_SIGNAL_TABLE.tsv missing regime_bucket")

    df = df[df["regime_bucket"].notna()].copy()
    if len(df) == 0:
        raise RuntimeError("zero labeled rows")

    relation_col = pick_relation_col(df)
    query_cols = pick_query_cols(df)

    num_cols = ["filtered_candidate_n", "top1_score", "margin_12", "top3_entropy", "top3_p1"]
    for c in num_cols:
        if c not in df.columns:
            df[c] = np.nan
        df[c] = pd.to_numeric(df[c], errors="coerce")

    for c in query_cols + [relation_col, "regime_bucket"]:
        df[c] = df[c].fillna("NA").astype(str)

    df["query_key"] = make_key(df, query_cols)

    uniq_queries = sorted(df["query_key"].dropna().astype(str).unique().tolist())
    if len(uniq_queries) < 5:
        raise RuntimeError(f"too few unique queries: {len(uniq_queries)}")

    def fold_of(q: str, k: int = 5) -> int:
        h = hashlib.md5(q.encode("utf-8")).hexdigest()
        return int(h[:8], 16) % k

    fold_map = {q: fold_of(q, 5) for q in uniq_queries}
    df["fold_id"] = df["query_key"].map(fold_map).astype(int)

    all_pred_rows = []
    fold_rows = []

    global_major = majority_label(df["regime_bucket"])

    for fold in range(5):
        train = df[df["fold_id"] != fold].copy()
        test = df[df["fold_id"] == fold].copy()
        if len(train) == 0 or len(test) == 0:
            continue

        edge_map = {c: fit_edges(train[c], q=4) for c in num_cols}
        for c in num_cols:
            train[f"{c}_bin"] = apply_edges(train[c], edge_map[c])
            test[f"{c}_bin"] = apply_edges(test[c], edge_map[c])

        train["local_signal_bin"] = (
            "cand=" + train["filtered_candidate_n_bin"].astype(str) +
            "|top1=" + train["top1_score_bin"].astype(str) +
            "|margin=" + train["margin_12_bin"].astype(str) +
            "|ent=" + train["top3_entropy_bin"].astype(str) +
            "|p1=" + train["top3_p1_bin"].astype(str)
        )
        test["local_signal_bin"] = (
            "cand=" + test["filtered_candidate_n_bin"].astype(str) +
            "|top1=" + test["top1_score_bin"].astype(str) +
            "|margin=" + test["margin_12_bin"].astype(str) +
            "|ent=" + test["top3_entropy_bin"].astype(str) +
            "|p1=" + test["top3_p1_bin"].astype(str)
        )

        relation_map = build_majority_map(train, [relation_col], "regime_bucket")
        local_map = build_majority_map(train, [relation_col, "local_signal_bin"], "regime_bucket")

        rel_preds = []
        local_preds = []
        support_flags = []
        pred_modes = []

        for _, r in test.iterrows():
            rel_key = (r[relation_col],)
            rel_pred = relation_map.get(rel_key, global_major)

            local_key = (r[relation_col], r["local_signal_bin"])
            if local_key in local_map:
                local_pred = local_map[local_key]
                supported = 1
                mode = "local_supported"
            else:
                local_pred = rel_pred
                supported = 0
                mode = "relation_backoff"

            rel_preds.append(rel_pred)
            local_preds.append(local_pred)
            support_flags.append(supported)
            pred_modes.append(mode)

        test["pred_relation_only"] = rel_preds
        test["pred_local_signal_rule"] = local_preds
        test["local_supported"] = support_flags
        test["pred_mode"] = pred_modes

        row_acc_rel = float((test["pred_relation_only"] == test["regime_bucket"]).mean())
        row_acc_local = float((test["pred_local_signal_rule"] == test["regime_bucket"]).mean())
        query_acc_rel = query_level_accuracy(test, "query_key", "regime_bucket", "pred_relation_only")
        query_acc_local = query_level_accuracy(test, "query_key", "regime_bucket", "pred_local_signal_rule")
        support_rate = float(test["local_supported"].mean())

        fold_rows.append({
            "fold_id": fold,
            "train_row_n": int(len(train)),
            "test_row_n": int(len(test)),
            "test_query_n": int(test["query_key"].nunique()),
            "relation_only_row_accuracy": row_acc_rel,
            "local_signal_rule_row_accuracy": row_acc_local,
            "relation_only_query_accuracy": query_acc_rel,
            "local_signal_rule_query_accuracy": query_acc_local,
            "local_signal_support_rate": support_rate,
        })

        all_pred_rows.append(test)

    pred = pd.concat(all_pred_rows, ignore_index=True, sort=False)
    pred.to_csv(outdir / "QUERY_DISJOINT_DETAIL.tsv", sep="\t", index=False)

    fold_df = pd.DataFrame(fold_rows).sort_values("fold_id")
    fold_df.to_csv(outdir / "FOLD_RESULTS.tsv", sep="\t", index=False)

    global_rows = []
    for scheme, pred_col, support_col in [
        ("relation_only", "pred_relation_only", None),
        ("relation_local_signal_rule", "pred_local_signal_rule", "local_supported"),
    ]:
        row_acc = float((pred[pred_col] == pred["regime_bucket"]).mean())
        query_acc = query_level_accuracy(pred, "query_key", "regime_bucket", pred_col)
        support_rate = float(pred[support_col].mean()) if support_col is not None else np.nan
        global_rows.append({
            "scheme": scheme,
            "row_n": int(len(pred)),
            "query_n": int(pred["query_key"].nunique()),
            "row_accuracy": row_acc,
            "query_accuracy": query_acc,
            "support_rate": support_rate,
        })
    global_df = pd.DataFrame(global_rows).sort_values("row_accuracy", ascending=False)
    global_df.to_csv(outdir / "GLOBAL.tsv", sep="\t", index=False)

    by_rel_rows = []
    for rel, g in pred.groupby(relation_col, dropna=False):
        for scheme, pred_col, support_col in [
            ("relation_only", "pred_relation_only", None),
            ("relation_local_signal_rule", "pred_local_signal_rule", "local_supported"),
        ]:
            row_acc = float((g[pred_col] == g["regime_bucket"]).mean())
            query_acc = query_level_accuracy(g, "query_key", "regime_bucket", pred_col)
            support_rate = float(g[support_col].mean()) if support_col is not None else np.nan
            by_rel_rows.append({
                relation_col: rel,
                "scheme": scheme,
                "row_n": int(len(g)),
                "query_n": int(g["query_key"].nunique()),
                "row_accuracy": row_acc,
                "query_accuracy": query_acc,
                "support_rate": support_rate,
            })
    by_rel_df = pd.DataFrame(by_rel_rows).sort_values([relation_col, "row_accuracy"], ascending=[True, False])
    by_rel_df.to_csv(outdir / "BY_RELATION.tsv", sep="\t", index=False)

    rel7 = pred[pred[relation_col].astype(str) == "7"].copy()
    if len(rel7) > 0:
        qrows = []
        for q, g in rel7.groupby("query_key", dropna=False):
            qrows.append({
                "query_key": q,
                "row_n": int(len(g)),
                "true_regime": majority_label(g["regime_bucket"]),
                "pred_relation_only": majority_label(g["pred_relation_only"]),
                "pred_local_signal_rule": majority_label(g["pred_local_signal_rule"]),
                "local_supported_rate": float(g["local_supported"].mean()),
            })
        pd.DataFrame(qrows).to_csv(outdir / "REL7_QUERY_LEVEL.tsv", sep="\t", index=False)

    best = global_df.iloc[0]
    receipt = {
        "status": "ok",
        "input_dir": str(input_dir),
        "outdir": str(outdir),
        "relation_col": relation_col,
        "query_cols": query_cols,
        "row_n": int(len(pred)),
        "query_n": int(pred["query_key"].nunique()),
        "best_scheme": str(best["scheme"]),
        "best_row_accuracy": float(best["row_accuracy"]),
        "best_query_accuracy": float(best["query_accuracy"]),
    }
    (outdir / "RECEIPT.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append(f"input_dir\t{input_dir}")
    lines.append(f"outdir\t{outdir}")
    lines.append(f"row_n\t{len(pred)}")
    lines.append(f"query_n\t{pred['query_key'].nunique()}")
    rel_base = global_df.loc[global_df["scheme"] == "relation_only"]
    loc_rule = global_df.loc[global_df["scheme"] == "relation_local_signal_rule"]
    if len(rel_base):
        lines.append(f"relation_only_row_accuracy\t{float(rel_base.iloc[0]['row_accuracy']):.6f}")
        lines.append(f"relation_only_query_accuracy\t{float(rel_base.iloc[0]['query_accuracy']):.6f}")
    if len(loc_rule):
        lines.append(f"local_signal_rule_row_accuracy\t{float(loc_rule.iloc[0]['row_accuracy']):.6f}")
        lines.append(f"local_signal_rule_query_accuracy\t{float(loc_rule.iloc[0]['query_accuracy']):.6f}")
        lines.append(f"local_signal_rule_support_rate\t{float(loc_rule.iloc[0]['support_rate']):.6f}")
    (outdir / "SUMMARY.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
