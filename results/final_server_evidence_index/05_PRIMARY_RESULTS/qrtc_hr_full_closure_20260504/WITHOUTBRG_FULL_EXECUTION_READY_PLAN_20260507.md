# PC_KEGG withoutBRG — full symmetric closure (execution-ready plan)

**Date:** 2026-05-07  
**Constraint:** No architecture modules beyond **Clean NBFNet** vs **QRTC-HR fused-compatible**; do **not** start below jobs until **full rank-pair GPU pipeline has finished** and GPU is idle.

---

## 1. Data path (confirmed on server)

| Item | Path |
|------|------|
| **Canonical dataset root** | `/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602` |
| **Splits** | `train1.txt`, `train2.txt`, `valid.txt`, `test.txt` |
| **withoutBRG flag** | YAML `include_factgraph: no` |

Existing closure YAMLs still cite `<REDACTED_SERVER_PATH> — **must rewrite or overlay** to the canonical `/root/autodl-tmp/...` path before any formal run (same fix pattern as withBRG).

---

## 2. Config preview (protocol parity target)

Match **withBRG formal** where applicable:

| Field | Clean withoutBRG | QRTC-HR withoutBRG |
|------|------------------|---------------------|
| **Template YAML** | `config/q2_sci_pc_kegg_20260428/pc_kegg_clean_nbfnet_withoutbrg_formal_seed1024_epoch8_batch16_neg512_20260502.yaml` | `config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_hronly_withoutbrg_mem_formal_seed1024_epoch8_batch16_neg512_20260430.yaml` |
| **Seed** | 1024 | 1024 |
| **batch_size** | 16 | 16 |
| **num_negative** | 512 | 512 |
| **num_epoch** | 8 | 8 |
| **smoke_skip_valid** | yes | yes |
| **heterogeneous_negative / heterogeneous_evaluation** | yes | yes |
| **sample_weight** | no | no |
| **full_batch_eval** | no | no |
| **NBFNet towers** | 32×6 hidden, distmult+pna, etc. | same |

**QRTC runtime env (train + eval)** — log verbatim into `$RUN/env_audit.txt`:

```bash
export QRTC_ENABLE=1
export QRTC_USE_MEMORY=1
export QRTC_TOPK=2
export QRTC_FORCE_MESSAGE_PATH=0
unset QRTC_CAND_READOUT_ENABLE
```

**Clean** runs:

```bash
export QRTC_ENABLE=0
```

---

## 3. Execution-path audit — may old withoutBRG QRTC be reused?

| Check | Evidence | Pass for Q2 formal? |
|-------|-----------|---------------------|
| **Repaired fused-compatible codebase** | Logs reference **`biopathnet_py310_bw`**, not current primary **`biopathnet_py310_torch201`** stack used for withBRG closure | **No** |
| **`QRTC_FORCE_MESSAGE_PATH=0`** | **Not logged** in captured stdout | **Unknown / fail audit** |
| **`QRTC_ENABLE=1` ≠ Clean** | Train intended QRTC-HR; env not captured in logs | **Unknown / fail audit** |
| **Checkpoint / config / log triple** | Train + eval logs exist under `qrtc_hronly_withoutbrg_FULL_EXPERIMENT_20260502/` | **Partial** |
| **Full valid / test (no cap)** | Valid/test metric lines present for Route A; **`eval_and_predict` test_pred phase** fails with missing `test_pred.txt` (same class as withBRG Clean) — **metrics-before-traceback OK** | **Metrics credible as historical** but **not code-path frozen** |

**Verdict:** Treat May‑2026 withoutBRG QRTC numbers as **engineering reference only**. For **Q2 paper package**, **re-run formal train + full valid + metrics-only full test** under **`biopathnet_py310_torch201`** with **`env_audit.txt`** and optional **`eval_test_metrics_only`** shim for test (no prediction phase).

**Clean withoutBRG:** prior train **failed** (spmm build in `bw` env) → **must run** on repaired toolchain matching withBRG site-packages fix.

---

## 4. batch16 / neg512 feasibility

- **withBRG formal** peaks ~**13.7 GiB** GPU (train telemetry).  
- **withoutBRG** removes fact-graph supervision edges → **same or lower** memory pressure at equal batch/neg.  
- **Risk:** first-touch CUDA extension compile jitter — not OOM class on **~98 GiB** GPU.

If rare OOM: ladder **batch 16 → 8** with **`gradient_interval: 2`** only as **documented fallback** (still no architecture change).

---

## 5. Train cost (order of magnitude)

Per track (8 epochs, batch16 neg512, PC_KEGG):

| Phase | Wall-clock band |
|-------|-----------------|
| **Formal train** | ~**4–6 h** (same class as withBRG QRTC train window) |
| **Full valid** | ~**1–1.5 h** |
| **Full test** (metrics-heavy) | ~**6–8 h** |

**Symmetric Clean + QRTC** sequential ≈ **2× (train+valid+test)** → **~2 GPU-days** conservative including compile & logs.

---

## 6. Queue order — **Clean first**

Reason: **no** surviving Clean withoutBRG ckpt; QRTC ablation needs **matched backbone protocol** and **Clean baseline row**. After Clean `model_epoch_8.pth` exists, launch **QRTC-HR** formal train with **identical** YAML skeleton + QRTC env.

---

## 7. Runnable script plan (**do not execute until rank-pair idle**)

Suggested repo-local staging:

```text
paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/withoutbrg_formal_rerun_20260507/
  env_audit_clean_train.txt
  env_audit_qrtc_train.txt
  logs/clean_train.log
  logs/clean_full_valid.log
  logs/clean_full_test.log
  logs/qrtc_train.log
  logs/qrtc_full_valid.log
  logs/qrtc_full_test.log
```

**Step 0 — gate**

```bash
nvidia-smi  # no python rank dump
pgrep -af dump_fulltest_filtered_ranks || true  # must be empty
```

**Step 1 — publish patched YAML copies** (human step): duplicate both formal YAMLs into `withoutbrg_formal_rerun_20260507/config/` with `dataset.path: /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602` and fresh `output_dir` under the staging folder.

**Step 2 — Clean formal train**

```bash
source /root/miniconda3/etc/profile.d/conda.sh && conda activate biopathnet_py310_torch201
cd /root/autodl-tmp/BioPathNet_fresh
export QRTC_ENABLE=0
python script/run.py -c <CLOSURE>/withoutbrg_formal_rerun_20260507/config/clean_withoutbrg_formal.yaml --gpus '[0]' -s 1024 2>&1 | tee <CLOSURE>/withoutbrg_formal_rerun_20260507/logs/clean_train.log
```

**Step 3 — Clean full valid** (`eval_valid_only.py` + abs ckpt YAML pattern — mirror `CLEAN_WITHBRG_EPOCH8_FULL_VALID` cards).

**Step 4 — Clean full test** (`eval_test_metrics_only_20260506.py` pattern preferred).

**Step 5 — QRTC formal train** (same config class + `env_audit` dumped before launch).

**Step 6 — QRTC full valid / full test** — symmetric to Clean.

---

## 8. First command to run **after rank-pair completes**

```bash
nvidia-smi && pgrep -af dump_fulltest_filtered_ranks || true
```

If idle → **Step 1** (write patched YAMLs) + **Step 2** Clean train command above.

---

## 9. Formal model code touched?

**No.** This plan uses existing `script/run.py`, `eval_valid_only.py`, and packaged eval shims only.
