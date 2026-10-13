import argparse
import json
from pathlib import Path

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m0", required=True)
    ap.add_argument("--m1", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    m0 = pd.read_csv(args.m0, sep="\t").rename(
        columns={
            "gold_score": "gold_score_m0",
            "gold_rank": "gold_rank_m0",
            "hit_at_1": "hit_at_1_m0",
            "hit_at_10": "hit_at_10_m0",
            "reciprocal_rank": "rr_m0",
        }
    )
    m1 = pd.read_csv(args.m1, sep="\t").rename(
        columns={
            "gold_score": "gold_score_m1",
            "gold_rank": "gold_rank_m1",
            "hit_at_1": "hit_at_1_m1",
            "hit_at_10": "hit_at_10_m1",
            "reciprocal_rank": "rr_m1",
        }
    )

    keep0 = [
        "query_id",
        "relation_name",
        "gold_tail_id",
        "candidate_n",
        "gold_score_m0",
        "gold_rank_m0",
        "hit_at_1_m0",
        "hit_at_10_m0",
        "rr_m0",
    ]
    keep1 = [
        "query_id",
        "gold_score_m1",
        "gold_rank_m1",
        "hit_at_1_m1",
        "hit_at_10_m1",
        "rr_m1",
    ]

    df = m0[keep0].merge(m1[keep1], on="query_id", how="inner")
    df["delta_rank"] = df["gold_rank_m0"] - df["gold_rank_m1"]
    df["delta_score"] = df["gold_score_m1"] - df["gold_score_m0"]
    df["winner"] = df["delta_rank"].map(lambda x: "M1" if x > 0 else ("M0" if x < 0 else "TIE"))

    df.to_csv(outdir / "M0_vs_M1.per_query_compare.tsv", sep="\t", index=False)

    rel = (
        df.groupby("relation_name", dropna=False)
        .agg(
            query_n=("query_id", "count"),
            m0_mrr=("rr_m0", "mean"),
            m1_mrr=("rr_m1", "mean"),
            m0_hit1=("hit_at_1_m0", "mean"),
            m1_hit1=("hit_at_1_m1", "mean"),
            m0_hit10=("hit_at_10_m0", "mean"),
            m1_hit10=("hit_at_10_m1", "mean"),
            m1_win_n=("winner", lambda s: int((s == "M1").sum())),
            m0_win_n=("winner", lambda s: int((s == "M0").sum())),
            tie_n=("winner", lambda s: int((s == "TIE").sum())),
        )
        .reset_index()
    )
    rel.to_csv(outdir / "M0_vs_M1.relation_summary.tsv", sep="\t", index=False)

    summary = {
        "query_n": int(len(df)),
        "m0_bounded_mrr": float(df["rr_m0"].mean()),
        "m1_bounded_mrr": float(df["rr_m1"].mean()),
        "delta_bounded_mrr_m1_minus_m0": float(df["rr_m1"].mean() - df["rr_m0"].mean()),
        "m0_bounded_hits_at_1": float(df["hit_at_1_m0"].mean()),
        "m1_bounded_hits_at_1": float(df["hit_at_1_m1"].mean()),
        "delta_bounded_hits_at_1_m1_minus_m0": float(df["hit_at_1_m1"].mean() - df["hit_at_1_m0"].mean()),
        "m0_bounded_hits_at_10": float(df["hit_at_10_m0"].mean()),
        "m1_bounded_hits_at_10": float(df["hit_at_10_m1"].mean()),
        "delta_bounded_hits_at_10_m1_minus_m0": float(df["hit_at_10_m1"].mean() - df["hit_at_10_m0"].mean()),
        "m1_win_n": int((df["winner"] == "M1").sum()),
        "m0_win_n": int((df["winner"] == "M0").sum()),
        "tie_n": int((df["winner"] == "TIE").sum()),
    }
    (outdir / "M0_vs_M1.summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
