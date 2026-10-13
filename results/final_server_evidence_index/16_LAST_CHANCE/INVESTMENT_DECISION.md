# INVESTMENT_DECISION — LAST_CHANCE V1

**Runtime status:** `NO_INVESTMENT_SIGNAL`

**Execution counters:** new_training_run=0 · optimizer_step=0 · backward=0 · canonical_source_modified=False · diagnostic_overlay_modified=True · TEST_used_for_selection=False

**GPU wall used (this pass):** 413.0s / ceiling 3670.5s · peak_alloc≈8840 MiB

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
          "U_vs_gNA_max_abs": 85.880859375,
          "U_vs_gNA_max_rel": 0.0024248455595453416,
          "U_vs_factorU_max_abs": 85.8828125
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
          "U_vs_gNA_max_abs": 354.59375,
          "U_vs_gNA_max_rel": 0.002480998028865576,
          "U_vs_factorU_max_abs": 354.625,
          "id_usage_norm_mean": 264486.59375,
          "id_mem_nor
```

## Candidate freeze

```json
{
  "status": "SELECTED",
  "formula": "g*A",
  "zero_exposure_rule": "N=0 => A=0 => S=0",
  "applies_to_layers": "all layers after first usage write (natural forward)",
  "topk_fusion": "TopK on S; precedent attention uses S magnitudes; no separate softmax temperature",
  "scale_control": "direct factor product; no U/N division",
  "data_context_primary": "LNC_wBRG",
  "constraint_context": "PC_wBRG",
  "selection_reasons": [
    "N_static_across_traced_forwards",
    "correct_ga_delta_mrr_ge_0.002_on_design"
  ],
  "design_delta_mrr_mean": -0.007843413115314526
}
```

## G3 snapshot

```json
{
  "LNC": {
    "n": 357,
    "RAW": {
      "mrr": 0.21489810137828816,
      "hits@1": 0.12044817927170869,
      "hits@10": 0.4173669467787115,
      "n_triples": 357,
      "n_ranks": 714,
      "params_sha256_before": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
      "params_sha256_after": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
      "buffers_sha256_before": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
      "buffers_sha256_after": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
      "params_unchanged": true,
      "buffers_unchanged": true,
      "import_model_path": "<REDACTED_SERVER_PATH>",
      "ckpt_sha256": "8609cdc353964e6a59a0b696e7d136676873fcdeb97a51efa386f7fe3134829f",
      "n_indices": 357,
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
        "U_vs_factorU_max_abs": 0.0,
        "id_usage_norm_mean": 9387636.0,
        "id_mem_norm_mean": 5.602560997009277
      }
    },
    "BASE": {
      "mrr": 0.20700692769484022,
      "hits@1": 0.11064425770308123,
      "hits@10": 0.4117647058823529,
      "n_triples": 357,
      "n_ranks": 714,
      "params_sha256_before": "d12b2aa7db6ec893b1a633551c074c40446c3a15984160e2f085b89c2889dec4",
      "params_sha256_after": "d12b2aa7db6ec893b1a633551c074c40446c3a15984160e2f085b89c2889dec4",
      "buffers_sha256_before": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
      "buffers_sha256_after": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
      "params_unchanged": true,
      "buffers_unchanged": true,
      "import_model_path": "<REDACTED_SERVER_PATH>",
      "ckpt_sha256": "a29b0a0647fb8f4b5f3429fcdbf49dedbdec083fbc0a1c7ef5467dcec7707590",
      "n_indices": 357,
      "mode": "noop",
      "method": "BASE",
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
        "U_vs_factorU_max_abs": 0.0,
        "id_usage_norm_mean": 9387636.0,
        "id_mem_norm_mean": 5.602560997009277
      }
    },
    "CORRECTED": {
      "mrr": 0.21280910564876782,
      "hits@1": 0.11904761904761904,
      "hits@10": 0.4103641456582633,
      "n_triples": 357,
      "n_ranks": 714,
      "params_sha256_before": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
      "params_sha256_after": "8f1602da413b85b9c27f09e9cab231bde23a0fa656d8de62e7725cd37329fcd0",
      "buffers_sha256_before": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
      "buffers_sha256_after": "9ac536bb0229bb29125cb6d7e741aeeb915dd10b3c7ed35db5f9051678fe71cc",
      "params_unchanged": true,
      "buffers_unchanged": true,
      "import_model_path": "<REDACTED_SERVER_PATH>",
      "ckpt_sha256": "8609cdc353964e6a59a0b696e7d136676873fcdeb97a51efa386f7fe3134829f",
      "n_indices": 357,
      "mode": "correct_ga",
      "method": "RAW",
      "dataset": "LNC",
      "index_space": "valid_txt_line",
      "overlay_stats": {
        "mode": "correct_ga",
        "n_usage_rewrites": 144,
        "n_zero_update": 0,
        "n_identity_shuffle": 0,
        "n_trace": 0,
        "U_vs_gNA_max_abs": 177.71484375,
        "U_vs_gNA_max_rel": 0.0028778933177505657,
        "U_vs_factorU_max_abs": 177.71875,
        "id_usage_norm_mean": 9387636.0,
        "id_mem_norm_mean": 5.602560997009277
      }
    },
    "delta_corr_raw_mrr": -0.002088995729520343,
    "delta_corr_base_mrr": 0.005802177953927595,
    "delta_raw_base_mrr": 0.007891173683447938,
    "delta_hits1": -0.0014005602240896448,
    "delta_hits10": -0.00700280112044821,
    "bootstrap_delta_mrr": {
      "n_groups_as_triples": 357,
      "mean": -0.0020889957295205748,
      "ci95_low": -0.008351198509230355,
      "ci95_high": 0.004199476930958881
    }
  },
  "PC": {
    "n": 1530,
    "RAW": {
      "mrr": 0.537172369862012,
      "hits@1": 0.4470588235294118,
      "hits@10": 0.7264705882352941,
      "n_triples": 1530,
      "n_ranks": 3060,
      "params_sha256_before": "54b3ecf41660762305c37484c3fb422b1bca1eb5412c65ff6b7d1c0fa88da53a",
      "params_sha256_after": "54b3ecf41660762305c37484c3fb422b1bca1eb5412c65ff6b7d1c0fa88da53a",
      "buffers_sha256_before": "925f92559e4ecbf44a4f33bee85a78f56ec2eb45a8f8c5143b1c4a6c4c0e945d",
      "buffers_sha256_after": "925f92559e4ecbf44a4f3
```
