from __future__ import annotations
import argparse
import csv
from collections import defaultdict, Counter
from pathlib import Path

def parse_float(x, default=0.0):
    try:
        return float(x)
    except:
        return default

def parse_int(x, default=0):
    try:
        return int(x)
    except:
        return default

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query-bucket", required=True)
    ap.add_argument("--query-stability", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    qb = Path(args.query_bucket).resolve()
    qs = Path(args.query_stability).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    bucket_map = {}
    with qb.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            key = (
                row["valid_original_index"],
                row["head_id"],
                row["relation_id"],
                row["gold_tail_id"],
            )
            bucket_map[key] = row

    groups = defaultdict(list)
    with qs.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            key = (
                row["valid_original_index"],
                row["head_id"],
                row["relation_id"],
                row["gold_tail_id"],
            )
            if key not in bucket_map:
                continue
            b = bucket_map[key]
            gkey = (row["relation_id"], row["relation_name"], b["combined_bucket"])
            groups[gkey].append(row)

    proto_rows = []
    anchor_rows = []

    for (rel_id, rel_name, bucket), rows in sorted(groups.items(), key=lambda x: (int(x[0][0]), x[0][2])):
        top1_counter = Counter(r["most_common_top1_id"] for r in rows if r["most_common_top1_id"])
        top3_counter = Counter(r["most_common_top3_ids"] for r in rows if r["most_common_top3_ids"])

        top1_id, top1_n = ("", 0)
        if top1_counter:
            top1_id, top1_n = top1_counter.most_common(1)[0]

        top3_ids, top3_n = ("", 0)
        if top3_counter:
            top3_ids, top3_n = top3_counter.most_common(1)[0]

        proto_rows.append({
            "relation_id": rel_id,
            "relation_name": rel_name,
            "combined_bucket": bucket,
            "query_n": len(rows),
            "mean_rank": sum(parse_float(r["mean_rank"]) for r in rows) / len(rows),
            "mean_std_rank": sum(parse_float(r["std_rank"]) for r in rows) / len(rows),
            "mean_top1_agreement": sum(parse_float(r["top1_agreement_rate"]) for r in rows) / len(rows),
            "mean_top3_agreement": sum(parse_float(r["top3_agreement_rate"]) for r in rows) / len(rows),
            "proto_top1_id": top1_id,
            "proto_top1_freq": top1_n,
            "proto_top3_ids": top3_ids,
            "proto_top3_freq": top3_n,
        })

        anchors = sorted(
            rows,
            key=lambda r: (
                parse_float(r["std_rank"]),
                -parse_float(r["top1_agreement_rate"]),
                parse_float(r["mean_rank"]),
            )
        )[:3]

        for r in anchors:
            anchor_rows.append({
                "relation_id": rel_id,
                "relation_name": rel_name,
                "combined_bucket": bucket,
                "head_name": r["head_name"],
                "gold_tail_name": r["gold_tail_name"],
                "run_n": r["run_n"],
                "mean_rank": r["mean_rank"],
                "std_rank": r["std_rank"],
                "top1_agreement_rate": r["top1_agreement_rate"],
                "top3_agreement_rate": r["top3_agreement_rate"],
                "most_common_top1_id": r["most_common_top1_id"],
                "most_common_top3_ids": r["most_common_top3_ids"],
            })

    proto_tsv = outdir / "BUCKET_PROTOTYPE_SUMMARY.tsv"
    with proto_tsv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(proto_rows[0].keys()), delimiter="\t")
        w.writeheader()
        for row in proto_rows:
            w.writerow(row)

    anchor_tsv = outdir / "BUCKET_ANCHOR_QUERIES.tsv"
    with anchor_tsv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(anchor_rows[0].keys()), delimiter="\t")
        w.writeheader()
        for row in anchor_rows:
            w.writerow(row)

    txt = outdir / "BUCKET_PROTOTYPE_SUMMARY.txt"
    lines = ["[BUCKET_PROTOTYPES]"]
    for row in proto_rows:
        lines.append(
            f'{row["relation_id"]}\t{row["relation_name"]}\t{row["combined_bucket"]}\t'
            f'query_n={row["query_n"]}\tmean_rank={float(row["mean_rank"]):.4f}\t'
            f'mean_std={float(row["mean_std_rank"]):.4f}\t'
            f'top1_agree={float(row["mean_top1_agreement"]):.4f}\t'
            f'top3_agree={float(row["mean_top3_agreement"]):.4f}\t'
            f'proto_top1={row["proto_top1_id"]}\tproto_top3={row["proto_top3_ids"]}'
        )
    lines += ["", "[ANCHOR_QUERIES]"]
    for row in anchor_rows:
        lines.append(
            f'{row["relation_id"]}\t{row["relation_name"]}\t{row["combined_bucket"]}\t'
            f'{row["head_name"]}->{row["gold_tail_name"]}\t'
            f'mean_rank={row["mean_rank"]}\tstd_rank={row["std_rank"]}\t'
            f'top1_agree={row["top1_agreement_rate"]}\ttop3_agree={row["top3_agreement_rate"]}'
        )
    txt.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote: {proto_tsv}")
    print(f"[OK] wrote: {anchor_tsv}")
    print(f"[OK] wrote: {txt}")

if __name__ == "__main__":
    main()
