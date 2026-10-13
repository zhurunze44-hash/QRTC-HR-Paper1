# RAW_QRTC_seed1024 — Forensic Audit & Lineage Admissibility

**Audit UTC:** 2026-10-02  
**Independent re-verify UTC:** 2026-10-02 (second agent; on-disk only; C1–C8 reconfirmed)  
**Panel:** `16_A1_QRTC_METHOD_PANEL_15RUN`  
**Scope:** on-disk only (no GPU / no retrain / no re-eval)  
**Adjudication rule:** MRR / scientific quality **must not** enter lineage admissibility.  
**Process label path:** interim `HOLD__EXECUTION_CONTAMINATION_REQUIRES_LINEAGE_ADJUDICATION` → final `ADMISSIBLE__FRESH_COMPLETED_LINEAGE` (never jumped straight to INVALID).

---

## 0. Status labels (ordered)

| Stage | Label | Meaning |
|-------|-------|---------|
| Pre-audit observation | `RAW1024_RESULT = 0.1946338713169098` | Receipt fact only |
| Eval-path check | `EVAL_ERROR = HIGH_CONFIDENCE_EXCLUDED` | Wrong dataset / wrong ckpt / receipt bleed ruled out |
| Train dynamics | `TRAINING_DIVERGENCE = ESTABLISHED` | BCE explodes epoch 6–8 |
| Interim (before 8-item lineage knife) | `HOLD__EXECUTION_CONTAMINATION_REQUIRES_LINEAGE_ADJUDICATION` | Dual-orchestrator / 28×OOM background |
| **Final (after 8-item knife)** | **`ADMISSIBLE__FRESH_COMPLETED_LINEAGE`** | Winning scientific lineage is isolated & contract-bound |

**Not used:** `INVALID__EXECUTION_FAILURE` / `INVALID__EXECUTION_LINEAGE_NOT_ISOLATED`  
**Not needed:** `UNRESOLVED__LINEAGE_EVIDENCE_INSUFFICIENT`

Companion machine receipt: `RAW1024_LINEAGE_ADMISSIBILITY.json`.

---

## 1. Cell inventory (sealed)

| Field | Value |
|-------|-------|
| Method / seed | RAW_QRTC / 1024 |
| Winning working dir | `.../NBFNet/2026-09-27-04-47-10-225368` |
| Train start (CST) | 2026-09-27 04:47:10 |
| Train end (CST) | 2026-09-27 09:51:51 |
| Heartbeat PID | `train_pid=1384252` @ `20260926T204708Z` |
| Eval working dir | `.../RAW_QRTC_seed1024_eval/.../2026-09-27-09-52-13-067870` |
| Receipt MRR | 0.1946338713169098 |
| epoch8 SHA256 | `d4874222a223ba905a11adddc8293f295cef7a13a064fcd8d121eeb7100df58d` |

Failed siblings under parent `runs/RAW_QRTC_seed1024/.../NBFNet/`: **29** timestamp dirs with **only** `log.txt` (0 `.pth`).  
Formal test metrics files for this cell: **1**.

---

## 2. What was already established (pre-lineage)

### 2.1 EVAL_ERROR excluded (high confidence)

- Dataset path (train + eval): `<REDACTED_SERVER_PATH>
- Counts: `#entity=31410`, `#train=22702`, `#valid=3227`, `#test=6438`
- Eval loaded exactly winning `model_epoch_8.pth`
- Full metric suite collapsed together (MRR / Hits@1 / AP / AUROC) — not a single-key extract bug

### 2.2 TRAINING_DIVERGENCE established

Average BCE on winning lineage:

| Epoch | BCE |
|------:|----:|
| 1 | 0.49859 |
| 2 | 0.480004 |
| 3 | 0.477848 |
| 4 | 0.479541 |
| 5 | 0.475958 |
| **6** | **0.512467** |
| **7** | **0.560691** |
| **8** | **0.559262** |

Compare RAW1025 / BASE1024 finals ≈ 0.475–0.478.  
Checkpoint tensors: no NaN/Inf; architecture matches historical RAW1024 formal (117 tensors).  
ep5→ep8 RMS weight change ≈ 0.15 (real parameter movement, not a stale copy).

**Note:** divergence ≠ execution invalidity. A1 frozen endpoint remains epoch 8.

### 2.3 Execution accident background (does not auto-INVALID)

