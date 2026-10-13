# Independent line audit — A1 / feedback-state program
**UTC:** 2026-09-25T03:12:00Z  
**Scope:** design → code semantics → execution plumbing → live run  
**Stance:** defect-first; do not protect prior GPT narrative

---

## Executive verdict

The **scientific object “A1 = QRTC method panel (BASE / GATE_ONLY / RAW_QRTC × 5 seeds)”** is internally coherent and **not** a method-collapse bug under the bound launchers.

But the broader GPT-directed line has **real problems**:

1. **Mechanism theater** — several “frozen” knobs do not affect the DistMult fused path that actually produces Table/A1 numbers.
2. **Naming overclaim** — `GATE_ONLY` is not a pure matched-topology gate switch; `FEEDBACK_STATE_MODE=canonical_raw` is unread by code.
3. **Execution P0** — the first A1 eval path would have failed on every cell (read-only `SOURCE_RESTORE` + `chdir` + `working_dir.tmp`).
4. **Operator P0** — overwriting a live bash orchestrator mid-run risked panel abort after first train; mitigated by orphaning train + resume watcher.

**Do not interpret A1 as feedback-state validity.** That remains A3 (still unauthorized). A1 answers method-panel questions only.

---

## Findings

### P0 — Eval would fail on read-only SOURCE_RESTORE
**Was:** `a1_eval_full_test_metrics_only.py` did `os.chdir(SOURCE_RESTORE)` then `util.create_working_directory`, which writes `working_dir.tmp` in cwd. `SOURCE_RESTORE` is mode `555` → PermissionError after every successful train.

**Fix:** Eval keeps writable launch cwd (`A1_EVAL_LAUNCH_CWD=panel`); SOURCE_RESTORE is **import-only**; refuse WORK-tree imports; dump `A1_TEST_METRICS.json`.

### P0 — Live orchestrator script replaced mid-flight
**Was:** Updating `run_a1_panel_oneshot.sh` on disk while bash PID 641274 was mid-`wait` on train could cause EOF/mis-exec after train.

**Fix:** `kill -9` orchestrator only; train PID 641335 survived (reparented to init); `watch_train_then_resume_panel.sh` waits for `model_epoch_8.pth` then runs resume-capable driver (`run_a1_cell.sh` per cell).

### P1 — Design / labeling defects (not silent compute bugs)

| Claim in protocol | Reality in SOURCE_RESTORE DistMult+PNA |
|-------------------|----------------------------------------|
| `QRTC_FEEDBACK_STATE_MODE=canonical_raw` controls computation | **Never read** by Python |
| `QRTC_MEMORY_ALPHA=0.35` shapes gate | **No-op** on fused DistMult path (alpha only in QueryAware `edge_gate=True` path) |
| `GATE_ONLY` = gate increment vs BASE | **Gate + learned `qrtc_init_memory`**, extra trainable params; not matched-topology ablation |
| A1 proves feedback-state validity | **False** — A1 is method panel only |

### P1 — Env defaults are footguns (mitigated by bound launchers)
- `QRTC_USE_MEMORY` default `"1"` → forgetting `=0` turns GATE into RAW  
- `QRTC_TOPK` default `"4"` → forgetting `=2` changes RAW Top-L  
Live BASE train environ audited: `QRTC_ENABLE=0`, `USE_MEMORY`/`TOPK` absent — **correct**.

### P2 — Metric receipt fragility
Old inline regex against logs is brittle; fixed path writes JSON + `extract_a1_metrics.py` fail-closed if MRR missing.

### P2 — `LD_LIBRARY_PATH` still mentions CUDA 11.8
Same host condition under which formal env binding replay passed (torch 2.8.0+cu128). Not treated as blocker; do not retune mid-panel.

---

## What is *not* wrong

- BASE / GATE_ONLY / RAW are **computationally distinct** under bound env (no P0 method collapse).
- Formal endpoint `model_epoch_8.pth` with `smoke_skip_valid` is correct.
- SOURCE_RESTORE import for live BASE train is correct (not WORK/OPT patches).
- Data SHA for PC_KEGG_0602 matches freeze.
- Launcher SHAs match independent guard adjudication.
- Comparing RAW−BASE / GATE−BASE / RAW−GATE as **method panel contrasts** is fine **if labeled honestly**.

---

## Live state after repair

```
BASE_seed1024 train: RUNNING (orphaned, ppid=1)
Watcher: watch_train_then_resume_panel.sh → resume panel on epoch8
Eval: FIXED (writable cwd)
A1_AUTHORIZED: true (unchanged)
A2/A3: false
```

---

## Recommended interpretation going forward

1. Keep A1 as **QRTC method panel** only.  
2. In any paper/dissertation text: rename/describe GATE_ONLY as **relation-gate + init-memory (no Top-L precedent)**.  
3. Stop advertising `FEEDBACK_STATE_MODE` / fused-path `MEMORY_ALPHA` as active controls unless code is changed (out of A1 scope; do not change code mid-panel).  
4. After 15 receipts: completeness → paired analysis → independent `A1_PANEL_COMPLETE` — no cherry-picking.
