from __future__ import annotations
import argparse
import csv
from collections import defaultdict
from pathlib import Path

def parse_int(x, default=0):
    try:
        return int(x)
    except:
        return default

def parse_float(x, default=0.0):
    try:
        return float(x)
    except:
        return default

def difficulty_bucket(mean_rank: float) -> str:
    if mean_rank <= 10:
        return "easy"
    if mean_rank <= 100:
        return "medium"
    if mean_rank <= 300:
        return "hard"
    return "miss"

def stability_bucket(std_rank: float, top1_agree: float) -> str:
    if std_rank <= 5 and top1_agree >= 0.8:
        return "very_stable"
    if std_rank <= 20 and top1_agree >= 0.6:
        return "stable"
    return "unstable"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query-stability", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    inp = Path(args.query_stability).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    with inp.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            mean_rank = parse_float(row["mean_rank"])
            std_rank = parse_float(row["std_rank"])
            top1_agree = parse_float(row["top1_agreement_rate"])

            d_bucket = difficulty_bucket(mean_rank)
            s_bucket = stability_bucket(std_rank, top1_agree)
            combo = f"{d_bucket}_{s_bucket}"

            rows.append({
                **row,
                "difficulty_bucket": d_bucket,
                "stability_bucket": s_bucket,
                "combined_bucket": combo,
            })

    q_out = outdir / "QUERY_BUCKET_SUMMARY.tsv"
    with q_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        for row in rows:
            w.writerow(row)

    rel_bucket = defaultdict(lambda: {"query_n": 0})
    for row in rows:
        key = (row["relation_id"], row["relation_name"], row["combined_bucket"])
        rel_bucket[key]["query_n"] += 1

    rel_rows = []
    by_rel_total = defaultdict(int)
    for row in rows:
        by_rel_total[(row["relation_id"], row["relation_name"])] += 1

    for (rel_id, rel_name, combo), stats in sorted(rel_bucket.items(), key=lambda x: (int(x[0][0]), x[0][2])):
        total = by_rel_total[(rel_id, rel_name)]
        rel_rows.append({
            "relation_id": rel_id,
            "relation_name": rel_name,
            "combined_bucket": combo,
            "query_n": stats["query_n"],
            "query_ratio": stats["query_n"] / total if total else 0.0,
        })

    r_out = outdir / "RELATION_BUCKET_SUMMARY.tsv"
    with r_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rel_rows[0].keys()), delimiter="\t")
        w.writeheader()
        for row in rel_rows:
            w.writerow(row)

    txt = outdir / "QUERY_BUCKET_SUMMARY.txt"
    lines = [
        f"QUERY_N\t{len(rows)}",
        "",
        "[QUERY_BUCKETS_TOP_40]"
    ]
    for row in rows[:40]:
        lines.append(
            f'{row["relation_id"]}\t{row["relation_name"]}\t'
            f'{row["head_name"]}->{row["gold_tail_name"]}\t'
            f'mean_rank={float(row["mean_rank"]):.4f}\tstd_rank={float(row["std_rank"]):.4f}\t'
            f'top1_agree={float(row["top1_agreement_rate"]):.4f}\t'
            f'bucket={row["combined_bucket"]}'
        )
    lines += ["", "[RELATION_BUCKETS]"]
    for row in rel_rows:
        lines.append(
            f'{row["relation_id"]}\t{row["relation_name"]}\t'
            f'{row["combined_bucket"]}\tquery_n={row["query_n"]}\tratio={float(row["query_ratio"]):.4f}'
        )
    txt.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote: {q_out}")
    print(f"[OK] wrote: {r_out}")
    print(f"[OK] wrote: {txt}")

if __name__ == "__main__":
    main()
