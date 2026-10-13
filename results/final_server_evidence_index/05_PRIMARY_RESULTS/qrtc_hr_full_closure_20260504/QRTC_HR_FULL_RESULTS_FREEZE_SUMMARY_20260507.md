# QRTC-HR withBRG — full valid/test results freeze (2026-05-07)

## Freeze declaration

The numbers below are **frozen** as the project’s formal **single-seed (1024)** comparison of **Clean NBFNet withBRG** vs **QRTC-HR fused withBRG** on **PC_KEGG_0602**, **epoch 8** checkpoint, **full** validation and **full** test — **no retraining, no re-eval, no model-code edits** under this freeze ticket.

---

## Frozen scalars

### QRTC-HR full test

| AP | AUROC | Hits@1 | Hits@3 | Hits@10 | Hits@20 | Hits@50 | Hits@100 | MR | MRR |
|---:|------:|-------:|-------:|--------:|--------:|--------:|---------:|---:|----:|
| 0.986643 | 0.985724 | 0.460158 | 0.592498 | 0.730429 | 0.793103 | 0.866418 | 0.907891 | 126.234 | 0.550018 |

### QRTC-HR vs Clean (test Δ)

| ΔAP | ΔAUROC | ΔHits@1 | ΔHits@3 | ΔHits@10 | ΔMR | ΔMRR |
|----:|-------:|--------:|--------:|---------:|----:|-----:|
| −0.001973 | −0.001483 | +0.019183 | +0.012194 | +0.006058 | +5.166 | +0.013720 |

### Valid-side asymmetry (for interpretation only)

On **full valid**, QRTC-HR **reduces** MR (−3.279 vs Clean) while on **full test** MR **increases** (+5.166). Hits@K / MRR gains are present on **both** splits.

---

## Judgment tag

**Ranking-positive but mixed:** stronger **top-of-list** behavior (Hits@1–10, MRR) with **small** drops in **AP/AUROC** and **test MR** deterioration versus Clean.

---

## Paper-facing recommendation (short)

| Can claim | Cannot claim | Seeds | Follow-on paper angles |
|-----------|----------------|-------|-------------------------|
| Under frozen protocol, QRTC-HR improves **filtered ranking** emphasis metrics (**Hits@1–10**, **MRR**) vs Clean on **both** valid and test; AP/AUROC deltas are **small negative**. | Uniform superiority on **all** KG metrics; **tail MR** improvement on **test**; **causal** statements about biological mechanisms without separate bio validation. | **Single seed (1024)** — multi-seed variance **unknown**; recommend reporting seed explicitly and optionally adding ± across seeds in revision scope **outside** this freeze. | **Calibration / score-shift analysis** (AP/AUROC vs Hits), **risk** or **worst-case** analysis on **long-tail ranks**, and **rank-export pair diagnostics** as optional **Paper II** or appendix-grade material — **not** asserted here without exports. |

---

## Paths

| Document | Path |
|----------|------|
| **Main table** | `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/CLEAN_VS_QRTC_HR_FULL_VALID_TEST_MAIN_TABLE_20260507.md` |
| **Rank-pair diagnosis** | `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/QRTC_HR_RANK_PAIR_DIAGNOSIS_AGGREGATE_20260507.md` |
| This freeze summary | `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/QRTC_HR_FULL_RESULTS_FREEZE_SUMMARY_20260507.md` |
