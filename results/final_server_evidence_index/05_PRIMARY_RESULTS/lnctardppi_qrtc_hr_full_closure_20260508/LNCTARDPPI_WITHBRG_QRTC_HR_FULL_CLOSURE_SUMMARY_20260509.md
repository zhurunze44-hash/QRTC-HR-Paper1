# LncTarD-PPI withBRG — QRTC-HR formal closure summary — 2026-05-09

Formal **withBRG** baseline (**Clean**) vs **QRTC-HR-only** (all other modules off). No RotatE, no withoutBRG, no new methods in this closure.

## 1. Data & setup

| Item | Value |
|------|------:|
| train1 | 1,035,133 |
| train2 | 4,867 |
| valid | 608 |
| test | 609 |
| entity | 16,844 |
| relation | 13 |
| include_factgraph | **yes** |
| symmetric | **no** |

**Why symmetric=no:** LncTarD-PPI **strict negative** batching conflicts with **symmetric=yes** assertions in the biomedical completion path; resolved via dedicated smoke / assert-fix before formal runs (see `LNCTARDPPI_CLEAN_WITHBRG_ASSERTFIX_DIAG_AND_SMOKE_STATUS_20260508.md`).

**Eval data path (full evals):** `/root/autodl-tmp/BioPathNet_fresh/data/lnctardppi`

**QRTC train / eval contract:** `QRTC_ENABLE=1`, `QRTC_USE_MEMORY=1`, `QRTC_TOPK=2`; `FAMILY_CTX_*`, `QAES_ENABLE`, `QAM_ENABLE`, `RICS_ENABLE`, `WSA_ENABLE`, `WSL_ENABLE`, `UAEP_ENABLE`, `QRDP_M2_ENABLE` all **0** (see QRTC full-test log header).

## 2. Clean — full valid / full test (epoch 8)

| Metric | Valid | Test |
|--------|------:|-----:|
| AP | 0.893819 | 0.898950 |
| AUROC | 0.881623 | 0.891295 |
| Hits@1 | 0.095395 | 0.096880 |
| Hits@3 | 0.199836 | 0.201970 |
| Hits@10 | 0.370066 | 0.385057 |
| Hits@20 | 0.486842 | 0.510673 |
| Hits@50 | 0.657072 | 0.664204 |
| Hits@100 | 0.765625 | 0.776683 |
| MR | 88.3586 | 87.5673 |
| MRR | 0.184122 | 0.188326 |

*Sources:* `LNCTARDPPI_CLEAN_WITHBRG_FORMAL_EPOCH8_FULLVALID_STATUS_20260508.md`, `LNCTARDPPI_CLEAN_WITHBRG_FORMAL_EPOCH8_FULLTEST_STATUS_20260508.md`.

## 3. QRTC-HR only — full valid / full test (epoch 8)

| Metric | Valid | Test |
|--------|------:|-----:|
| AP | 0.894171 | 0.901080 |
| AUROC | 0.884695 | 0.894475 |
| Hits@1 | 0.100329 | 0.082923 |
| Hits@3 | 0.194901 | 0.192939 |
| Hits@10 | 0.369243 | 0.395731 |
| Hits@20 | 0.483553 | 0.514778 |
| Hits@50 | 0.657895 | 0.674877 |
| Hits@100 | 0.768914 | 0.784072 |
| MR | 86.3035 | 82.8292 |
| MRR | 0.187343 | 0.179300 |

*Sources:* `LNCTARDPPI_QRTC_HRONLY_WITHBRG_FORMAL_EPOCH8_FULLVALID_STATUS_20260508.md`, `LNCTARDPPI_QRTC_HRONLY_WITHBRG_FORMAL_EPOCH8_FULLTEST_STATUS_20260508.md` (and full-test log).

## 4. Valid: QRTC − Clean (Δ)

| Metric | Δ |
|--------|---:|
| AP | +0.000352 |
| AUROC | +0.003072 |
| Hits@1 | +0.004934 |
| Hits@3 | −0.004935 |
| Hits@10 | −0.000823 |
| Hits@20 | −0.003289 |
| Hits@50 | +0.000823 |
| Hits@100 | +0.003289 |
| MR | −2.0551 |
| MRR | +0.003221 |

## 5. Test: QRTC − Clean (Δ)

| Metric | Δ |
|--------|---:|
| AP | +0.002130 |
| AUROC | +0.003180 |
| Hits@1 | −0.013957 |
| Hits@3 | −0.009031 |
| Hits@10 | +0.010674 |
| Hits@20 | +0.004105 |
| Hits@50 | +0.010673 |
| Hits@100 | +0.007389 |
| MR | −4.7381 |
| MRR | −0.009026 |

## 6. Rank-pair diagnosis (full test, filtered, *n*=609)

*Directory:* `lnctardppi_withbrg_fulltest_rankpair_diag_20260509/`  
*Status:* `LNCTARDPPI_WITHBRG_FULLTEST_RANKPAIR_DIAGNOSIS_STATUS_20260509.md` (**PASS**)

**Pair-level (tail ∪ head, Δ = QRTC − Clean):** improved **555**, worsened **491**, unchanged **172**.

**Triple-level net (Δtail+Δhead):** net improved **323**, net worsened **261**, net unchanged **25**.

**Mean shifts:** mean Δtail **−9.67** (better tail ranks under QRTC on average); mean Δhead **+0.20** (slight head-side regression on average). Combined mean **−9.48** per triple — consistent with **lower test MR** for QRTC.

**Hit boundaries:** tail Hit@1 **8 gain / 21 loss**; head Hit@1 **14 gain / 18 loss** — aligns with **lower MRR / Hits@1** despite broad tail-rank improvements. Hit@10 **head** gains (**37 / 25**) align with higher **Hits@10–100**.

**Outliers:** largest positive combined Δ dominated by **tail** worsening on some relations (e.g. r=9) and **head-only** spikes; see `rankpair_summary.json` and `relation_mean_delta.tsv`.

## 7. Conclusion boundaries (paper-safe)

- **Not** a claim of **comprehensive** improvement: **MRR** and **Hits@1** **decrease** on **test** under QRTC vs Clean.
- **QRTC-HR changes front- and mid-rank retrieval** where metrics support it: **Hits@10/20/50/100** **increase** on **test**; **pair-level** rank moves show **555** improved vs **491** worsened (still mixed).
- **AP / AUROC** **increase** on **valid** and **test** — report as **gains in score-pair discrimination**, with **trade-off** vs **rank@1 / MRR** (calibration and tail mass differ from top-1 behavior).
- **MR** **decreases** (improves) on **valid** and **test** — **trade-off** with **MRR / Hits@1** is explicit; rank-pair attributes mean MR gain primarily to **tail** ranks, with **head** mean Δ near **zero** but **nonzero outlier** triples.

## 8. Review & traceability

- Full eval cross-check: `LNCTARDPPI_WITHBRG_FULL_EVAL_REVIEW_STATUS_20260509.md` (**VERDICT A** — Clean + QRTC train / full valid / full test confirmed).
- Rank-pair run log: `logs/lnctardppi_withbrg_fulltest_rankpair_diag_20260509.log`.
