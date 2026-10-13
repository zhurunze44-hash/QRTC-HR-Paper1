# INVESTMENT_DECISION — LAST_CHANCE V1

**Runtime status:** `NO_INVESTMENT_SIGNAL`

**Execution counters:** new_training_run=0 · optimizer_step=0 · backward=0 · canonical_source_modified=False · diagnostic_overlay_modified=True · TEST_used_for_selection=False

**GPU wall used (this pass):** 82.8s / ceiling 3670.5s · peak_alloc≈8758 MiB

## What the evidence supports
- Within this budget, no unique intervenable factor cleared the pre-registered bar for further low-cost investment.
- This does **not** prove Paper1 / all feedback methods permanently infeasible.

## What it does not support
- No invented success probabilities.
- No TRAINING_AUTHORIZED.
- No inclusion of original A1 STOP panel as credit.

## Future training cells (report only)
```json
{
  "definition": "1 cell = 1 data context \u00d7 1 method \u00d7 1 seed",
  "explore_2cell_primary_only": "LNC \u00d7 {RAW, CORRECTED} \u00d7 1 seed = 2 cells (requires BASE already bound)",
  "two_task_raw_corr": 4,
  "two_task_raw_corr_3seed": 12,
  "two_task_base_raw_corr_3seed": 18,
  "two_task_base_raw_corr_5seed": 30,
  "historical_T_sec": 14682,
  "note": "G3 success does NOT set TRAINING_AUTHORIZED. A1 STOP panel cannot offset cells."
}
```

## G1 snapshot

```json
{
  "LNC": {
    "metrics": {
      "noop": {
        "mrr": 0.1853258858451314,
        "hits@1": 0.109375,
        "hits@10": 0.375,
        "n_triples": 64,
        "n_ranks": 128,
        "params_sha256_before": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
        "params_sha256_after": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
        "buffers_sha256_before": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
        "buffers_sha256_after": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
        "params_unchanged": true,
        "buffers_unchanged": true,
        "import_model_path": "<REDACTED_SERVER_PATH>",
        "ckpt_sha256": "8609cdc353964e6a59a0b696e7d136676873fcdeb97a51efa386f7fe3134829f",
        "n_indices": 64,
        "mode": "noop",
        "method": "RAW",
        "dataset": "LNC",
        "index_space": "valid_txt_line",
        "overlay_stats": {
          "mode": "noop",
          "n_usage_rewrites": 0,
          "n_zero_update": 0,
          "n_identity_shuffle": 0,
          "n_trace": 0,
          "U_vs_gNA_max_abs": 0.0,
          "U_vs_gNA_max_rel": 0.0,
          "U_vs_factorU_max_abs": 0.0
        }
      },
      "zero_update": {
        "mrr": 0.1888872906046038,
        "hits@1": 0.109375,
        "hits@10": 0.3671875,
        "n_triples": 64,
        "n_ranks": 128,
        "params_sha256_before": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
        "params_sha256_after": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
        "buffers_sha256_before": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
        "buffers_sha256_after": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
        "params_unchanged": true,
        "buffers_unchanged": true,
        "import_model_path": "<REDACTED_SERVER_PATH>",
        "ckpt_sha256": "8609cdc353964e6a59a0b696e7d136676873fcdeb97a51efa386f7fe3134829f",
        "n_indices": 64,
        "mode": "zero_update",
        "method": "RAW",
        "dataset": "LNC",
        "index_space": "valid_txt_line",
        "overlay_stats": {
          "mode": "zero_update",
          "n_usage_rewrites": 0,
          "n_zero_update": 20,
          "n_identity_shuffle": 0,
          "n_trace": 0,
          "U_vs_gNA_max_abs": 0.0,
          "U_vs_gNA_max_rel": 0.0,
          "U_vs_factorU_max_abs": 0.0
        }
      },
      "identity_control": {
        "mrr": 0.18462534696244817,
        "hits@1": 0.1015625,
        "hits@10": 0.375,
        "n_triples": 64,
        "n_ranks": 128,
        "params_sha256_before": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
        "params_sha256_after": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
        "buffers_sha256_before": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
        "buffers_sha256_after": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
        "params_unchanged": true,
        "buffers_unchanged": true,
        "import_model_path": "<REDACTED_SERVER_PATH>",
        "ckpt_sha256": "8609cdc353964e6a59a0b696e7d136676873fcdeb97a51efa386f7fe3134829f",
        "n_indices": 64,
        "mode": "identity_control",
        "method": "RAW",
        "dataset": "LNC",
        "index_space": "valid_txt_line",
        "overlay_stats": {
          "mode": "identity_control",
          "n_usage_rewrites": 0,
          "n_zero_update": 0,
          "n_identity_shuffle": 20,
          "n_trace": 0,
          "U_vs_gNA_max_abs": 0.0,
          "U_vs_gNA_max_rel": 0.0,
          "U_vs_factorU_max_abs": 0.0,
          "id_usage_norm_mean": 264486.78125,
          "id_mem_norm_mean": 4.824151039123535
        }
      }
    },
    "delt
```

## G2 snapshot

