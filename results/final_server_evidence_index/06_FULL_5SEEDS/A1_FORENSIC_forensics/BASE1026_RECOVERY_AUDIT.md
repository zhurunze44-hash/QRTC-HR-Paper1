# BASE1026 Recovery Audit
UTC: 2026-10-02T09:40:43Z

Checkpoint path:
`runs/BASE_seed1026/.../2026-09-30-11-49-19-486498/model_epoch_3.pth`

## Contents (from prior CPU inspect; torch.load avoided this pass due to segfault risk)
| Field | Present |
|-------|---------|
| model | YES |
| optimizer | YES |
| scheduler | NO |
| GradScaler | NO |
| epoch / global_step top-level | NO |
| Python/NumPy/torch/CUDA RNG | NO |
| sampler / dataloader state | NO |

Top-level keys observed previously: `model`, `optimizer`.

## Verdict
**BASE1026_RECOVERY_MODE = FRESH_RESTART_FROM_EPOCH0_IF_PANEL_CONTINUES**

Preserve lineage as INTERRUPTED__HOST_REBOOT. Fresh restart is not outcome-driven (no formal test receipt). Not authorizing start.
