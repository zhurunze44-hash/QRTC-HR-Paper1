# LncTarD-PPI withoutBRG Clean vs QRTC-HR — full-test rank-pair diagnosis — Stage 7 status (2026-05-09)

## VERDICT

**Stage 7: PASS** — 全部约定产物已生成；**609** test triples（TSV **610** 行含表头）；**`EXIT_CODE=0`**（流水线 `PIPE_EXIT=0`）；主日志无 Traceback / RuntimeError / CUDA OOM / AssertionError / NaN；未使用 **EVAL_*_CAP**；未串联 train/eval（仅 rank dump + merge）。

可进入 **Stage 8**。

---

## 路径

| 项 | 路径 |
|----|------|
| 输出目录 | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/lnctardppi_withoutbrg_fulltest_rankpair_diag_20260509` |
| 主日志 | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/lnctardppi_withoutbrg_fulltest_rankpair_diag_20260509.log` |

**脚本：** `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/scripts/dump_fulltest_filtered_ranks_20260506.py`

**关键环境：** `PC_KEGG_DATA_ROOT=/root/autodl-tmp/BioPathNet_fresh/data/lnctardppi`（覆盖脚本内对 YAML `dataset.path` 的重写）；`RANKPAIR_CFG_CLEAN` → `lnctardppi_clean_withoutbrg_epoch8_fulltest_20260509.yaml`；`RANKPAIR_CFG_QRTC` → `lnctardppi_qrtc_hronly_withoutbrg_epoch8_fulltest_20260509.yaml`；`RANKPAIR_DIAG_MD_NAME=LNCTARDPPI_WITHOUTBRG_FULLTEST_RANKPAIR_DIAGNOSIS_20260509.md`；`EVAL_SKIP_OPTIMIZER_LOAD=1`；clean 步骤 `QRTC_ENABLE=0`，qrtc 步骤 `QRTC_ENABLE=1 QRTC_USE_MEMORY=1 QRTC_TOPK=2`。

---

## 产物核对（PASS 清单）

| 文件 | 状态 |
|------|------|
| `clean_fulltest_filtered_rankpairs.tsv` | ✓ **609** 数据行 |
| `qrtc_fulltest_filtered_rankpairs.tsv` | ✓ **609** 数据行 |
| `matched_rank_delta.tsv` | ✓ |
| `relation_mean_delta.tsv` | ✓ |
| `rankpair_summary.json` | ✓ |
| `LNCTARDPPI_WITHOUTBRG_FULLTEST_RANKPAIR_DIAGNOSIS_20260509.md` | ✓（含追加的聚合 MR/MRR/head–tail 解读） |

辅助：`dump_clean_meta.json`、`dump_qrtc_meta.json`，控制台日志 `dump_*_console.log`。

---

## 摘要数字（`rankpair_summary.json`）

- **Pair-level（Δ = QRTC − Clean rank）：** improved **526**，worsened **456**，unchanged **236**（共 **1218** rank-pairs）。
- **Triple-level net（Δtail+Δhead）：** net improved **306**，net worsened **276**，net unchanged **27**。
- **Mean Δ：** tail **−1.680**，head **−0.455**（平均而言 QRTC 秩更优）。
- **MR/MRR 重组（meta）：** MR **87.272 → 86.204**（↓）；MRR **0.1836 → 0.1845**（↑）；**head MRR** 略降、**tail MRR** 上升 — 详见 diagnosis md **aggregate** 表与 **head/tail long-tail** 小节。

---

## 合规

- **无 cap：** 未设置 `EVAL_VALID_CAP` / `EVAL_TEST_CAP`。
- **无 train：** 仅加载 checkpoint 做 rank dump。
- **未覆盖** Stage 2 full-valid / 其他状态卡（本任务仅新增本文件与诊断目录）。

---

## 退出码

- 流水线 shell **退出码 0**；merge 完成并打印 `Wrote … rankpair_summary.json and … diagnosis md`。
