# withoutBRG QRTC runtime probe — 2026-05-08

**Purpose:** Minimal **read-only** check that **QRTC toggles** and **predict outputs** differ from Clean — **does not** prove full hop-level correctness.

**VERDICT=`PROBE_RUNTIME_SCORES_DIVERGE_DEBUG_LAYERS_EMPTY_ON_PREDICT`**

## Artifacts

| Item | Path |
|------|------|
| Log | `withoutbrg_qrtc_runtime_probe_20260508.log` |
| Script | `/root/autodl-tmp/BioPathNet_fresh/script/withoutbrg_qrtc_runtime_probe_20260508.py` |

## Environment (printed)

| Variant | QRTC_ENABLE | QRTC_USE_MEMORY | QRTC_TOPK |
|---------|---------------|-----------------|-----------|
| clean | 0 | (unset) | (unset) |
| qrtc | 1 | 1 | 2 |

## NBFNet flags (`nbf.*`)

| | clean | qrtc |
|---|-------|------|
| `qrtc_enable` | **False** | **True** |
| `qrtc_use_memory` | True (module defaults) | True |
| `qrtc_topk` | 4 (unused when disabled) | **2** |

## QRTC parameter tensors

- **Count** of `*`qrtc`*` named params: **13** (both variants — modules exist even when disabled).
- **No NaN/inf** in QRTC params (both).
- **Aggregate L2 norm** differs (Clean-disabled load vs QRTC-enabled load): **~9.28** vs **~14.44** — consistent with **different checkpoints** and **QRTC weights being exercised** in the QRTC run.

## `predict()` output (first valid mini-batch, batch_size=8)

| Variant | shape | mean abs | std |
|---------|-------|---------:|----:|
| clean | (8, 2, 8321) | 2.543 | 1.194 |
| qrtc | (8, 2, 8321) | 2.334 | 2.124 |

- **All finite:** yes.
- **Conclusion:** **Raw score tensors differ** between Clean and QRTC loads — **not** bit-identical forward.

## `QRTC_DEBUG` / `_last_qrtc_debug_layers`

- **`len(_last_qrtc_debug_layers)==0`** for **both** variants under this probe (`task.predict` short path).
- **Interpretation:** Layer-wise debug collection may **not** attach to the **`predict()`** API path used here — **do not** equate empty debug with “QRTC hop machinery off” **without** a separate forward hook on `bellmanford` / message path.

## Bottom line

- **Not `CURRENT_QRTC_RUNTIME_BROKEN` by score identity:** outputs **differ**.
- **Debug visibility:** **inconclusive** from this probe alone.
