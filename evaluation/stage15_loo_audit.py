from __future__ import annotations
from pathlib import Path
import json
import pandas as pd


ROOT = Path("<REDACTED_SERVER_PATH>")


def latest_dir(prefix: str) -> Path:
    ds = [p for p in ROOT.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not ds:
        raise FileNotFoundError(f"missing dir prefix={prefix}")
    return sorted(ds, key=lambda p: p.name)[-1]


def pick_relation_col(df: pd.DataFrame) -> str:
    if "relation_id" in df.columns:
        return "relation_id"
    if "relation_name" in df.columns:
        return "relation_name"
    raise RuntimeError("missing relation column")


def make_key(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    x = df[cols[0]].fillna("NA").astype(str)
    for c in cols[1:]:
        x = x + "||" + df[c].fillna("NA").astype(str)
    return x


def dominant_label(counts: dict[str, int]) -> str | None:
    items = [(lab, n) for lab, n in counts.items() if n > 0]
    if not items:
        return None
    items.sort(key=lambda x: (-x[1], x[0]))
    return items[0][0]


def loo_eval(df: pd.DataFrame, label_col: str, group_cols: list[str], relation_col: str) -> dict:
    work = df.copy()
    for c in group_cols + [relation_col, label_col]:
        work[c] = work[c].fillna("NA").astype(str)

    work["__group_key"] = make_key(work, group_cols)
    work["__rel_key"] = make_key(work, [relation_col])

    group_label_counts = (
        work.groupby(["__group_key", label_col], dropna=False)
        .size()
        .rename("n")
        .reset_index()
    )
    rel_label_counts = (
        work.groupby(["__rel_key", label_col], dropna=False)
        .size()
        .rename("n")
        .reset_index()
    )

    gmap: dict[str, dict[str, int]] = {}
    for _, r in group_label_counts.iterrows():
        gmap.setdefault(r["__group_key"], {})[r[label_col]] = int(r["n"])

    rmap: dict[str, dict[str, int]] = {}
    for _, r in rel_label_counts.iterrows():
        rmap.setdefault(r["__rel_key"], {})[r[label_col]] = int(r["n"])

    supported_n = 0
    supported_correct = 0
    backoff_correct = 0

    detail = []
    for _, row in work.iterrows():
        true_lab = row[label_col]
        gk = row["__group_key"]
        rk = row["__rel_key"]

        gcounts = dict(gmap.get(gk, {}))
        gcounts[true_lab] = gcounts.get(true_lab, 0) - 1
        if gcounts[true_lab] <= 0:
            gcounts.pop(true_lab, None)

        if gcounts:
            pred = dominant_label(gcounts)
            supported = 1
            correct = int(pred == true_lab)
            supported_n += 1
            supported_correct += correct
            final_pred = pred
            final_correct = correct
            final_mode = "group_supported"
        else:
            rcounts = dict(rmap.get(rk, {}))
            rcounts[true_lab] = rcounts.get(true_lab, 0) - 1
            if rcounts[true_lab] <= 0:
                rcounts.pop(true_lab, None)
            pred = dominant_label(rcounts)
            correct = int(pred == true_lab) if pred is not None else 0
            backoff_correct += correct
            final_pred = pred
            final_correct = correct
            final_mode = "relation_backoff"

        detail.append({
            "relation_value": row[relation_col],
            "true_regime": true_lab,
            "group_key": gk,
            "pred_regime": final_pred,
            "is_supported": supported if gcounts else 0,
            "pred_mode": final_mode,
            "is_correct": final_correct,
        })

    row_n = len(work)
    unsupported_n = row_n - supported_n
    overall_correct = supported_correct + backoff_correct

    return {
        "row_n": int(row_n),
        "supported_row_n": int(supported_n),
        "unsupported_row_n": int(unsupported_n),
        "support_rate": float(supported_n / row_n) if row_n else 0.0,
        "supported_accuracy": float(supported_correct / supported_n) if supported_n else 0.0,
        "overall_accuracy_with_relation_backoff": float(overall_correct / row_n) if row_n else 0.0,
        "detail_df": pd.DataFrame(detail),
    }


def main() -> None:
    input_dir = latest_dir("stage15_regime_predictability_audit_")
    outdir = ROOT / f"stage15_loo_audit_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_dir / "LOCAL_SIGNAL_TABLE.tsv", sep="\t")
    if "regime_bucket" not in df.columns:
        raise RuntimeError("LOCAL_SIGNAL_TABLE.tsv missing regime_bucket")
    df = df[df["regime_bucket"].notna()].copy()
    if len(df) == 0:
        raise RuntimeError("LOCAL_SIGNAL_TABLE.tsv has zero labeled rows")

    relation_col = pick_relation_col(df)

    needed = ["local_signal_bin", "top1_pred_id", "top3_proto_family"]
    for c in needed:
        if c not in df.columns:
            df[c] = "NA"
    df["top1_pred_id"] = df["top1_pred_id"].fillna("NA").astype(str)
    df["top3_proto_family"] = df["top3_proto_family"].fillna("NA").astype(str)
    df["local_signal_bin"] = df["local_signal_bin"].fillna("NA").astype(str)
    df["regime_bucket"] = df["regime_bucket"].fillna("NA").astype(str)

    schemes = [
        ("relation_only", [relation_col]),
        ("relation_local_signal_bin", [relation_col, "local_signal_bin"]),
        ("relation_top1_pred_id", [relation_col, "top1_pred_id"]),
        ("relation_top3_proto_family", [relation_col, "top3_proto_family"]),
        ("relation_proto_plus_local", [relation_col, "top3_proto_family", "local_signal_bin"]),
    ]

    global_rows = []
    detail_frames = []

    for name, cols in schemes:
        stat = loo_eval(df, "regime_bucket", cols, relation_col)
        global_rows.append({
            "scheme": name,
            "group_cols": "|".join(cols),
            "row_n": stat["row_n"],
            "supported_row_n": stat["supported_row_n"],
            "unsupported_row_n": stat["unsupported_row_n"],
            "support_rate": stat["support_rate"],
            "supported_accuracy": stat["supported_accuracy"],
            "overall_accuracy_with_relation_backoff": stat["overall_accuracy_with_relation_backoff"],
        })
        d = stat["detail_df"].copy()
        d["scheme"] = name
        detail_frames.append(d)

    global_df = pd.DataFrame(global_rows).sort_values(
        ["overall_accuracy_with_relation_backoff", "supported_accuracy", "support_rate"],
        ascending=[False, False, False],
    )
    global_df.to_csv(outdir / "LOO_GLOBAL.tsv", sep="\t", index=False)

    by_rel_rows = []
    for rel, g in df.groupby(relation_col, dropna=False):
        for name, cols in schemes[1:]:
            stat = loo_eval(g.copy(), "regime_bucket", cols, relation_col)
            by_rel_rows.append({
                relation_col: rel,
                "scheme": name,
                "row_n": stat["row_n"],
                "supported_row_n": stat["supported_row_n"],
                "unsupported_row_n": stat["unsupported_row_n"],
                "support_rate": stat["support_rate"],
                "supported_accuracy": stat["supported_accuracy"],
                "overall_accuracy_with_relation_backoff": stat["overall_accuracy_with_relation_backoff"],
            })
    by_rel_df = pd.DataFrame(by_rel_rows).sort_values(
        [relation_col, "overall_accuracy_with_relation_backoff", "supported_accuracy"],
        ascending=[True, False, False],
    )
    by_rel_df.to_csv(outdir / "LOO_BY_RELATION.tsv", sep="\t", index=False)

    detail_df = pd.concat(detail_frames, ignore_index=True, sort=False)
    detail_df.to_csv(outdir / "LOO_DETAIL.tsv", sep="\t", index=False)

    if relation_col in df.columns and (df[relation_col].astype(str) == "7").any():
        rel7 = df[df[relation_col].astype(str) == "7"].copy()
        rule = (
            rel7.groupby(["local_signal_bin", "regime_bucket"], dropna=False)
            .size()
            .rename("n")
            .reset_index()
        )
        total = rule.groupby(["local_signal_bin"], dropna=False)["n"].sum().rename("group_n").reset_index()
        top = rule.groupby(["local_signal_bin"], dropna=False)["n"].max().rename("top_n").reset_index()
        rule = rule.merge(total, on="local_signal_bin", how="left").merge(top, on="local_signal_bin", how="left")
        rule["purity"] = rule["top_n"] / rule["group_n"]
        rule.sort_values(["purity", "group_n", "n"], ascending=[False, False, False]).to_csv(
            outdir / "REL7_LOCAL_SIGNAL_RULES.tsv", sep="\t", index=False
        )

    receipt = {
        "status": "ok",
        "input_dir": str(input_dir),
        "outdir": str(outdir),
        "row_n": int(len(df)),
        "relation_col": relation_col,
        "best_scheme": str(global_df.iloc[0]["scheme"]),
        "best_overall_accuracy_with_relation_backoff": float(global_df.iloc[0]["overall_accuracy_with_relation_backoff"]),
    }
    (outdir / "RECEIPT.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append(f"input_dir\t{input_dir}")
    lines.append(f"outdir\t{outdir}")
    lines.append(f"row_n\t{len(df)}")
    base = global_df.loc[global_df["scheme"] == "relation_only", "overall_accuracy_with_relation_backoff"]
    if len(base):
        lines.append(f"relation_only_overall_accuracy_with_relation_backoff\t{float(base.iloc[0]):.6f}")
    lines.append(f"best_scheme\t{receipt['best_scheme']}")
    lines.append(f"best_overall_accuracy_with_relation_backoff\t{receipt['best_overall_accuracy_with_relation_backoff']:.6f}")
    (outdir / "SUMMARY.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
