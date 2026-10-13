# A1_ORIGINAL_FROZEN_CONTRACT_RECONSTRUCTED

Rebuilt from pre-outcome binding artifacts only (not from Oct-2 forensic narratives).

## Binding layers
- `11_A1_PREFLIGHT_BINDING_V1/` (authorized=false)
- `15_A1_EXECUTION_GUARD_PATCH_NO_TRAINING/` + launchers
- `16_A1_QRTC_METHOD_PANEL_15RUN/authority/A1_AUTHORIZATION.md` (GO 15-run)
- `A1_SCIENTIFIC_INTERPRETATION_FREEZE.md`
- `METHOD_LAUNCHER_ENV_CONTRACT.yaml`
- Stats rule / CONFIG+DATA+SOURCE identity freezes under preflight

## Panel
- Methods: BASE, GATE_ONLY, RAW_QRTC
- Seeds: 1024..1028 → 15 cells
- Role: QRTC METHOD PANEL (not feedback-state validity)
- Primary: paired MRR(RAW−BASE); t95 df=4 = 2.776445105
- Endpoint: model_epoch_8.pth + smoke_skip_valid
- Historical seed1024 checkpoints: reproduction reference only

## Method env
| | BASE | GATE_ONLY | RAW_QRTC |
|--|------|-----------|----------|
| QRTC_ENABLE | 0 | 1 | 1 |
| QRTC_USE_MEMORY | unset | 0 | 1 |
| QRTC_TOPK | unset | 2 | 2 |

## Noncontrolling under SOURCE_RESTORE DistMult fused path
- QRTC_FEEDBACK_STATE_MODE: unread
- QRTC_MEMORY_ALPHA: edge_gate path only; A1 edge_gate=false

## Train hparams
Adam lr=0.005, batch=16, negatives=512, epochs=8, dataset PC_KEGG_0602, single GPU.

## Forbidden
Outcome-driven seed/endpoint/metric selection; dropping ugly cells; mixing historical metrics into the 15-run panel; selling A1 as feedback-state proof.
