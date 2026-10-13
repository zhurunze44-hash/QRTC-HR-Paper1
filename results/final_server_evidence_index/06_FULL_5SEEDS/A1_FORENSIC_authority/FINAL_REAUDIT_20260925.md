# Final re-audit checklist — 2026-09-25 (second full pass)

## Result

```
FINAL_REAUDIT = PASS__EXECUTION_CHAIN_HARDENED
TRAIN_LIVE = BASE_seed1024 (PID 641335) OK
WATCHER = waits for train-exit AND epoch8 before resume panel
EVAL = writable cwd; SOURCE_RESTORE import-only; WORK scrub
EXTRACT = exact keys; mr≠mrr; fail-closed
CONFIGS = 15/15 science-bound; data SHA OK; launcher SHA OK
AUTH_GUARD = fail-closed (false/True/1/unset → 78)
```

## Fixes applied this pass

1. **Watcher GPU race** — old watcher could start eval when `model_epoch_8.pth` appeared while train still held GPU. Now requires **train process exit + epoch8**.
2. **Cell eval race** — `run_a1_cell.sh` waits for train exit before eval; scrubs ambient QRTC env between cells.
3. **Metric extract** — exact key match (no `mrr`→`mr` bleed); JSON + log fallbacks; fail-closed.
4. **Eval metric dump** — robust to tensor / tuple keys.

## Intentionally unchanged (mid-panel freeze)

- seeds / methods / launchers / hparams / primary / t95 / proceed-stop
- SOURCE_RESTORE code
- A1_AUTHORIZED=true; A2/A3 false

## Design caveats (not execution blockers)

- `FEEDBACK_STATE_MODE` unread by code
- `MEMORY_ALPHA` noop on fused DistMult
- `GATE_ONLY` = gate + init_memory (not pure matched ablation)
- A1 ≠ feedback-state validity

Machine checklist: `FINAL_REAUDIT_CHECKLIST_20260925.json`
