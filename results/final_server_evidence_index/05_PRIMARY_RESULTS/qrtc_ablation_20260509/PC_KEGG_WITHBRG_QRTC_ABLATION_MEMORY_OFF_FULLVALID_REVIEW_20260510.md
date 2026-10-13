# PC_KEGG withBRG — QRTC memory_off — Full Valid Eval — Read-only Review

**Audit date:** 2026-05-10 (local `date` on review host)  
**Scope:** Post-hoc verification of `memory_off` epoch-8 full valid eval (no rerun, no model edits, no closure overwrite).

---

## 1. VERDICT

**FULLVALID_PASS_READY_FOR_FULLTEST**

---

## 2. Running eval-related processes

**No.** A targeted check for `eval_valid_only`, `BioPathNet_fresh` `run.py`, or `KnowledgeGraphCompletion` reported **NO_EVAL_SPECIFIC_PROCESS**.

Note: A broad `ps | grep python` may list unrelated services (e.g. TensorBoard, Jupyter); those are **not** this full-valid eval job.

---

## 3. GPU occupancy by this eval

**No.** `nvidia-smi` showed **0 MiB** GPU memory in use and **no** compute processes attached to the GPU at audit time. **GPU is idle** for this workload.

---

## 4. Log: `Evaluate on valid`

**Yes.** Present (e.g. log line with timestamp `21:03:06`).

---

## 5. Log: `VALID_ONLY_EVAL_DONE`

**Yes.** Present after metrics block.

---

## 6. Log: `EXIT_CODE:0`

**Yes.** `EXIT_CODE:0` appears (twice at end of log; benign duplication).

---

## 7. Full valid metrics (from log)

| Metric | Value |
|--------|--------|
| **AP** | 0.986614 |
| **AUROC** | 0.985405 |
| **Hits@1** | 0.433685 |
| **Hits@3** | 0.572978 |
| **Hits@10** | 0.71692 |
| **Hits@20** | 0.784785 |
| **Hits@50** | 0.862566 |
| **Hits@100** | 0.909049 |
| **MR** | 125.346 |
| **MRR** | 0.526857 |

---

## 8. Errors / anomalies

**None observed** in log grep for: `Traceback`, `RuntimeError`, `CUDA out of memory`, `AssertionError`, `killed`, `NaN`.

Non-fatal: `torch.meshgrid` user warning; Torch CUDA extension warnings (`TORCH_CUDA_ARCH_LIST`). No impact on verdict.

---

## 9. Config verification

**File:** `config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fullvalid_20260509.yaml`

| Check | Result |
|-------|--------|
| `checkpoint` → `model_epoch_8.pth` under memory_off seed1024 epoch8 run | **OK** (absolute path matches stated train artifact) |
| `dataset.path` → `PC_KEGG_0602` | **OK** (`/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602`) |
| `include_factgraph: yes` | **OK** |
| No `EVAL_VALID_CAP` / `EVAL_TEST_CAP` | **OK** (not present; comment explicitly forbids for formal metrics) |
| No formal-eval subset caps (`cap32` / `cap64` / `bounded` / `subset` as eval mode) | **OK** (not present in this YAML) |

**Note:** `train.smoke_skip_valid: yes` is a **training** smoke knob, not an eval cap; log shows full valid evaluation on the real valid set with complete metric tuple. Runtime resolved `include_factgraph: True` on train/valid/test subsets in engine dump.

---

## 10. Status card

**Written/updated:** `PC_KEGG_WITHBRG_QRTC_ABLATION_MEMORY_OFF_EPOCH8_FULLVALID_STATUS_20260509.md` with **`verdict: FULLVALID_PASS`** (file was missing before this audit; created on pass).

---

## 11–13. Rerun / PASS policy

- **PASS:** No automatic full test or topk runs performed per instructions.
- **Next step (suggestion only):** Proceed to **memory_off full test** when you explicitly request it in a follow-up message.

---

## References (read-only)

- **Log:** `paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fullvalid_20260509.log`
- **Config:** `config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fullvalid_20260509.yaml`
- **Checkpoint:** `.../pc_kegg_withbrg_qrtc_memory_off_seed1024_epoch8/.../model_epoch_8.pth`
