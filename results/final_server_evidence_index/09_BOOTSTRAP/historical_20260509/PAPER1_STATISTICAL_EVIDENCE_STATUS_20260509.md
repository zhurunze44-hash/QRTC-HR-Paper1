# Paper 1 — Statistical evidence run — status card — 2026-05-09

## VERDICT

**STATISTICAL_ARTIFACTS_COMPLETE_READ_ONLY** — Per-query rank-pair summaries, paired tests, and bootstrap confidence intervals were computed **only from existing** `matched_rank_delta.tsv` exports (plus bundled rankpair JSON/TSV where referenced). **No** training, evaluation dumps, RotatE/baseline/multiseed/ablation launches, or model-code edits were performed in this step.

## Read-only

**YES.** Inputs were read; outputs below were written under  
`/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/paper1_statistical_evidence_20260509`.

## GPU / compute tasks launched

**NO.**

## SciPy

**AVAILABLE** — `scipy.stats.binomtest` (two-sided sign test on discordant rank moves) and `scipy.stats.wilcoxon(..., zero_method="wilcox")` on paired \(\Delta\) reciprocal-rank were used.

## Merge safety

**MERGE_UNSAFE did not occur.** Each analyzed block had parseable `matched_rank_delta.tsv` with `rank_tail_*` / `rank_head_*` columns; pairs were expanded to **two rows per triple** (side `TAIL` / `HEAD`). No ad hoc joins between separate clean/qrtc exports were required.

## Rank-pair sources located

| Block | Role | Authoritative / chosen directory | Primary evidence files |
|-------|------|----------------------------------|-------------------------|
| **A** | PC_KEGG withoutBRG | `qrtc_hr_full_closure_20260504/withoutbrg_fulltest_rankpair_diag_20260508/` | `matched_rank_delta.tsv`, `rankpair_summary.json`, `clean_fulltest_filtered_rankpairs.tsv`, `qrtc_fulltest_filtered_rankpairs.tsv`, diagnosis MD |
| **B** | PC_KEGG withBRG | `qrtc_hr_full_closure_20260504/rankpair_diag_fulltest_20260506/` (**chosen** over ad hoc dated folders; aligns with closure freeze references—see note below) | same pattern |
| **C** | LncTarD-PPI withBRG | `lnctardppi_qrtc_hr_full_closure_20260508/lnctardppi_withbrg_fulltest_rankpair_diag_20260509/` | `matched_rank_delta.tsv`, `rankpair_summary.json`, filtered rank TSVs |
| **D** | LncTarD-PPI withoutBRG | `lnctardppi_qrtc_hr_full_closure_20260508/lnctardppi_withoutbrg_fulltest_rankpair_diag_20260509/` | same |

### Block B — candidate policy

Only one **full-test paired export tree** under `qrtc_hr_full_closure_20260504` matches **withBRG** rank-pair artifacts (`rankpair_diag_fulltest_20260506/` with `matched_rank_delta.tsv` + `rankpair_summary.json`). The separately dated **`withoutbrg_*`** directory applies to **withoutBRG**, not block B.

### Block A — authority alignment warning (critical)

Frozen **withoutBRG QRTC table metrics** are locked to **historical May-02 epoch-8** and protected arbitration re-eval per  
`PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md`.  
The **May-08 bad rerun checkpoint** is explicitly excluded from trusted tables.

The **rank-pair folder analyzed here for block A** was produced by the **2026-05-08** diagnosis pipeline, whose status card documents QRTC eval YAML  
`qrtc_hronly_withoutbrg_eval_abs_ckpt_20260508.yaml` — i.e. **not** the May-02 authoritative checkpoint path used for the frozen aggregate metrics card.

**Therefore:** block A **rank-pair statistics are empirical diagnostics for that dump only** and **must not** be interpreted as corroborating the May-02 locked AP/AUROC/MR/MRR numbers, nor as proving failure of the May-02 model. **Do not** blend AP/AUROC storylines with these rank-pair summaries.

## Outputs generated (this directory)

1. `PAPER1_STATISTICAL_EVIDENCE_STATUS_20260509.md` (this file)  
2. `paper1_rankpair_statistical_tests_20260509.tsv`  
3. `paper1_rankpair_bootstrap_ci_20260509.tsv`  
4. `paper1_rankpair_hit_transition_summary_20260509.tsv`  
5. `paper1_rankpair_side_breakdown_summary_20260509.tsv`  
6. `PAPER1_STATISTICAL_EVIDENCE_SUMMARY_20260509.md`  
7. `PAPER1_CLAIM_BOUNDARY_WITH_STATS_20260509.md`  

## Blocks missing rank-pair inputs

**None** — all four blocks had usable `matched_rank_delta.tsv`.

## Next-step suggestion (single recommendation)

**Draft the manuscript narrative first**, anchoring aggregate metrics to the existing **freeze / authority** packages and using rank-pair statistics only where checkpoint alignment is explicit and claims stay bounded (see summary + claim-boundary docs). Defer optional baseline / ablation / multiseed work unless a reviewer or internal audit demands it—do **not** react to non-significant \(p\)-values by retuning hyperparameters.
