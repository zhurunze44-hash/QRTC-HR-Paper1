# Known Limitations

## Scientific / evidence gaps (do not overclaim)

1. **Complete formal multi-seed (5-seed) panel** is missing on disk; A1 panel provenance was rejected for formal use.
2. **`PC_WOBRG_MAY02_QRTC` checkpoint** is missing and not reconstructible without new training (forbidden under freeze).
3. **Exact live replay** of sealed metrics was not re-run in the 2026-10-05 evidence bundle (`HISTORICAL_BINDING_PASS__LIVE_REPLAY_NOT_RUN`).
4. Included `.pth` files contain **historical negative evidence** names such as `BAD_RERUN` and `NOT_MAY02`. See `docs/WEIGHTS_INDEX.md`. Do **not** treat every weight as a formal primary result.

## Publication / redistribution

5. **Dataset redistribution rights** for PC_KEGG / LncTarD-derived graphs are **not independently cleared**. Treat `data/` and split-provenance graphs as **reviewer-restricted** unless/until licenses are confirmed. Prefer upstream acquisition instructions for any public redistribution.
6. This **public/reviewer pack** deliberately **omits** journal submission internals (cover letters, reviewer persona / response banks, submission zips) and nested zip/tar process archives. The larger internal master archive remains offline-only.
7. Local SHA256 restore of the freeze proves **archive integrity**, not that every paper table has been re-executed end-to-end on a clean machine in this publication pass.

## Accurate claim language

Allowed after GitHub remote verification: assets available, checksum-verifiable, limitations disclosed.

**Forbidden:** “Fully reproducible”, “All experiments reproduced”, “100% reproducibility”.


## Sanitized dedicated-repo pack (2026-10-13)

- Restricted graph split files removed from both Git history inputs and Release.
- `.bak` backups removed from Code tree.
- Large `results/` binary/data payloads not committed; small index/docs only.
