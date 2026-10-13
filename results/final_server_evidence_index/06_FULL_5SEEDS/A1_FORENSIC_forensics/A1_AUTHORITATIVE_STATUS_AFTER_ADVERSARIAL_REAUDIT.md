# A1 authoritative status after adversarial re-audit (revised)

**UTC:** 2026-10-02T09:35:00Z  
**Scope:** forensics-only status seal. No GPU. No resume. Does not rewrite scientific receipts/checkpoints.

```
A1_ORIGINAL_PANEL =
HOLD__PROVENANCE_AND_PRE_POST_PATCH_COMPARABILITY_UNRESOLVED

A1_RESUME_AUTHORIZED = false
A2 = NOT_AUTHORIZED
A3 = NOT_AUTHORIZED
GENERIC_KG = NOT_AUTHORIZED
GPU = DO_NOT_TOUCH
```

## RAW1024 — split propositions (do not collapse)

```
RAW1024_NUMERICAL_RESULT =
ESTABLISHED__MRR_0.1946338713169098

RAW1024_FRESH_LINEAGE =
ESTABLISHED

RAW1024_WITHIN_RUN_LATE_TRAINING_DIVERGENCE =
ESTABLISHED

RAW1024_CONTRACT_ADMISSIBILITY =
HOLD__RUNTIME_SOURCE_IMPORT_PROVENANCE_REQUIRES_FINAL_BINDING
```

**Withdrawn as premature:**
`ADMISSIBLE__WITH_OPERATIONAL_INCIDENTS_NOT_AFFECTING_SCIENCE`

Reason: lineage cleanliness + numerical establishment do **not** by themselves prove the run executed the frozen SOURCE_RESTORE scientific implementation under a fully bound import provenance. `run.py` uses `sys.path.append` (not scrub); historical `PYTHONPATH` is NOT_PROVEN; successful trains lack `module.__file__` receipts.

If Gate 1 is later closed (runtime import = frozen SOURCE_RESTORE hashes), upgrade only then to:
`ADMISSIBLE__WITH_OPERATIONAL_INCIDENTS_NOT_AFFECTING_SCIENCE`
and keep 0.1946 in primary — never delete because ugly.

## Three gates (current)

| Gate | Status | Note |
|------|--------|------|
| 1 Runtime import of first 6 | **PARTIALLY_BOUND** | Tracebacks show SOURCE_RESTORE only (0 WORK/worktree). Freeze SHA ≡ live; source mtimes May-2026. BASE1024 weak (almost no stack). Winning silent runs inferred. Not FULLY_BOUND. |
| 2 Old vs V2 harness science equivalence | **UNRESOLVED** | Most patches operational-only; sys.path/shim scrub exceptional; historical script bytes not recoverable (no git). |
| 3 BASE1026 | **Policy-ready** | ckpt has `model`+`optimizer` only; no RNG/scheduler/scaler. If original A1 continues: keep INTERRUPTED lineage + **fresh restart seed1026 from epoch0** (no formal test outcome ⇒ not outcome-driven). Exact resume not claimed. |

Evidence: `GATE1_RUNTIME_IMPORT_PROVENANCE_EVIDENCE.json`

## Two clean endgames (still not executing)

**A — Rescue original A1** only if Gate1 FULLY closed + Gate2 science-equivalent + eval semantics match → then GO under frozen contract; RAW1024 enters primary if contract-admissible.

**B — Cannot audit-rescue** → `STOP__A1_ORIGINAL_PANEL_PROVENANCE_INSUFFICIENT`. Any A1-R/V2 is a **post-hoc** new experiment, not the confirmatory A1. Do not default-authorize 15-run rerun.

## Separation of levels (the actual finding)

| Level | Status |
|-------|--------|
| One run’s lineage clean | RAW1024 fresh lineage ESTABLISHED |
| Current harness repaired | 8/8 MATCH now — does not wash Sep runs |
| Entire 15-cell primary panel still legal | **NOT PROVEN** → HOLD |
