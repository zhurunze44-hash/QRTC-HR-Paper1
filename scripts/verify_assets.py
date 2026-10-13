#!/usr/bin/env python3
"""Verify frozen_assets against manifests/PUBLIC_INCLUSION_MANIFEST.tsv."""
from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manifests" / "PUBLIC_INCLUSION_MANIFEST.tsv"
ASSETS = ROOT / "frozen_assets"

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    if not MAN.is_file():
        print("MISSING_MANIFEST", MAN)
        return 2
    if not ASSETS.is_dir():
        print("MISSING_FROZEN_ASSETS_DIR", ASSETS)
        print("Run scripts/download_assets.sh after the Release is published.")
        return 2
    rows = list(csv.DictReader(MAN.open(encoding="utf-8"), delimiter="\t"))
    ok = fail = missing = 0
    for r in rows:
        rel = r["canonical_source_path"]
        p = ASSETS / rel
        if not p.is_file():
            missing += 1
            print("MISSING", rel)
            continue
        digest = sha256(p)
        if digest != r["sha256"] or p.stat().st_size != int(r["bytes"]):
            fail += 1
            print("FAIL", rel)
        else:
            ok += 1
    summary = {"ok": ok, "fail": fail, "missing": missing, "total": len(rows)}
    print(json.dumps(summary, indent=2))
    return 0 if fail == 0 and missing == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
