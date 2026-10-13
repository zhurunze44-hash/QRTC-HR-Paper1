# A1_EXECUTION_CHAIN_ERRATUM_V1

**UTC freeze:** 2026-09-25T03:16:00Z  
**Status:** FROZEN  
**Adjudication:** operational repair after A1 start; scientific contract unchanged

```
A1_AUTHORIZED = true
A1_STATUS = RUNNING__EXECUTION_CHAIN_HARDENED
A1_SCIENTIFIC_CONTRACT_CHANGED = false
A1_EXECUTION_HARNESS_CHANGED = true
A1_EXECUTION_ERRATUM_REQUIRED = true  →  THIS DOCUMENT
```

---

## 1. Original authorized method launchers (unchanged; still authoritative for train env)

These hashes were independently adjudicated in `FOR_GPT_A1_EXECUTION_GUARD_PATCH_RETURN.zip`  
(SHA256 `76babe51db04c38d37fdbff3d1e1520c3243f7d19c3128f9642a38a99243e4df`).

| Launcher | SHA256 |
|----------|--------|
| `a1_launch_BASE.sh` | `500a220b937564e691c16a1699d07edb2dbff6179fd702863b566a4cd8563965` |
| `a1_launch_GATE_ONLY.sh` | `b45d10cd53dedc4b830088c38f8d8ee7e59f7a8003d1c97896f69c331a2474f0` |
| `a1_launch_RAW_QRTC.sh` | `d9857317207278b8daccaddf11729562ca20e0eec9ca69622d418fd59d0fcf1d` |

**Statement:** Method identity for training is still enforced exclusively by these three launchers  
(`A1_AUTHORIZED=true` fail-closed + QRTC_* disposition). They were **not** rewritten after authorization.

---

## 2. Why harness changed after A1 start (execution-layer only)

| Issue | Severity | Effect if unfixed |
|-------|----------|-------------------|
| Eval `chdir(SOURCE_RESTORE)` + write `working_dir.tmp` on mode-555 tree | P0 | All post-train evals fail |
| Live bash orchestrator script overwritten mid-wait | P0 | Panel may EOF-abort after first train |
| Watcher start-eval on epoch8 while train still holds GPU | P0 race | Eval/train GPU contention |
| Ambient QRTC env leakage across cells in parent shell | P1 | Method identity bleed risk |
| Metric extract `endswith("mr")` matching `mrr` | P1 | Corrupt MR receipt |

These are **orchestration / eval harness** defects, not changes to `run.py`, SOURCE_RESTORE, YAML science fields, seeds, or stats contract.

---

## 3. Explicitly unchanged scientific contract

```
seeds = [1024,1025,1026,1027,1028]
methods = [BASE, GATE_ONLY, RAW_QRTC]
model source = QRTC_HR_SOURCE_RESTORE_20260908
training YAML science fields = frozen (only dataset.path + output_dir rewritten)
optimizer / lr / epochs / negatives / temperature / batch size = unchanged
test dataset = PC_KEGG_0602 (SHA frozen)
evaluator API/semantics = load_dataset_and_solver(..., "test.txt") → evaluate("test")
statistical contract = paired MRR contrasts + mean/SD/t95(df=4) frozen pre-outcome
```

```
SCIENTIFIC_CONTRACT_CHANGED = false
```

---

## 4. New execution harness hashes (post-start operational repair)

Under `16_A1_QRTC_METHOD_PANEL_15RUN/scripts/` (as of this erratum):

| File | Role | SHA256 |
|------|------|--------|
| `run_a1_cell.sh` | per-cell train/eval/receipt; resume-safe; seals BASE1024 orphan | `50be8e49d5f4519edc5ff639c7d128b294ad650f946f5f7fb98ddc75686b7ff8` |
| `run_a1_panel_oneshot.sh` | 15-cell driver; skip complete receipts | `3c47de2c2d32e245a20cbefd3869b16c60e57a6846e9e180836ea7979e645f99` |
| `watch_train_then_resume_panel.sh` | wait train-exit + epoch8 + **log terminal markers** → driver | `1294003e7e6c2488317a84a458b1e3e32b4fcfc88a46eb4788ba6484422c8009` |
| `a1_eval_full_test_metrics_only.py` | SOURCE_RESTORE import; writable cwd eval | `d336b56230a7bc918d2d42a166fb4b27202e91fa643848d387d99a56e76cb037` |
| `extract_a1_metrics.py` | fail-closed metrics → receipt | `bc1b1c30081d81360d851564420123e7ac73b99405da6d9450882cf47a16bdf8` |
| `seal_base1024_orphan_lineage.sh` | seal orphan lineage after BASE1024 eval | `9d12eb75fdd65f3139712f89eb05189e3a1641c3983ff2dd4044f495ebca0c3c` |

