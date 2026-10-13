# QRTC-HR (Paper1)

Dedicated repository for the QRTC-HR / Paper1 reproducibility package.

**Scientific freeze:** no new training / no sealed-metric edits.

| Item | Value |
|------|------|
| Release tag | `paper1-qrtchr-sanitized-20261013-v1` |
| Sanitized freeze | `paper1-qrtchr-sanitized-20261013-v1.tar.zst` |
| SHA256 | `4e6eb69686f83a372105cfbf1830dfbd1c96808c5491bbc6c59ee42178ca1915` |
| Freeze files | 1419 |
| Code files (this tree) | 677 |

## Important

- **PC_KEGG / LncTarD graph splits are not in this repo or Release** until redistribution rights are cleared. See `data/README_DATA_ACQUISITION.md` and `DATA_AVAILABILITY.md`.
- Not every `.pth` is a formal primary result weight (`docs/WEIGHTS_INDEX.md`).
- Do **not** claim “fully reproducible”. See `KNOWN_LIMITATIONS.md`.

## After Release publish

```bash
git clone <THIS_REPO_URL>
cd QRTC-HR-Paper1
REPO=<owner>/QRTC-HR-Paper1 bash scripts/download_assets.sh
python scripts/verify_assets.py
```

## Audits

- `docs/INDEPENDENT_AUDIT_20261013.md`
- `docs/SECOND_INDEPENDENT_AUDIT_20261013.md`
