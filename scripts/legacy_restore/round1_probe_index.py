from __future__ import annotations
import argparse
import csv
from pathlib import Path
from collections import defaultdict

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    inv = Path(args.inventory).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    if not inv.is_file():
        raise SystemExit(f"[ERR] inventory not found: {inv}")

    groups = defaultdict(lambda: {
        "summary": [],
        "topk": [],
        "other_probe": [],
    })

    with inv.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            kind = row.get("kind", "")
            path = row.get("path", "")
            name = row.get("name", "")
            parent = row.get("parent", "")
            if kind != "probe_tsv":
                continue
            key = parent
            if name == "valid_tail_probe_summary.tsv":
                groups[key]["summary"].append(path)
            elif name == "valid_tail_probe_topk.tsv":
                groups[key]["topk"].append(path)
            else:
                groups[key]["other_probe"].append(path)

    rows = []
    for run_dir, d in sorted(groups.items()):
        summary_n = len(d["summary"])
        topk_n = len(d["topk"])
        other_n = len(d["other_probe"])
        pair_status = "paired" if summary_n >= 1 and topk_n >= 1 else "incomplete"
        rows.append({
            "run_dir": run_dir,
            "summary_n": summary_n,
            "topk_n": topk_n,
            "other_probe_n": other_n,
            "pair_status": pair_status,
            "summary_path": d["summary"][0] if d["summary"] else "",
            "topk_path": d["topk"][0] if d["topk"] else "",
        })

    out_tsv = outdir / "ROUND1_PROBE_RUNS.tsv"
    with out_tsv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "run_dir", "summary_n", "topk_n", "other_probe_n",
                "pair_status", "summary_path", "topk_path"
            ],
            delimiter="\t"
        )
        w.writeheader()
        for row in rows:
            w.writerow(row)

    paired = [x for x in rows if x["pair_status"] == "paired"]
    txt = outdir / "ROUND1_PROBE_RUNS.txt"
    lines = [
        f"TOTAL_RUN_DIRS\t{len(rows)}",
        f"PAIRED_RUN_DIRS\t{len(paired)}",
        "",
        "[PAIRED_TOP_80]"
    ]
    for row in paired[:80]:
        lines.append(f"{row['run_dir']}\t{row['summary_path']}\t{row['topk_path']}")
    txt.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote: {out_tsv}")
    print(f"[OK] wrote: {txt}")
    print(f"[OK] total_run_dirs={len(rows)} paired_run_dirs={len(paired)}")

if __name__ == "__main__":
    main()