Machine lock: `authority/HARNESS_HASH_LOCK.txt`

---

## 5. Old → new semantic diff (harness only)

| Component | Pre-start / initial | Hardened |
|-----------|---------------------|----------|
| Train launch | Bound `a1_launch_*.sh` | **Same** bound launchers |
| Panel loop | Monolithic `run_a1_panel_oneshot.sh` in-memory | External `run_a1_cell.sh` per cell (hot-fixable) |
| Eval cwd | Incorrectly assumed writable SOURCE_RESTORE | Panel writable cwd; SOURCE_RESTORE import-only |
| Eval code root | Risk of WORK contamination | Explicit SOURCE_RESTORE `__file__` refuse WORK |
| Post-train gate | epoch8 file alone | PID exit + epoch8 + **final log terminal markers** (`Save checkpoint to model_epoch_8.pth` + `skip immediate test() in run.py`) |
| Metrics | Log regex only | `A1_TEST_METRICS.json` + exact-key extract |
| BASE1024 shell exit | Normal subprocess code | `UNAVAILABLE__ORPHANED_AFTER_ORCHESTRATOR_TERMINATION` (honest) |

---

## 6. BASE_seed1024 special orphan lineage (do not fabricate exit 0)

```
ORIGINAL_TRAIN_PID = 641335
TRAIN_PROCESS_EXIT_CODE = UNAVAILABLE__ORPHANED_AFTER_ORCHESTRATOR_TERMINATION
CURRENT_CELL_ADMISSIBILITY = PENDING_TERMINAL_LINEAGE_RECEIPT
```

Terminal admissibility for this cell requires **all** of:

1. PID 641335 no longer alive  
2. `model_epoch_8.pth` exists  
3. checkpoint SHA256 recorded  
4. training log shows legitimate final-epoch completion markers  
5. no second `BASE_seed1024` training process existed  
6. source = SOURCE_RESTORE  
7. config SHA = frozen BASE YAML identity (science fields)  
8. QRTC env = BASE contract  
9. full-test eval completes once  
10. `A1_TEST_METRICS.json` complete + extract PASS  

Receipt path (to be written at completion):  
`receipts/BASE_seed1024_ORPHAN_LINEAGE_RECEIPT.json`

---

## 7. NEW_FORMAL_TRAINING_RUNS accounting

```
NEW_FORMAL_TRAINING_RUNS does NOT reset
BASE_seed1024 counts as the first formal A1 training cell
Do not hide / renumber / replace this run
```

---

## 8. Permanent scientific interpretation corrections

| Topic | Frozen wording |
|-------|----------------|
| A1 role | `A1 = QRTC METHOD PANEL` — **not** feedback-state validity |
| A3 role | `A3 = ORTHOGONAL FEEDBACK-STATE VALIDITY` (unauthorized) |
| `FEEDBACK_STATE_MODE` | `NONCONTROLLING_IN_SOURCE_RESTORE` (provenance only) |
| `MEMORY_ALPHA=0.35` | `BOUND_BUT_NONCONTROLLING_ON_FORMAL_FUSED_PATH` |
| Internal ID `GATE_ONLY` | Keep in receipts |
| Paper prose for GATE_ONLY | “Gate + learned initialization, without cross-layer memory update” — **not** “pure gate ablation” |

### Contrast meanings (frozen)

- **RAW − BASE** = full canonical QRTC vs backbone method effect  
- **GATE_ONLY − BASE** = gated + learned-init variant vs backbone (**capacity/topology caveat**)  
- **RAW − GATE_ONLY** = cross-layer precedent-memory update increment on shared gated/init architecture  

None of these prove feedback-state correctness.

---

## 9. Governance from this moment

**Allowed:** crash-safe resume; wait; log preservation; receipt generation; resource cleanup; fail-closed detection; this erratum.

**Forbidden without STOP + new adjudication:** change `run.py` / SOURCE_RESTORE / YAML science / QRTC semantics / seeds / epochs / eval metric / stats rules; silent hot-fix after further bugs; cherry-pick / rerun for aesthetics.

**If new exec bug:** `FAIL/STOP CELL → preserve evidence → adjudicate` — no silent continue.

```
A2_AUTHORIZED = false
A3_AUTHORIZED = false
NO_INTERIM_SCIENTIFIC_INTERPRETATION = true
```
