# FIVE_SEED_SELECTION_AUDIT

## Formal Paper 1 (seed1024 Base / gated-init / QRTC)

Train YAMLs include `train.num_epoch: 8` and `smoke_skip_valid: yes` (QRTC fused withBRG formal YAML). Checkpoint used for tables is **`model_epoch_8.pth`**, i.e. last epoch, not a validation-selected best epoch.

| Question | Answer |
|----------|--------|
| Which round checkpoint? | epoch **8** (fixed) |
| Selected by validation metric? | **No** on formal train YAML (`smoke_skip_valid: yes`) |
| Base and QRTC same rule? | **Yes** (both epoch8 formal protocol) |
| Test-aware checkpoint swap? | **No evidence** of swapping after seeing test |
| Seeds excluded from formal 5-seed? | Formal 5-seed panel **does not exist** on disk |

**TEST_AWARE_SELECTION_DETECTED:** not found for formal seed1024 tables.

## A1 15-run panel (not Paper1 formal 5-seeds)

A1 aimed at BASE / GATE_ONLY / RAW_QRTC × seeds 1024–1028. Completions with test metrics receipts: 1024 and 1025 for all three methods. BASE seed1026 **INTERRUPTED__HOST_REBOOT**. 1027–1028 not completed.

A1 STOP reason is **runtime import provenance insufficient**, not because metrics were ugly (RAW1024 MRR 0.195 was ordered to remain if panel continued).

A1 checkpoint rule: see `A1_SEED_CONTRACT_AUDIT.md` in forensic copy. Do **not** promote A1 metrics to Paper1 tables.

**TEST_AWARE_SELECTION_DETECTED:** not used as the STOP reason. RAW1024 forensic explicitly forbade dropping the ugly seed.
