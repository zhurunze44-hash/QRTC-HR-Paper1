# G0 Authority Lock — LAST_CHANCE V1 (2026-10-02)

**Package:** `PAPER1_FEEDBACK_STATE_LAST_CHANCE_V1_20261002`  
**Gate:** G0 only (asset / identity / cost PLAN)  
**Mode:** ZERO-TRAINING · CPU/read-only · **no GPU** · **no torch CUDA** · do not touch PID 93604 / sara / `/data/hwy/CoRe-MRN-Evidence`

## Sealed sources reused (not reinvented)

| Artifact | Path in this package | Upstream |
|----------|----------------------|----------|
| Asset ledger | `AUTHORITATIVE_ASSET_LEDGER.tsv` | CMPB `01_ASSET_AUDIT/` |
| Binding table | `BINDING_TABLE.tsv` | CMPB `01_ASSET_AUDIT/` |
| Audit status | `AUTHORITATIVE_ASSET_AUDIT_STATUS.txt` | CMPB (PARTIAL) |
| Checkpoint SHA256 | `AUTHORITATIVE_CHECKPOINT_SHA256.tsv` | CMPB `05_REPRODUCIBILITY/` |
| A1 preflight binding | `A1_PREFLIGHT_BINDING.yaml` | Validity `11_A1_PREFLIGHT_BINDING_V1/` |
| Source/config/data/evaluator freezes | `*_IDENTITY_FREEZE.json` | Validity `11_A1_PREFLIGHT_BINDING_V1/` |
| Launcher env contract | `METHOD_LAUNCHER_ENV_CONTRACT.yaml` | Validity `11_A1_PREFLIGHT_BINDING_V1/` |

## Scope of G0

1. Confirm authoritative **BASE** and **Raw (RAW_QRTC)** checkpoints for **PC KEGG wBRG** and **LncTarD wBRG**, plus source / config / splits / entity–relation maps / evaluator.  
2. Document how loaded models bind to formal results; memory-update on formal forward; empty diagnosis does not change outputs; params/buffers frozen — **proof recipes only; no GPU inference this pass**.  
3. Timing/cost **PLAN** from existing evidence; GPU timing deferred.  
4. Budget ceiling ≤ **1/4** of one full training cell; calendar stop ~**1–2 days** (document only; no invented success probabilities).

## Explicit non-claims

- No live formal-stack replay this pass.  
- No new training / optimizer steps.  
- A1 panel seeds 1025/1026 remain **UNRESOLVED_PROVENANCE** for core empirical support (ledger).  
- `QRTC_FEEDBACK_STATE_MODE` is **unread** by SOURCE_RESTORE Python (A1 forensics); feedback-state validity is **not** closed by G0 asset lock alone.

## G0 status

```text
G0_ASSET_IDENTITY = PASS_WITH_DOCUMENTED_GAPS
G0_LIVE_GPU_PROOF = DEFERRED
G0_GPU_TIMING = DEFERRED_PLAN
NEW_TRAINING_RUNS = 0
OPTIMIZER_STEPS = 0
GPU_USED_THIS_PASS = false
SARA_PID_93604_TOUCHED = false
```
