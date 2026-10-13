# withoutBRG QRTC-HR-only formal train — 真实性审计（2026-05-08）

**范围**：只读；未启动实验、未 kill 进程、未改代码。  
**工作目录**：`<REDACTED_SERVER_PATH>

---

##  Config 路径说明（用户给定 vs 实际）

- 用户提示路径：`config/q2_sci_pc_kegg_20260428/qrtc_hronly_withoutbrg_direct_train_20260508.yaml` → 在仓库 **`config/` 下未找到该文件**（`Glob` 结果为 0）。
- **日志 `CFG=` / `Config file:` 给出的权威路径**（与磁盘一致）：

`<REDACTED_SERVER_PATH>

以下 **「复查 config 是否 formal」** 均基于上述 YAML + 日志展开块。

---

## 一、复查 config 是否 formal

| 检查项 | 值 | formal 说明 |
|--------|-----|-------------|
| **output_dir** | `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/withoutbrg_formal_rerun_20260507/qrtc_hronly_train_direct_20260508` | 无 `smoke` / `cap32` / `cap64` / `lowmem` / `tiny` 字样 |
| **dataset path** | `/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602` | 完整 PC_KEGG 数据路径（日志加载 `train2.txt` **22702** 行） |
| **include_factgraph** | `no`（YAML）；日志中为 `False` | **withoutBRG** 一致 |
| **batch_size** | **16**（`engine.batch_size`） | 属正式尺度，非极小 smoke batch |
| **num_negative** | **512** | 正式设定 |
| **num_epoch** | **8** | **满足 formal 判据** |
| **smoke_skip_valid** | `yes` | **训练阶段跳过 valid**；与「formal train」不冲突（用户允许） |
| **checkpoint** | YAML **未显式**配置 `checkpoint` 字段 | 使用框架默认写入 **run working directory**；日志可见 `Save checkpoint to model_epoch_*.pth` |
| **batch_per_epoch** | **不存在**（YAML 无；日志无） | **无截断 epoch 的小 batch_per_epoch** |
| **test_batch_size / valid** | engine 仅 **batch_size: 16**；task `full_batch_eval: no` | 与日志中 engine dump 一致 |
| **smoke / debug / cap / tiny / lowmem**（文件名与 output_dir） | 文件名含 `direct_train`、日期后缀；路径 **不含** `smoke`、`tiny`、`lowmem`；**不含** `cap32`/`cap64` 实验标签 | 通过命名筛查 |

**日志头部模块开关（应为 QRTC-on，其余 off）**

| 变量 | 值 |
|------|-----|
| QRTC_ENABLE | **1** |
| QRTC_USE_MEMORY | **1** |
| QRTC_TOPK | **2** |
| WSA_ENABLE / WSL_ENABLE | **0** |
| QAES_ENABLE / QAM_ENABLE | **0** |
| RICS_ENABLE / UAEP_ENABLE | **0** |
| QRDP_M2_ENABLE | **0** |
| QCES_ENABLE | **0** |
| FAMILY_CTX_* | **0** |

**注意**：日志/engine 展开模型字段中有 `router_type_vocab_cap: 64`，此为 **NBFNet router 超参名**，**不是**实验目录名里的 `cap32/cap64`，不构成「短训路径」证据。

---

## 二、复查 log 是否完整训练 8 epoch

### 统计摘要

| 指标 | 结果 |
|------|------|
| **Epoch begin 次数** | **8**（`Epoch 0` … `Epoch 7 begin`） |
| **Epoch end 次数** | **8**（`Epoch 0` … `Epoch 7 end`） |
| **每 epoch average BCE** | **8 次均有**（每个 `Epoch k end` 后均有 `average binary cross entropy`） |
| **checkpoint** | **`model_epoch_1.pth` … `model_epoch_8.pth`** 均在日志中保存记录 |
| **train end** | **有**：`=== QRTC-HR-only train end … ===` |
| **EXIT_CODE** | **`EXIT_CODE=0`** |
| **Traceback / RuntimeError / OOM** | **未发现**（仅有 PyTorch JIT / torchdrug **Warning**） |
| **batch_per_epoch 或极少 batch 证据** | **无**；每 epoch **duration ~2.06–3.00 min**，**speed ~7.87–11.50 batch/s**，与全数据训练一致 |

### 全数据 batch 合理性（反证 short/smoke）

