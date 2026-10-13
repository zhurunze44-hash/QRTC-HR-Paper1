# Paper 1 — Statistical evidence summary — 2026-05-09

## Scope

This note summarizes **read-only** per-query **rank-pair** analyses (mean rank, MRR, Hits@K transitions) with **sign tests** and **bootstrap 95% CIs** (5000 resamples, seed 1024). It does **not** re-derive or replace **global** AP, AUROC, or other metrics that come from full eval logs; those must stay in their own tables and must not be equated with paired-rank shift statistics.

## Input files (by block)

### A — PC_KEGG withoutBRG

- `qrtc_hr_full_closure_20260504/withoutbrg_fulltest_rankpair_diag_20260508/matched_rank_delta.tsv`
- `.../rankpair_summary.json`
- `.../clean_fulltest_filtered_rankpairs.tsv`, `.../qrtc_fulltest_filtered_rankpairs.tsv`
- `.../relation_mean_delta.tsv`
- `.../WITHOUTBRG_QRTC_HR_VS_CLEAN_FULLTEST_RANKPAIR_DIAGNOSIS_20260508.md`
- **Authority lock (QRTC table metrics, not automatically the same as this rank-pair dump):**  
  `PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md` (May-02 trusted vs May-08 bad-rerun ban)

### B — PC_KEGG withBRG

- `qrtc_hr_full_closure_20260504/rankpair_diag_fulltest_20260506/matched_rank_delta.tsv`
- `.../rankpair_summary.json`, filtered rank TSVs, `relation_mean_delta.tsv`, diagnosis MD in the same tree

### C — LncTarD-PPI withBRG

- `lnctardppi_qrtc_hr_full_closure_20260508/lnctardppi_withbrg_fulltest_rankpair_diag_20260509/matched_rank_delta.tsv`  
- (plus `rankpair_summary.json`, `relation_mean_delta.tsv`, filtered rank TSVs in that directory)

### D — LncTarD-PPI withoutBRG

- `lnctardppi_qrtc_hr_full_closure_20260508/lnctardppi_withoutbrg_fulltest_rankpair_diag_20260509/matched_rank_delta.tsv`  
- (plus companion JSON/TSV in the same directory)

**Parsing rule:** each triple row was split into **two pair rows** (tail-prediction rank and head-prediction rank), matching the `n_rank_pairs = 2 * n_triples` convention in `rankpair_summary.json`.

## Per-block: rank-pair found? and `n_pairs`

| Block | Rank-pair present | `n_pairs` (tail ∪ head) |
|-------|-------------------|-------------------------|
| A `PC_KEGG_withoutBRG` | Yes | **12876** (6438 triples × 2) |
| B `PC_KEGG_withBRG` | Yes | **12876** |
| C `LncTarD-PPI_withBRG` | Yes | **1218** (609 × 2) |
| D `LncTarD-PPI_withoutBRG` | Yes | **1218** |

## Primary statistical snapshots (from `paper1_rankpair_statistical_tests_20260509.tsv`)

| Block | Mean rank clean → QRTC | \(\Delta\)MR (QRTC−Clean) | \(\Delta\)MRR (QRTC−Clean) | Sign test \(p\) (discordant ranks) | Wilcoxon \(p\) on \(\Delta RR\) |
|-------|------------------------|---------------------------|----------------------------|--------------------------------------|--------------------------------|
| A | 273.91 → 959.17 | **+685.26** | **−0.100** | \(\ll 0.001\) (asymmetric toward worsening) | \(\ll 0.001\) |
| B | 121.07 → 126.23 | **+5.17** | **+0.0137** | **1.10×10⁻⁴** (more improvements than worsening among discordant) | **8.5×10⁻¹⁰** |
| C | 87.57 → 82.83 | **−4.74** | **−0.00903** | 0.051 (not significant at 0.05) | 0.46 |
| D | 87.27 → 86.20 | **−1.07** | **+0.00087** | **0.028** | 0.13 |

