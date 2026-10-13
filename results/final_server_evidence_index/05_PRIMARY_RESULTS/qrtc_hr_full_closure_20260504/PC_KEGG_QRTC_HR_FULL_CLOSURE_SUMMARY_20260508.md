# PC_KEGG — QRTC-HR Paper 1 closure summary — 2026-05-08

**Scope:** Tables combine **frozen withBRG** references with **new withoutBRG** runs from this session. **RotatE withoutBRG** uses epoch-30 formal train as baseline (same recipe family as historical PC_KEGG RotatE configs).

**Conda used:** `biopathnet_py310_torch201`.

---

## 1. withBRG Clean vs QRTC-HR — full valid

(Source: `CLEAN_VS_QRTC_HR_FULL_VALID_TEST_MAIN_TABLE_20260507.md` §2 — frozen 2026-05-07.)

| Metric | Clean | QRTC-HR | Δ |
|--------|------:|--------:|--:|
| AP | 0.988077 | 0.987018 | −0.001059 |
| AUROC | 0.986829 | 0.985864 | −0.000965 |
| Hits@1 | 0.427022 | 0.445460 | +0.018438 |
| Hits@3 | 0.572358 | 0.579641 | +0.007283 |
| Hits@10 | 0.712581 | 0.720948 | +0.008367 |
| Hits@20 | 0.782770 | 0.788813 | +0.006043 |
| Hits@50 | 0.863960 | 0.864735 | +0.000775 |
| Hits@100 | 0.904865 | 0.905485 | +0.000620 |
| MR | 126.674 | 123.395 | −3.279 |
| MRR | 0.524037 | 0.536668 | +0.012631 |

---

## 2. withBRG Clean vs QRTC-HR — full test

(Source: same doc §3.)

| Metric | Clean | QRTC-HR | Δ |
|--------|------:|--------:|--:|
| AP | 0.988616 | 0.986643 | −0.001973 |
| AUROC | 0.987207 | 0.985724 | −0.001483 |
| Hits@1 | 0.440975 | 0.460158 | +0.019183 |
| Hits@3 | 0.580304 | 0.592498 | +0.012194 |
| Hits@10 | 0.724371 | 0.730429 | +0.006058 |
| Hits@20 | 0.793336 | 0.793103 | −0.000233 |
| Hits@50 | 0.866107 | 0.866418 | +0.000311 |
| Hits@100 | 0.908046 | 0.907891 | −0.000155 |
| MR | 121.068 | 126.234 | +5.166 |
| MRR | 0.536298 | 0.550018 | +0.013720 |

---

## 3. withoutBRG Clean vs QRTC-HR — full valid

