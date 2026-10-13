# withoutBRG — full test rank-pair diagnosis — 2026-05-08

## Status

**PASS** — pipeline completed; `n_triples=6438` for both variants; merge succeeded.

## Script / outputs

| Item | Path |
|------|------|
| Runner | `scripts/run_withoutbrg_fulltest_rankpair_20260508.sh` |
| Pipeline log | `withoutbrg_fulltest_rankpair_diag_20260508/full_pipeline_20260508.log` |
| Clean TSV | `withoutbrg_fulltest_rankpair_diag_20260508/clean_fulltest_filtered_rankpairs.tsv` |
| QRTC TSV | `withoutbrg_fulltest_rankpair_diag_20260508/qrtc_fulltest_filtered_rankpairs.tsv` |
| Delta TSV | `withoutbrg_fulltest_rankpair_diag_20260508/matched_rank_delta.tsv` |
| Relation table | `withoutbrg_fulltest_rankpair_diag_20260508/relation_mean_delta.tsv` |
| Summary JSON | `withoutbrg_fulltest_rankpair_diag_20260508/rankpair_summary.json` |
| Diagnosis MD | `withoutbrg_fulltest_rankpair_diag_20260508/WITHOUTBRG_QRTC_HR_VS_CLEAN_FULLTEST_RANKPAIR_DIAGNOSIS_20260508.md` |

## Config injection

Dump script extended with **`RANKPAIR_CFG_CLEAN`** / **`RANKPAIR_CFG_QRTC`** env vars (see `dump_fulltest_filtered_ranks_20260506.py`). This run pointed them at:

- Clean eval yaml: `clean_withoutbrg_eval_abs_ckpt_20260508_020728.yaml`  
- QRTC eval yaml: `qrtc_hronly_withoutbrg_eval_abs_ckpt_20260508.yaml`  

## headline numbers (from `rankpair_summary.json`)

- **n_triples:** 6438  
- **Pair-level (Δ = QRTC − Clean rank; tail ∪ head):** improved (Δ&lt;0) **2135**, worsened (Δ&gt;0) **7145**, unchanged **3596**  
- **Triple-level net (Δtail+Δhead):** net improved **727**, net worsened **5608**, unchanged **103**  
- **Mean Δrank:** tail **−0.48** (slight improvement on average), head **+1371** (large degradation on average) — MR trade-off concentrated on **head** side in this aggregate.  
- **Hit@1:** tail gain 209 / loss 225; head gain 90 / loss **1005**  
- **Hit@10:** tail gain 109 / loss 126; head gain 95 / loss **2179**  

## Patch rationale

Adding env-based YAML selection preserves existing **withBRG** default configs while enabling **withoutBRG** dumps without duplicating the merge logic.

## Retention

**Retain** — empirical diagnosis for withoutBRG Clean vs QRTC-HR on **same** 6438 test triples.

## Next

RotatE baseline status cards + PC_KEGG closure summary.
