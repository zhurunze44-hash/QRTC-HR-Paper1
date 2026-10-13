# Reproducibility

## Scope

This package supports **frozen-asset verification** and, where environment and checkpoints allow, **evaluation without retraining**. It does not authorize or provide a path to reopen training.

## Steps

1. Clone the published Git repository (source + manifests + docs).
2. Download Release tag `paper1-qrtchr-frozen-20261013-v1` via `scripts/download_assets.sh`.
3. Run `python scripts/verify_assets.py` and require all SHA256 checks to pass.
4. Inspect `manifests/CLAIM_TO_ARTIFACT_MAP.tsv` for claim → checkpoint → result bindings.
5. Use historical entry `evaluation/eval_and_predict.py` only with the sealed configs/checkpoints and a compatible environment (`docs/environment/`).

## Verified on build host (not yet from GitHub)

| Check | Result |
|-------|--------|
| Inclusion packing | 1567 unique files |
| Local zstd/tar restore SHA256 | PASS (1567/1567) |
| Remote GitHub re-download | **NOT RUN** (network/auth blocked) |

## Known non-reproducible items

See `KNOWN_LIMITATIONS.md` and `docs/EVIDENCE_BUNDLE_STATUS.json` fields:

- `five_seed_status`: `MISSING_FORMAL_COMPLETE_PANEL`
- `checkpoint_status`: `FOUND_EXCEPT_PC_WOBRG_MAY02_QRTC`
- `a1_status`: `STOP__A1_ORIGINAL_PANEL_PROVENANCE_INSUFFICIENT`
- `exact_replay_status`: `HISTORICAL_BINDING_PASS__LIVE_REPLAY_NOT_RUN`