**LOCKED (2026-05-08):** QRTC-HR column = **May-02 historical checkpoint**, **protected arbitration re-eval** — see `PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md`. **May-08** QRTC full-split numbers (`AP 0.889313`, `MR 973.794`, etc.) are **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`** — **not** this table.

**Clean:** `WITHOUTBRG_CLEAN_FULL_VALID_STATUS_20260508.md`. **QRTC:** `WITHOUTBRG_HIST_MAY02_QRTC_FULL_VALID_REEVAL_STATUS_20260508.md` / `hist_may02_qrtc_protected_full_valid_arbitration_20260508.log`.

| Metric | Clean | QRTC-HR | Δ |
|--------|------:|--------:|--:|
| AP | 0.951666 | 0.952 | +0.000334 |
| AUROC | 0.945955 | 0.948784 | +0.002829 |
| Hits@1 | 0.313914 | 0.328633 | +0.014719 |
| Hits@3 | 0.417106 | 0.435699 | +0.018593 |
| Hits@10 | 0.549737 | 0.559498 | +0.009761 |
| Hits@20 | 0.616362 | 0.626278 | +0.009916 |
| Hits@50 | 0.713511 | 0.724202 | +0.010691 |
| Hits@100 | 0.778742 | 0.787729 | +0.008987 |
| MR | 279.247 | 263.658 | −15.589 |
| MRR | 0.391859 | 0.406578 | +0.014719 |

---

## 4. withoutBRG Clean vs QRTC-HR — full test

**LOCKED:** same authority as §3. **QRTC:** `WITHOUTBRG_HIST_MAY02_QRTC_FULL_TEST_REEVAL_STATUS_20260508.md` / `hist_may02_qrtc_protected_full_test_arbitration_20260508.log`.

| Metric | Clean | QRTC-HR | Δ |
|--------|------:|--------:|--:|
| AP | 0.952662 | 0.952694 | +0.000032 |
| AUROC | 0.947710 | 0.949748 | +0.002038 |
| Hits@1 | 0.326033 | 0.341799 | +0.015766 |
| Hits@3 | 0.433054 | 0.448975 | +0.015921 |
| Hits@10 | 0.562908 | 0.574324 | +0.011416 |
| Hits@20 | 0.631796 | 0.640727 | +0.008931 |
| Hits@50 | 0.720954 | 0.728332 | +0.007378 |
| Hits@100 | 0.780833 | 0.789997 | +0.009164 |
| MR | 273.914 | 261.621 | −12.293 |
| MRR | 0.405033 | 0.419978 | +0.014945 |

---

## 5. RotatE baseline — withoutBRG (epoch 30)

| Split | AP | AUROC | Hits@1 | Hits@3 | Hits@10 | Hits@20 | Hits@50 | Hits@100 | MR | MRR |
|-------|---:|------:|-------:|-------:|--------:|--------:|--------:|---------:|---:|----:|
| Valid | 0.559524 | 0.500000 | 0 | 0 | 0 | 0 | 0.250 | 0.500 | 972.25 | 0.014098 |
| Test | 0.578835 | 0.590410 | 0.002951 | 0.009708 | 0.028114 | 0.056695 | 0.135989 | 0.242622 | 1457.70 | 0.016508 |

---

## 6. withBRG rank-pair diagnosis (reference)

Frozen artifacts under `rankpair_diag_fulltest_20260506/` — see `QRTC_HR_RANK_PAIR_DIAGNOSIS_AGGREGATE_20260507.md` and pipeline log. **Do not treat as withoutBRG.**

---

## 7. withoutBRG rank-pair diagnosis (this session)

Directory: `withoutbrg_fulltest_rankpair_diag_20260508/`.

**High-level:** Pair-level outcomes show **many more worsened than improved** ranks vs Clean; triple-level net worsening dominates (**5608** vs **727** improved). Mean Δrank is **slightly negative on tail** but **strongly positive on head** (mean Δhead ≈ **+1371**), driving MR degradation — consistent with aggregate MR/Hits regression above. Hit@1 / Hit@10 losses on **head** far exceed gains.

Full tables: `rankpair_summary.json`, `WITHOUTBRG_QRTC_HR_VS_CLEAN_FULLTEST_RANKPAIR_DIAGNOSIS_20260508.md`.

---

## 8. Final judgment (careful wording)

- **withBRG:** QRTC-HR shows **consistent gains** in Hits@1–10 and MRR on valid/test with **small AP/AUROC trade-offs**; **MR improves on valid but worsens on test** — not “uniform improvement.”
- **withoutBRG (this run):** Aggregate metrics show **QRTC-HR below Clean** on Hits@K, MRR, AP, AUROC, with **large MR increase**. Rank-pair diagnosis attributes much pressure to **head-side** rank degradation. **Do not claim broad retrieval improvement** for withoutBRG QRTC-HR from these numbers alone.
- **Mechanism prose:** The withoutBRG pattern is **not** the same as withBRG; **LncTarD-PPI** (second dataset) remains necessary before any cross-dataset generalization claim.

---

## 9. Engineering notes for reproducibility

- **JIT lock hang:** stale `/root/.cache/torch_extensions/torch_ext/lock` after interrupted compile; fixed via cleanup + `eval_valid_only.py` warmup (`EVAL_JIT_WARMUP` lines in log).
- **WORLD_SIZE:** eval scripts export `WORLD_SIZE=1` so Engine GPU count matches single-process launch.