**Interpretation discipline:** sign tests address **symmetry of directional moves** among non-tied pairs; they are **not** biological validation. Wilcoxon tests differences in paired \(\Delta RR\) distribution.

## Bootstrap CI support (`paper1_rankpair_bootstrap_ci_20260509.tsv`)

Column **`ci_supports_positive`** uses the runbook convention: for **\(\Delta\)MR**, “positive QRTC effect” means **\(\Delta\)MR &lt; 0** (lower rank is better); for **\(\Delta\)MRR** and **\(\Delta\)Hits@K**, “positive” means CI entirely **above** 0.

### Block A

- **\(\Delta\)MR:** CI excludes improvement for QRTC (supports **no** gain; MR direction harmful here).  
- **\(\Delta\)MRR / all \(\Delta\)Hits@K:** CIs entirely **below** 0 → **no** bootstrap support for QRTC improvement on these paired metrics **for this dump**.

### Block B

- **\(\Delta\)MRR, \(\Delta\)Hits@1–10:** **yes** — bootstrap CIs strictly positive.  
- **\(\Delta\)MR:** **mixed** (interval crosses 0) → cannot claim mean-rank improvement from rank-pair alone.  
- **\(\Delta\)Hits@20, @50, @100:** **mixed** → headline Hits story should stay at **small–K** where CI supports movement.

### Block C

- **\(\Delta\)MR:** **yes** for negative \(\Delta\)MR (mean rank improves).  
- **\(\Delta\)MRR, all \(\Delta\)Hits@K:** **mixed or no** → no stable paired improvement story on reciprocal rank / Hits at most K in this slice.

### Block D

- **\(\Delta\)MR and all other metrics:** **mixed** at almost every K → weak paired evidence despite nominal sign-test \(p\) on discordant rank directions.

## Trade-offs evident from artifacts

1. **MR vs Hits / MRR (block B):** Paired mean rank **increases slightly** while MRR and Hits@1–10 gain—consistent with **mean-heavy tail sensitivity** already discussed in closure prose; do not flatten into “everything improves.”  
2. **Head vs tail (see side breakdown TSV):** On PC_KEGG withoutBRG, **head** ranks explode while **tail** rows look mildly improved—massive **side asymmetry** drives aggregate \(\Delta\)MR.  
3. **Checkpoint mismatch (block A):** Rank-pair path is tied to the **2026-05-08** eval wiring documented in the diagnosis card; **do not** narrate it as confirmation of **May-02** frozen-table superiority or failure.  
4. **Small-N dataset (C/D):** 609 triples → wide CIs on LncTarD; combine with qualitative caution.

## Effect on the main paper claim

- **withBRG PC_KEGG** remains the strongest **rank-pair–consistent** channel for **MRR / Hits@1–10** improvements with bootstrap backing, with explicit **MR / larger-K Hits** nuance.  
- **withoutBRG PC_KEGG rank-pair file** should appear—if at all—as a **diagnostic exhibit** with checkpoint caveats, **not** as the quantitative twin of the locked May-02 metrics card.  
- **LncTarD** supports **directionally mixed** statements only; do not mirror PC_KEGG strength.

## Recommendations on further experiments

| Topic | Guidance |
|-------|-----------|
| Baseline (RotatE, etc.) | Useful for related-work positioning; **not** demanded by these rank-pair \(p\)-values alone. |
| Ablation | Treat as mechanistic depth; schedule when a specific claim requires isolation—**not** because Wilcoxon is flat on block C. |
| Multiseed | Valuable for variance bounds; **lower priority** than tightening prose given small LncTarD \(n\) and frozen PC_KEGG story. |
| Writing | **Proceed**: freeze tables already carry AP/AUROC/MR/MRR; this package adds **paired-shift** language where aligned. |

**Chosen single recommendation:** prioritize **manuscript drafting** with the claim boundaries in `PAPER1_CLAIM_BOUNDARY_WITH_STATS_20260509.md`.
