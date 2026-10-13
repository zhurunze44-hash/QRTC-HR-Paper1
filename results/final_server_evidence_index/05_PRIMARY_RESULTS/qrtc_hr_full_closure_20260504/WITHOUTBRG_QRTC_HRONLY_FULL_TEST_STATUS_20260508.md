# withoutBRG QRTC-HR-only — full test — 2026-05-08

> **`BAD_RERUN_CHECKPOINT_NOT_FOR_TABLE`** — May-08 checkpoint eval artifact **only**. **Do not** cite metrics below as **final PC_KEGG QRTC** results. **Authoritative row:** `WITHOUTBRG_HIST_MAY02_QRTC_FULL_TEST_REEVAL_STATUS_20260508.md` + `PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md`.

## Status

**PASS** — `EXIT_CODE:0`, `VALID_ONLY_EVAL_DONE`.

## Paths

| Item | Path |
|------|------|
| Config | `withoutbrg_formal_rerun_20260507/config/qrtc_hronly_withoutbrg_eval_abs_ckpt_20260508.yaml` |
| Checkpoint | Same epoch-8 QRTC-HR-only ckpt as valid. |
| Log | `withoutbrg_formal_rerun_20260507/logs/qrtc_hronly_withoutbrg_full_test_direct_20260508.log` |
| Launcher | `scripts/run_withoutbrg_qrtc_hronly_direct_eval_20260508.sh test` |

## Timing

- Metrics timestamp ~14:09:41  

## Metrics (full test)

| Metric | Value |
|--------|------:|
| AP | 0.891110 |
| AUROC | 0.879970 |
| Hits@1 | 0.253728 |
| Hits@3 | 0.323082 |
| Hits@10 | 0.399736 |
| Hits@20 | 0.445325 |
| Hits@50 | 0.514834 |
| Hits@100 | 0.566480 |
| MR | 959.173 |
| MRR | 0.304778 |

## Retention

**Retain.**

## Next

**withoutBRG full-test rank-pair diagnosis** (`withoutbrg_fulltest_rankpair_diag_20260508/`).
