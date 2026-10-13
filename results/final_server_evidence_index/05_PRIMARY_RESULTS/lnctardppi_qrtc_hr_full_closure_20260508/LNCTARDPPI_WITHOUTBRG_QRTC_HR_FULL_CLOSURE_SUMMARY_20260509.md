# LncTarD-PPI withoutBRG — QRTC-HR full closure summary (2026-05-09)

## 1. VERDICT

**MIXED_POSITIVE** (with explicit **TRADEOFF** characterization)

**Rationale (metric-grounded, no preset optimism):**

- **Full valid:** QRTC improves **MR**, **MRR**, and most **Hits@k**, but **Hits@100** is lower than Clean (−0.018 on absolute scale). Not a clean sweep.
- **Full test:** QRTC improves **AP**, **AUROC**, **MR** (lower is better), and **MRR** slightly, but **Hits@1 / @3 / @10 / @50** are lower than Clean while **Hits@20 / @100** edge up. This is **not** “uniform improvement”; it matches a **ranking-cut vs mean-rank / scoring-metric trade-off**.
- **Rank-pair (609 test triples):** **526** rank-pairs improved vs **456** worsened (Δ = QRTC − Clean rank); **306** triples net-improved vs **276** net-worsened by (Δtail+Δhead). **Median** Δtail/Δhead are **0** — gains are **not** universal; **tail** moves show heavier **p99** outliers than **head**. **Relation 5** shows the largest mean improvement (very small *n*=7); **relation 1** mean Δtail is **positive** (QRTC worse on average for that relation’s tail ranks).

**Not selected:** **PASS_POSITIVE** (several Hits@ regressions invalidate a blanket “pass”). **FAIL_NEGATIVE** rejected (aggregate MR/MRR/AP/AUROC do not collapse; QRTC is competitive with mixed directional splits). **TRADEOFF** alone understates the net MR/MRR/AP gains — hence **MIXED_POSITIVE** as the primary label, with trade-offs spelled out in §10.

---

## 2. Dataset / protocol

| Item | Value |
|------|--------|
| Benchmark | **LncTarD-PPI** |
| Split files (triples, on disk) | **train1** 1,035,133 · **train2** 4,867 · **valid** 608 · **test** 609 |
| **include_factgraph** | **no** (withoutBRG: BRG / `train1` **not** in the loaded reasoning graph; training/eval follow `biomedical` with `chosen_files = files[1:]` → **train2, valid, test**) |
| **Loaded graph (Stage 1 / 4 engine logs)** | **#entity 2,646 · #relation 6 · #triplet 6,084** |
| Full KG with BRG (reference, when `train1` participates in vocab/graph) | **#entity 16,844 · #relation 13** (e.g. withBRG Clean formal load — not the graph used in withoutBRG runs) |
| **symmetric** | **no** |
| **seed** | **1024** |
| **batch_size** | **32** |
| **num_negative** | **32** |
| **adversarial_temperature** | **0.5** |
| **epoch** | **8** |

---

## 3. Clean — full valid metrics (*n* = 608)

| AP | AUROC | Hits@1 | Hits@3 | Hits@10 | Hits@20 | Hits@50 | Hits@100 | MR | MRR |
|---:|------:|-------:|-------:|--------:|--------:|--------:|---------:|---:|----:|
| 0.883481 | 0.87732 | 0.087171 | 0.189145 | 0.364309 | 0.482730 | 0.652138 | 0.787007 | 87.4918 | 0.177524 |

*Source: Stage 2 eval log (`eval_valid_only.py`).*

---

## 4. Clean — full test metrics (*n* = 609)

| AP | AUROC | Hits@1 | Hits@3 | Hits@10 | Hits@20 | Hits@50 | Hits@100 | MR | MRR |
|---:|------:|-------:|-------:|--------:|--------:|--------:|---------:|---:|----:|
| 0.891054 | 0.885696 | 0.093596 | 0.200328 | 0.390805 | 0.505747 | 0.668309 | 0.781609 | 87.2718 | 0.183579 |

*Source: Stage 3 eval log.*

---

## 5. QRTC — full valid metrics (*n* = 608)

| AP | AUROC | Hits@1 | Hits@3 | Hits@10 | Hits@20 | Hits@50 | Hits@100 | MR | MRR |
|---:|------:|-------:|-------:|--------:|--------:|--------:|---------:|---:|----:|
| 0.883970 | 0.878079 | 0.101974 | 0.189967 | 0.375000 | 0.484375 | 0.652961 | 0.768914 | 86.7821 | 0.188492 |

*Source: Stage 5 eval log.*

---

## 6. QRTC — full test metrics (*n* = 609)

| AP | AUROC | Hits@1 | Hits@3 | Hits@10 | Hits@20 | Hits@50 | Hits@100 | MR | MRR |
|---:|------:|-------:|-------:|--------:|--------:|--------:|---------:|---:|----:|
| 0.894121 | 0.887355 | 0.089491 | 0.197865 | 0.384236 | 0.509031 | 0.660920 | 0.784072 | 86.2061 | 0.184451 |

