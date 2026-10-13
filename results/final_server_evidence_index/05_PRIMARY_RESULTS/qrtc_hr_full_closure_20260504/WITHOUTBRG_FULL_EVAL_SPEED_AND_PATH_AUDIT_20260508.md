# withoutBRG full-eval speed & path audit — 2026-05-08

**Audit mode:** read-only. Goal: find mistakes, not justify success.

**Repo / root used for paths:** `/root/autodl-tmp/BioPathNet_fresh` (same tree also referenced as `<REDACTED_SERVER_PATH> in logs and scripts).

---

## 〇、VERDICT (single choice)

**D. PARTIAL_TRUST_ONLY**

**Rationale (concise):**

- **NBFNet withoutBRG Clean + QRTC-HR** full valid / full test: log evidence supports **full PC_KEGG_0602 splits**, intended checkpoints, and **QRTC eval env** on the QRTC runs. QRTC–Clean gap is **internally consistent** with rank-pair diagnosis (`n_triples=6438`, head-side MR collapse).
- **RotatE withoutBRG “full valid”** is **not** a full valid eval: logs show **`EVAL_VALID_CAP=2`** → only **2** valid triples evaluated. RotatE **full test** log shows **Evaluate on test** with **no `EVAL_TEST_CAP`** and aggregate metrics consistent with a **6438-triple** run.
- **Git diff for `eval_valid_only.py`:** workspace has **no git repository** here → **GIT_DIFF: NOT_AVAILABLE** (cannot verify delta vs baseline via `git diff`).

This verdict **does not** claim the low QRTC-HR scores are “bugs”; they may be **real under this protocol**. It **does** claim at least one parallel track (RotatE valid) is **mislabeled** in status cards.

---

## 一、墙钟时间（log mtime + 首尾时间戳 + EXIT_CODE）

**方法：** `stat` mtime；log 内 `=== … start/end ===` 与指标行时间；`EXIT_CODE:0` / `EXIT=0`。

| Stage | Start (log) | End (log) | Wall clock | Log path | Config path | Command / script | PID / nohup |
|-------|-------------|-----------|------------|----------|-------------|------------------|-------------|
| 1 Clean full valid | `2026-05-08T13:21:17+08:00` | `2026-05-08T13:25:50+08:00` | **~4 min 33 s** | `withoutbrg_formal_rerun_20260507/logs/clean_withoutbrg_full_valid_direct_20260508.log` | `withoutbrg_formal_rerun_20260507/config/clean_withoutbrg_eval_abs_ckpt_20260508_020728.yaml` | `scripts/run_withoutbrg_clean_direct_eval_20260508.sh valid` → `python script/eval_valid_only.py …` | No PID in header; stack traces show pid **11953** (CUDA warn). **EXIT_CODE:0** |
| 2 Clean full test | `2026-05-08T13:26:45` & **again** `13:26:56` | `2026-05-08T13:34:57+08:00` | **~8 min** from last start to end | `…/clean_withoutbrg_full_test_direct_20260508.log` | same yaml | `…_clean_direct_eval_20260508.sh test` | warn pid **12994**; **EXIT_CODE:0** |
| 3 QRTC full valid | `2026-05-08T13:55:16+08:00` | `2026-05-08T14:00:19+08:00` | **~5 min 3 s** | `…/qrtc_hronly_withoutbrg_full_valid_direct_20260508.log` | `…/qrtc_hronly_withoutbrg_eval_abs_ckpt_20260508.yaml` | `scripts/run_withoutbrg_qrtc_hronly_direct_eval_20260508.sh valid` | pid **18336**; **EXIT_CODE:0** |
| 4 QRTC full test | `2026-05-08T14:00:33+08:00` | `2026-05-08T14:09:42+08:00` | **~9 min 9 s** | `…/qrtc_hronly_withoutbrg_full_test_direct_20260508.log` | same yaml | `…_qrtc_hronly_direct_eval_20260508.sh test` | pid **19268**; **EXIT_CODE:0** |
| 5 Rank-pair full test | `2026-05-08T14:15:13+08:00` | `2026-05-08T14:31:36+08:00` | **~16 min 23 s** | `withoutbrg_fulltest_rankpair_diag_20260508/full_pipeline_20260508.log` | via `RANKPAIR_CFG_*` (see §七) | `scripts/run_withoutbrg_fulltest_rankpair_20260508.sh` | **no PID** in header; end marker present |
| 6 RotatE train | `14:32:16` | `14:33:01` (`EXIT=0`) | **~45 s wall** (epoch0 ~40 s; ep1–29 sub-second each) | `rotate_withoutbrg_formal_seed1024_epoch30_20260508/logs/train_20260508.log` | `…/pc_kegg_rotate_withoutbrg_formal_seed1024_epoch30_20260508.yaml` | (train launcher not searched in this audit) | train log |
| 7 RotatE eval valid | `14:33:53+08:00` | `14:34:36` | **~43 s** | `rotate_withoutbrg_eval_workdir_20260508/full_valid_20260508.log` | `…/pc_kegg_rotate_withoutbrg_eval_epoch30_20260508.yaml` | (eval launcher not found under closure `**/rotate*eval*.sh`) | pid **24245**; **EXIT_CODE:0** |
| 8 RotatE eval test | `14:34:48+08:00` | `14:35:37` | **~49 s** | `…/full_test_20260508.log` | same | — | pid **24512**; **EXIT_CODE:0** |

**Log file mtime (`stat`) vs end line:** all sampled logs’ mtime matches final log timestamp within 1 s (files are **real writes**, not stale placeholders).

**是否独立完成：** 无证据表明直接复制旧日志文本；时间序列连贯、含 JIT 编译警告与单次指标块。异常点：**Clean test** 同一 log 内 **两次** `=== split=test start ===`（13:26:45 与 13:26:56），仅 **一轮** `Evaluate on test` → 疑似 **短时间内两次启动脚本追加同一文件**，但最终 **`EXIT_CODE:0` 且仅一条指标块**。

---

## 二、Eval 是否 full split（Clean / QRTC valid & test）

### 2.1 日志中的样本规模

| Run | Split | Evidence in log | # evaluated (subset size) | Full split? |
|-----|-------|-----------------|---------------------------|-------------|
| Clean valid | valid | `#train: 22702, #valid: 3227, #test: 6438`；`valid_set` `indices': range(22702, 25929)`（3227） | **3227** | **Yes** |
| Clean test | test | 同上 + `test_set` `range(25929, 32367)`（6438） | **6438** | **Yes** |
| QRTC valid | valid | 同上 | **3227** | **Yes** |
| QRTC test | test | 同上 | **6438** | **Yes** |

与 **PC_KEGG_0602 withoutBRG** 期望 **valid=3227, test=6438** 一致（`#triplet: 32367 = 22702+3227+6438`）。

未发现 log 中的 **EVAL_VALID_CAP / EVAL_TEST_CAP** 对该四轮 NBFNet eval 生效（无 `runtime_subset` cap 行）。

### 2.2 危险字段扫描（config / 打印的 engine dict）

| Field | NBFNet eval logs | Effect on these runs |
|-------|------------------|----------------------|
| `router_type_vocab_cap: 64` | 出现在 model 字段 | **模型结构参数**，非 eval subset cap |
| `capturable: False` | Optimizer | 无关 split |
| `num_epoch: 8` | 仅在 cfg dump | **eval 仍走 `eval_valid_only.py`**，训练 epoch 不缩短本次 ranking |
| `smoke_skip_valid: yes` | 在 cfg | 训练用；**eval 脚本硬编码在 metrics 后 `sys.exit(0)`**，不会跑 train |
| `batch_per_epoch` | **未出现** | — |

**仍存在的运行时风险（见 §六）：** `solver_load` 使用 **`strict=False`**（代码固定），日志 **未** 打印 missing/unexpected keys。

### 2.3 Clean valid：FAULTHANDLER 与栈追踪

- Log **开头**仍打印 **`EVAL_FAULTHANDLER_TIMEOUT=25`**（Launcher 虽 `unset`，可能 conda/用户环境再次注入）。
- 在 **首次** valid eval中出现 **`Timeout (0:00:25)!`** + 长栈（JIT **rspmm** 编译阻塞主线程）。随后在 **`13:25:49`** 正常打印 **完整指标** 与 **`EXIT_CODE:0`**。
- **解释：** 25 s **dump 栈但不中断进程**；后续 eval **继续跑完**。**不**构成自动 “subset eval” 证据，但属于 **日志噪声 / 环境仍有 FAULT timeout** 的红旗。

---

## 三、QRTC eval 是否真实启用 QRTC

**要求：** eval 实际命令 + log 证明（不仅 train env）。

| Variable | QRTC valid log | QRTC test log |
|----------|----------------|---------------|
| `QRTC_ENABLE` | **1** | **1** |
| `QRTC_USE_MEMORY` | **1** | **1** |
| `QRTC_TOPK` | **2** | **2** |
| `FAMILY_CTX_*` / `QAES` / `QAM` / `RICS` / `WSA` / `WSL` / `UAEP` / `QRDP_M2_ENABLE` | **0** | **0** |

来源：`scripts/run_withoutbrg_qrtc_hronly_direct_eval_20260508.sh` **显式 export**，且 log 中 `env | grep` 块一致。

**结论：** **CONFIRMED** — QRTC eval 路径启用 QRTC，且无关模块关闭。

---

## 四、Checkpoint 一致性

| Track | Required / actual path | Config `checkpoint:` | Log `Load checkpoint from` | File stat |
|-------|------------------------|----------------------|------------------------------|-----------|
| Clean eval | Clean formal epoch 8 | `clean_withoutbrg_eval_abs_ckpt_20260508_020728.yaml` → `…/clean_train_out/…/model_epoch_8.pth` | 与 yaml 一致 | **3224523 bytes**, mtime **2026-05-08 02:24:07 +0800** |
| QRTC eval | User-specified epoch 8 | `qrtc_hronly_withoutbrg_eval_abs_ckpt_20260508.yaml` → `…/qrtc_hronly_train_direct_20260508/…/2026-05-08-13-35-27-655973/model_epoch_8.pth` | 与 yaml 一致 | **3274679 bytes**, mtime **2026-05-08 13:53:03 +0800** |

**加载失败 / 随机初始化？** 日志 **无** “failed to load” / “size mismatch” / User-visible missing keys。**但是：** `solver_load` 使用 **`load_state_dict(..., strict=False)`**（`script/eval_valid_only.py`），**静默丢键在理论上是可能的**；本轮日志 **未** 提供 `strict=True` 或 missing-key 列表。

---

## 五、Clean vs QRTC config / dataset 对比（摘要）

| Item | Clean eval yaml | QRTC eval yaml |
|------|-----------------|----------------|
| `dataset.path` | `/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602` | 相同 |
| `include_factgraph` | **no** | **no** |
| `task.class` | `KnowledgeGraphCompletionBiomed` | 相同 |
| `task.model.class` | `NBFNet` | 相同 |
| `num_negative` | **512** | **512** |
| `engine.batch_size` | **16** | **16** |
| `filtered_ranking`（engine task dump） | **True** | **True** |
| `checkpoint` | Clean `model_epoch_8.pth` | QRTC `model_epoch_8.pth`（不同文件大小） |

**结论：** 未发现 **withBRG** 路径混用；split 由 **`EVAL_ONLY_SPLIT`** 选择；两者 **同一数据根**。

---

## 六、`eval_valid_only.py` 审计（无 git → 基于当前源码）

**Git diff：** **`NOT_AVAILABLE`**（`/root/autodl-tmp/BioPathNet_fresh` **不是** git 仓库）。

**当前文件行为摘要：**

1. **`_clear_stale_torch_jit_lock_files`** — 删 JIT lock；**不改变 ranking 数学**。
2. **`_warm_torchdrug_rspmm_extension`** — 提前 import；**仅影响 JIT 时机**。
3. **`EVAL_ONLY_SPLIT`** — `test()` 内设置 `solver.model.split` 并 `solver.evaluate(split)`；**仅切 valid/test**。
4. **`EXIT_CODE:0` print + `sys.exit(0)`** — **日志与提前退出**；后面的 prediction 阶段 **不可达**。
5. **`solver_load`：`strict=False`** — **会影响 checkpoint 完整性判定**；若存在未加载层，**分数可能不代表完整训练权重**（本轮无反证日志）。
6. **`EVAL_VALID_CAP` / `EVAL_TEST_CAP`** — **会缩小 runtime subset**（见 RotatE）。

---

## 七、Rank-pair diagnosis（full test）

| Check | Result |
|-------|--------|
| Clean / QRTC TSV 行数 | **`6439`** 行 each（**= 1 header + 6438 data**） |
| `matched_rank_delta.tsv` | **6439** 行 |
| `rankpair_summary.json` **`n_triples`** | **6438** |
| **`n_rank_pairs`** | **12876** (= 6438×2 tail+head) |
| Pipeline log | `variant=clean … n_triples=6438`、`variant=qrtc … n_triples=6438`；recomputed metrics **与 direct full-test eval 一致** |
| YAML injection | `full_pipeline` 使用 **`/root/autodl-tmp/.../data`**；`RANKPAIR_CFG_CLEAN` / `RANKPAIR_CFG_QRTC` 在 **`run_withoutbrg_fulltest_rankpair_20260508.sh`** 中设置为 **withoutBRG eval yaml**；dump 段 **`unset EVAL_*_CAP`** |
| 脚本 `REPO="<REDACTED_SERVER_PATH>"` vs 运行路径 | Log 证明数据与 ckpt 解析到 **`/root/autodl-tmp/...`**（通常为同盘挂载）；**若两处代码版本分叉则为风险** — 本轮 **not proven divergent** |

**结论：** Rank-pair **full-test、双侧 rank、6438 triples** — **CONFIRMED**（与 summary JSON 一致）。

---

## 八、RotatE withoutBRG（速度与可信度）

### Train

- **`num_epoch: 30`**，`smoke_skip_valid: yes` — **正式 30 epoch**，非 `num_epoch: 1` smoke。
- **无 `batch_per_epoch`**。
- **Train triples:** **22702**（log）。
- **Epoch 0 duration ~40 s**（含 JIT）；**Epoch 1–29 ~0.13 s/epoch** — 因 **batch_size=4096** → 每 epoch **ceil(22702/4096)=6** batches，**wall 短但逻辑上可能是完整 epoch 扫描**。

### Eval

| Log | Danger | Effect |
|-----|--------|--------|
| `full_valid_20260508.log` | **`EVAL_VALID_CAP=2`** → `#valid: 2`，`runtime_subset.indices = range(22702, 22704)` | **Valid 指标仅基于 2 条 triple — 不是 full valid。** |
| `full_test_20260508.log` | 同上 cap 行 printed，`Evaluate on **test**` | **`EVAL_VALID_CAP` 只缩小 valid_set；`test_set` 仍为 `range(25929,32367)`，`#test:6438`** → **test 指标面向 full test。** |

**RotatE 可信度小结：**

- **Train + full test eval：** 可作为 **弱 KGE baseline**（极低 MRR 也可能真实）。
- **Full valid 状态卡：** **不可信** — 与 **full valid** 声称矛盾。

---

## 九、回答「速度异常快」

- **NBFNet：** valid **~4–5 min**，test **~8–9 min**，与 **filtered ranking × 数千三元组 × JIT 首次编译** 相容；**非秒级完成**。
- **RotatE train：** **30 epoch ~45 s** — 由 **每 epoch 极少 batch（≈6）** + **epoch 1+ 无重复 JIT** 解释；**非 necessarily 错误**，但与「重型 DL」直觉不同。
- **Rank-pair：** **~16 min** pipeline — 非异常短。

---

## 十、是否写入 PC_KEGG 总结表（论文级）

按用户规则：**在 VERDICT ≠ `SPEED_FAST_BUT_FULL_EVAL_CONFIRMED` 时，不得将本次 withoutBRG QRTC-HR 指标当作正式论文结论。**

本次 **VERDICT = D**，因此：

- **NBFNet QRTC-HR withoutBRG 指标：** 本轮审计 **未发现 wrong-split / wrong-env / cap** 的硬证据；但 **`strict=False` 加载** 与 **无 git diff** 构成 **残余不确定性**。
- **正式论文结论文本：** **不建议** 把 QRTC-HR 数字当作 **最终定论**，直至至少：**(1)** RotatE 等并行行修正标注或重跑；**(2)** 可选：`strict` 加载审计或显式 missing-key 日志。

**RotatE valid 数字：** **禁止** 作为 full valid baseline进表，直至 **去掉 `EVAL_VALID_CAP`** 并重跑。

---

## 十一、回传摘要（用户 §十格式）

1. **VERDICT:** **D. PARTIAL_TRUST_ONLY**
2. **总墙钟：** 见 §一表（NBFNet 四段合计有序衔接约 **~27 min** 量级；rank-pair **~16 min**；RotatE 整条 **~3 min** 量级）。
3. **四 eval split：** Clean/QRTC valid **3227**；test **6438** — log 与 indices **一致**。
4. **QRTC env：** **CONFIRMED**（`QRTC_ENABLE=1`, `USE_MEMORY=1`, `TOPK=2`；余模块 0）。
5. **Checkpoint：** 路径与文件存在；**`strict=False`** 为残留风险。
6. **Config diff：** 见 §五。
7. **`eval_valid_only.py` diff：** **GIT 不可用 — NOT_TRUSTED for baseline comparison**；行为见 §六。
8. **Rank-pair：** **6438 triples，12876 pairs**，TSV **6438 行数据** — **full test 确认**。
9. **RotatE：** Train / **full test** 可信叙述需谨慎；**full valid 不可信**（**CAP=2**）。
10. **PC_KEGG 表：** 按用户口径 **VERDICT≠A → 不把 QRTC-HR 作正式结论**；若仅作 **internal/debug**，需脚注 **RotatE valid + strict=False**。

---

*Audit generated from filesystem evidence on 2026-05-08.*
