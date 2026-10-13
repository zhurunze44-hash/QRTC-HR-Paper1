# LncTarD-PPI QRTC-HR only withoutBRG — epoch 8 full test-only eval — Stage 6 status (2026-05-09)

## VERDICT

**Stage 6: PASS** — **`Evaluate on test`**；**`#test: 609`**；输出 **AP / AUROC / Hits@1/3/10/20/50/100 / MR / MRR**；**`EXIT_CODE:0`**；无 Traceback / RuntimeError / CUDA OOM / AssertionError / NaN；**未设置** `EVAL_VALID_CAP` / `EVAL_TEST_CAP`；eval 使用 **`QRTC_ENABLE=1`、`QRTC_USE_MEMORY=1`、`QRTC_TOPK=2`**（与 Stage 4/5 一致）。

可进入 **Stage 7**。

---

## 命令与产物

| 项 | 值 |
|----|-----|
| 入口 | `python script/eval_valid_only.py -c config/knowledge_graph/biomedical/lnctardppi_qrtc_hronly_withoutbrg_epoch8_fulltest_20260509.yaml --gpus '[0]' -s 1024` |
| Split | **`EVAL_ONLY_SPLIT=test`** |
| Config | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_qrtc_hronly_withoutbrg_epoch8_fulltest_20260509.yaml` |
| Checkpoint | Stage 4：`…/2026-05-09-16-18-58-695278/model_epoch_8.pth` |
| 日志 | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/qrtc_hronly_withoutbrg_formal_epoch8_fulltest_20260509.log` |

**Shell 环境：** `env -u EVAL_VALID_CAP -u EVAL_TEST_CAP`，**`QRTC_ENABLE=1` `QRTC_USE_MEMORY=1` `QRTC_TOPK=2`**，`FAMILY_CTX_*`、`QAES_ENABLE`、`QAM_ENABLE`、`RICS_ENABLE`、`WSA_ENABLE`、`WSL_ENABLE`、`UAEP_ENABLE`、`QRDP_M2_ENABLE` 均为 **0**。

---

## 规模核对

- 日志：`#train: 4867, #valid: 608, **#test: 609**`
- **`Evaluate on test`**（L108）

---

## Test 指标（日志 L114–L123）

| 指标 | 值 |
|------|-----|
| ap | 0.894121 |
| auroc | 0.887355 |
| hits@1 | 0.089491 |
| hits@3 | 0.197865 |
| hits@10 | 0.384236 |
| hits@20 | 0.509031 |
| hits@50 | 0.66092 |
| hits@100 | 0.784072 |
| mr | 86.2061 |
| mrr | 0.184451 |

脚本在完成评估后打印 `VALID_ONLY_EVAL_DONE`（`eval_valid_only.py` 固定文案）；随后 **`EXIT_CODE:0`**。

---

## 合规说明（cap / smoke / bounded / subset）

- **未使用** eval 子集 cap：`EVAL_VALID_CAP`、`EVAL_TEST_CAP` 已从环境中移除。
- 日志中的 **`dataset.Subset`** 为 PyTorch `Subset` 类型名。
- **`capturable`** / **`router_type_vocab_cap`**（若出现在引擎 dump 中）为框架/模型字段名。
- Config **无 `smoke_skip_valid`**；日志 **无 `smoke` / `bounded`** 字样。

---

## PASS 清单

- [x] Evaluate on **test**
- [x] **test = 609**
- [x] AP / AUROC / Hits@1/3/10/20/50/100 / MR / MRR  
- [x] **EXIT_CODE=0**
- [x] 无 Traceback / RuntimeError / CUDA OOM / AssertionError / killed / NaN  
- [x] 无不恰当的 cap / subset / smoke / bounded 语义（见上）
