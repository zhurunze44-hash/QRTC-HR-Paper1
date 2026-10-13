from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

PATTERNS = [
    ("log", "**/log.txt"),
    ("ckpt", "**/model_epoch*.pth"),
    ("yaml", "**/*.yaml"),
    ("probe_tsv", "**/*probe*.tsv"),
    ("topk_tsv", "**/*topk*.tsv"),
    ("valid_tsv", "**/*valid*.tsv"),
    ("test_tsv", "**/*test*.tsv"),
    ("router_tsv", "**/*router*.tsv"),
    ("pred_tsv", "**/*pred*.tsv"),
]

def guess_bucket(path: Path) -> str:
    s = str(path)
    if "stage1_mainline_freeze" in s:
        return "stage_bind"
    if "bind_" in s or "/shells/" in s:
        return "bind_or_shell"
    if "/KnowledgeGraphCompletionBiomed/" in s:
        return "run_artifact"
    return "other"

def collect(root: Path):
    rows = []
    seen = set()
    for kind, pat in PATTERNS:
        for p in root.glob(pat):
            if not p.is_file():
                continue
            rp = str(p.resolve())
            if rp in seen:
                continue
            seen.add(rp)
            st = p.stat()
            rows.append({
                "kind": kind,
                "bucket": guess_bucket(p),
                "name": p.name,
                "path": rp,
                "parent": str(p.parent.resolve()),
                "size": st.st_size,
                "mtime": int(st.st_mtime),
            })
    rows.sort(key=lambda x: (-x["mtime"], x["kind"], x["path"]))
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--search-root", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    root = Path(args.search_root).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    if not root.is_dir():
        raise SystemExit(f"[ERR] search root not found: {root}")

    rows = collect(root)

    by_kind = {}
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1

    summary = {
        "search_root": str(root),
        "file_count": len(rows),
        "by_kind": by_kind,
    }

    (outdir / "ROUND1_ASSET_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    with (outdir / "ROUND1_ASSET_INVENTORY.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["kind", "bucket", "name", "size", "mtime", "parent", "path"],
            delimiter="\t",
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)

    lines = [
        f"SEARCH_ROOT\t{root}",
        f"FILE_COUNT\t{len(rows)}",
        "",
        "[BY_KIND]",
    ]
    for k, v in sorted(by_kind.items()):
        lines.append(f"{k}\t{v}")
    lines.append("")
    lines.append("[TOP_RECENT_80]")
    for r in rows[:80]:
        lines.append(f"{r['kind']}\t{r['bucket']}\t{r['path']}")
    (outdir / "ROUND1_ASSET_INVENTORY.txt").write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote: {outdir / 'ROUND1_ASSET_SUMMARY.json'}")
    print(f"[OK] wrote: {outdir / 'ROUND1_ASSET_INVENTORY.tsv'}")
    print(f"[OK] wrote: {outdir / 'ROUND1_ASSET_INVENTORY.txt'}")
    print("[OK] by_kind =", json.dumps(by_kind, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
