# PC_KEGG — withoutBRG QRTC authority lock — 2026-05-08

## VERDICT

`VERDICT=WITHOUTBRG_QRTC_AUTHORITY_LOCKED`

This card **finalizes** documentation-only asset lock. **No** withoutBRG QRTC **training** or **eval** is part of this step; **no** model/code changes.

---

## Authority

| Item | Value |
|------|--------|
| **Authoritative QRTC checkpoint** | **Historical May-02** withoutBRG QRTC epoch-8: `paper1_q2_sci_package_20260428/pc_kegg_qrtc_hronly_withoutbrg_mem_formal_seed1024_epoch8_batch16_neg512/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-02-14-41-05-535438/model_epoch_8.pth` |
| **Authoritative QRTC eval** | **Protected arbitration re-eval 20260508** — config `withoutbrg_formal_rerun_20260507/config/pc_kegg_hist_may02_qrtc_epoch8_EVAL_PROTECTED_ARBITRATION_20260508.yaml`; logs `logs/hist_may02_qrtc_protected_full_valid_arbitration_20260508.log`, `logs/hist_may02_qrtc_protected_full_test_arbitration_20260508.log`; status `WITHOUTBRG_HIST_MAY02_QRTC_FULL_*_REEVAL_STATUS_20260508.md` |
| **May-08 QRTC checkpoint** | **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`** — `qrtc_hronly_train_direct_20260508/.../2026-05-08-13-35-27-655973/model_epoch_8.pth` (cards `WITHOUTBRG_QRTC_HRONLY_FULL_*_STATUS_20260508.md` = **invalid for tables**) |

---

## Canonical withoutBRG QRTC metrics（final paper table）

| Split | AP | AUROC | MR | MRR |
|-------|---:|------:|---:|----:|
| **Valid** | **0.952** | **0.948784** | **263.658** | **0.406578** |
| **Test** | **0.952694** | **0.949748** | **261.621** | **0.419978** |

(Full Hits@K: `PC_KEGG_QRTC_HR_FINAL_TRUSTED_RESULT_PACKAGE_20260508.md` §三.)

---

## May-08 bad metrics — allowed context only

The following **must not** appear as **trusted / final** QRTC results. If cited at all, label **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`** / **audit exhibit**:  
AP **0.889313** (valid), AP **0.891110** (test), MR **973.794** / **959.173**, MRR **0.296707** / **0.304778**.

---

## GPU

**No GPU process running** on device at lock check (`nvidia-smi` **Processes: No running processes found**; 2026-05-08 lock pass). *Infrastructure may change; this lock step did not launch compute.*

---

## Cross-references

- `WITHOUTBRG_QRTC_AUTHORITY_ARBITRATION_20260508.md` — arbitration record (column **(4)** = bad rerun exhibit).
- `PC_KEGG_QRTC_HR_FINAL_TRUSTED_RESULT_PACKAGE_20260508.md` — master freeze (§三 + asset index).
- `PC_KEGG_QRTC_HR_FINAL_TRUSTED_RESULT_PACKAGE_20260508_AUTHORITY_UPDATE.md` — addendum.

---

*Authority lock recorded 2026-05-08 — documentation only.*
