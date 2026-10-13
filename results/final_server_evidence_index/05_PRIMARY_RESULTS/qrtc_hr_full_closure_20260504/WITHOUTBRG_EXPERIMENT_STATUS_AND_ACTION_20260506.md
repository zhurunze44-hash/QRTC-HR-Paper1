# PC_KEGG withoutBRG — status & Q2 closure actions

**Date:** 2026-05-06  
**Constraint:** No new architecture modules; Clean vs **QRTC-HR only**.

---

## Current evidence

### Clean withoutBRG

- **Train:** **FAILED** early (`CLEAN_WITHOUTBRG_FULL_EXPERIMENT_STATUS_20260502.md`) — TorchDrug CUDA extension (**spmm**) build failure in env **`biopathnet_py310_bw`**.
- **Formal full valid/test:** **Absent** (no epoch8 Clean ckpt path comparable to withBRG closure).

### QRTC-HR withoutBRG

- **Train:** **Completed** per `ROUTE_A_FULL_EXPERIMENT_STATUS_20260502.md` — ckpt  
  `paper1_q2_sci_package_20260428/pc_kegg_qrtc_hronly_withoutbrg_mem_formal_seed1024_epoch8_batch16_neg512/.../model_epoch_8.pth`
- **Full valid / test logs:** Present under `qrtc_hronly_withoutbrg_FULL_EXPERIMENT_20260502/` (e.g. `full_valid_*144101.log`, `full_test_*144101.log`).
- **Alternate eval trace:** `ROUTE_A_EPOCH8_EVAL_WITH_ABS_CKPT_PATCHED_LOAD_STATUS_20260502.md` prints **valid + test metrics**; shell RC on chained **eval_and_predict** may reflect **post-metric prediction path** — treat metrics lines as authoritative if no Traceback precedes them.

### Execution-path audit (credibility)

- Logs timestamp **2026-05-02**, conda **`biopathnet_py310_bw`**, while **withBRG fused-compatible formal closure** is documented **2026-05-04+** with **`biopathnet_py310_torch201`** for primary metrics.
- **Not proven** that May‑02 forward matched **current** `model.py` QRTC messaging semantics (`QRTC_FORCE_MESSAGE_PATH`, fused routing parity).

---

## Verdict for Q2 SCI

| Question | Answer |
|----------|--------|
| May withoutBRG numbers enter **main table without caveat**? | **No** |
| Minimum scientific repair | **Parity re-eval** of frozen **QRTC** ckpt using **current** codebase + documented **`QRTC_*` env**, metrics-only path preferred (`eval_test_metrics_only` pattern). |
| Full Q2 closure | **Clean withoutBRG formal train** (after fixing extension/toolchain parity with active env) + **QRTC** either **re-eval only** (if code audit passes) or **formal re-train** if mismatch found. |

---

## Recommended sequence

1. **Config preview** — duplicate `pc_kegg_clean_nbfnet_withoutbrg_formal_*` / `pc_kegg_qrtc_hronly_withoutbrg_mem_formal_*` YAMLs with **absolute** `dataset.path` → `/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602`, `include_factgraph: no`.  
2. **Parity smoke** — one-batch forward + `EVAL_TEST_CAP` sanity in **`biopathnet_py310_torch201`**.  
3. **Clean formal train** — unblock spmm/rspmm first (match site-packages repair used for withBRG).  
4. **Full valid → full test** — strict separation; metrics-only test acceptable if prediction dataset absent.  
5. **Execution-path memo** — attach git hash + `QRTC_*` dump + log excerpts for QRTC rows.

---

## Deliverables when closed

- Status card: `WITHOUTBRG_FORMAL_CLEAN_AND_QRTC_STATUS_<DATE>.md`  
- Logs + ckpts under deterministic `output_dir` names  
- Optional **rank-pair** mirror of withBRG if MR deltas warrant it
