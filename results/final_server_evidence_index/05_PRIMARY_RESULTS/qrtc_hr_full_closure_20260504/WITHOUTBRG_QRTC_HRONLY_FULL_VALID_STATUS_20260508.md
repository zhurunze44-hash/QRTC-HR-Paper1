# withoutBRG QRTC-HR-only — full valid — 2026-05-08

> **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`** — May-08 checkpoint eval artifact **only**. **Do not** cite metrics below as **final PC_KEGG QRTC** results. **Authoritative row:** `WITHOUTBRG_HIST_MAY02_QRTC_FULL_VALID_REEVAL_STATUS_20260508.md` + `PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md`.

## Status

**PASS** — `EXIT_CODE:0`, `VALID_ONLY_EVAL_DONE`.

## Env toggles (eval)

Same QRTC / anti-module set as train (`QRTC_ENABLE=1`, `QRTC_USE_MEMORY=1`, `QRTC_TOPK=2`; others 0).

## Paths

| Item | Path |
|------|------|
| Config | `withoutbrg_formal_rerun_20260507/config/qrtc_hronly_withoutbrg_eval_abs_ckpt_20260508.yaml` |
| Checkpoint | `withoutbrg_formal_rerun_20260507/qrtc_hronly_train_direct_20260508/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-08-13-35-27-655973/model_epoch_8.pth` |
| Log | `withoutbrg_formal_rerun_20260507/logs/qrtc_hronly_withoutbrg_full_valid_direct_20260508.log` |
| Launcher | `scripts/run_withoutbrg_qrtc_hronly_direct_eval_20260508.sh valid` |

## Timing

- **Evaluate on valid:** from log ~13:55:20 to metrics ~14:00:18  

## Metrics (full valid)

| Metric | Value |
|--------|------:|
| AP | 0.889313 |
| AUROC | 0.876478 |
| Hits@1 | 0.244035 |
| Hits@3 | 0.317323 |
| Hits@10 | 0.395414 |
| Hits@20 | 0.440502 |
| Hits@50 | 0.510846 |
| Hits@100 | 0.563991 |
| MR | 973.794 |
| MRR | 0.296707 |

## Interpretation (non-final prose)

vs **withoutBRG Clean valid**, QRTC-HR shows **lower** Hits@K / MRR / AP/AUROC and **much higher MR** on this split — report as **mixed / negative aggregate ranking on valid** for this run; pair-level diagnosis may still localize **where** shifts occur.

## Retention

**Retain.**

## Next

Full test, then rank-pair diagnosis.