*Source: Stage 6 eval log.*

---

## 7. Valid delta table — **Δ = QRTC − Clean**

Higher is better for AP, AUROC, Hits@*, MRR unless noted. **MR: lower is better** — a **negative Δ** means QRTC improved MR.

| Metric | Δ (QRTC − Clean) | Interpretation |
|--------|------------------|----------------|
| AP | **+0.000489** | QRTC higher |
| AUROC | **+0.000759** | QRTC higher |
| Hits@1 | **+0.014803** | QRTC higher |
| Hits@3 | **+0.000822** | QRTC higher |
| Hits@10 | **+0.010691** | QRTC higher |
| Hits@20 | **+0.001645** | QRTC higher |
| Hits@50 | **+0.000823** | QRTC higher |
| Hits@100 | **−0.018093** | QRTC **lower** |
| MR | **−0.7097** | QRTC **better** (MR↓) |
| MRR | **+0.010968** | QRTC higher |

---

## 8. Test delta table — **Δ = QRTC − Clean**

| Metric | Δ (QRTC − Clean) | Interpretation |
|--------|------------------|----------------|
| AP | **+0.003067** | QRTC higher |
| AUROC | **+0.001659** | QRTC higher |
| Hits@1 | **−0.004105** | QRTC **lower** |
| Hits@3 | **−0.002463** | QRTC **lower** |
| Hits@10 | **−0.006569** | QRTC **lower** |
| Hits@20 | **+0.003284** | QRTC higher |
| Hits@50 | **−0.007389** | QRTC **lower** |
| Hits@100 | **+0.002463** | QRTC higher |
| MR | **−1.0657** | QRTC **better** (MR↓) |
| MRR | **+0.000872** | QRTC higher |

---

## 9. Rank-pair diagnosis summary

**Scope:** Full filtered-rank dump on **609** test triples (1,218 rank-pairs); Δrank = QRTC − Clean (**negative** ⇒ better rank for QRTC).

| Level | Improved | Worsened | Unchanged |
|-------|----------|----------|-----------|
| **Pair-level** (tail ∪ head) | **526** | **456** | **236** |
| **Triple-level** (Δtail + Δhead net sign) | **306** | **276** | **27** |

**Head / tail breakdown**

- **Mean Δtail:** **−1.680** · **Mean Δhead:** **−0.455** (average rank improves under QRTC on both sides; tail magnitude larger).
- **Median Δtail / Δhead:** **0** / **0** (many ties; improvements are not universal).
- **Strict-improved fractions:** tail **42.2%** · head **44.2%** (remainder worsened or unchanged).
- **p99 |Δ|:** tail **~212** rank units vs head **~74** — **tail long-tail** dominates extreme moves.
- **Hit@1 / Hit@10 flip counts** (pair logic in merger): tail gains/losses and head gains/losses are **mixed** (see `rankpair_summary.json`).
- **Recomputed meta (dump):** aggregate **MR** and **MRR** favor QRTC; **MRR_head** slightly lower under QRTC vs Clean while **MRR_tail** rises — **head vs tail trade-off** on inverse-rank mean.

**Relation-level (mean Δtail, mean Δhead; sorted by effect size in diag)**

| relation_id | n_triples | Mean Δtail | Mean Δhead | Role |
|------------:|----------:|-----------:|-----------:|------|
| 5 | 7 | **−176.43** | **−18.14** | Largest **improver** (small *n*) |
| 3 | 47 | −0.30 | −6.26 | Strong **head** improvement on average |
| 2 | 28 | −1.04 | **+4.86** | **Tail better / head worse** pattern |
| 1 | 228 | **+4.04** | −0.75 | **Largest-*n* relation with mean tail **worse** under QRTC |
| 0 | 247 | −3.21 | +0.74 | Mixed |
| 4 | 52 | +2.48 | −0.06 | Mild tail worsening on average |

**Top worsener triples (largest positive Δtail+Δhead)** — examples from merger “top 10 positive MR pressure”: e.g. **idx 593** (*r*=1) **Δsum = +457** (QRTC much worse than Clean on that triple).

**MR/MRR trade-off:** Aggregate recomputed **MR** and **MRR** improve under QRTC vs Clean on this dump, but **strict top-* Hits** on **test** regress for several *k* — report as **metric inconsistency across cuts**, not as pure uplift.

---

## 10. Claim boundary

- State only what tables and rank-pair JSON support: **mixed** directional effects; **no** claim of “comprehensive improvement.”
- **Test:** AP/AUROC/MR/MRR largely favor QRTC; several **Hits@k** favor Clean — call this a **trade-off**, not uniform gain.
- **Valid:** Hits@100 favors Clean; other metrics favor QRTC — do not flatten into one headline.
- Do **not** tune or explain away regressions; **withoutBRG QRTC is not a silent win on every ranking cut.**

---

## 11. Asset paths

### Stage 0 preview

