# withoutBRG QRTC-HR-only — formal train (epoch 8, seed 1024) — 2026-05-08

## Status

**PASS** — `EXIT_CODE=0`; `model_epoch_8.pth` written.

## Environment

- **Conda:** `biopathnet_py310_torch201`.

## Env toggles (training)

| Variable | Value |
|----------|-------|
| QRTC_ENABLE | 1 |
| QRTC_USE_MEMORY | 1 |
| QRTC_TOPK | 2 |
| FAMILY_CTX_ENABLE | 0 |
| FAMILY_CTX_WSA_ENABLE | 0 |
| FAMILY_CTX_RISK_GATE_ENABLE | 0 |
| FAMILY_CTX_CAND_RISK_ENABLE | 0 |
| QAES_ENABLE | 0 |
| QAM_ENABLE | 0 |
| RICS_ENABLE | 0 |
| WSA_ENABLE | 0 |
| WSL_ENABLE | 0 |
| UAEP_ENABLE | 0 |
| QRDP_M2_ENABLE | 0 |
| QCES_ENABLE | 0 |

## Paths

| Item | Path |
|------|------|
| Config | `withoutbrg_formal_rerun_20260507/config/qrtc_hronly_withoutbrg_direct_train_20260508.yaml` |
| Output dir | `withoutbrg_formal_rerun_20260507/qrtc_hronly_train_direct_20260508/` |
| Checkpoint | `.../KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-08-13-35-27-655973/model_epoch_8.pth` |
| Log | `withoutbrg_formal_rerun_20260507/logs/qrtc_hronly_withoutbrg_direct_train_20260508.log` |
| Launcher | `scripts/run_withoutbrg_qrtc_hronly_direct_train_20260508.sh` |

## Train notes

- **smoke_skip_valid:** yes (no in-loop valid/test).  
- **Final epoch (8) avg BCE:** 0.603865  
- **Peak GPU memory (epoch 8):** 2766.8 MiB  

## Retention

**Retain** — do not overwrite; new directory distinct from Clean train.

## Next

Full valid / full test using eval config `qrtc_hronly_withoutbrg_eval_abs_ckpt_20260508.yaml`.
