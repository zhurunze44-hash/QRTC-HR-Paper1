# LncTarD-PPI Clean withBRG — formal epoch8 full valid (2026-05-08)

**VERDICT=LNCTARDPPI_CLEAN_WITHBRG_FORMAL_EPOCH8_FULLVALID_PASS**

## Scope

- **Split:** valid only (`EVAL_ONLY_SPLIT=valid`, `script/eval_valid_only.py`).
- **Not run:** full test, QRTC, retrain.

## Config & checkpoint

| Item | Path |
|------|------|
| Eval YAML | `/root/autodl-tmp/BioPathNet_fresh/config/knowledge_graph/biomedical/lnctardppi_clean_withbrg_formal_epoch8_fullvalid_20260508.yaml` |
| Log | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/clean_withbrg_formal_epoch8_fullvalid_20260508.log` |
| Checkpoint | Clean **model_epoch_8.pth** (absolute path in log): `.../2026-05-08-16-03-58-170358/model_epoch_8.pth` |

## Full-valid checks

| Check | Result |
|--------|--------|
| `#valid` | **608** (log: `#train: 4867, #valid: 608, #test: 609`) |
| `Evaluate on valid` | **yes** |
| Cap / subset / smoke eval env | **no** `EVAL_VALID_CAP` / bounded-eval strings in log (normal `dataset.Subset` / Adam `capturable` appear in config dump only) |
| Errors | **no** Traceback / RuntimeError / OOM / AssertionError / killed / NaN |
| **EXIT_CODE** | **0** (log lines `EXIT_CODE:0`) |

## Valid metrics (log timestamp 17:21:14)

| Metric | Value |
|--------|-------|
| ap | 0.893819 |
| auroc | 0.881623 |
| hits@1 | 0.0953947 |
| hits@3 | 0.199836 |
| hits@10 | 0.370066 |
| hits@20 | 0.486842 |
| hits@50 | 0.657072 |
| hits@100 | 0.765625 |
| mr | 88.3586 |
| mrr | 0.184122 |

## Next

**Full test** is **not** run here. Proceed only after explicit approval and a separate eval-only config / `EVAL_ONLY_SPLIT=test` flow.
