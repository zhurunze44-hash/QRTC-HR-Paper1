# LncTarD-PPI Clean withBRG — formal epoch8 full test (2026-05-08)

**VERDICT=LNCTARDPPI_CLEAN_WITHBRG_FORMAL_EPOCH8_FULLTEST_PASS**

## Paths

| Item | Path |
|------|------|
| Config | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_clean_withbrg_formal_epoch8_fulltest_20260508.yaml` |
| Log | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/clean_withbrg_formal_epoch8_fulltest_20260508.log` |
| Checkpoint | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/clean_withbrg_formal_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-08-16-03-58-170358/model_epoch_8.pth` |

## Run checks

| Check | Result |
|--------|--------|
| **#test** | **609** (log: `#train: 4867, #valid: 608, #test: 609`) |
| **Evaluate on test** | yes |
| **EXIT_CODE** | **0** |
| Traceback / RuntimeError / OOM / AssertionError / killed / NaN | none observed in log |
| cap / subset / smoke eval | not used (no EVAL_*_CAP; normal config strings only) |

## Test metrics (from log)

```
18:09:05   ap: 0.89895
18:09:05   auroc: 0.891295
18:09:05   hits@1: 0.0968801
18:09:05   hits@10: 0.385057
18:09:05   hits@100: 0.776683
18:09:05   hits@20: 0.510673
18:09:05   hits@3: 0.20197
18:09:05   hits@50: 0.664204
18:09:05   mr: 87.5673
18:09:05   mrr: 0.188326
```

## QRTC-HR withBRG config preview

**YES, WAITING_USER_APPROVAL** — do not start QRTC until you explicitly approve the next config/command.
