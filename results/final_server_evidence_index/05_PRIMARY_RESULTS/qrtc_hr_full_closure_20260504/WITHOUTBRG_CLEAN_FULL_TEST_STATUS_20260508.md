# withoutBRG Clean — full test — 2026-05-08

## Status

**PASS** — full test split (6438 triples), `EXIT_CODE:0`, `VALID_ONLY_EVAL_DONE`.

## Environment

- **Conda:** `biopathnet_py310_torch201`.

## Paths

| Item | Path |
|------|------|
| Config | `withoutbrg_formal_rerun_20260507/config/clean_withoutbrg_eval_abs_ckpt_20260508_020728.yaml` |
| Checkpoint | Same as valid (`model_epoch_8.pth` from Clean formal train 2026-05-08). |
| Log | `withoutbrg_formal_rerun_20260507/logs/clean_withoutbrg_full_test_direct_20260508.log` |
| Launcher | `scripts/run_withoutbrg_clean_direct_eval_20260508.sh test` |

## Timing

- **Start:** 2026-05-08T13:26:45+08:00  
- **End:** 2026-05-08T13:34:57+08:00  

## Exit / markers

- **Exit code:** 0  
- **EVAL_ONLY_SPLIT:** test  
- **VALID_ONLY_EVAL_DONE:** yes  

## Metrics (full test)

| Metric | Value |
|--------|------:|
| AP | 0.952662 |
| AUROC | 0.947710 |
| Hits@1 | 0.326033 |
| Hits@3 | 0.433054 |
| Hits@10 | 0.562908 |
| Hits@20 | 0.631796 |
| Hits@50 | 0.720954 |
| Hits@100 | 0.780833 |
| MR | 273.914 |
| MRR | 0.405033 |

## Retention

**Retain.**

## Next

**withoutBRG QRTC-HR formal train** (new output dir `qrtc_hronly_train_direct_20260508/`).
