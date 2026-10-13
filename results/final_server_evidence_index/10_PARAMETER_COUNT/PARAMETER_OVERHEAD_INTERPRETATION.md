# Parameter overhead (Phase D)

## Finding
Formal Clean Base and QRTC-HR checkpoints on the same graph share **identical total state_dict sizes** because the architecture always instantiates QRTC module tensors; `QRTC_ENABLE=0` disables their use but does not remove them from the checkpoint.

## Authoritative counts (PC KEGG wBRG, seed1024 epoch8)
| Variant | total | backbone | QRTC-module tensors |
|---------|------:|--------:|--------------------:|
| Base / QRTC / memory-off | 343,911 | 332,291 | 11,620 |

Relative module overhead vs backbone: **11,620 / 332,291 = +3.497%**.

### Formal-active vs stored-but-inactive QRTC tensors
Formal fused path uses: `qrtc_gate_mlp`, `qrtc_precedent_mlp`, `qrtc_init_memory`.
- Formal-active ≈ 5,314 params
- Stored inactive (cpacc_gate_mlp + qrtc_usage_mlp; unused on formal path) ≈ 6,306 params

### Naming correction (HARD)
Historical label `GATE_ONLY` / memory-off ablation MUST be reported as:
**memory-off gated/init variant** (gate + `qrtc_init_memory`; NOT pure gate-only).
No pure-gate causal interpretation.

### Capacity confound (CRITICAL risk remains)
Even with small absolute overhead, QRTC training optimizes additional modules vs Base; this is **not** a parameter-matched control. Do not claim capacity-matched superiority.

### LncTarD / woBRG sizes
Differ by entity/relation embedding table size (graph vocabulary), not by QRTC toggle:
- Lnc wBRG: 330,725 total (QRTC module 11,620)
- Lnc woBRG: 238,423
- PC woBRG Clean May08 archetype: 172,493 (May-02 QRTC live ckpt NOT_ON_DISK)
