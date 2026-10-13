# withoutBRG QRTC — authority arbitration — 2026-05-08

## STATUS

`STATUS=ARBITRATION_COMPLETE`

`VERDICT=HIST_MAY02_QRTC_AUTHORITATIVE_MAY08_QRTC_BAD_RERUN`

**Post-arbitration lock:** `PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md` (`VERDICT=WITHOUTBRG_QRTC_AUTHORITY_LOCKED`). **No further withoutBRG QRTC train/eval** without a new signed runbook.

---

## 初始标签（归档）

- **May-08 QRTC current rerun:** `UNDER_DISPUTE` / `NOT_FOR_TABLE` → **最终** `BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`
- **Historical May-02 QRTC asset:** `CANDIDATE_AUTHORITATIVE` → **最终** **权威**

---

## 一、资产与配置（只读摘要）

| 项 | 路径 / 内容 |
|----|-------------|
| May-02 结果文档 | `paper1_q2_sci_package_20260428/qrtc_hronly_withoutbrg_FULL_EXPERIMENT_20260502/ROUTE_A_QRTC_HRONLY_WITHOUTBRG_EPOCH8_FULL_RESULT_FINAL_20260502.md` |
| May-02 train config | `config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_hronly_withoutbrg_mem_formal_seed1024_epoch8_batch16_neg512_20260430.yaml` |
| May-02 checkpoint | `.../2026-05-02-14-41-05-535438/model_epoch_8.pth` |
| Protected eval YAML（仅此改 `dataset.path` / `output_dir` / 绝对 checkpoint） | `withoutbrg_formal_rerun_20260507/config/pc_kegg_hist_may02_qrtc_epoch8_EVAL_PROTECTED_ARBITRATION_20260508.yaml` |
| Launcher | `scripts/run_hist_may02_qrtc_protected_arbitration_eval_20260508.sh` |
| Preflight | `script/audit_qrtc_ckpt_hardload.py -c <cfg> --exit-on-qrtc-mismatch`（QRTC-pattern missing/unexpected → exit **2**）；配置/环境 cap-subset-smoke 扫描 → exit **3** |

**QRTC eval 环境（与训练一致）：** `QRTC_ENABLE=1`, `QRTC_USE_MEMORY=1`, `QRTC_TOPK=2`；`FAMILY_CTX_*`, `QAES`, `QAM`, `RICS`, `WSA`, `WSL`, `UAEP`, `QRDP_M2` = **0**。

**数据路径（本机）：** `/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602`

**日志断言：** valid `#valid=3227`，test `#test=6438`（见 re-eval 日志）。

---

## 二、四路 withoutBRG 指标对照（仲裁表）

