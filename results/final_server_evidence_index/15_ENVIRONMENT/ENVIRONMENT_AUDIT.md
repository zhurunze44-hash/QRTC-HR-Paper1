# ENVIRONMENT_AUDIT — A0.3

## Host

- hostname: nux208-Precision-3680
- GPU: NVIDIA GeForce RTX 4090
- Driver/CUDA (nvidia-smi): 580.159.03 / CUDA 13.0
- RAM: ~125 GiB

## Formal historical stack (Table-binding target)

- Conda env name (historical): `biopathnet_py310_torch201`
- PyTorch **2.8.0+cu128** / TorchDrug 0.2.1 / Python 3.10
- **ABSENT on this host** (confirmed Sep-15 + A0 re-check)

## A0 audit environment used

- `biopathnet_py310_smoke`: torch **2.0.1+cu118**, torchdrug 0.2.1
- Purpose: tensor-level factorization / instrumentation unit tests only
- **Not** authorized as formal Table replay stack

## Ruling

Live full-model checkpoint evaluation replay remains `NOT_EXECUTED` / `WHY_NOT_EXECUTABLE` under same formal-stack policy as Sep-15 reconciliation. A0 does not substitute smoke stack for scientific replay.
