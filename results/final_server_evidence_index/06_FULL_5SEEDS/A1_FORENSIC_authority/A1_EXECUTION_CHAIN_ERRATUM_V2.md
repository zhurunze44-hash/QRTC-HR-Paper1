# A1_EXECUTION_CHAIN_ERRATUM_V2

**UTC freeze:** 2026-10-02T08:50:00Z  
**Final repair stamp:** 2026-10-02T09:00:00Z  
**Status:** FROZEN  
**Adjudication:** operational repair after RAW1024 lineage knife; scientific contract unchanged

```
A1_AUTHORIZED = true
A1_SCIENTIFIC_CONTRACT_CHANGED = false
A1_EXECUTION_HARNESS_CHANGED = true
A1_EXECUTION_ERRATUM_REQUIRED = true  →  THIS DOCUMENT (supersedes V1 harness hashes only)
```

---

## 1. Why harness changed again (execution-layer only)

Discovered during RAW1024 independent re-audit (CPU/logs/hashes; no GPU):

| Issue | Severity | Historical effect | Fix |
|-------|----------|-------------------|-----|
| Dual panel drivers (PID lock race) | P0 | Concurrent `CELL_BEGIN` / cold starts → GPU contention / OOM storm | `flock` singleton on `A1_PANEL_FLOCK` |
| Multiple guardians | P0 | Cascading restarts | `flock` on `A1_GUARDIAN_FLOCK` |
| `wait_existing_train` hard wall = 3600s | P0 | Declared FATAL while healthy ~5h train still live | Stall-only abort; wait until exit or epoch8 |
| Pre-eval wait hard wall = 1200s | P1 | Same class of false FATAL | Stall-only |
| `logc` tee + panel redirect | P2 | Every cell log line duplicated → false “dual orchestrator” forensic noise | `logc` stdout-only |
| Cold start into occupied GPU | P1 | RAW1024: foreign ~13.4 GiB + self ~9.2 GiB → 28× OOM | Refuse/wait until foreign < 2 GiB |
| Stale zombie locks after host reboot | P2 | Panel claimed RUNNING while PIDs dead | Cleared 2026-10-02; status rewritten |
| `HARNESS_HASH_LOCK.txt` drifted from live scripts | P2 | Lock listed V1 hashes; live scripts already post-V1 | Relocked to current scripts |

### Final-pass residual defects (found & fixed same UTC)

| Issue | Severity | Fix |
|-------|----------|-----|
| Guardian panel-flock probe used `<file` → FD0, not FD7 → always “held” | P0 | `exec 7<>A1_PANEL_FLOCK` then `flock -n 7` |
| Guardian stall-bounce during GPU / existing-train wait | P1 | Skip bounce for `GPU_WAIT` / `WAIT_EXISTING_TRAIN` / `PAUSED*`; touch train_log + status during waits |
| `a1_train_shim.py` absent from hash lock | P1 | Added to lock; cell fail-closed SHA check before run |
| Shim did not scrub contaminated `sys.path` | P1 | Mirror eval scrub + SOURCE_RESTORE pin |
| `extract_a1_metrics` panel-wide newest JSON fallback | P1 | Cell-scoped only; refuse cross-cell pointer |
| `pgrep "${cell}_train"` over-match | P2 | Match `run.py`/`shim` + `-c …_train` only |
| No GPU gate before eval | P2 | Same foreign-GPU wait before eval |
| Waiter `log` double-wrote GLOG | P2 | Waiter uses echo → GLOG only |

**Not changed:** launchers, SOURCE_RESTORE, YAML science fields, seeds, methods, endpoint=`model_epoch_8.pth`, dataset, stats contract, RAW1024 admissibility.

---

## 2. New harness hashes (final)

Under `16_A1_QRTC_METHOD_PANEL_15RUN/scripts/`:

| File | SHA256 |
|------|--------|
| `a1_eval_full_test_metrics_only.py` | `d336b56230a7bc918d2d42a166fb4b27202e91fa643848d387d99a56e76cb037` (unchanged) |
| `extract_a1_metrics.py` | `d904cafced48b45194904d51711b7cd3779c15665964adb438543ec1e2cff2a3` |
| `run_a1_cell.sh` | `8a697abe44391e8d9fe22a86f5e716971611dcf31bf43d7beac120f67f30e8e6` |
| `run_a1_panel_oneshot.sh` | `bc4a324e8dc2b6edee5594aeec9ac5755c7f8e55f3278201ec10519758759f8f` |
| `seal_base1024_orphan_lineage.sh` | `9d12eb75fdd65f3139712f89eb05189e3a1641c3983ff2dd4044f495ebca0c3c` (unchanged) |
| `watch_train_then_resume_panel.sh` | `37d3726bab91220664d6dc83a98f113d7a3780bc5d76cd9f2a94fd42d9f8ee8c` |
| `a1_health_guardian.sh` | `fcb78a5bb7bffce0f13d9b123d07a84f169886044e5b1b9c3348d2b4f2ff5169` |
| `a1_train_shim.py` | `a1c8d9b4fbb6afed9883bdf9b22fd1c064dbcba0232f7b800e8358b2cf012727` (**now locked**) |

Machine lock: `authority/HARNESS_HASH_LOCK.txt`.

Method launchers (unchanged; still authoritative):

| Launcher | SHA256 |
|----------|--------|
| `a1_launch_BASE.sh` | `500a220b937564e691c16a1699d07edb2dbff6179fd702863b566a4cd8563965` |
| `a1_launch_GATE_ONLY.sh` | `b45d10cd53dedc4b830088c38f8d8ee7e59f7a8003d1c97896f69c331a2474f0` |
| `a1_launch_RAW_QRTC.sh` | `d9857317207278b8daccaddf11729562ca20e0eec9ca69622d418fd59d0fcf1d` |

---

## 3. Explicit non-actions

- No epoch5 / epoch8 GPU re-eval
- No BASE1026 resume in this erratum
- No deletion of RAW1024 winning lineage
- No change to RAW1024 admissibility (already knifed result-blind)
- No panel restart (operator must explicitly authorize)

---

## 4. Panel operational state after this erratum

```
A1_STATUS = PAUSED__RAW1024_LINEAGE_ADJUDICATED__HARNESS_V2
RAW_QRTC_seed1024 = ADMISSIBLE__FRESH_COMPLETED_LINEAGE (MRR 0.1946 enters primary)
resume_training = not_authorized_until_operator_explicitly_restarts_panel
```

### Verification stamps (final pass)

- 8/8 harness scripts MATCH lock (incl. shim)
- flock free-probe OK; old FD0 pattern fails as expected
- extract reproduces RAW1024 MRR; cross-cell pointer REFUSE
- `run_a1_cell.sh RAW_QRTC 1024` / `BASE 1024` → `SKIP_COMPLETE`
- C1–C8 spot check PASS; no A1 train/eval GPU jobs live
