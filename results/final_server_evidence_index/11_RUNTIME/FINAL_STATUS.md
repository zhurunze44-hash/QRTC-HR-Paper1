# FINAL_STATUS — QRTC Runtime Forensic Seal

```
FINAL_STATUS = PASS__QRTC_RUNTIME_ROOT_CAUSE__ALGORITHM_DOMINANT
```

**Sealed without GPU / training / HuRI / SOURCE or PAIR_KG edits / optimization patches.**

## Primary result (real PC-KEGG microbatch)

| Quantity | Value |
|----------|-------|
| BioPathNet median | 138.12 ms |
| QRTC-off median | 138.36 ms |
| QRTC-on median | 203.47 ms |
| R_WRAPPER (C/B) | ≈ 1.002 |
| R_QRTC (D/C) | ≈ 1.471 |
| R_TOTAL (D/B) | ≈ 1.473 |
| MESSAGE_CALL_RATIO | both_zero_fused_path |
| PROPAGATION_CALL_RATIO | 1.0 |
| MAA_RATIO | 1.0 |

Synthetic secondary: R_WRAPPER≈1.00, R_QRTC≈1.21 (smaller graph).

## Locked adjudication

```
QRTC_FORWARD_RUNTIME_FORENSIC = PASS__ALGORITHM_DOMINANT
ROOT_CAUSE_FORWARD            = ALGORITHM_DOMINANT_WITH_OPTIMIZABLE_ON_PATH_OVERHEAD
QRTC_WRAPPER_OVERHEAD         = NEGLIGIBLE
QRTC_WRAPPER_BACKBONE_OVERHEAD = ABSENT
DUPLICATE_PROPAGATION         = FALSE
QRTC_FORWARD_INCREMENTAL_COST = MATERIAL
QRTC_ON_ENGINEERING_DEBT      = PRESENT
QRTC_READOUT_ONLY_CONTRACT    = CONTRADICTED_BY_RECOVERED_IMPLEMENTATION
                                (pending full submitted-manuscript text audit)
QRTC_RUNTIME_OPTIMIZATION_V1  = AUTHORIZED__OPT1_PASS__OPT2_PASS
HEADROOM_V1                   = NOT_AUTHORIZED
NEW_PAIR_KG_MODEL             = FORBIDDEN
```

## What this does / does not explain

- **Explains:** ~47% QRTC-on forward incremental cost on real PC-KEGG microbatch; not wrapper re-run; not duplicate bellmanford.
- **Does not explain:** historical multi-× epoch wall-clock (30–40 min vs ~10 min). That still needs forward / forward+backward / validation decomposition before Phase-1 QRTC seed0.

## Contract (implementation)

- Shared propagation backbone = **YES**
- QRTC only final readout = **NO** (relation gate inside message passing)
- B≡C scores = **YES**; D differs intentionally

## Next (priority order)

1. ~~Paper-1 claim–implementation audit~~ → **Case A** (`21_`, writing-core expanded in `23_`)
2. ~~OPT-1~~ → **PASS** (reaudit TOPK=2)
3. ~~OPT-2~~ → **PASS** (\(R\approx 1.470\to 1.207\)); OPT-3/OPT-4 next; epoch fwd/bwd/val decomposition still open
4. NBFNet / BioPathNet seed0 may continue in parallel

## Claim audit (follow-up)

```
CASE = A
SUBMITTED_TEX_PDF = ABSENT_ON_HOST
INDEPENDENT_REAUDIT = 23_INDEPENDENT_LINE_REAUDIT_20260908.md
```

Working description locked (internal): relation-conditioned multi-stage reasoning intervention (gate in message passing).  
**Deprecated:** “readout-only intervention.”

## OPT-1 (reaudit)

```
PASS__OPT1_SEMANTICS_PRESERVING
formal_TOPK = 2
R_QRTC_old ≈ 1.466
R_QRTC_new ≈ 1.470
R_QRTC_before_locked = 1.471
```

Details: `02_runtime_opt_v1/OPT1/` · full line reaudit: `01_runtime_forensic/23_INDEPENDENT_LINE_REAUDIT_20260908.md`

## OPT-2

```
PASS__OPT2_SEMANTICS_PRESERVING
PRE_OPT2_BASELINE sealed; formal_TOPK = 2
R_QRTC_pre ≈ 1.470
R_QRTC_post ≈ 1.207
usage microbench ≈ 3.78×
```

Details: `02_runtime_opt_v1/OPT2/OPT2_SEAL.md`
