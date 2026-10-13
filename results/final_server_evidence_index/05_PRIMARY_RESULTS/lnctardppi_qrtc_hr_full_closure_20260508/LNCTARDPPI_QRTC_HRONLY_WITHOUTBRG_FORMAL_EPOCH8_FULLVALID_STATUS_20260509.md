# LncTarD-PPI QRTC-HR only withoutBRG — epoch 8 full valid-only eval — Stage 5 status (2026-05-09)

## VERDICT

**Stage 5: PASS** — **`Evaluate on valid`**；**`#valid: 608`**；输出 **AP / AUROC / Hits@1/3/10/20/50/100 / MR / MRR**；**`VALID_ONLY_EVAL_DONE`**；**`EXIT_CODE:0`**；无 Traceback / RuntimeError / CUDA OOM / AssertionError / NaN；**`EVAL_VALID_CAP` / `EVAL_TEST_CAP` 未设置**（`env -u …`）；eval 运行时 **`QRTC_ENABLE=1`、`QRTC_USE_MEMORY=1`、`QRTC_TOPK=2`**（与 Stage 4 训练一致），其余扩展开关为 **0**。

可进入 **Stage 6**。

---

## 命令与产物

| 项 | 值 |
|----|-----|
| 入口 | `python script/eval_valid_only.py -c config/knowledge_graph/biomedical/lnctardppi_qrtc_hronly_withoutbrg_epoch8_fullvalid_20260509.yaml --gpus '[0]' -s 1024` |
| Eval config | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_qrtc_hronly_withoutbrg_epoch8_fullvalid_20260509.yaml` |
| Checkpoint | Stage 4：`…/2026-05-09-16-18-58-695278/model_epoch_8.pth` |
| 日志 | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/qrtc_hronly_withoutbrg_formal_epoch8_fullvalid_20260509.log` |

**Shell 环境（eval 进程）：** `env -u EVAL_VALID_CAP -u EVAL_TEST_CAP`，并显式设置 **`QRTC_ENABLE=1` `QRTC_USE_MEMORY=1` `QRTC_TOPK=2`**，`FAMILY_CTX_*`、`QAES_ENABLE`、`QAM_ENABLE`、`RICS_ENABLE`、`WSA_ENABLE`、`WSL_ENABLE`、`UAEP_ENABLE`、`QRDP_M2_ENABLE` 均为 **0**。

---

## 规模核对

- 日志：`#train: 4867, #valid: 608, #test: 609`
- **`#valid: 608`** — full valid

---

## Valid 指标（日志 L114–L123）

| 指标 | 值 |
|------|-----|
| ap | 0.88397 |
| auroc | 0.878079 |
| hits@1 | 0.101974 |
| hits@3 | 0.189967 |
| hits@10 | 0.375 |
| hits@20 | 0.484375 |
| hits@50 | 0.652961 |
| hits@100 | 0.768914 |
| mr | 86.7821 |
| mrr | 0.188492 |

---

## 合规说明（cap / smoke / bounded / subset）

- **未使用** `EVAL_VALID_CAP` / `EVAL_TEST_CAP`；日志无 **`EVAL_*_CAP=`** 子集提示。
- 日志中 **`dataset.Subset`** 为 PyTorch `Subset` 类型名；**`capturable`** / **`router_type_vocab_cap`** 为框架字段。
- Config **无 `smoke_skip_valid`**（`train.num_epoch: 0`）；日志 **无 `smoke` / `bounded`** 字样。

---

## PASS 清单

- [x] Evaluate on valid  
- [x] valid = **608**  
- [x] AP / AUROC / Hits@1/3/10/20/50/100 / MR / MRR  
- [x] `VALID_ONLY_EVAL_DONE`  
- [x] `EXIT_CODE=0`  
- [x] 无 Traceback / RuntimeError / CUDA OOM / AssertionError / killed / NaN  
- [x] 无不恰当的 cap / subset / smoke / bounded 语义（见上）