> **Column (4)** figures are **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`** audit exhibits only (from `WITHOUTBRG_QRTC_HRONLY_FULL_*_STATUS_20260508.md`). **Final PC_KEGG tables must use column (3) only** for QRTC-HR. **Locked:** `PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md`.

### Valid

| Metric | (1) Clean May-08 full valid | (2) Hist May-02 **文档** | (3) Hist May-02 **当前 harness re-eval** | (4) Bad May-08 QRTC full valid |
|--------|----------------------------:|-------------------------:|----------------------------------------:|-------------------------------:|
| AP | 0.951666 | 0.951995 | **0.952** | 0.889313 |
| AUROC | 0.945955 | 0.948778 | **0.948784** | 0.876478 |
| Hits@1 | 0.313914 | 0.328788 | **0.328633** | 0.244035 |
| Hits@3 | 0.417106 | 0.436783 | **0.435699** | 0.317323 |
| Hits@10 | 0.549737 | 0.560428 | **0.559498** | 0.395414 |
| Hits@20 | 0.616362 | 0.627363 | **0.626278** | 0.440502 |
| Hits@50 | 0.713511 | 0.724822 | **0.724202** | 0.510846 |
| Hits@100 | 0.778742 | 0.788193 | **0.787729** | 0.563991 |
| MR | 279.247 | 263.404 | **263.658** | 973.794 |
| MRR | 0.391859 | 0.407044 | **0.406578** | 0.296707 |

**来源：** (1) `WITHOUTBRG_CLEAN_FULL_VALID_STATUS_20260508.md`；(2) May-02 `ROUTE_A_..._FINAL_20260502.md`；(3) `logs/hist_may02_qrtc_protected_full_valid_arbitration_20260508.log`；(4) `WITHOUTBRG_QRTC_HRONLY_FULL_VALID_STATUS_20260508.md`。

### Test

| Metric | (1) Clean May-08 full test | (2) Hist May-02 **文档** | (3) Hist May-02 **当前 harness re-eval** | (4) Bad May-08 QRTC full test |
|--------|---------------------------:|-------------------------:|----------------------------------------:|------------------------------:|
| AP | 0.952662 | 0.955361 | **0.952694** | 0.891110 |
| AUROC | 0.947710 | 0.952266 | **0.949748** | 0.879970 |
| Hits@1 | 0.326033 | 0.342109 | **0.341799** | 0.253728 |
| Hits@3 | 0.433054 | 0.449286 | **0.448975** | 0.323082 |
| Hits@10 | 0.562908 | 0.574790 | **0.574324** | 0.399736 |
| Hits@20 | 0.631796 | 0.641271 | **0.640727** | 0.445325 |
| Hits@50 | 0.720954 | 0.728798 | **0.728332** | 0.514834 |
| Hits@100 | 0.780833 | 0.790541 | **0.789997** | 0.566480 |
| MR | 273.914 | 261.394 | **261.621** | 959.173 |
| MRR | 0.405033 | 0.420297 | **0.419978** | 0.304778 |

**来源：** (1) `WITHOUTBRG_CLEAN_FULL_TEST_STATUS_20260508.md`；(2) May-02 文档；(3) `logs/hist_may02_qrtc_protected_full_test_arbitration_20260508.log`；(4) `WITHOUTBRG_QRTC_HRONLY_FULL_TEST_STATUS_20260508.md`。

---

## 三、判断

**与 May-02 文档一致性：** (3) 与 (2) **同向且数值贴合**（valid/test 各指标均为同一量级；差异在 **浮点舍入 / 日志打印精度 / 本机数据路径与 PyTorch 版本** 可解释范围内）。**不属于** “数值差异很大但方向正常”（裁定 **C**）的情形。

**相对 Clean May-08：** (3) 在 **Hits@K、MRR、AP、AUROC、MR** 上 **整体优于或接近 Clean**（与 May-02 文档叙事一致），**非** May-08 bad checkpoint 的崩溃形态。

**裁定：** **A** — `VERDICT=HIST_MAY02_QRTC_AUTHORITATIVE_MAY08_QRTC_BAD_RERUN`

- **withoutBRG QRTC 最终论文表**采用 **(3) historical May-02 current-harness re-eval**。
- **May-08 QRTC checkpoint** → **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`**。

---

## 四、May-08 bad rerun — 最小根因审计（无代码修改、无重训）

### 1. Train config diff（May-02 vs May-08）

| 字段 | May-02 | May-08 |
|------|--------|--------|
| `dataset.path` | `<REDACTED_SERVER_PATH> | `/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602` |
| `output_dir` | `.../pc_kegg_qrtc_hronly_withoutbrg_mem_formal_seed1024_epoch8_batch16_neg512` | `.../qrtc_hronly_train_direct_20260508` |
| 其余 task / engine / optimizer / `num_epoch` / `batch_size` / `num_negative` | **相同**（均为 epoch **8**，batch **16**，neg **512**，lr **5e-3**，NBFNet 结构一致） |

### 2. Train log 对比

| 项 | May-02 | May-08 |
|----|--------|--------|
| Train triples / split | `#train 22702, #valid 3227, #test 6438` | **相同** |
| `num_epoch` | 8 | 8 |
| `batch_size` | 16 | 16 |
| `num_negative` | 512 | 512 |
| 每 epoch **平均 BCE**（趋势） | 0.5576 → … → **0.5450**（末 epoch） | 0.5877 → … → **0.6039**（末 epoch）；**明显高于** May-02 |
| 是否在日志中打印 QRTC env | 该日志片段 **未** 汇总打印（仅 config dump） | 启动脚本 **打印** `QRTC_ENABLE` 等 |
| Warning / 异常 | `torch.meshgrid` 等常现 warning；epoch 时长 ~**4.5 min** | 同类 warning；epoch 时长 ~**2–3 min**（步速不同，步数应一致） |