```json
{
  "U_eq_gNA_max_abs_mean": 99.04251797993977,
  "U_eq_gNA_max_abs_max": 328.84375,
  "U_eq_gNA_max_rel_mean": 0.0005949298210400974,
  "U_eq_gNA_max_rel_max": 0.002365661782550552,
  "U_eq_rtol": 0.005,
  "U_eq_checked_against": "formal_rel_usage_next_vs_reconstructed_gNA_relative",
  "trace_only_vs_noop": {
    "n": 64,
    "delta_mrr_mean": 0.0,
    "delta_mrr_median": 0.0,
    "frac_mrr_drop": 0.0,
    "frac_mrr_up": 0.0,
    "delta_rank_mean": 0.0,
    "delta_rel_score_mean": -2.3283064365386963e-10,
    "frac_rel_score_drop": 0.0078125,
    "n_rel_score": 128
  },
  "N_analysis": {
    "n_trace_rows": 24,
    "N_vector": [
      469203.0,
      144259.0,
      154868.0,
      3305.0,
      141554.0,
      114698.0,
      7246.0,
      2305.0,
      1530.0,
      272.0,
      366.0,
      351.0,
      43.0,
      469203.0,
      144259.0,
      154868.0,
      3305.0,
      141554.0,
      114698.0,
      7246.0,
      2305.0,
      1530.0,
      272.0,
      366.0,
      351.0,
      43.0
    ],
    "constant_across_traced_forwards": true
  },
  "probe_correct_ga_on_design": {
    "metrics": {
      "mrr": 0.17480581753208244,
      "hits@1": 0.0859375,
      "hits@10": 0.359375,
      "n_triples": 64,
      "n_ranks": 128,
      "params_sha256_before": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
      "params_sha256_after": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
      "buffers_sha256_before": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
      "buffers_sha256_after": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
      "params_unchanged": true,
      "buffers_unchanged": true,
      "import_model_path": "<REDACTED_SERVER_PATH>",
      "ckpt_sha256": "8609cdc353964e6a59a0b696e7d136676873fcdeb97a51efa386f7fe3134829f",
      "n_indices": 64,
      "mode": "correct_ga",
      "method": "RAW",
      "dataset": "LNC",
      "index_space": "valid_txt_line",
      "overlay_stats": {
        "mode": "correct_ga",
        "n_usage_rewrites": 24,
        "n_zero_update": 0,
        "n_identity_shuffle": 0,
        "n_trace": 0,
        "U_vs_gNA_max_abs": 206.21875,
        "U_vs_gNA_max_rel": 0.002388882867113835,
        "U_vs_factorU_max_abs": 206.21875,
        "correct_ga_scale_match": true
      }
    },
    "delta_vs_raw": {
      "n": 64,
      "delta_mrr_mean": -0.010520068313048952,
      "delta_mrr_median": 0.0,
      "frac_mrr_drop": 0.4375,
      "frac_mrr_up": 0.46875,
      "delta_rank_mean": -2.828125,
      "delta_rel_score_mean": 0.05226468702312559,
      "frac_rel_score_drop": 0.328125,
      "n_rel_score": 128
    },
    "raw_metrics": {
      "mrr": 0.1853258858451314,
      "hits@1": 0.109375,
      "hits@10": 0.375,
      "n_triples": 64,
      "n_ranks": 128,
      "params_sha256_before": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
      "params_sha256_after": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
      "buffers_sha256_before": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
      "buffers_sha256_after": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
      "params_unchanged": true,
      "buffers_unchanged": true,
      "import_model_path": "<REDACTED_SERVER_PATH>",
      "ckpt_sha256": "8609cdc353964e6a59a0b696e7d136676873fcdeb97a51efa386f7fe3134829f",
      "n_indices": 64,
      "mode": "noop",
      "method": "RAW",
      "dataset": "LNC",
      "index_space": "valid_txt_line",
      "overlay_stats": {
        "mode": "noop",
        "n_usage_rewrites": 0,
        "n_zero_update": 0,
        "n_identity_shuffle": 0,
        "n_trace": 0,
        "U_vs_gNA_max_abs": 0.0,
        "U_vs_gNA_max_rel": 0.0,
        "U_vs_factorU_max_abs": 0.0
      }
    },
    "scale_match": true
  },
  "probe_correct_ga_unscaled_
```

## Candidate freeze

```json
{
  "status": "NOT_SELECTED",
  "formula": null,
  "selection_reasons": [
    "N_static_across_traced_forwards",
    "correct_ga_scaled_hurts_design_mrr__not_repair_direction"
  ],
  "design_delta_mrr_mean": -0.010520068313048952,
  "design_delta_mrr_unscaled_diagnostic": -0.007843413115314526,
  "N_constant": true
}
```

## G3 snapshot

```json
{
  "status": "SKIPPED_NOT_SELECTED",
  "reason": "G2 did not freeze a repair-direction candidate; D_check not opened",
  "candidate_freeze": {
    "N_constant": true,
    "design_delta_mrr_mean": -0.010520068313048952,
    "design_delta_mrr_unscaled_diagnostic": -0.007843413115314526,
    "formula": null,
    "selection_reasons": [
      "N_static_across_traced_forwards",
      "correct_ga_scaled_hurts_design_mrr__not_repair_direction"
    ],
    "status": "NOT_SELECTED"
  },
  "written_utc": "2026-10-03T03:50:20Z",
  "note": "Backfilled after repaired re-run; G3 was correctly skipped by pipeline early-return."
}
```
