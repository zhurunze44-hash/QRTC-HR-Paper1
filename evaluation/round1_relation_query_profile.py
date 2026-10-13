from __future__ import annotations
import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")

def median(xs):
    if not xs:
        return float("nan")
    ys = sorted(xs)
    n = len(ys)
    m = n // 2
    if n % 2:
        return ys[m]
    return (ys[m - 1] + ys[m]) / 2.0

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
            if row["pair_status"] == "paired" and row["summary_path"]:
                rows.append(row)
    return rows

def profile_one_summary(run_dir: str, summary_path: Path):
    buckets = defaultdict(list)

    with summary_path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            rel_id = row["relation_id"]
            rel_name = row["relation_name"]
            key = (rel_id, rel_name)

            buckets[key].append({
                "rank": parse_int(row["gold_tail_filtered_rank"], default=10**9),
                "hit1": parse_int(row["hit_at_1"]),
                "hit10": parse_int(row["hit_at_10"]),
                "hit100": parse_int(row["hit_at_100"]),
                "cand_n": parse_int(row["filtered_candidate_n"]),
                "gold_score": parse_float(row["gold_tail_score"]),
            })

    out_rows = []
    for (rel_id, rel_name), items in sorted(buckets.items(), key=lambda x: int(x[0][0])):
        ranks = [x["rank"] for x in items]
        hit1s = [x["hit1"] for x in items]
        hit10s = [x["hit10"] for x in items]
        hit100s = [x["hit100"] for x in items]
        cand_ns = [x["cand_n"] for x in items]
        scores = [x["gold_score"] for x in items]

        out_rows.append({
            "run_dir": run_dir,
            "summary_path": str(summary_path),
            "relation_id": rel_id,
            "relation_name": rel_name,
            "query_n": len(items),
            "mean_rank": mean(ranks),
            "median_rank": median(ranks),
            "hits1_rate": mean(hit1s),
            "hits10_rate": mean(hit10s),
            "hits100_rate": mean(hit100s),
            "mean_filtered_candidate_n": mean(cand_ns),
            "median_filtered_candidate_n": median(cand_ns),
            "mean_gold_tail_score": mean(scores),
            "median_gold_tail_score": median(scores),
        })
    return out_rows

def build_stability(profile_rows):
    by_rel = defaultdict(list)
    for row in profile_rows:
        key = (row["relation_id"], row["relation_name"])
        by_rel[key].append(row)

    out_rows = []
    for (rel_id, rel_name), rows in sorted(by_rel.items(), key=lambda x: int(x[0][0])):
        mean_ranks = [float(r["mean_rank"]) for r in rows]
        hits10 = [float(r["hits10_rate"]) for r in rows]
        hits100 = [float(r["hits100_rate"]) for r in rows]
        query_ns = [int(r["query_n"]) for r in rows]
        cand_ns = [float(r["mean_filtered_candidate_n"]) for r in rows]
        scores = [float(r["mean_gold_tail_score"]) for r in rows]

        out_rows.append({
            "relation_id": rel_id,
            "relation_name": rel_name,
            "run_n": len(rows),
            "mean_query_n": mean(query_ns),
            "mean_of_mean_rank": mean(mean_ranks),
            "std_of_mean_rank": std(mean_ranks),
            "mean_hits10_rate": mean(hits10),
            "std_hits10_rate": std(hits10),
            "mean_hits100_rate": mean(hits100),
            "std_hits100_rate": std(hits100),
            "mean_filtered_candidate_n": mean(cand_ns),
            "std_filtered_candidate_n": std(cand_ns),
            "mean_gold_tail_score": mean(scores),
            "std_gold_tail_score": std(scores),
        })
    return out_rows

def write_tsv(path: Path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        for row in rows:
            w.writerow(row)

def write_txt(path: Path, profile_rows, stability_rows):
    lines = [
        f"PROFILE_ROW_N\t{len(profile_rows)}",
        f"STABILITY_ROW_N\t{len(stability_rows)}",
        "",
        "[TOP_STABLE_BY_LOW_RANK_STD]"
    ]
    top = sorted(stability_rows, key=lambda r: (float(r["std_of_mean_rank"]), -float(r["mean_hits10_rate"])))[:20]
    for r in top:
        lines.append(
            f'{r["relation_id"]}\t{r["relation_name"]}\trun_n={r["run_n"]}\t'
            f'mean_rank={r["mean_of_mean_rank"]:.4f}\tstd_rank={r["std_of_mean_rank"]:.4f}\t'
            f'hits10={r["mean_hits10_rate"]:.4f}\thits100={r["mean_hits100_rate"]:.4f}'
        )
    path.write_text("\n".join(lines), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-runs", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    probe_runs = Path(args.probe_runs).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    run_rows = load_probe_runs(probe_runs)

    profile_rows = []
    for row in run_rows:
        run_dir = row["run_dir"]
        summary_path = Path(row["summary_path"])
        if summary_path.is_file():
            profile_rows.extend(profile_one_summary(run_dir, summary_path))

    stability_rows = build_stability(profile_rows)

    write_tsv(outdir / "RELATION_QUERY_PROFILE.tsv", profile_rows)
    write_tsv(outdir / "RELATION_QUERY_STABILITY.tsv", stability_rows)
    write_txt(outdir / "RELATION_QUERY_PROFILE.txt", profile_rows, stability_rows)

    print(f"[OK] wrote: {outdir / 'RELATION_QUERY_PROFILE.tsv'}")
    print(f"[OK] wrote: {outdir / 'RELATION_QUERY_STABILITY.tsv'}")
    print(f"[OK] wrote: {outdir / 'RELATION_QUERY_PROFILE.txt'}")

if __name__ == "__main__":
    main()