- 30 `TRAIN_ATTEMPT`, 28 `OutOfMemoryError` before the winning cold start
- Dual panel drivers (master log lines duplicated; `CELL_BEGIN RAW_QRTC_seed1024` ×32)
- OOM stacks show concurrent GPU occupant (~13.4 GiB) during the storm
- Panel driver declared `FATAL` @ `20260926T204723Z` while trainer was still live
- Guardian correctly: `GUARDIAN_ATTACH_TRAIN_WAITER (panel dead, train live — will resume panel after train exits)` then `RESUME_EVAL_ONLY` after epoch8 existed

---

## 3. Eight lineage admissibility checks

Adjudication unit = **winning TorchDrug working directory**  
`2026-09-27-04-47-10-225368`  
(not the parent `output_dir`, which is only a container for timestamped lineages).

### C1 — Independent fresh initialization (not resume from failed attempts)

**PASS**

- Attempt banner: `TRAIN_ATTEMPT ... done_epoch=0`
- Config: cold `configs/RAW_QRTC_seed1024_train.yaml` (no `RAW_QRTC_seed1024_train_RESUME.yaml` exists)
- Heartbeat: `latest=` empty at start
- Winning `log.txt`: **no** `Load checkpoint` / `Resume mode` / `A1_RESUME`
- All 29 failed siblings: **0** `.pth` files — nothing to resume from

### C2 — Winning output directory written only by this trainer

**PASS** (lineage dir)

- Winning dir contents: `log.txt` + `model_epoch_{1..8}.pth` only
- No second writer after train end: epoch8 `birth ≈ mtime ≈ ctime = 2026-09-27 09:51:51`
- Parent container has 29 failed sibling dirs; each is a **different** working dir and left no weights

### C3 — Winning trainer: 8 epochs continuous; no OOM / abnormal exit of that process

**PASS**

- Exactly 8 `Epoch N end` + 8 `Save checkpoint` in the entire train log; all inside the winning block
- Epoch spacing ≈ 38.00 min (ep1→ep8), matching healthy RAW cells
- Winning block contains **no** `OutOfMemoryError` / traceback
- Ends cleanly with `smoke_skip_valid` messages (no mid-run crash)
- Orchestrator FATAL / dual drivers are **around** the trainer; guardian waited for this live train

### C4 — source / YAML / seed / QRTC env match frozen contract

**PASS**

| Contract item | Observed |
|---------------|----------|
| Source | Launcher `exec` → `QRTC_HR_SOURCE_RESTORE_20260908/script/run.py` |
| YAML | `RAW_QRTC_seed1024_train.yaml` SHA `c30710d5...`; differs from seed1025 **only** by `output_dir` |
| Seed | `Input Seed: 1024` / `Set Seed: 1024` |
| Dataset | `PC_KEGG_0602` |
| Hparams | batch16, neg512, lr 5e-3, epoch8, smoke_skip_valid |
| QRTC env (logged) | `ENABLE=1 USE_MEMORY=1 TOPK=2 MEMORY_ALPHA=0.35 FEEDBACK_STATE_MODE=canonical_raw CAND_READOUT_ENABLE=0 ...` |
| Launcher SHA | `d9857317207278b8daccaddf11729562ca20e0eec9ca69622d418fd59d0fcf1d` (matches `run_a1_cell.sh` lock) |

### C5 — Checkpoints epoch1–8 same PID / lineage

**PASS** (lineage-unique; PID continuity inferred)

- Start PID recorded: `1384252`
- Panel died shortly after spawn → heartbeat was **not** updated per epoch (single line only)
- Proxy evidence that epoch1–8 are one lineage:
  - single working directory
  - continuous `log.txt` from 04:47→09:51 with no second `Working directory:` line
  - monotonic ~38 min save cadence
  - exclusive `.pth` set; inode sequence contiguous
- Residual: no OS-level mid-epoch PID re-probe. This does **not** create an alternate competing lineage.

### C6 — epoch8 not overwritten after train end

**PASS**

- `model_epoch_8.pth` birth/mtime/ctime all `2026-09-27 09:51:51`
- No files in winning dir newer than train end except later **access** times from this audit
- SHA256 stable: `d4874222a223ba905a11adddc8293f295cef7a13a064fcd8d121eeb7100df58d`

### C7 — Evaluator loaded only this epoch8

**PASS**

- Eval cfg + eval log + receipt all point to the same winning epoch8 path
- Dual `EVAL_BEGIN` (two drivers) both referenced **the same** ckpt
- Metrics produced once: `.../2026-09-27-09-52-13-067870/A1_TEST_METRICS.json`
- Sibling eval dir `2026-09-27-09-52-10-142624` is **empty** (no log, no metrics) — aborted; no alternate score

