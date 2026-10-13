# LncTarD-PPI Clean withoutBRG — epoch 8 full test-only eval — Stage 3 status (2026-05-09)

## VERDICT

**Stage 3: PASS** — **`Evaluate on test`**；**`#test: 609`**；输出 **AP / AUROC / Hits@1/3/10/20/50/100 / MR / MRR**；**`EXIT_CODE:0`**；无 Traceback / RuntimeError / CUDA OOM / AssertionError / NaN；**未设置** `EVAL_VALID_CAP` / `EVAL_TEST_CAP`（`env -u …`）；本次**未运行训练**；**未修改** full valid 状态卡文件。

可进入 **Stage 4**。

---

## 命令与产物

| 项 | 值 |
|----|-----|
| 入口 | `python script/eval_valid_only.py -c config/knowledge_graph/biomedical/lnctardppi_clean_withoutbrg_epoch8_fulltest_20260509.yaml --gpus '[0]' -s 1024` |
| Test split | **`EVAL_ONLY_SPLIT=test`** |
| Config | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_clean_withoutbrg_epoch8_fulltest_20260509.yaml` |
| Checkpoint | `…/2026-05-09-16-06-40-709140/model_epoch_8.pth`（与 Stage 1/2 同源） |
| 日志 | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/clean_withoutbrg_formal_epoch8_fulltest_20260509.log` |

环境与 Stage 2 一致：`QRTC_ENABLE=0` 及所列扩展开关均为 **0**。

---

## 规模核对

- 日志：`#train: 4867, #valid: 608, **#test: 609**`
- **`Evaluate on test`**（L108）

---

## Test 指标（日志 L114–L123）

| 指标 | 值 |
|------|-----|
| ap | 0.891054 |
| auroc | 0.885696 |
| hits@1 | 0.0935961 |
| hits@3 | 0.200328 |
| hits@10 | 0.390805 |
| hits@20 | 0.505747 |
| hits@50 | 0.668309 |
| hits@100 | 0.781609 |
| mr | 87.2718 |
| mrr | 0.183579 |

脚本在完成评估后仍打印 `VALID_ONLY_EVAL_DONE`（`eval_valid_only.py` 固定文案）；随后 **`EXIT_CODE:0`**。

---

## 合规说明（cap / smoke / bounded / subset）

- **未使用** eval 子集 cap：`EVAL_VALID_CAP`、`EVAL_TEST_CAP` 已从环境中移除。
- 日志中 **`dataset.Subset`** 为 PyTorch `torch.utils.data.Subset` 类型名（划分 train/valid/test），**不是**人为 subset 评估模式。
- **`capturable`** / **`router_type_vocab_cap`** 与 Stage 2 相同，为优化器与模型字段名。
- 本 Stage **config 不含 `smoke_skip_valid`**（使用 `train.num_epoch: 0` 占位）；日志 **无 `smoke`** 字样。

---

## PASS 清单

- [x] Evaluate on **test**
- [x] **test = 609**
- [x] AP / AUROC / Hits@1/3/10/20/50/100 / MR / MRR  
- [x] **EXIT_CODE=0**
- [x] 无 Traceback / RuntimeError / CUDA OOM / AssertionError / killed / NaN  
- [x] 无不恰当的 cap / bounded / eval-subset 语义（见上）

---

## 备注

首次在本会话中触发的一次 shell 运行被中断且日志为空；随后**单次成功跑完**并得到上述日志与退出码 **0**。Stage 3 以成功这次为准。
