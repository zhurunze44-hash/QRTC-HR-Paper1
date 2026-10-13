from __future__ import annotations
import argparse
import csv
import math
from collections import defaultdict, Counter
from pathlib import Path

def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")

def std(xs):
    if len(xs) <= 1:
        return 0.0
    mu = mean(xs)
    return math.sqrt(sum((x - mu) ** 2 for x in xs) / (len(xs) - 1))

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

def load_probe_runs(path: Path):
    rows = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            if row["pair_status"] == "paired" and row["summary_path"] and row["topk_path"]:
                rows.append(row)
    return rows

def query_key(row):
    return (
        row["valid_original_index"],
        row["head_id"],
        row["relation_id"],
        row["gold_tail_id"],
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-runs", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--topk-cut", type=int, default=3)
    args = ap.parse_args()

    probe_runs = Path(args.probe_runs).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    run_rows = load_probe_runs(probe_runs)

    by_query = defaultdict(list)

    for run in run_rows:
        run_dir = run["run_dir"]
        summary_path = Path(run["summary_path"])
        topk_path = Path(run["topk_path"])

        summary_map = {}
        with summary_path.open("r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                k = query_key(row)
                summary_map[k] = {
                    "valid_original_index": row["valid_original_index"],
                    "head_id": row["head_id"],
                    "head_name": row["head_name"],
                    "relation_id": row["relation_id"],
                    "relation_name": row["relation_name"],
                    "gold_tail_id": row["gold_tail_id"],
                    "gold_tail_name": row["gold_tail_name"],
                    "gold_rank": parse_int(row["gold_tail_filtered_rank"], 10**9),
                    "hit1": parse_int(row["hit_at_1"]),
                    "hit10": parse_int(row["hit_at_10"]),
                    "hit100": parse_int(row["hit_at_100"]),
                    "cand_n": parse_int(row["filtered_candidate_n"]),
                    "gold_score": parse_float(row["gold_tail_score"]),
                }

        topk_map = defaultdict(list)
        with topk_path.open("r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                rank = parse_int(row["topk_rank"], 10**9)
                if rank <= args.topk_cut:
                    k = query_key(row)
                    topk_map[k].append((rank, row["pred_tail_id"], row["pred_tail_name"], parse_float(row["pred_score"])))

        for k, s in summary_map.items():
            topk_sorted = sorted(topk_map.get(k, []), key=lambda x: x[0])
            top1_id = topk_sorted[0][1] if len(topk_sorted) >= 1 else ""
            top1_name = topk_sorted[0][2] if len(topk_sorted) >= 1 else ""
            top3_ids = "|".join(x[1] for x in topk_sorted)
            top3_names = "|".join(x[2] for x in topk_sorted)

            by_query[k].append({
                "run_dir": run_dir,
                **s,
                "top1_pred_id": top1_id,
                "top1_pred_name": top1_name,
                "top3_pred_ids": top3_ids,
                "top3_pred_names": top3_names,
            })

    stability_rows = []
    for k, rows in by_query.items():
        if len(rows) < 2:
            continue

        ranks = [r["gold_rank"] for r in rows]
        hit10s = [r["hit10"] for r in rows]
        hit100s = [r["hit100"] for r in rows]
        cand_ns = [r["cand_n"] for r in rows]
        scores = [r["gold_score"] for r in rows]

        top1_counter = Counter(r["top1_pred_id"] for r in rows if r["top1_pred_id"])
        top3_counter = Counter(r["top3_pred_ids"] for r in rows if r["top3_pred_ids"])

        most_common_top1_id, most_common_top1_n = ("", 0)
        if top1_counter:
            most_common_top1_id, most_common_top1_n = top1_counter.most_common(1)[0]

        most_common_top3_ids, most_common_top3_n = ("", 0)
        if top3_counter:
            most_common_top3_ids, most_common_top3_n = top3_counter.most_common(1)[0]

        ref = rows[0]
        stability_rows.append({
            "valid_original_index": ref["valid_original_index"],
            "head_id": ref["head_id"],
            "head_name": ref["head_name"],
            "relation_id": ref["relation_id"],
            "relation_name": ref["relation_name"],
            "gold_tail_id": ref["gold_tail_id"],
            "gold_tail_name": ref["gold_tail_name"],
            "run_n": len(rows),
            "mean_rank": mean(ranks),
            "std_rank": std(ranks),
            "min_rank": min(ranks),
            "max_rank": max(ranks),
            "mean_hits10": mean(hit10s),
            "mean_hits100": mean(hit100s),
            "mean_candidate_n": mean(cand_ns),
            "std_candidate_n": std(cand_ns),
            "mean_gold_score": mean(scores),
            "std_gold_score": std(scores),
            "distinct_top1_n": len(top1_counter),
            "top1_agreement_rate": (most_common_top1_n / len(rows)) if rows else 0.0,
            "most_common_top1_id": most_common_top1_id,
            "distinct_top3_n": len(top3_counter),
            "top3_agreement_rate": (most_common_top3_n / len(rows)) if rows else 0.0,
            "most_common_top3_ids": most_common_top3_ids,
        })

    stability_rows.sort(key=lambda r: (-r["run_n"], float(r["std_rank"]), r["relation_id"], r["valid_original_index"]))

    out_tsv = outdir / "QUERY_REPEAT_STABILITY.tsv"
    if stability_rows:
        with out_tsv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(stability_rows[0].keys()), delimiter="\t")
            w.writeheader()
            for row in stability_rows:
                w.writerow(row)
    else:
        out_tsv.write_text("", encoding="utf-8")

    out_txt = outdir / "QUERY_REPEAT_STABILITY.txt"
    lines = [
        f"QUERY_REPEAT_N\t{len(stability_rows)}",
        "",
        "[TOP_40_BY_RUN_COUNT_THEN_LOW_STD]"
    ]
    for r in stability_rows[:40]:
        lines.append(
            f'{r["relation_id"]}\t{r["relation_name"]}\t'
            f'query={r["head_name"]}->{r["gold_tail_name"]}\t'
            f'run_n={r["run_n"]}\tmean_rank={r["mean_rank"]:.4f}\tstd_rank={r["std_rank"]:.4f}\t'
            f'top1_agree={r["top1_agreement_rate"]:.4f}\ttop3_agree={r["top3_agreement_rate"]:.4f}'
        )
    out_txt.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote: {out_tsv}")
    print(f"[OK] wrote: {out_txt}")

if __name__ == "__main__":
    main()
