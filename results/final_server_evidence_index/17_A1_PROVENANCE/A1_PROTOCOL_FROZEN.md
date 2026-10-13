# A1_PROTOCOL_FROZEN (not executed) — scientific role corrected 2026-09-24

**A1_AUTHORIZED = false**  
**A1_SCIENTIFIC_ROLE = QRTC_METHOD_PANEL** (NOT feedback-state validity)

## Goal

PC KEGG wBRG repeated-training **method panel** under canonical RAW feedback (`S=g·N·A`).

Does **not** adjudicate which factorized feedback state is valid — that is A3 only.

## Fixed seeds

1024, 1025, 1026, 1027, 1028  
(all 15 runs fresh under one formal environment; historical seed1024 = reproduction reference only)

## Fixed methods

| Method | Meaning |
|--------|---------|
| BASE | Clean NBFNet (`QRTC_ENABLE=0`) |
| GATE_ONLY | Gate on; memory update off; formal init (`USE_MEMORY=0`, `TOPK=2`) |
| RAW_QRTC | Canonical full QRTC (`USE_MEMORY=1`, `TOPK=2`, `FEEDBACK_STATE_MODE=canonical_raw`) |

## Paired contrasts (METHOD PANEL)

| Contrast | Meaning |
|----------|---------|
| RAW_QRTC − BASE | canonical full QRTC total method effect |
| GATE_ONLY − BASE | relation-gate increment |
| RAW_QRTC − GATE_ONLY | cross-layer memory beyond gate **under canonical gNA** |

A robust positive RAW−GATE result does **not** prove gNA is the correct feedback state.

## Train contract (historical PC KEGG formal)

epochs=8, batch_size=16, negative=512, adversarial_temperature=1.0, lr=0.005, Adam.  
All other parameters from authoritative config — do not invent.

## Endpoints

- PRIMARY: MRR  
- KEY SECONDARY: Hits@1, Hits@10, MR  
- AUX: AP, AUROC  

No TEST-driven selection of epoch/seed/metric/hyperparameter/run retention.  
Formal output = epoch-8 checkpoint.

## Source

A1 must import `QRTC_HR_SOURCE_RESTORE_20260908` only — never A3-patched worktree.
