# PC_KEGG Paper 1 — trusted package authority update — 2026-05-08

**Addendum to:** `PC_KEGG_QRTC_HR_FINAL_TRUSTED_RESULT_PACKAGE_20260508.md`  
**Arbitration card:** `WITHOUTBRG_QRTC_AUTHORITY_ARBITRATION_20260508.md`  
**VERDICT:** `HIST_MAY02_QRTC_AUTHORITATIVE_MAY08_QRTC_BAD_RERUN`

---

## 裁定摘要

1. **withoutBRG QRTC-HR 正式论文表**应使用 **historical May-02 epoch-8 checkpoint** 在 **当前 harness** 下的 **protected full valid / full test re-eval** 指标（见 `WITHOUTBRG_HIST_MAY02_QRTC_FULL_*_REEVAL_STATUS_20260508.md` 与仲裁总卡中的对比表）。
2. **May-08 withoutBRG QRTC-HR rerun checkpoint**（`2026-05-08-13-35-27-655973/model_epoch_8.pth`）标记为 **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`**：**不得**再作为表格或结论文本中的 QRTC 数字来源。
3. **原因（证据链）：** 同一 cap64 slice 上 May-08 QRTC checkpoint 行为异常；**historical May-02 QRTC** 与 **Clean** 在该 slice 上表现正常。Protected 全量 valid/test 复评显示 **May-02 文档指标方向与当前 harness 数值一致**（仅浮点/日志舍入级差异），而 May-08 全量 eval 与 May-02 / Clean 严重偏离。

---

## 权威指标指针（withoutBRG QRTC-HR）

| Split | 指标来源 |
|-------|-----------|
| Valid | `logs/hist_may02_qrtc_protected_full_valid_arbitration_20260508.log` |
| Test | `logs/hist_may02_qrtc_protected_full_test_arbitration_20260508.log` |
| Checkpoint | `pc_kegg_qrtc_hronly_withoutbrg_mem_formal_seed1024_epoch8_batch16_neg512/.../2026-05-02-14-41-05-535438/model_epoch_8.pth` |
| Eval config | `withoutbrg_formal_rerun_20260507/config/pc_kegg_hist_may02_qrtc_epoch8_EVAL_PROTECTED_ARBITRATION_20260508.yaml` |

### 锁定用锚点数值（论文表 / 引用只允许此组）

| Split | AP | AUROC | MR | MRR |
|-------|---:|------:|---:|----:|
| **Valid** | **0.952** | **0.948784** | **263.658** | **0.406578** |
| **Test** | **0.952694** | **0.949748** | **261.621** | **0.419978** |

**Final lock:** `PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md` — `VERDICT=WITHOUTBRG_QRTC_AUTHORITY_LOCKED`.

---

## 与旧 PROVISIONAL 行的关系

主包中曾引用 **May-08** `WITHOUTBRG_QRTC_HRONLY_FULL_*_STATUS_20260508.md` 的数字作为 **UNDER_DISPUTE** 行。**那些 May-08 数字作废**；代之以本 addendum 与仲裁卡中的 **May-02 current-harness re-eval**。

---

*Authority update recorded 2026-05-08 — no retraining; eval-only arbitration.*
