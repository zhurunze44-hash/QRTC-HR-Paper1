# LncTarD-PPI Clean withoutBRG — epoch 8 full valid-only eval — Stage 2 status (2026-05-09)

## VERDICT

**Stage 2: PASS** — `EXIT_CODE=0`；**full valid（608）**；输出 **AP / AUROC / Hits@1/3/10/20/50/100 / MR / MRR**；**`VALID_ONLY_EVAL_DONE`**；无 Traceback / RuntimeError / CUDA OOM / AssertionError / NaN；启动时 **`EVAL_VALID_CAP` / `EVAL_TEST_CAP` 未设置**（`env -u …`），日志中无 **`EVAL_VALID_CAP=`** 子集提示。

可进入 **Stage 3**。

---

## 命令与产物

| 项 | 值 |
|----|-----|
| 入口 | `python script/eval_valid_only.py -c config/knowledge_graph/biomedical/lnctardppi_clean_withoutbrg_epoch8_fullvalid_20260509.yaml --gpus '[0]' -s 1024` |
| Eval config | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_clean_withoutbrg_epoch8_fullvalid_20260509.yaml` |
| Checkpoint | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/clean_withoutbrg_formal_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-09-16-06-40-709140/model_epoch_8.pth` |
| 日志 | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/clean_withoutbrg_formal_epoch8_fullvalid_20260509.log` |

环境（与 Stage 1 对齐，避免额外模块）：`QRTC_ENABLE=0`，`FAMILY_CTX_*`、`QAES_ENABLE`、`QAM_ENABLE`、`RICS_ENABLE`、`WSA_ENABLE`、`WSL_ENABLE`、`UAEP_ENABLE`、`QRDP_M2_ENABLE` 均为 **0**。

---

## 规模核对

- 日志：`#train: 4867, #valid: 608, #test: 609`
- **`#valid: 608`** — full valid

---

## Valid 指标（日志摘录）

| 指标 | 值 |
|------|-----|
| ap | 0.883481 |
| auroc | 0.87732 |
| hits@1 | 0.0871711 |
| hits@3 | 0.189145 |
| hits@10 | 0.364309 |
| hits@20 | 0.48273 |
| hits@50 | 0.652138 |
| hits@100 | 0.787007 |
| mr | 87.4918 |
| mrr | 0.177524 |

完成标记：`VALID_ONLY_EVAL_DONE -> exit before test/prediction phase`；`EXIT_CODE:0`。

---

## 合规说明（cap / smoke / bounded）

- **未使用** `EVAL_VALID_CAP`；未出现 `EVAL_VALID_CAP=… -> …indices` 类日志。
- 日志中出现的 **`capturable`**（Adam）、**`router_type_vocab_cap`**（模型配置字段）为框架/模型固定字段名，**不是** valid 子集截断。

---

## PASS 清单

- [x] Evaluate on valid  
- [x] valid = **608**  
- [x] AP / AUROC / Hits@1/3/10/20/50/100 / MR / MRR  
- [x] `VALID_ONLY_EVAL_DONE`  
- [x] `EXIT_CODE=0`  
- [x] 无 Traceback / RuntimeError / CUDA OOM / AssertionError / killed / NaN  
- [x] 无 `EVAL_VALID_CAP`  
- [x] 正式评估语义上非 cap/smoke/subset 运行（见上）
