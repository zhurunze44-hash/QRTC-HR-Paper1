# PC_KEGG withBRG — QRTC-HR memory_off ablation — closure summary

**Read-only synthesis.** No train/eval/rank-pair runs performed for this document.  
**Output dir:** `paper1_q2_sci_package_20260428/qrtc_ablation_20260509/`  
**Date:** 2026-05-10

---

## VERDICT

**MIXED_MEMORY_EFFECT**

Under the frozen **full valid / full test** protocol, **QRTC-HR with memory disabled** (`QRTC_USE_MEMORY=0`) is **not** uniformly weaker or stronger than **QRTC-HR memory-on**. On **full test**, memory-off is **worse** than memory-on on **top-heavy ranking** (Hits@1/3/10, MRR) but **better on MR** (lower is better) and shows **tiny** AP/AUROC differences versus memory-on. Relative to **Clean**, memory-off remains **ranking-positive on some Hits/MRR axes** but **mixed versus Clean** on AP/AUROC and MR (see delta tables). This pattern supports **mixed memory effect**, not a single headline that “memory is essential” or “memory is irrelevant.”

---

## Protocol

| Item | Value |
|------|--------|
| **Dataset** | PC_KEGG_0602 |
| **Graph setting** | withBRG (`include_factgraph`: yes in frozen Clean/QRTC runs) |
| **Seed** | 1024 |
| **batch_size** | 16 |
| **num_negative** | 512 |
| **epoch** | 8 (`model_epoch_8.pth`) |
| **Clean / QRTC memory-on authority** | `qrtc_hr_full_closure_20260504/CLEAN_VS_QRTC_HR_FULL_VALID_TEST_MAIN_TABLE_20260507.md` |
| **QRTC memory-on env (frozen runs)** | QRTC-HR fused withBRG formal epoch-8 train/eval as documented in freeze table |
| **QRTC memory-off env (ablation)** | `QRTC_ENABLE=1`, `QRTC_USE_MEMORY=0`, `QRTC_TOPK=2` |
| **Contamination modules** | All disabled per train status (`FAMILY_CTX_*`, `QAES_ENABLE`, … = 0) |

---

## Memory-off train evidence

Source: `PC_KEGG_WITHBRG_QRTC_ABLATION_MEMORY_OFF_FORMAL_TRAIN_STATUS_20260509.md`

| Field | Value |
|-------|--------|
| **Final BCE** | 0.474884 |
| **Wall time** | ~4h04m42s (2026-05-09 16:53:28 → 20:58:10) |
| **Peak GPU memory** | 13735.2 MiB |
| **Checkpoint** | `paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-09-16-53-28-980276/model_epoch_8.pth` |
| **EXIT_CODE** | 0 |

---

## Memory-off full valid metrics

| AP | AUROC | Hits@1 | Hits@3 | Hits@10 | Hits@20 | Hits@50 | Hits@100 | MR | MRR |
|---:|------:|-------:|-------:|--------:|--------:|--------:|---------:|---:|----:|
| 0.986614 | 0.985405 | 0.433685 | 0.572978 | 0.716920 | 0.784785 | 0.862566 | 0.909049 | 125.346 | 0.526857 |

---

## Memory-off full test metrics

| AP | AUROC | Hits@1 | Hits@3 | Hits@10 | Hits@20 | Hits@50 | Hits@100 | MR | MRR |
|---:|------:|-------:|-------:|--------:|--------:|--------:|---------:|---:|----:|
| 0.986863 | 0.985671 | 0.448820 | 0.583722 | 0.725691 | 0.792171 | 0.865719 | 0.907580 | 122.678 | 0.540014 |

---

## Clean vs QRTC memory-on vs memory-off comparison

Scalars for **Clean** and **QRTC-HR memory-on** are taken from **`CLEAN_VS_QRTC_HR_FULL_VALID_TEST_MAIN_TABLE_20260507.md`** (§2 valid, §3 test). **Memory-off** scalars from ablation status cards above.

### Full validation

| Metric | Clean NBFNet | QRTC-HR memory-on | QRTC-HR memory-off |
|--------|-------------:|------------------:|-------------------:|
| AP | 0.988077 | 0.987018 | 0.986614 |
| AUROC | 0.986829 | 0.985864 | 0.985405 |
| Hits@1 | 0.427022 | 0.445460 | 0.433685 |
| Hits@3 | 0.572358 | 0.579641 | 0.572978 |
| Hits@10 | 0.712581 | 0.720948 | 0.716920 |
| Hits@20 | 0.782770 | 0.788813 | 0.784785 |
| Hits@50 | 0.863960 | 0.864735 | 0.862566 |
| Hits@100 | 0.904865 | 0.905485 | 0.909049 |
| MR | 126.674 | 123.395 | 125.346 |
| MRR | 0.524037 | 0.536668 | 0.526857 |

### Full test

| Metric | Clean NBFNet | QRTC-HR memory-on | QRTC-HR memory-off |
|--------|-------------:|------------------:|-------------------:|
| AP | 0.988616 | 0.986643 | 0.986863 |
| AUROC | 0.987207 | 0.985724 | 0.985671 |
| Hits@1 | 0.440975 | 0.460158 | 0.448820 |
| Hits@3 | 0.580304 | 0.592498 | 0.583722 |
| Hits@10 | 0.724371 | 0.730429 | 0.725691 |
| Hits@20 | 0.793336 | 0.793103 | 0.792171 |
| Hits@50 | 0.866107 | 0.866418 | 0.865719 |
| Hits@100 | 0.908046 | 0.907891 | 0.907580 |
| MR | 121.068 | 126.234 | 122.678 |
| MRR | 0.536298 | 0.550018 | 0.540014 |

---

## Delta tables

