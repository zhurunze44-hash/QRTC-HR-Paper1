# 06 — Reproducibility Audit

## Scientific freeze respected

- No training launched
- No hyperparameter search
- No new model/experiment design
- No sealed metric rewriting
- LAST_CHANCE / A1 / WP5B-R not reopened

## Evidence completeness (from sealed Oct 5 bundle)

| Area | Status |
|------|--------|
| Formal source | FOUND (`QRTC_HR_SOURCE_RESTORE_20260908`) |
| Primary results | MATCH |
| Formal checkpoints | FOUND except `PC_WOBRG_MAY02_QRTC` |
| 5-seed panel | MISSING formal complete panel; A1 rejected |
| Bootstrap | REAUDIT_CPU_DONE |
| Exact replay | Historical binding PASS; live replay not run |
| Bundle final_status | `PASS__PAPER1_FINAL_SERVER_EVIDENCE_BUNDLE_COMPLETE_WITH_DOCUMENTED_GAPS` |

## Delivery reproducibility

| Layer | Status |
|-------|--------|
| Source tree staged | YES (`04_repo_build/qrtc-hr-paper1`) |
| Freeze archive local integrity | PASS |
| GitHub source commit | NO |
| GitHub Release | NO |
| Remote re-download verify | NO |
| Frozen eval end-to-end on this host | NOT RUN (would need env+GPU; not required for archival gate) |

## Accurate claim language

Allowed after full remote verification: assets available + checksum-verifiable + limitations disclosed.

**Forbidden now:** “Fully reproducible”, “All experiments reproduced”, “100% reproducibility”.

Closest honest terminal if only local work counted:

`HOLD__GITHUB_AUTH_REQUIRED` (publication incomplete)

If GitHub publish later succeeds with gaps disclosed:

`PASS__PAPER1_AVAILABLE_ASSETS_PUBLISHED__REPRO_LIMITATIONS_DISCLOSED`
