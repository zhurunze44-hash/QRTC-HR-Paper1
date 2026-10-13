# Public / Reviewer Release Notes (2026-10-13)

## Decision

- **INTERNAL master** `paper1-qrtchr-frozen-20261013-v1` (1567 files): offline only — unchanged.
- **PUBLIC/REVIEWER** `paper1-qrtchr-public-reviewer-20261013-v1`: curated subset for GitHub Code + Release.

## Independent audit

See `docs/INDEPENDENT_AUDIT_20261013.md` (LOCAL_INVENTORY_ACCOUNTING=PASS; PUBLIC_RELEASE was HOLD until this remediation).

## Dropped from public pack (133 files)

Primary reasons:

- Journal submission internals (`JIIS_SUBMISSION_*`, `PAPER1_CMPB_FINAL_*`, `jiis/` submission zip)
- Nested zip/tar process archives and `_local_archives/`
- Upload/helper tooling prefixes

Full list: `PUBLIC_DROP_MANIFEST.tsv`

## Accounting note (1590 vs 1965/1966)

- Unique SHA256 objects in inventory: **1590** (= 3556 − **1966** duplicate path entries)
- Publication path-dedup count **1965** satisfies 1567 + 24 + 1965 = 3556
- Both are valid; they measure different things. Document both; no science gap.

## Still HOLD / human actions

1. Confirm PC_KEGG / LncTarD redistribution rights before making the repo/Release world-readable.
2. Rotate any SSH passwords that ever appeared in restore helpers; audit old git history if those scripts were ever pushed.
3. Publish Code + Draft Release, then re-download and verify SHA256 before marking Release non-draft.
4. Prefer a dedicated Paper1 repo for any future public mirror; do not flip the whole lab vault to Public.
