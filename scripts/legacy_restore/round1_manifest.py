from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

PATTERNS = [
    ("log", "**/log.txt"),
    ("ckpt", "**/model_epoch*.pth"),
    ("yaml", "**/*.yaml"),
    ("probe", "**/*probe*.tsv"),
    ("topk", "**/*topk*.tsv"),
    ("valid_tsv", "**/*valid*.tsv"),
    ("test_tsv", "**/*test*.tsv"),
]

def collect(runroot: Path):
    rows = []
    for kind, pat in PATTERNS:
        for p in sorted(runroot.glob(pat)):
            if p.is_file():
                rows.append({
                    "kind": kind,
                    "path": str(p),
                    "name": p.name,
                    "parent": str(p.parent),
                    "size": p.stat().st_size,
                })
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runroot", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    runroot = Path(args.runroot).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    if not runroot.is_dir():
        raise SystemExit(f"[ERR] runroot not found: {runroot}")

    rows = collect(runroot)

    manifest_json = outdir / "ROUND1_MANIFEST.json"
    manifest_tsv = outdir / "ROUND1_MANIFEST.tsv"
    manifest_txt = outdir / "ROUND1_MANIFEST.txt"

    payload = {
        "runroot": str(runroot),
        "file_count": len(rows),
        "rows": rows,
    }
    manifest_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with manifest_tsv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["kind", "name", "parent", "size", "path"], delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    lines = [
        f"RUNROOT\t{runroot}",
        f"FILE_COUNT\t{len(rows)}",
        ""
    ]
    for r in rows:
        lines.append(f"{r['kind']}\t{r['path']}")
    manifest_txt.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote: {manifest_json}")
    print(f"[OK] wrote: {manifest_tsv}")
    print(f"[OK] wrote: {manifest_txt}")

if __name__ == "__main__":
    main()
