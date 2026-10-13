# PC_KEGG withBRG — QRTC Ablation — memory_off — Epoch 8 — Full Valid Status

**Run:** full valid only (no train, no test in same invocation)  
**Config:** `config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fullvalid_20260509.yaml`  
**Log:** `paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fullvalid_20260509.log`  
**Checkpoint:** `paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-09-16-53-28-980276/model_epoch_8.pth`

---

## verdict

**FULLVALID_PASS**

Formal full valid evaluation completed with full metric block and `EXIT_CODE:0`. Status card finalized on **2026-05-10** (read-only audit).

---

## Metrics (full valid)

| Metric | Value |
|--------|--------|
| AP | 0.986614 |
| AUROC | 0.985405 |
| Hits@1 | 0.433685 |
| Hits@3 | 0.572978 |
| Hits@10 | 0.71692 |
| Hits@20 | 0.784785 |
| Hits@50 | 0.862566 |
| Hits@100 | 0.909049 |
| MR | 125.346 |
| MRR | 0.526857 |

---

## Exit / completion

- **VALID_ONLY_EVAL_DONE:** yes (log)  
- **EXIT_CODE:** 0  

---

## Next (paper workflow; not auto-started)

- **Allowed next step:** memory_off **full test** when explicitly requested.  
- **Not started here:** full test, topk1, topk3.