Convention: **Δ = row_metric − reference_metric**. For **MR**, negative Δ means **better** (lower rank).

### Full test — memory-on − Clean

| Metric | Δ |
|--------|--:|
| AP | −0.001973 |
| AUROC | −0.001483 |
| Hits@1 | +0.019183 |
| Hits@3 | +0.012194 |
| Hits@10 | +0.006058 |
| Hits@20 | −0.000233 |
| Hits@50 | +0.000311 |
| Hits@100 | −0.000155 |
| MR | +5.166 |
| MRR | +0.013720 |

*(Matches freeze main table §3.)*

### Full test — memory-off − Clean

| Metric | Δ |
|--------|--:|
| AP | −0.001753 |
| AUROC | −0.001536 |
| Hits@1 | +0.007845 |
| Hits@3 | +0.003418 |
| Hits@10 | +0.001320 |
| Hits@20 | −0.001165 |
| Hits@50 | −0.000388 |
| Hits@100 | −0.000466 |
| MR | +1.610 |
| MRR | +0.003716 |

### Full test — memory-off − memory-on

| Metric | Δ |
|--------|--:|
| AP | +0.000220 |
| AUROC | −0.000053 |
| Hits@1 | −0.011338 |
| Hits@3 | −0.008776 |
| Hits@10 | −0.004738 |
| Hits@20 | −0.000932 |
| Hits@50 | −0.000699 |
| Hits@100 | −0.000311 |
| MR | −3.556 |
| MRR | −0.010004 |

### Full valid — memory-off − memory-on

| Metric | Δ |
|--------|--:|
| AP | −0.000404 |
| AUROC | −0.000459 |
| Hits@1 | −0.011775 |
| Hits@3 | −0.006663 |
| Hits@10 | −0.004028 |
| Hits@20 | −0.004028 |
| Hits@50 | −0.002169 |
| Hits@100 | +0.003564 |
| MR | +1.951 |
| MRR | −0.009811 |

*(Valid deltas for interpretation only; primary stop/go uses **test** — see decision card.)*

---

## Interpretation

1. **Versus memory-on (full test):** Memory-off **loses** on **Hits@1/3/10** and **MRR**, so one **cannot** claim that trajectory memory is irrelevant for the **same top-heavy ranking emphasis** captured by those metrics. At the same time, memory-off **improves MR** versus memory-on on test (**ΔMR = −3.556**), so memory is **not** a monotone “quality knob” across all ranking summaries.

2. **Versus memory-on (full valid):** The same broad tension appears: memory-off is **lower** on most Hits and MRR but **higher** on Hits@100 and has **worse MR** than memory-on on valid (**ΔMR +1.951**). Valid vs test **direction differs for MR** between memory-off and memory-on profiles — consistent with **mixed**, split-sensitive tail behavior (aligned with the freeze narrative on Clean vs QRTC MR asymmetry).

3. **Honest summary:** **Memory contribution is limited / not decisive** as a single-story explanation: disabling memory **does not** reproduce Clean, but also **does not** match memory-on’s Hits@1–10/MRR bundle on test. **Mixed memory effect.**

4. **If memory_off were uniformly above memory-on:** one could not claim memory as the **key** gain source; here memory-off is **not** uniformly above memory-on on test, so the strict version of that caveat does not apply — instead, **memory helps** for the **specific** memory-on ranking bundle while **hurting MR** on test relative to memory-on.

---

## Claim impact

| Topic | Guidance |
|-------|----------|
| **“Memory-enhanced QRTC-HR”** | **Soften.** Prefer **“QRTC-HR with optional trajectory memory”** or describe memory as one **component** of the hop/readout stack. Do **not** imply memory is the **sole** or **guaranteed** mechanism for reported ranking lifts. |
| **Primary contribution** | Emphasize **query-conditioned multi-hop readout / routing** (the stable QRTC core with `QRTC_ENABLE=1`, `QRTC_TOPK=2`) as the **main architectural narrative**, with memory as **auxiliary**. |
| **Memory role** | Treat memory as **implementation option / ablation finding**: it **modulates** top-heavy Hits and MRR versus the memory-off variant but **trades off** with MR on test versus memory-on. |

---

## Next action (topk1/topk3)

See **`PC_KEGG_WITHBRG_QRTC_ABLATION_STOP_GO_DECISION_20260510.md`**. Default recommendation: **do not auto-start** top-k sweeps; **prioritize prose alignment + baseline feasibility audit** unless a human explicitly authorizes a narrow top-k probe.

---

## Artifact index

| Asset | Path |
|-------|------|
| Train status | `qrtc_ablation_20260509/PC_KEGG_WITHBRG_QRTC_ABLATION_MEMORY_OFF_FORMAL_TRAIN_STATUS_20260509.md` |
| Full valid status | `qrtc_ablation_20260509/PC_KEGG_WITHBRG_QRTC_ABLATION_MEMORY_OFF_EPOCH8_FULLVALID_STATUS_20260509.md` |
| Full test status | `qrtc_ablation_20260509/PC_KEGG_WITHBRG_QRTC_ABLATION_MEMORY_OFF_EPOCH8_FULLTEST_STATUS_20260510.md` |
| Clean vs QRTC freeze table | `qrtc_hr_full_closure_20260504/CLEAN_VS_QRTC_HR_FULL_VALID_TEST_MAIN_TABLE_20260507.md` |
| Freeze summary | `qrtc_hr_full_closure_20260504/QRTC_HR_FULL_RESULTS_FREEZE_SUMMARY_20260507.md` |
| Comparison TSV | `qrtc_ablation_20260509/PC_KEGG_WITHBRG_QRTC_ABLATION_MEMORY_OFF_COMPARISON_TABLE_20260510.tsv` |
