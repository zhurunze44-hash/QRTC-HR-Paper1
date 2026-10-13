# withoutBRG Clean — full valid — 2026-05-08

## Status

**PASS** — full valid split (3227 triples), `EXIT_CODE:0`, `VALID_ONLY_EVAL_DONE`.

## Environment

- **Conda:** `biopathnet_py310_torch201` (`biopathnet_py310_smoke` not installed).

## Paths

| Item | Path |
|------|------|
| Config | `withoutbrg_formal_rerun_20260507/config/clean_withoutbrg_eval_abs_ckpt_20260508_020728.yaml` |
| Checkpoint | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/withoutbrg_formal_rerun_20260507/clean_train_out/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-08-02-07-31-368798/model_epoch_8.pth` |
| Log | `withoutbrg_formal_rerun_20260507/logs/clean_withoutbrg_full_valid_direct_20260508.log` |
| Launcher | `scripts/run_withoutbrg_clean_direct_eval_20260508.sh valid` |

## Timing

- **Start:** 2026-05-08T13:21:17+08:00  
- **End:** 2026-05-08T13:25:50+08:00  

## Exit / markers

- **Exit code:** 0 (`EXIT_CODE:0` in log).  
- **VALID_ONLY_EVAL_DONE:** yes.

## Metrics (full valid)

| Metric | Value |
|--------|------:|
| AP | 0.951666 |
| AUROC | 0.945955 |
| Hits@1 | 0.313914 |
| Hits@3 | 0.417106 |
| Hits@10 | 0.549737 |
| Hits@20 | 0.616362 |
| Hits@50 | 0.713511 |
| Hits@100 | 0.778742 |
| MR | 279.247 |
| MRR | 0.391859 |

## Engineering fix (hang root cause)

Prior runs stalled after `Evaluate on valid` because PyTorch JIT extension compile locks under `~/.cache/torch_extensions/torch_ext/lock` survived a killed build; main thread waited in `FileBaton.wait`. **Resolution:** remove stale locks + `eval_valid_only.py` now clears default lock path and warms rspmm import (`EVAL_JIT_WARMUP`). Does **not** change ranking math.

## Retention

**Retain** — canonical withoutBRG Clean full valid for Paper 1 PC_KEGG withoutBRG track.

## Next

Run **withoutBRG Clean full test** (same checkpoint), then QRTC-HR train/eval.
