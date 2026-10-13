# PC_KEGG Paper 1 — final trusted result package (freeze) — 2026-05-08

**Purpose:** Freeze a **teacher-reviewable, auditable** asset list for **Paper 1 / PC_KEGG**.  
**Rules honored:** No new training, no new eval, no narrative inflation — **organize and label only**.

**Repo anchor:** `/root/autodl-tmp/BioPathNet_fresh`  
**Closure root (relative):** `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/`

> **STATUS (2026-05-08 arbitration):** **`withoutBRG QRTC-HR`** is **RESOLVED** — use **historical May-02 checkpoint + current-harness protected re-eval** as the **authoritative table source** (`PC_KEGG_QRTC_HR_FINAL_TRUSTED_RESULT_PACKAGE_20260508_AUTHORITY_UPDATE.md`, `WITHOUTBRG_QRTC_AUTHORITY_ARBITRATION_20260508.md`). **May-08 withoutBRG QRTC-HR rerun checkpoint** is **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`** (logs/cards retained as audit only). Earlier **PROVISIONAL / UNDER_DISPUTE** notes refer to the **superseded May-08 rerun row**; see `PC_KEGG_QRTC_HR_FINAL_TRUSTED_RESULT_PACKAGE_20260508_REVIEW_ADDENDUM.md` / `WITHOUTBRG_QRTC_PROTOCOL_CONFLICT_AUDIT_20260508.md` for historical context only.

---

## 一、可信性分级

### A. FORMAL_TRUSTED

| Asset | Trust basis |
|-------|-------------|
| **withBRG Clean** full valid / full test | Full-split logs + status cards; frozen table `CLEAN_VS_QRTC_HR_FULL_VALID_TEST_MAIN_TABLE_20260507.md` §sources |
| **withBRG QRTC-HR** full valid / full test | Same freeze chain + `QRTC_HR_FULL_RESULTS_FREEZE_SUMMARY_20260507.md` |
| **withBRG** full-test rank-pair **interpretation doc** | `QRTC_HR_RANK_PAIR_DIAGNOSIS_AGGREGATE_20260507.md` (**aggregate / theory boundary**: no per-query rank tensors retained for this closure — see doc §0) |
| **withoutBRG Clean** full valid / full test | `WITHOUTBRG_CLEAN_FULL_*_STATUS_20260508.md` + audit `WITHOUTBRG_FULL_EVAL_SPEED_AND_PATH_AUDIT_20260508.md` |
| **withoutBRG QRTC-HR** full valid / full test | **FORMAL_TRUSTED (2026-05-08)** — **May-02 checkpoint** + **`WITHOUTBRG_HIST_MAY02_QRTC_FULL_*_REEVAL_STATUS_20260508.md`** / **`PC_KEGG_QRTC_HR_FINAL_TRUSTED_RESULT_PACKAGE_20260508_AUTHORITY_UPDATE.md`** |
| **withoutBRG** full-test rank-pair diagnosis | `WITHOUTBRG_FULLTEST_RANKPAIR_DIAGNOSIS_STATUS_20260508.md`, `withoutbrg_fulltest_rankpair_diag_20260508/rankpair_summary.json` |
| **RotatE withoutBRG** full **test** | `ROTATE_WITHOUTBRG_FULL_TEST_STATUS_20260508.md` |
| **RotatE withoutBRG** full **valid** — **no-cap re-eval only** | `ROTATE_WITHOUTBRG_FULL_VALID_REEVAL_NOCAP_STATUS_20260508.md` |

### B. INVALID_OR_SUPERSEDED

| Item | Reason |
|------|--------|
| **`ROTATE_WITHOUTBRG_FULL_VALID_STATUS_20260508.md`** | **`EVAL_VALID_CAP=2`** → **INVALID_AS_FULL_VALID** — superseded by **`ROTATE_WITHOUTBRG_FULL_VALID_REEVAL_NOCAP_STATUS_20260508.md`** |
| **`WITHOUTBRG_QRTC_HRONLY_FULL_*_STATUS_20260508.md`** (May-08 rerun) | **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`** — superseded by **May-02** protected re-eval (`WITHOUTBRG_HIST_MAY02_QRTC_FULL_*_REEVAL_STATUS_20260508.md`) |
| **`QRTC_HRONLY_FUSED_WITHBRG_FORMAL_EPOCH8_CAP32_VALIDONLY_STATUS_20260506.md`** & related **cap32 / valid-only** rows | **Bounded / capped** — **exclude from final full-split results table** |
| Any **`SMOKE` / `onebatch` / `minitrain` / `LG`** staging logs in `QRTC_HR_LARGEGPU_*`, `*_SMOKE_*` status cards | **Preflight / smoke** — not formal full-split |