- 日志：`#train: 22702`，`batch_size: 16` → 每 epoch 约 **⌈22702/16⌉ = 1419** 个 batch。  
- 例如 `Epoch 7`：`duration: 2.07 mins`，`speed: 11.45 batch / sec` → 约 **11.45 × 124 ≈ 1420** batch，与全 epoch 一致。  
- **非**「8 个名义 epoch 但每 epoch 仅几十个 batch」的短训模式。

### 时长与显存

| 项目 | 值 |
|------|-----|
| **单 epoch 用时** | Epoch0 **3.00 min**；Epoch1–7 各约 **2.06–2.11 min** |
| **总训练时长（wall）** | 约 **13:35:28**（首个 `Epoch 0 begin`）→ **13:53:03**（`Epoch 7 end`）≈ **17.6 min**（含首 epoch JIT） |
| **peak GPU memory（日志每 epoch）** | **2766.8 MiB**（各 epoch 一致） |

### Epoch 表（训练循环为 0-based；checkpoint 为 1-based 命名）

| epoch (0-based) | begin_seen | end_seen | average BCE | checkpoint_saved |
|-----------------|------------|----------|-------------|------------------|
| 0 | yes | yes | 0.587737 | model_epoch_1.pth |
| 1 | yes | yes | 0.554919 | model_epoch_2.pth |
| 2 | yes | yes | 0.598101 | model_epoch_3.pth |
| 3 | yes | yes | 0.604967 | model_epoch_4.pth |
| 4 | yes | yes | 0.604814 | model_epoch_5.pth |
| 5 | yes | yes | 0.603972 | model_epoch_6.pth |
| 6 | yes | yes | 0.602704 | model_epoch_7.pth |
| 7 | yes | yes | 0.603865 | model_epoch_8.pth |

---

## 三、Checkpoint 定位

**Run directory（日志 Working directory）**

`paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/withoutbrg_formal_rerun_20260507/qrtc_hronly_train_direct_20260508/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-08-13-35-27-655973`

**绝对路径（最终 checkpoint）**

`<REDACTED_SERVER_PATH>

| 属性 | 值 |
|------|-----|
| **file size** | **3274679** bytes |
| **mtime** | **2026-05-08 13:53:03 +0800**（与日志 `Save checkpoint to model_epoch_8.pth` 一致） |
| **model_epoch_1 … model_epoch_8** | **均存在**，同目录，大小均为 **3274679** bytes |

---

## 四、正式判定 — VERDICT

### **FORMAL_TRAIN_CONFIRMED**

**理由摘要**：`num_epoch=8`；**无 `batch_per_epoch`**；日志 **8× begin / 8× end**；每 epoch **全数据量级**的 duration 与 batch/s；**`model_epoch_1`–`model_epoch_8` 齐全**；**`EXIT_CODE=0`**；无异常栈；config/output 命名无 smoke/cap32/cap64/lowmem；QRTC 开关正确、其它模块关闭。

---

## 五、下一步建议（仅列出，未启动）

1. withoutBRG **QRTC-HR full valid**  
2. withoutBRG **QRTC-HR full test**  
3. withoutBRG **Clean vs QRTC full-test rank-pair diagnosis**  
4. **RotatE baseline**

---

## 六、审计结论一览（便于粘贴）

| 项 | 值 |
|----|-----|
| **VERDICT** | **FORMAL_TRAIN_CONFIRMED** |
| **config path（实际）** | `…/withoutbrg_formal_rerun_20260507/config/qrtc_hronly_withoutbrg_direct_train_20260508.yaml` |
| **log path** | `…/withoutbrg_formal_rerun_20260507/logs/qrtc_hronly_withoutbrg_direct_train_20260508.log` |
| **output_dir** | `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/withoutbrg_formal_rerun_20260507/qrtc_hronly_train_direct_20260508` |
| **checkpoint path（最终）** | `…/2026-05-08-13-35-27-655973/model_epoch_8.pth` |
| **num_epoch** | **8** |
| **batch_per_epoch** | **不存在** |
| **epoch begin/end** | **各 8 次** |
| **model_epoch_8** | **存在** |
| **EXIT_CODE** | **0** |
| **是否可保留为正式 withoutBRG QRTC-HR train 资产** | **是** |
| **status card path** | `<REDACTED_SERVER_PATH> |