### C8 — Failed attempts died before formal test metrics; no cherry-pick

**PASS**

- Failed attempt logs end at `Epoch 0 begin` then OOM; zero train metrics, zero test metrics
- Pre-winning portion of train log: 0 hits for `A1_TEST_METRICS` / `mrr:` / `hits@1:`
- Exactly one formal receipt / one metrics JSON
- Selection was not “pick among completed MRRs”; only one completed scientific lineage exists

---

## 4. Final lineage verdict

```
ADMISSIBLE__FRESH_COMPLETED_LINEAGE
```

**Interpretation (result-blind):**

- Surrounding execution was contaminated (dual orchestrator, 28×OOM, panel FATAL while train live).
- The **completed scientific lineage** `04-47-10` is still an independent fresh cold start, contract-bound, continuously finished to epoch8, and uniquely evaluated.
- Therefore MRR=0.1946 **must enter** the 5-seed A1 primary panel as-is.
- Do **not** invent a rerun because the number is ugly.
- Do **not** switch endpoint to epoch5 even if epoch5 would look healthier.

---

## 5. Scientific context (NOT part of admissibility)

These notes are for Paper1 risk assessment only; they did not drive C1–C8.

| Seed | BASE | GATE | RAW | RAW−BASE |
|-----:|-----:|-----:|----:|---------:|
| 1024 | 0.545 | 0.548 | **0.195** | **−0.350** |
| 1025 | 0.549 | 0.547 | 0.546 | −0.003 |

If this admissible 0.195 stands, 1026–1028 would need ≈ **+0.118 MRR each** on average for 5-seed RAW−BASE mean > 0 — far above historical QRTC effect size.  
A1 “stable positive RAW vs BASE” is already under extreme pressure. Remaining cells still required for frozen panel closure; BASE1026 remains `INTERRUPTED__HOST_REBOOT` and should stay frozen until panel policy decides.

Historical formal replay MRR=0.550018 used a **different** May-2026 checkpoint, not this fresh A1 epoch8 — it validates the eval stack, not this training run.

---

## 6. Explicit non-actions from this audit

- No epoch5 / epoch8 GPU re-eval
- No BASE1026 resume
- No lock cleanup required for this decision (zombie locks noted separately)
- No deletion / quarantine of winning lineage artifacts

---

## 7. Sealed hashes (audit-time)

```
model_epoch_1  0c43b13822e7b0f78bd9df7dde954020956cd1e2a1ec8af7abd4a334efc23f8e
model_epoch_2  d920c9538ae08b36a953f3b22652c39f6f85bd8d147f34373fee8c181af1f4b9
model_epoch_3  abbd061df377d6a18b72b994b10f908432c09a51c7c0e753b333bb9bc125940c
model_epoch_4  8c6da3c1270a137641b3592202b76fb985da431659441ceac5b70001fc7954af
model_epoch_5  6346ef14cc92aebbafb4d524030441bd7db8b6bb8de362c120a78dd275650028
model_epoch_6  0616ecfd1e087763416efd607ea69cb4696114fd589cf3053a898bedcf9aca8f
model_epoch_7  d824146de4dcde4615b07a97421742455ebbfa0da6b52e3710ec9fa29da5098f
model_epoch_8  d4874222a223ba905a11adddc8293f295cef7a13a064fcd8d121eeb7100df58d
train_yaml     c30710d5a24f46045ab69a7fe240e9567aaf361c17ac7054d69eb2528e531179
launcher       d9857317207278b8daccaddf11729562ca20e0eec9ca69622d418fd59d0fcf1d
eval_py        d336b56230a7bc918d2d42a166fb4b27202e91fa643848d387d99a56e76cb037
receipt        653df876230cd7a1faca95f9c1553df42ace58d2e85d4707b549c56954c40683
metrics_json   75c47f4a12d1fd3f829c9c64df3b535cea6fbf0eaa62a093dc52161733f7efab
train1.txt     7eada252e712da7788f02a546e66dfa9ce3fb6f60be29af493de5b561f0d02e3
train2.txt     f6d20ef0e055091bf16e02451b3423bb9f6c6a51a6c1413d6b2bf3174548153f
valid.txt      41e111bc36fe68fa14b6d39a51b63b9cb17ab9998e607921a892ae01bf115259
test.txt       d002b54d454ee0344c53ec712079e7b93bc612f31409fa68b659ff47d6c11f48
```