### C. PREFLIGHT_ONLY_OR_BLOCKED

| Item | Status |
|------|--------|
| **LncTarD-PPI** second-task closure | **BLOCKED — data missing** (`data/lnctardppi` **not present** on this server snapshot). |

---

## 二、PC_KEGG withBRG — formal comparison（teacher-facing）

**Sources:** `CLEAN_VS_QRTC_HR_FULL_VALID_TEST_MAIN_TABLE_20260507.md` (frozen 2026-05-07); metrics reproduced in `PC_KEGG_QRTC_HR_FULL_CLOSURE_SUMMARY_20260508.md`.

### Valid — Clean vs QRTC-HR

| Metric | Clean | QRTC-HR | Δ (QRTC − Clean) |
|--------|------:|--------:|------------------:|
| Hits@1 | 0.427022 | 0.445460 | **+0.018438** |
| Hits@3 | 0.572358 | 0.579641 | **+0.007283** |
| Hits@10 | 0.712581 | 0.720948 | **+0.008367** |
| MRR | 0.524037 | 0.536668 | **+0.012631** |
| AP | 0.988077 | 0.987018 | −0.001059 |
| AUROC | 0.986829 | 0.985864 | −0.000965 |
| MR | 126.674 | 123.395 | **−3.279** |

### Test — Clean vs QRTC-HR

| Metric | Clean | QRTC-HR | Δ (QRTC − Clean) |
|--------|------:|--------:|------------------:|
| Hits@1 | 0.440975 | 0.460158 | **+0.019183** |
| Hits@3 | 0.580304 | 0.592498 | **+0.012194** |
| Hits@10 | 0.724371 | 0.730429 | **+0.006058** |
| MRR | 0.536298 | 0.550018 | **+0.013720** |
| AP | 0.988616 | 0.986643 | −0.001973 |
| AUROC | 0.987207 | 0.985724 | −0.001483 |
| MR | 121.068 | 126.234 | **+5.166** |

### Prose constraints（必须遵守）

- **Allowed:** QRTC-HR **improves** filtered **top-k** retrieval (**Hits@1 / @3 / @10**) and **MRR** vs Clean on **both** splits under this protocol; **AP / AUROC** move **slightly lower**.
- **Required:** **Test MR worsens** (+5.166) while **valid MR improves** (−3.279) — **not** a monotone story on mean rank.
- **Rank-pair / MR narrative (withBRG):** The frozen aggregate note **`QRTC_HR_RANK_PAIR_DIAGNOSIS_AGGREGATE_20260507.md`** explains **how** MR can rise while Hits/MRR rise (**mean-heavy tail sensitivity**). It **explicitly states** that **per-query head/tail rank exports were not retained** for that closure — therefore **do not** claim an **empirical** “head-only” decomposition from that artifact. (**Empirical** head-vs-tail Δrank is documented for **withoutBRG** rank-pair — §三.)
- **Forbidden wording:** “comprehensive improvement,” “uniformly better on all metrics,” or implying **test MR** improved.

---

## 三、PC_KEGG withoutBRG — formal comparison（边界结果）

