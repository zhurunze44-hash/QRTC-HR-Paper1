# withoutBRG QRTC-HR — protocol conflict audit — 2026-05-08

**Scope:** Resolve whether the **May-2026-08** withoutBRG QRTC-HR rerun is a **protocol/eval bug** vs a **real checkpoint / history conflict**.  
**No** retrain, **no** QRTC formula edits, **no** LncTarD-PPI.

---

## VERDICT (single choice)

### **A. CURRENT_QRTC_RERUN_PROTOCOL_MATCHED_BUT_RESULT_CONFLICTS_HISTORY**

**Reasoning:**

1. **Historical formal asset exists** (May-2026-02 closure) with metrics matching the “positive withoutBRG QRTC” impression (**AP ~0.952, MRR ~0.407** on full valid — see §3).
2. **Train/eval YAML** for historical vs **May-2026-08** current run is **field-aligned** on all substantive keys (§4) — differences are **`dataset.path` prefix** (`<REDACTED_SERVER_PATH> vs `/root/autodl-tmp/...`) and **`output_dir` / checkpoint identity**, **not** architecture switches.
3. **Controlled diagnostic (`EVAL_VALID_CAP=64`, same valid prefix slice):**
   - **Historical QRTC ckpt (May-02 train)** → MR **211.68**, MRR **0.438** — **consistent with** the historical “good” regime on the **same** 64 triples.
   - **Current Clean ckpt (May-08 train)** → MR **244.33**, MRR **0.417** — coherent with strong Clean.
   - **Current QRTC ckpt (May-08 train)** → MR **741.35**, MRR **0.304** — reproduces the **degraded** pattern on the **identical** slice.
   
   Therefore the eval harness is **not** the sole explanation for gap vs history — the **May-08 QRTC checkpoint** behaves badly **relative to both May-02 QRTC ckpt and May-08 Clean ckpt** under matched caps.

4. **Runtime probe:** Clean vs QRTC **`predict()`** tensors **are not identical**; QRTC-named weights **change norm** under QRTC-enabled load — **not** consistent with “QRTC completely inert” (`WITHOUTBRG_QRTC_RUNTIME_PROBE_STATUS_20260508.md`). **`QRTC_DEBUG` layer list empty** on `predict()` path → **visibility gap**, not automatic proof of inactive hops.

**Not B as primary label:** No smoking-gun **wrong `include_factgraph` / wrong split / hidden smoke flag** in YAML between histories — **code revision parity across dates** is **not git-verified** (no repo), listed as **residual uncertainty**.

**Not C:** Scores **differ** Clean vs QRTC; params **not** NaN/inf.

**Not D:** Historical asset **found**.

---

## 一、撤销 / 争议入口

See **`PC_KEGG_QRTC_HR_FINAL_TRUSTED_RESULT_PACKAGE_20260508_REVIEW_ADDENDUM.md`**  
**VERDICT=`WITHOUTBRG_QRTC_RESULT_UNDER_DISPUTE_NOT_FINAL`**

---

## 二、历史 withoutBRG QRTC-HR 正式资产（已找到）

**NOT** `HISTORICAL_WITHOUTBRG_QRTC_ASSET_NOT_FOUND`.

### Anchor document

| Field | Value |
|-------|-------|
| **Status / write-up** | `paper1_q2_sci_package_20260428/qrtc_hronly_withoutbrg_FULL_EXPERIMENT_20260502/ROUTE_A_QRTC_HRONLY_WITHOUTBRG_EPOCH8_FULL_RESULT_FINAL_20260502.md` |
| **Train config** | `config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_hronly_withoutbrg_mem_formal_seed1024_epoch8_batch16_neg512_20260430.yaml` |
| **Eval config** | `paper1_q2_sci_package_20260428/qrtc_hronly_withoutbrg_FULL_EXPERIMENT_20260502/pc_kegg_qrtc_hronly_withoutbrg_epoch8_EVAL_WITH_ABS_CKPT_20260502.yaml` |
| **Train log** | `.../train_withoutbrg_qrtc_hronly_epoch8_20260502_144101.log` |
| **Full valid log** | `.../full_valid_WITH_ABS_CKPT_PATCHED_LOAD_withoutbrg_qrtc_hronly_epoch8_20260502_152423.log` |
| **Full test log** | `.../full_test_WITH_ABS_CKPT_PATCHED_LOAD_withoutbrg_qrtc_hronly_epoch8_20260502_152423.log` |
| **Checkpoint** | `.../pc_kegg_qrtc_hronly_withoutbrg_mem_formal_seed1024_epoch8_batch16_neg512/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-02-14-41-05-535438/model_epoch_8.pth` |
| **output_dir (train yaml)** | `paper1_q2_sci_package_20260428/pc_kegg_qrtc_hronly_withoutbrg_mem_formal_seed1024_epoch8_batch16_neg512` |
| **Dataset path (historical yaml)** | `<REDACTED_SERVER_PATH> |
| **include_factgraph** | **no** |
| **num_relation** | **1** (PC_KEGG single relation idiom — from dataset) |
| **Model class** | **NBFNet** (`task.model.class`) |
| **QRTC implementation** | Env-gated modules in **`biopathnet/model.py`** (`QRTC_ENABLE`, `QRTC_USE_MEMORY`, `QRTC_TOPK`; message wrappers / readout). |

### Frozen scalars (historical full valid / test)

| Split | AP | MRR | Hits@10 | MR |
|-------|---:|----:|--------:|---:|
| Valid | 0.951995 | 0.407044 | 0.560428 | 263.404 |
| Test | 0.955361 | 0.420297 | 0.574790 | 261.394 |

---

## 三、当前（May-08）vs 历史 — 数值对照

> **Post-lock (2026-05-08):** The **May-08 QRTC** row below is **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`** (audit / dispute-era snapshot). **Final PC_KEGG QRTC** = May-02 protected re-eval — `PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md`.

### Full eval (from session status cards / closure summary)

| Track | AP (valid) | MRR (valid) | MR (valid) |
|-------|------------|-------------|------------|
| **Historical QRTC** (May-02 ckpt) | 0.951995 | 0.407044 | 263.404 |
| **Current Clean** (May-08 ckpt) | 0.951666 | 0.391859 | 279.247 |
| **Current QRTC** (May-08 ckpt) — **INVALID FOR TABLE** | 0.889313 | 0.296707 | 973.794 |

### Diagnostic cap64 (same `EVAL_VALID_CAP=64` prefix of valid — **not** a paper table)

| Track | MR | MRR | AP |
|-------|---:|----:|---:|
| Hist QRTC ckpt | 211.68 | 0.438 | 0.957 |
| Curr Clean ckpt | 244.33 | 0.417 | 0.956 |
| Curr QRTC ckpt | 741.35 | 0.304 | 0.898 |

**Read:** Historical QRTC checkpoint **matches** “good regime” on the diagnostic slice; current QRTC checkpoint **does not**. **Current Clean** remains strong on the same slice — isolates issue to **May-08 QRTC training realization**, not dataset swap.

**Rank rows:** First **20** triples **unfiltered tail rank** dump appended to **`withoutbrg_cap64_protocol_diag_20260508.log`** (`idx h t r unfiltered_tail_rank`) — **diagnostic only**, not filtered MR protocol.

---

## 四、协议级 YAML diff（当前 Clean vs 当前 QRTC）

Compared files:

| Role | Path |
|------|------|
| Clean train | `withoutbrg_formal_rerun_20260507/config/clean_withoutbrg_formal_torch201_20260507.yaml` |
| Clean eval | `withoutbrg_formal_rerun_20260507/config/clean_withoutbrg_eval_abs_ckpt_20260508_020728.yaml` |
| QRTC train | `withoutbrg_formal_rerun_20260507/config/qrtc_hronly_withoutbrg_direct_train_20260508.yaml` |
| QRTC eval | `withoutbrg_formal_rerun_20260507/config/qrtc_hronly_withoutbrg_eval_abs_ckpt_20260508.yaml` |

### Train: Clean vs QRTC (`*_formal_*` vs `*_direct_train_*`)

| Field | Clean train | QRTC train |
|-------|-------------|------------|
| dataset.path | `/root/autodl-tmp/.../PC_KEGG_0602` | **same** |
| include_factgraph | no | **same** |
| task.class | KnowledgeGraphCompletionBiomed | **same** |
| model.class | NBFNet | **same** |
| input_dim / hidden_dims | 32 / [32]×6 | **same** |
| message_func / aggregate_func | distmult / pna | **same** |
| short_cut / dependent | yes / yes | **same** |
| remove_one_hop | **not in yaml** (model default False) | **same** |
| num_negative | 512 | **same** |
| batch_size | 16 | **same** |
| optimizer / lr | Adam / 5e-3 | **same** |
| num_epoch | 8 | **same** |
| smoke_skip_valid | yes | **same** |
| output_dir | `.../clean_train_out` | `.../qrtc_hronly_train_direct_20260508` |
| checkpoint | *(train yaml typically none)* | **same** |

**QRTC has no extra YAML keys** — runtime toggles are **environment variables** during train/eval (`QRTC_ENABLE`, etc.), **not** duplicated in these YAMLs.

### Eval: Clean vs QRTC

| Field | Clean eval | QRTC eval |
|-------|------------|-----------|
| dataset.path | `/root/.../PC_KEGG_0602` | **same** |
| include_factgraph | no | **same** |
| task/model architecture block | identical NBFNet hyperparameters | **same** |
| checkpoint | Clean `model_epoch_8.pth` path | QRTC `model_epoch_8.pth` path (**different file**) |
| train.num_epoch | 8 | **same** |
| smoke_skip_valid | yes | **same** |
| batch_per_epoch | **absent** | **absent** |
| cap / debug / subset | **absent** | **absent** |

**Split:** chosen at runtime via **`EVAL_ONLY_SPLIT`** (`valid` / `test`), not duplicated as separate YAML files.

---

## 五、Runtime probe（摘要）

See **`WITHOUTBRG_QRTC_RUNTIME_PROBE_STATUS_20260508.md`** + **`withoutbrg_qrtc_runtime_probe_20260508.log`**.

---

## 六、是否“当前 rerun 跑错”？

**Eval harness / wrong split / swapped yaml:** **Not supported** — cap64 control shows **historical ckpt healthy** and **current Clean healthy** on the **same slice**; only **current QRTC ckpt** collapses.

**Residual risks (explicit):**

- **Code drift** between **2026-05-02** train date and **2026-05-08** (no git pin).
- **`QRTC_DEBUG` layers** empty on **`predict()`** probe — hop-level tracing needs a **deeper hook** (out of scope).

---

## 七、论文表与冻结包处置

- **`PC_KEGG_QRTC_HR_FINAL_TRUSTED_RESULT_PACKAGE_20260508.md`** remains **PROVISIONAL / UNDER DISPUTE** for **withoutBRG QRTC-HR** rows per **REVIEW ADDENDUM**.
- **Current withoutBRG QRTC-HR full metrics:** **must not** be written as **final** scientific conclusions until **human** decides whether **May-08 QRTC train** is the intended canonical replicate of **May-02**.

---

## 八、日志索引（本轮审计）

| Log | Role |
|-----|------|
| `withoutbrg_qrtc_runtime_probe_20260508.log` | Runtime probe |
| `withoutbrg_cap64_protocol_diag_20260508.log` | cap64 triple-run + first-20 unfiltered ranks |

---

*Audit completed 2026-05-08.*
