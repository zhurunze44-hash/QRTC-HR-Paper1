from __future__ import annotations
import argparse
import csv
from pathlib import Path

def read_header(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t")
        try:
            return next(r)
        except StopIteration:
            return []

def count_rows(path: Path, limit: int = 3):
    rows = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for i, row in enumerate(r):
            if i >= limit:
                break
            rows.append(row)
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-runs", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--limit", type=int, default=12)
    args = ap.parse_args()

    probe_runs = Path(args.probe_runs).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    with probe_runs.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            if row["pair_status"] == "paired":
                rows.append(row)

    rows = rows[:args.limit]

    summary_lines = []
    topk_lines = []

    for i, row in enumerate(rows, 1):
        summary_path = Path(row["summary_path"])
        topk_path = Path(row["topk_path"])

        s_header = read_header(summary_path)
        t_header = read_header(topk_path)

        summary_lines.append(f"[{i}] RUN_DIR\t{row['run_dir']}")
        summary_lines.append(f"[{i}] SUMMARY_HEADER\t" + "\t".join(s_header))
        for ex in count_rows(summary_path, limit=3):
            summary_lines.append(f"[{i}] SUMMARY_EXAMPLE\t{ex}")

        topk_lines.append(f"[{i}] RUN_DIR\t{row['run_dir']}")
        topk_lines.append(f"[{i}] TOPK_HEADER\t" + "\t".join(t_header))
        for ex in count_rows(topk_path, limit=3):
            topk_lines.append(f"[{i}] TOPK_EXAMPLE\t{ex}")

    (outdir / "ROUND1_SUMMARY_SCHEMA.txt").write_text("\n".join(summary_lines), encoding="utf-8")
    (outdir / "ROUND1_TOPK_SCHEMA.txt").write_text("\n".join(topk_lines), encoding="utf-8")

    print(f"[OK] wrote: {outdir / 'ROUND1_SUMMARY_SCHEMA.txt'}")
    print(f"[OK] wrote: {outdir / 'ROUND1_TOPK_SCHEMA.txt'}")

if __name__ == "__main__":
    main()