**Authoritative source (withoutBRG QRTC-HR):** `WITHOUTBRG_HIST_MAY02_QRTC_FULL_VALID_REEVAL_STATUS_20260508.md`, `WITHOUTBRG_HIST_MAY02_QRTC_FULL_TEST_REEVAL_STATUS_20260508.md`, logs `hist_may02_qrtc_protected_full_*_arbitration_20260508.log`, and `PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md`.  
**Clean:** `WITHOUTBRG_CLEAN_FULL_*_STATUS_20260508.md`.  
**Do not** use `WITHOUTBRG_QRTC_HRONLY_FULL_*_STATUS_20260508.md` (May-08 **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`**) or the **pre-lock** QRTC column in any rollup for **final tables**.  
`PC_KEGG_QRTC_HR_FULL_CLOSURE_SUMMARY_20260508.md` §3–4 is aligned **post-lock** to these numbers (see lock card).

### Canonical anchor（withoutBRG QRTC — for citation / copy-paste）

| Split | AP | AUROC | MR | MRR |
|-------|---:|------:|---:|----:|
| **Valid** | **0.952** | **0.948784** | **263.658** | **0.406578** |
| **Test** | **0.952694** | **0.949748** | **261.621** | **0.419978** |

(Full Hits@K in tables below.)

### Valid — Clean vs QRTC-HR (**authoritative QRTC = May-02 ckpt, current-harness re-eval 2026-05-08**)

| Metric | Clean | QRTC-HR | Δ (QRTC − Clean) |
|--------|------:|--------:|------------------:|
| Hits@1 | 0.313914 | 0.328633 | **+0.014719** |
| Hits@3 | 0.417106 | 0.435699 | **+0.018593** |
| Hits@10 | 0.549737 | 0.559498 | **+0.009761** |
| MRR | 0.391859 | 0.406578 | **+0.014719** |
| AP | 0.951666 | 0.952 | **+0.000334** |
| AUROC | 0.945955 | 0.948784 | **+0.002829** |
| MR | 279.247 | 263.658 | **−15.589** |

### Test — Clean vs QRTC-HR (**same authority**)

| Metric | Clean | QRTC-HR | Δ (QRTC − Clean) |
|--------|------:|--------:|------------------:|
| Hits@1 | 0.326033 | 0.341799 | **+0.015766** |
| Hits@3 | 0.433054 | 0.448975 | **+0.015921** |
| Hits@10 | 0.562908 | 0.574324 | **+0.011416** |
| MRR | 0.405033 | 0.419978 | **+0.014945** |
| AP | 0.952662 | 0.952694 | **+0.000032** |
| AUROC | 0.947710 | 0.949748 | **+0.002038** |
| MR | 273.914 | 261.621 | **−12.293** |

### Prose constraints

- **Fact (updated):** Under the **May-02 withoutBRG QRTC** checkpoint and **current eval harness**, QRTC-HR is **slightly above Clean** on **Hits@1–@10**, **MRR**, **AP/AUROC**, and **better than Clean on MR** (lower is better) on **both** splits — a **small positive margin** on this track, **not** a headline withBRG-scale claim.
- **Label:** **withoutBRG** remains **ablation / boundary channel**; the **primary** quantitative story for Paper 1 stays **withBRG** (§二).
- **Required caveat:** The **May-08 withoutBRG QRTC rerun** was **invalid for tables** (**`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`**); do **not** mix May-08 QRTC numbers into this comparison.
- **Interpretation:** Treat as **conditional** evidence that QRTC-HR **can** help **even without BRG** under a **healthy checkpoint**, while **withBRG** remains the **main** evidentiary path.

### Rank-pair (withoutBRG full test, empirical)

From `withoutbrg_fulltest_rankpair_diag_20260508/rankpair_summary.json` / diagnosis MD: **mean Δrank (head)** ≫ **mean Δrank (tail)** — MR tension **concentrates on head-side** ranks in this export (**6438** triples, **12876** directed pairs).

---

## 四、RotatE baseline（withoutBRG）

**Role:** **Weak classical KGE baseline** — useful as **sanity bounds**, not as a competitive primary model.

| Split | Status card | MR | MRR | Hits@10 | AP | AUROC |
|-------|-------------|---:|----:|--------:|---:|------:|
| **Valid** | **`ROTATE_WITHOUTBRG_FULL_VALID_REEVAL_NOCAP_STATUS_20260508.md`** | 1485.03 | 0.0167032 | 0.0319182 | 0.583149 | 0.584417 |
| **Test** | **`ROTATE_WITHOUTBRG_FULL_TEST_STATUS_20260508.md`** | 1457.70 | 0.016508 | 0.028114 | 0.578835 | 0.590410 |

- **Superseded / invalid for valid:** **`ROTATE_WITHOUTBRG_FULL_VALID_STATUS_20260508.md`** (**`EVAL_VALID_CAP=2`**).
- **Checkpoint (both evals):** `rotate_withoutbrg_formal_seed1024_epoch30_20260508/.../2026-05-08-14-32-16-015464/model_epoch_30.pth` (see each card).

---

## 五、最终论文结论约束（冻结用语）

1. **Strongest quantitative evidence for Paper 1’s PC_KEGG claim** remains **withBRG** (background relation graph present).
2. **withoutBRG** is **ablation / boundary analysis** — **not** the primary channel for the **headline** claim; any **withoutBRG QRTC** statement must cite the **May-02 authoritative re-eval**, **not** the **May-08 bad rerun**.
3. **Do not** claim QRTC-HR **universally improves** all settings or all metrics.
4. **Supported qualified claim:** On **PC_KEGG with BRG**, QRTC-HR tends to improve **top-heavy filtered retrieval** (**Hits@1–10**, **MRR**) with **small** **AP/AUROC** trade-offs and **non-monotone** **MR** (**valid MR better, test MR worse** under the frozen table). On **withoutBRG**, the **May-02 QRTC** checkpoint shows **modest gains vs Clean** on **Hits@K / MRR / AP / AUROC / MR** under the **2026-05-08** harness — **not** the **catastrophic** pattern seen under the **May-08 bad checkpoint** (retained only as a **negative control** artifact).
5. **Q2 / external generalization:** A **second primary task** (**LncTarD-PPI full closure**) is still **required** for external support — **currently blocked** by missing data (§一 C).

---

## 六、资产索引（paths + metrics + trust）

**Convention:** Paths below are under **`paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/`** unless noted `config/` or absolute.

### withBRG — Clean NBFNet

| Split | Status card | Config (repo `config/`) | Log | Checkpoint | Trust |
|-------|-------------|-------------------------|-----|------------|-------|
| Valid | `CLEAN_WITHBRG_EPOCH8_FULL_VALID_STATUS_20260504.md` | `q2_sci_pc_kegg_20260428/pc_kegg_clean_nbfnet_withbrg_epoch8_FULL_VALID_WITH_ABS_CKPT_20260504.yaml` | `clean_withbrg_epoch8_FULL_VALID_20260504.log` | `clean_withbrg_formal_seed1024_batch16_neg512_epoch8/.../2026-05-04-12-10-56-719935/model_epoch_8.pth` | **FORMAL_TRUSTED** |
| Test | `CLEAN_WITHBRG_EPOCH8_FULL_TEST_STATUS_20260504.md` | `..._FULL_TEST_WITH_ABS_CKPT_20260504.yaml` | `clean_withbrg_epoch8_FULL_TEST_20260504.log` | **same** `model_epoch_8.pth` | **FORMAL_TRUSTED** (metrics valid; prediction phase FileNotFound noted in card) |

### withBRG — QRTC-HR

| Split | Status card | Log | Trust |
|-------|-------------|-----|-------|
| Valid | `QRTC_HRONLY_FUSED_WITHBRG_FULL_VALID_MONITOR_SUMMARY_20260506.md` | `logs/qrtc_hronly_fused_withbrg_formal_epoch8_full_valid_nocap_20260506.log` | **FORMAL_TRUSTED** |
| Test | `QRTC_HRONLY_FUSED_WITHBRG_FULL_TEST_METRICS_SUMMARY_20260506.md` | `logs/qrtc_hronly_fused_withbrg_formal_epoch8_full_test_metrics_only_20260506.log` | **FORMAL_TRUSTED** |

**Train / ckpt anchor:** `QRTC_HRONLY_FUSED_WITHBRG_FORMAL_TRAIN_SEED1024_BATCH16_NEG512_EPOCH8_STATUS_20260505.md` → `qrtc_hronly_fused_withbrg_formal_seed1024_batch16_neg512_epoch8_20260505/.../model_epoch_8.pth`.

**Aggregate table / freeze:** `CLEAN_VS_QRTC_HR_FULL_VALID_TEST_MAIN_TABLE_20260507.md`, `QRTC_HR_FULL_RESULTS_FREEZE_SUMMARY_20260507.md`.

**Rank-pair (interpretation):** `QRTC_HR_RANK_PAIR_DIAGNOSIS_AGGREGATE_20260507.md` — **FORMAL_TRUSTED** as **written interpretation** (see §二 boundary).

### withoutBRG — Clean / QRTC-HR NBFNet

| Track | Split | Status card | Config (`withoutbrg_formal_rerun_20260507/config/`) | Log (`.../logs/`) | Checkpoint | Trust |
|-------|-------|-------------|-----------------------------------------------------|-------------------|------------|-------|
| Clean | Valid | `WITHOUTBRG_CLEAN_FULL_VALID_STATUS_20260508.md` | `clean_withoutbrg_eval_abs_ckpt_20260508_020728.yaml` | `clean_withoutbrg_full_valid_direct_20260508.log` | `clean_train_out/.../2026-05-08-02-07-31-368798/model_epoch_8.pth` | **FORMAL_TRUSTED** |
| Clean | Test | `WITHOUTBRG_CLEAN_FULL_TEST_STATUS_20260508.md` | same | `clean_withoutbrg_full_test_direct_20260508.log` | **same** | **FORMAL_TRUSTED** |
| QRTC-HR | Valid | `WITHOUTBRG_HIST_MAY02_QRTC_FULL_VALID_REEVAL_STATUS_20260508.md` | `pc_kegg_hist_may02_qrtc_epoch8_EVAL_PROTECTED_ARBITRATION_20260508.yaml` | `hist_may02_qrtc_protected_full_valid_arbitration_20260508.log` | `pc_kegg_qrtc_hronly_withoutbrg_mem_formal_seed1024_epoch8_batch16_neg512/.../2026-05-02-14-41-05-535438/model_epoch_8.pth` | **FORMAL_TRUSTED** |
| QRTC-HR | Test | `WITHOUTBRG_HIST_MAY02_QRTC_FULL_TEST_REEVAL_STATUS_20260508.md` | same | `hist_may02_qrtc_protected_full_test_arbitration_20260508.log` | **same** | **FORMAL_TRUSTED** |
| QRTC-HR (May-08 rerun) | Valid / Test | `WITHOUTBRG_QRTC_HRONLY_FULL_*_STATUS_20260508.md` | `qrtc_hronly_withoutbrg_eval_abs_ckpt_20260508.yaml` | `qrtc_hronly_withoutbrg_full_*_direct_20260508.log` | `qrtc_hronly_train_direct_20260508/.../2026-05-08-13-35-27-655973/model_epoch_8.pth` | **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`** |

**Audits (withoutBRG trust hardening):**  
`WITHOUTBRG_FULL_EVAL_SPEED_AND_PATH_AUDIT_20260508.md`, `WITHOUTBRG_QRTC_HARDLOAD_AND_CODEPATH_AUDIT_20260508.md`, `WITHOUTBRG_QRTC_AUTHORITY_ARBITRATION_20260508.md`.

### withoutBRG — rank-pair

| Artifact | Path | Trust |
|----------|------|-------|
| Pipeline / summary | `WITHOUTBRG_FULLTEST_RANKPAIR_DIAGNOSIS_STATUS_20260508.md`, `withoutbrg_fulltest_rankpair_diag_20260508/` | **FORMAL_TRUSTED** |

### RotatE withoutBRG

| Split | Status card | Config | Log | Trust |
|-------|-------------|--------|-----|-------|
| Valid (canonical) | `ROTATE_WITHOUTBRG_FULL_VALID_REEVAL_NOCAP_STATUS_20260508.md` | `withoutbrg_formal_rerun_20260507/config/pc_kegg_rotate_withoutbrg_eval_epoch30_20260508.yaml` | `rotate_withoutbrg_eval_workdir_20260508/full_valid_nocap_reeval_20260508.log` | **FORMAL_TRUSTED** |
| Test | `ROTATE_WITHOUTBRG_FULL_TEST_STATUS_20260508.md` | same | `rotate_withoutbrg_eval_workdir_20260508/full_test_20260508.log` | **FORMAL_TRUSTED** |
| Valid (invalid) | `ROTATE_WITHOUTBRG_FULL_VALID_STATUS_20260508.md` | — | `full_valid_20260508.log` | **INVALID_OR_SUPERSEDED** |

---

## 七、下一步建议（仅两项）

**A.** If compute continues: **restore LncTarD-PPI data** to the agreed **`data/lnctardppi`** layout → **integrity preflight only** (checksums / schema / splits) — **no training** until signed off.

**B.** If data is unavailable: **stop GPU burn**, **retain** this closure directory + checkpoints as the frozen asset pack.

---

## 附：汇总索引文档（non-authoritative pointers）

| Doc | Role |
|-----|------|
| `PC_KEGG_QRTC_HR_FULL_CLOSURE_SUMMARY_20260508.md` | Numeric rollup; **withoutBRG QRTC** column must match **§三 / lock card** (May-02 protected re-eval). **May-08 bad QRTC numbers are not final.** |
| `QRTC_HR_FULL_RESULTS_FREEZE_SUMMARY_20260507.md` | withBRG freeze declaration |
| `PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md` | **Final lock** — `WITHOUTBRG_QRTC_AUTHORITY_LOCKED` |

---

*Package frozen 2026-05-08 — read-only curation; **withoutBRG QRTC authority locked** (`PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md`); no new experiments executed for this file.*