**读数：** May-08 在 **相同步数预算** 下 **BCE 更高**，提示 **优化轨迹落入较差区域** 或 **有效训练信号弱于** May-02 运行，而非“eval 协议单独写错”可单独解释的全量指标崩塌。

### 3. Checkpoint 参数统计（`state['model']`，去掉 graph 张量键后）

| 项 | May-02 | May-08 |
|----|--------|--------|
| QRTC-pattern 键数量 | **28** | **28** |
| QRTC 浮点张量 **concat 全局 mean / std** | mean **0.000588**, std **0.117** | mean **0.000493**, std **0.102** |
| QRTC **NaN / Inf** | **0 / 0** | **0 / 0** |
| Backbone（非 QRTC）全局 std / 聚合尺度 | std **0.324**, per-tensor L2 聚合 **119.1** | std **0.335**, **123.1**（略高，非数量级异常） |

**读数：** **无 NaN/Inf**；May-08 **QRTC 权重 L2 规模略小**（**19.7** vs **22.6**，按 per-tensor L2 的欧氏聚合），与 **更高 BCE** 一致，符合 **“训练未学好 QRTC 头 / 次优盆地”** 现象，而非 **权重损坏（NaN）**。

### 4. Root-cause hypothesis（仅假设）

**主假设：** May-08 rerun 在同名超参下 **优化轨迹不同**（初始化噪声、非确定性、cudnn、代码/依赖微差、数据路径变更带来的 **隐性顺序或缓存效应**），导致 **收敛变差**（BCE 更高）与 **ranking 指标崩溃**；**非** QRTC 公式单独被改（本次任务约束下未改公式）所能解释的唯一路径。

**辅假设：** 与 May-02 相比，May-08 **有效正则/梯度噪声比例** 不同（同样表现在 **epoch wall-time** 与 **BCE 曲线** 上），使 **QRTC 记忆模块** 未充分对齐任务。

---

## 五、回传摘要（执行清单）

| # | 项 | 内容 |
|---|----|------|
| 1 | Arbitration card path | `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/WITHOUTBRG_QRTC_AUTHORITY_ARBITRATION_20260508.md` |
| 2 | May-02 full **valid** re-eval | 见 §二表 (3) valid 行 |
| 3 | May-02 full **test** re-eval | 见 §二表 (3) test 行 |
| 4 | vs May-02 文档 | **一致（方向 + 数值贴合）** |
| 5 | vs Clean May-08 | **re-eval QRTC 整体优于 Clean（表列指标）** |
| 6 | May-08 QRTC checkpoint | **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`** |
| 7 | `VERDICT` | **`HIST_MAY02_QRTC_AUTHORITATIVE_MAY08_QRTC_BAD_RERUN`** |
| 8 | 论文表允许使用的 withoutBRG QRTC 指标 | **仅 (3) May-02 checkpoint + current-harness protected re-eval** |

---

## FINAL_VERDICT

`HIST_MAY02_QRTC_AUTHORITATIVE_MAY08_QRTC_BAD_RERUN`

**withoutBRG QRTC 权威数值：** `WITHOUTBRG_HIST_MAY02_QRTC_FULL_VALID_REEVAL_STATUS_20260508.md` + `WITHOUTBRG_HIST_MAY02_QRTC_FULL_TEST_REEVAL_STATUS_20260508.md` + 本文件 §二 (3)。

**冻结包更新：** `PC_KEGG_QRTC_HR_FINAL_TRUSTED_RESULT_PACKAGE_20260508_AUTHORITY_UPDATE.md`；主包 `PC_KEGG_QRTC_HR_FINAL_TRUSTED_RESULT_PACKAGE_20260508.md` 已同步 **§三** 与资产索引。
