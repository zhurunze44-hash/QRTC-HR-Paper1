# RUNTIME_EVIDENCE_AUDIT

Source: `QRTC_HR_WORK_20260908/01_runtime_forensic/` (copied summaries + scripts; chrome traces left in place).

## Microbench (real_pc_kegg, warmup 20, repeats 100, CUDA timed)

| mode | median_ms (10_REAL_RUNTIME.tsv) |
|------|----------------------------------|
| A BioPathNet | 137.970 |
| B QRTC wrappers off / baseline | 138.119 |
| C QRTC-off | 138.357 |
| D QRTC-on | 203.467 |

Locked ratios in FINAL_STATUS.json: Base~138.12 ms, QRTC-off~138.36 ms, QRTC-on~203.47 ms, **R_QRTC≈1.47x**.

Device: CUDA (see 09_REAL_WORKLOAD_FREEZE.json). Batch 2, 32 candidates, valid split probe — **not** full test ranking wall-clock.

## Formal train/eval wall times

CMPB `PAPER1_RUNTIME_MEMORY_COST_TABLE_20260510.md`: Clean/QRTC withBRG formal train/eval bundle **MISSING** as single-number freeze. Memory-off train ~14682 s logged.

**RUNTIME_STATUS=INSUFFICIENT_FOR_MANUSCRIPT** if the manuscript needs end-to-end train or full-test seconds. Microbench is real but narrow.

No new training was run to fill wall-clock gaps.
