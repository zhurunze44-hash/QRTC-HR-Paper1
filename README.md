# QRTC-HR (Paper1)

Dedicated **public** repository for the QRTC-HR / Paper1 sanitized source code, documentation, and reproducibility materials.

**Scientific freeze:** no new training / no sealed-metric edits.

| Item | Value |
|------|------|
| Repository | https://github.com/zhurunze44-hash/QRTC-HR-Paper1 |
| Source commit | `08cbcce6630bfacf41f3c6062dd38415d83801c5` |
| Draft Release tag | `paper1-qrtchr-sanitized-20261013-v1` |
| Draft Release | Unpublished; not publicly accessible |
| Archive | `paper1-qrtchr-sanitized-20261013-v1.tar.zst` |
| SHA256 | `4e6eb69686f83a372105cfbf1830dfbd1c96808c5491bbc6c59ee42178ca1915` |
| Remote re-download verify | **PASS** (2026-10-13) |

## Important

- **PC_KEGG / LncTarD graph splits are not in this repo or Release** until redistribution rights are cleared. See `data/README_DATA_ACQUISITION.md`.
- Not every `.pth` is a formal primary result weight (`docs/WEIGHTS_INDEX.md`).
- Do **not** claim “fully reproducible”. See `KNOWN_LIMITATIONS.md`.
- The repository is public, but the large-asset Release remains an unpublished draft and is not publicly accessible. Publication requires redistribution-rights clearance and an audit of the release contents.

## Asset verification (requires access to the unpublished Release)
```bash
git clone https://github.com/zhurunze44-hash/QRTC-HR-Paper1.git
cd QRTC-HR-Paper1
REPO=zhurunze44-hash/QRTC-HR-Paper1 bash scripts/download_assets.sh
python scripts/verify_assets.py
```

## Audits

- `docs/INDEPENDENT_AUDIT_20261013.md`
- `docs/SECOND_INDEPENDENT_AUDIT_20261013.md`
