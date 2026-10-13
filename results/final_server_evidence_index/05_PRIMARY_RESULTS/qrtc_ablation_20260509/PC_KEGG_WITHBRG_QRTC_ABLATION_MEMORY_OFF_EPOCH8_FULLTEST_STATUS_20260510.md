# PC_KEGG withBRG — QRTC Ablation — memory_off — Epoch 8 — Full Test Status

**Stage 3 (full test–only eval):** completed **2026-05-10**  
**Depends on:** full valid PASS (`PC_KEGG_WITHBRG_QRTC_ABLATION_MEMORY_OFF_EPOCH8_FULLVALID_STATUS_20260509.md`, verdict **FULLVALID_PASS**).

---

## 1. VERDICT

**FULLTEST_PASS**

---

## 2. Config path

`/root/autodl-tmp/BioPathNet_fresh/config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest_20260510.yaml`

---

## 3. Checkpoint path

`/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-09-16-53-28-980276/model_epoch_8.pth`

---

## 4. Log path

`/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_20260510.log`

---

## 5. Environment variable snapshot (launcher)

Formal invocation:

```bash
env -u EVAL_VALID_CAP -u EVAL_TEST_CAP \
EVAL_ONLY_SPLIT=test \
QRTC_ENABLE=1 \
QRTC_USE_MEMORY=0 \
QRTC_TOPK=2 \
FAMILY_CTX_ENABLE=0 \
FAMILY_CTX_WSA_ENABLE=0 \
FAMILY_CTX_RISK_GATE_ENABLE=0 \
FAMILY_CTX_CAND_RISK_ENABLE=0 \
QAES_ENABLE=0 \
QAM_ENABLE=0 \
RICS_ENABLE=0 \
WSA_ENABLE=0 \
WSL_ENABLE=0 \
UAEP_ENABLE=0 \
QRDP_M2_ENABLE=0 \
/root/miniconda3/envs/biopathnet_py310_torch201/bin/python script/eval_valid_only.py \
  -c /root/autodl-tmp/BioPathNet_fresh/config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest_20260510.yaml \
  --gpus '[0]' -s 1024
```

Append to log: `echo "EXIT_CODE:$?" >> …log` (outer shell; duplicates numeric exit banner).

---

## 6. split=test evidence

| Evidence | Detail |
|----------|--------|
| **Launcher** | **`EVAL_ONLY_SPLIT=test`** (unset caps via `env -u EVAL_VALID_CAP -u EVAL_TEST_CAP`) |
| **Harness** | `script/eval_valid_only.py` → `test()`: `split = os.environ.get("EVAL_ONLY_SPLIT", "valid")`; then `solver.model.split = split`; `solver.evaluate(split)` |
| **Log** | **`Evaluate on test`** immediately after checkpoint load |
| **Vs valid** | Engine dump **`#valid: 3227`, `#test: 6438`** — evaluated split matches **full test** size (**6438**), not valid (**3227**) |

**Note:** The script always prints `VALID_ONLY_EVAL_DONE -> exit before prediction phase` on exit; wording is legacy. Split selection is controlled by **`EVAL_ONLY_SPLIT`** + **`Evaluate on …`** line in the log.

---

## 7. Test quantity

**6438** (`#test: 6438` in log; PC_KEGG_0602 `test.txt` loaded with full split indices).

---

## 8. Metrics (full test)

| Metric | Value |
|--------|--------|
| **AP** | 0.986863 |
| **AUROC** | 0.985671 |
| **Hits@1** | 0.44882 |
| **Hits@3** | 0.583722 |
| **Hits@10** | 0.725691 |
| **Hits@20** | 0.792171 |
| **Hits@50** | 0.865719 |
| **Hits@100** | 0.90758 |
| **MR** | 122.678 |
| **MRR** | 0.540014 |

---

## 9. Cap / subset / smoke (formal eval)

| Check | Result |
|-------|--------|
| **`EVAL_VALID_CAP` / `EVAL_TEST_CAP`** | **Unset** in launcher (`env -u …`) |
| **Log lines `EVAL_*_CAP=… -> runtime_subset`** | **Absent** |
| **YAML `cap32` / `cap64` / `bounded` / `subset` eval knobs** | **Absent** |
| **`train.smoke_skip_valid: yes`** | Present for **config parity** with train YAMLs only; this eval **did not** run training — no smoke skip of valid/test during eval |

---

## 10. Error scan (log)

Searched for: `Traceback`, `RuntimeError`, `CUDA out of memory`, `AssertionError`, `killed`, `NaN`, `EVAL_VALID_CAP`, `EVAL_TEST_CAP`, `runtime_subset`.

**No matches.**

Benign: `torch.meshgrid` user warning; Torch `TORCH_CUDA_ARCH_LIST` JIT warnings.

---

## 11. Exit code

- **`EXIT_CODE:0`** appended at end of log (Python `sys.exit(0)` + shell echo).
- Outer driver **`exit_code: 0`** (job wrapper).

---

## 12. Next step

**FULLTEST_PASS → authorized:** write **memory_off ablation closure summary** (when requested).  

**Not run here:** topk1/topk3, rank-pair, train, valid re-eval, closure asset overwrite.