`/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/LNCTARDPPI_WITHOUTBRG_FORMAL_CONFIG_PREVIEW_STATUS_20260509.md`

### Clean withoutBRG

| Asset | Path |
|-------|------|
| Train config | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_clean_withoutbrg_formal_seed1024_20260509.yaml` |
| Train log | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/clean_withoutbrg_formal_seed1024_epoch8_20260509.log` |
| Checkpoint | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/clean_withoutbrg_formal_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-09-16-06-40-709140/model_epoch_8.pth` |
| Full-valid eval config | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_clean_withoutbrg_epoch8_fullvalid_20260509.yaml` |
| Full-test eval config | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_clean_withoutbrg_epoch8_fulltest_20260509.yaml` |
| Train status | `…/LNCTARDPPI_CLEAN_WITHOUTBRG_FORMAL_TRAIN_STATUS_20260509.md` |
| Full-valid status | `…/LNCTARDPPI_CLEAN_WITHOUTBRG_FORMAL_EPOCH8_FULLVALID_STATUS_20260509.md` |
| Full-test status | `…/LNCTARDPPI_CLEAN_WITHOUTBRG_FORMAL_EPOCH8_FULLTEST_STATUS_20260509.md` |

### QRTC-HR only withoutBRG

| Asset | Path |
|-------|------|
| Train config | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_qrtc_hronly_withoutbrg_formal_seed1024_20260509.yaml` |
| Train log | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/qrtc_hronly_withoutbrg_formal_seed1024_epoch8_20260509.log` |
| Checkpoint | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/qrtc_hronly_withoutbrg_formal_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-09-16-18-58-695278/model_epoch_8.pth` |
| Full-valid eval config | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_qrtc_hronly_withoutbrg_epoch8_fullvalid_20260509.yaml` |
| Full-test eval config | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_qrtc_hronly_withoutbrg_epoch8_fulltest_20260509.yaml` |
| Train status | `…/LNCTARDPPI_QRTC_HRONLY_WITHOUTBRG_FORMAL_TRAIN_STATUS_20260509.md` |
| Full-valid status | `…/LNCTARDPPI_QRTC_HRONLY_WITHOUTBRG_FORMAL_EPOCH8_FULLVALID_STATUS_20260509.md` |
| Full-test status | `…/LNCTARDPPI_QRTC_HRONLY_WITHOUTBRG_FORMAL_EPOCH8_FULLTEST_STATUS_20260509.md` |

### Rank-pair

| Asset | Path |
|-------|------|
| Output directory | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/lnctardppi_withoutbrg_fulltest_rankpair_diag_20260509` |
| Status card | `…/LNCTARDPPI_WITHOUTBRG_FULLTEST_RANKPAIR_DIAGNOSIS_STATUS_20260509.md` |
| Pipeline log | `…/logs/lnctardppi_withoutbrg_fulltest_rankpair_diag_20260509.log` |

### This summary

`/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/LNCTARDPPI_WITHOUTBRG_QRTC_HR_FULL_CLOSURE_SUMMARY_20260509.md`

---

## 12. Next recommended action

- **VERDICT is MIXED_POSITIVE:** proceed to **Paper 1 main table integration** with **explicit footnotes** on Hits@ trade-offs and relation-level heterogeneity.
- **Do not** auto-start RotatE, extra baselines, or multiseed sweeps unless separately approved.
- If future work focuses on **boundary evidence** only, treat this closure as **non-tuned** reference — **no** silent hyperparameter rescue.

---

## Appendix — quick reference (metrics & deltas)

**Clean valid:** AP 0.883481 · AUROC 0.87732 · Hits@1/3/10/20/50/100 0.0872 / 0.1891 / 0.3643 / 0.4827 / 0.6521 / 0.7870 · MR 87.49 · MRR 0.1775  

**Clean test:** AP 0.891054 · AUROC 0.885696 · Hits@1/3/10/20/50/100 0.0936 / 0.2003 / 0.3908 / 0.5057 / 0.6683 / 0.7816 · MR 87.27 · MRR 0.1836  

**QRTC valid:** AP 0.883970 · AUROC 0.878079 · Hits@1/3/10/20/50/100 0.1020 / 0.1900 / 0.3750 / 0.4844 / 0.6530 / 0.7689 · MR 86.78 · MRR 0.1885  

**QRTC test:** AP 0.894121 · AUROC 0.887355 · Hits@1/3/10/20/50/100 0.0895 / 0.1979 / 0.3842 / 0.5090 / 0.6609 / 0.7841 · MR 86.21 · MRR 0.1845  

**Δ valid:** MR **−0.71** (better) · MRR **+0.0110** · Hits@100 **−0.0181** (worse for QRTC)  

**Δ test:** MR **−1.07** (better) · MRR **+0.00087** · Hits@1 **−0.0041** (worse for QRTC)  

**Final VERDICT:** **MIXED_POSITIVE** (with documented **TRADEOFF** between Hits@* cuts and MR/AP/AUROC aggregates).
