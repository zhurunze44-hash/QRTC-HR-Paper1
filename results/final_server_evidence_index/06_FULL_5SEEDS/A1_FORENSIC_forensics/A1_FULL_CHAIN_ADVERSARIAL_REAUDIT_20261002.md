# A1 FULL CHAIN ADVERSARIAL RE-AUDIT
**UTC:** 2026-10-02T09:25:00Z  
**Stance:** treat prior ADMISSIBLE / “可续跑” conclusions as hypotheses, not authority  
**Constraints honored:** READ ONLY on science objects; GPU_TOUCHED=false; TRAINING_STARTED=false; only new files under `forensics/`

Companion artifacts:
- `FULL_CHAIN_REAUDIT_SNAPSHOT.json`
- `A1_FULL_CHAIN_ADVERSARIAL_REAUDIT.json`
- `A1_CELL_RUNTIME_PROVENANCE_MATRIX.csv`
- `A1_HARNESS_VERSION_MATRIX.csv`
- `A1_PRIOR_CLAIM_REAUDIT_TABLE.md`
- `A1_ORIGINAL_FROZEN_CONTRACT_RECONSTRUCTED.md` (section 1 below is the reconstruction)

Legend: **FACT** / **INFERENCE** / **NOT PROVEN**

---

## AUDIT 0 — Site freeze

| Item | Result |
|------|--------|
| Git roots (panel / base / paper1 / SOURCE_RESTORE) | **FACT:** none — no commit provenance |
| A1 trainers / panel / guardian | **FACT:** none live |
| GPU | **FACT:** only `gnome-remote-desktop-daemon` ~392 MiB |
| Authority / receipts / epoch8 / harness hashes | sealed in `FULL_CHAIN_REAUDIT_SNAPSHOT.json` |
| Files modified outside forensics | **FACT:** false (this audit) |

---

## AUDIT 1 — Original frozen scientific contract (reconstructed, pre-outcome)

Sources: `11_A1_PREFLIGHT_BINDING_V1`, `15_A1_EXECUTION_GUARD_PATCH_NO_TRAINING`, `A1_AUTHORIZATION.md`, `A1_SCIENTIFIC_INTERPRETATION_FREEZE.md`, `METHOD_LAUNCHER_ENV_CONTRACT.yaml`, launchers, configs (not from Oct-2 forensic summaries).

| Field | Frozen value |
|-------|----------------|
| Role | **QRTC METHOD PANEL** — not feedback-state validity (A3) |
| Methods | BASE, GATE_ONLY, RAW_QRTC |
| Seeds | 1024–1028 (15 cells) |
| Primary | paired MRR(RAW−BASE), mean + SD + t95(df=4)=2.776445105 |
| Mechanism | GATE−BASE, RAW−GATE |
| Endpoint | `model_epoch_8.pth`, `smoke_skip_valid` |
| Train | Adam lr=5e-3, batch16, neg512, epoch8, dataset `PC_KEGG_0602` |
| Source | `QRTC_HR_SOURCE_RESTORE_20260908` only |
| Forbidden | seed/endpoint/metric selection; drop bad seeds; outcome-driven rerun; mix historical metrics into panel |

**A. GATE_ONLY:** ENABLE=1, USE_MEMORY=0, TOPK=2 — “gate + learned init, memory update OFF”; **not** “pure matched-topology gate” (**FACT** freeze text).  
**B. RAW_QRTC:** ENABLE=1, USE_MEMORY=1, TOPK=2.  
**C. FEEDBACK_STATE_MODE:** **FACT** zero reads under SOURCE_RESTORE `*.py` → noncontrolling.  
**D. MEMORY_ALPHA:** **FACT** only on `edge_gate=True` QueryAware path; A1 YAML `edge_gate` default false → noncontrolling on fused DistMult.  
**E. Compute-affecting knobs:** ENABLE, USE_MEMORY, TOPK (when memory on), plus forced-off cand-readout / FORCE_MESSAGE_PATH=0.  
**F. A1 = method panel only.**  
**G. Historical seed1024 ckpt = reproduction reference only; fresh seed1024 is an A1 panel member.**

---

## AUDIT 2 — Historical RAW1024 vs A1 fresh RAW1024

| | Historical May-2026 | A1 fresh 2026-09-27-04-47-10 |
|--|---------------------|------------------------------|
| Epoch8 SHA | `e3fb9d65…` | `d4874222…` |
| Formal/replay MRR | 0.550018 | 0.1946338713169098 |
| YAML science | Adam 5e-3, ep8, bs16, neg512, DistMult+PNA | same |
| Seed | 1024 | 1024 |
| QRTC knobs | ENABLE/MEMORY/TOPK=2 | same (logged) |
| Dataset counts | 31410/22702/3227/6438 | same; split file SHA sealed |
| Torch | 2.8.0+cu128 family | 2.8.0+cu128 (panel start receipt) |
| Source tree SHA at *train time* | **NOT PROVEN** (no contemporaneous hash) | launcher `exec` absolute SOURCE_RESTORE `run.py`; OOM stacks show SOURCE_RESTORE `biopathnet/*` |

**HISTORICAL_VS_A1_TRAINING_CONTRACT = `SCIENTIFICALLY_EQUIVALENT_WITH_LISTED_OPERATIONAL_DIFFERENCES`**

Operational diffs: host/path, `TORCH_CUDA_ARCH_LIST`, env banner verbosity, independent retrain noise.  
**Forbidden phrasing:** “同 seed1024 从 0.55 训练成 0.195 证明优化不稳定” as a *same realization* claim.  
**Allowed:** two independent trains under a nominally shared science contract produced different outcomes; historical 0.550018 validates *eval stack on old weights*, not A1 fresh train.

---

## AUDIT 3 — RAW1024 winning lineage independence

**Timeline (FACT):** 30 `TRAIN_ATTEMPT`; 28 `OutOfMemoryError`; 29 sibling workdirs with **0** `.pth`; winning `2026-09-27-04-47-10-225368` has epochs 1–8; dual `CELL_BEGIN RAW_QRTC_seed1024` at identical UTC in master log; `FATAL … exceeded wait 3600s` class failures; guardian waiter attach.

| Claim | Verdict |
|-------|---------|
| Fresh init (no Load checkpoint) | **FACT** — winning log has 0 `Load checkpoint`; cold YAML; no RAW1024 RESUME yaml; code loads ckpt only if `cfg.checkpoint` set |
| No previous-attempt weights | **FACT** — siblings 0 `.pth` |
| Optimizer/scheduler fresh | **INFERENCE** from no checkpoint load |
| RNG fresh | **INFERENCE** — seeds set in `run.py` after cwd create; no cudnn deterministic |
| Exclusive workdir writer | **FACT** ep1–8 mtimes ~38min cadence; birth≈mtime epoch8 |
| Same process PID ep1–8 | **NOT PROVEN** OS-level (heartbeat single spawn line); lineage-unique workdir+log **FACT** |
| Other trainer on GPU during win | **NOT PROVEN** (no nvidia-smi time series); OOM storm *before* win strongly suggests contention then clearance |
| Hidden auto-resume / framework restore | **FACT** cold path: `bypass_auto_resume` when no cfg.checkpoint; winning config dump has no checkpoint key |

---

## AUDIT 4 — Shared science-state pollution

| Write class | Finding |
|-------------|---------|
| Dataset `PC_KEGG_0602` | **FACT** only 6 files; split mtimes 2026-04-28; **no** mtime in OOM window 2026-09-27 04:13–04:47 |
| `working_dir.tmp` | transient under panel cwd; world_size=1 uses local path var (**FACT** code); remove after create |
| TorchDrug workdirs | under per-attempt timestamp dirs |
| B-class shared cache read by winner | **NOT PROVEN**; no candidate B artifact found under dataset |

**Conclusion:** no demonstrated science-affecting shared state from 28 OOMs into winner. Residual: GPU driver/cudnn caches = class A.

---

## AUDIT 5 — Seed contract

`run.py` order (**FACT**): `create_working_directory` → then `random.seed` / `np.random.seed` / `torch.manual_seed` → dataset → solver.  
**Missing (**FACT**):** `torch.cuda.manual_seed_all`, `cudnn.deterministic`, `worker_init_fn` (`num_worker: 0` in engine dump mitigates workers), `PYTHONHASHSEED` binding.  
**Hardcoded (**FACT**):** `dataset.py` / `task.py` use `manual_seed(0)` / `np.random.seed(0)` in places — not the CLI seed.

**SEED_CONTRACT = `PARTIALLY_BOUND`**

Paired-seed BASE/GATE/RAW at same CLI seed: **partially** interpretable (shared CLI seed + same code path) but **not** a fully deterministic shared stochastic realization.

---

## AUDIT 6 — Method factor only?

| Cell | params (tensor) | qrtc tensors | init_memory in sd |
|------|-----------------|--------------|-------------------|
| BASE1024 | 343911 / 115 | 13 | yes |
| GATE1024 | 343911 / 115 | 13 | yes |
| RAW1024 | 343911 / 115 | 13 | yes |

**FACT:** identical parameter key sets across BASE/GATE/RAW1024 → **not** a param-count topology difference in saved state.  
**INFERENCE:** method factor is env-gated forward (ENABLE/USE_MEMORY/TOPK), not different `#params`.  
**GATE−BASE as “pure gate”:** **FALSE** per freeze; also not “extra params vs BASE” in this architecture. Correct label: gating + whether memory-update path runs + init_memory *use* in forward.  
**RAW−GATE as memory isolate:** **INFERENCE** supported by USE_MEMORY 1 vs 0 on shared module set — best available isolate under this code, not name-magic.

All 6 receipts: `metrics_source` under that cell’s `*_eval/` (**FACT** PASS — no cross-cell extract poison detected).

---

## AUDIT 7 — Harness V2 vs harness that ran the first 6

**FACT:** `run_a1_cell.sh`, `a1_train_shim.py`, `extract_a1_metrics.py`, `a1_health_guardian.sh` mtimes **2026-10-02** — after all completed cells.  
**FACT:** no git → cannot restore byte-level script SHA at each cell’s train time.  
**FACT:** launcher SHAs still match guard-patch pins; launchers unchanged.  
**FACT:** `run.py` uses `sys.path.append(SOURCE_RESTORE)` (not insert/scrub). Ambient earlier `biopathnet` would win — **current** env has no site-packages biopathnet; **historical PYTHONPATH** = **NOT PROVEN**.  
**FACT:** OOM stack traces resolve to SOURCE_RESTORE `biopathnet/{task,model,layer,qrtc_common}.py`.

Patch taxonomy: see `A1_HARNESS_VERSION_MATRIX.csv`. Most patches OPERATIONAL_ONLY.  
`shim_sys_path_scrub` and historical `extract` global-newest = **SCIENCE_AFFECTING_IF_…**; extract risk audited clear for existing receipts.

**Current 8/8 hash MATCH ≠ historical runtime equivalence.**

---

## AUDIT 8 — Can pre-6 + post-9 form one primary panel?

Required YES conditions cannot all be closed:

1. All diffs operational-only — **NOT PROVEN** (shim scrub class; unknown historical script bytes)  
2. Identical imported source — **PARTIALLY** (stacks + append-from-`__file__`; no `__file__` receipt; ambient path **NOT PROVEN**)  
3–6. configs/train/eval/metric semantics — **LIKELY** same launchers/YAML/endpoint; eval script mtime pre-dates cells  
7. no hidden shared-state difference — **LIKELY** for dataset; **NOT PROVEN** fully  
8. no method-specific patch interaction — **LIKELY**

**PRE_POST_PATCH_PANEL_COMPATIBILITY = `UNRESOLVED`**

Therefore: **do not authorize** remaining-9 resume as automatic continuation of the same frozen primary panel.

---

## AUDIT 9 — RAW1024 admissibility (independent; revised)

MRR not used for contract adjudication.

**Split (do not collapse):**

| Proposition | Verdict |
|-------------|---------|
| RAW1024_NUMERICAL_RESULT | **ESTABLISHED** (MRR 0.1946338713169098) |
| RAW1024_FRESH_LINEAGE | **ESTABLISHED** |
| RAW1024_WITHIN_RUN_LATE_TRAINING_DIVERGENCE | **ESTABLISHED** |
| **RAW1024_CONTRACT_ADMISSIBILITY** | **`HOLD__RUNTIME_SOURCE_IMPORT_PROVENANCE_REQUIRES_FINAL_BINDING`** |

**Withdrawn as premature:** `ADMISSIBLE__WITH_OPERATIONAL_INCIDENTS_NOT_AFFECTING_SCIENCE`

Why HOLD on contract (not INVALID, not ADMISSIBLE):
- Lineage/eval/ckpt hygiene ESTABLISHED — necessary, not sufficient for contract-admissibility
- Gate1: OOM stacks for this cell resolve only to SOURCE_RESTORE (`run/model/layer/task/qrtc_common`); **0** WORK/worktree paths; freeze SHA ≡ live; source mtimes May-2026
- But: winning quiet train has no `module.__file__` receipt; evidence is largely from **failed sibling attempts** under same launcher `exec`; `run.py` **appends** path (ambient earlier biopathnet would win); historical PYTHONPATH **NOT_PROVEN**
- Therefore cannot yet certify “this was the frozen QRTC implementation” at the standard required for primary-panel contract binding

If Gate1 later FULLY closes → upgrade to ADMISSIBLE__WITH_OPERATIONAL_INCIDENTS… and **keep 0.1946 in primary**.  
Never INVALID solely because MRR is ugly.

---

## AUDIT 10 — Divergence

| Layer | Verdict |
|-------|---------|
| WITHIN_RUN_LATE_TRAINING_DIVERGENCE (this lineage) | **ESTABLISHED** — BCE ep5≈0.476 → ep8≈0.559; multi-metric collapse |
| QRTC_OPTIMIZATION_INSTABILITY_GENERALIZED | **NOT_ESTABLISHED** — one admissible catastrophic seed ≠ method-wide law; historical 0.55≠same draw |

---

## AUDIT 11 — Can A1 still answer the reviewer?

**A1_DESIGN_VALIDITY = `VALID_WITH_LIMITATIONS`**

| Question | Answer |
|----------|--------|
| Multi-seed robustness? | Design yes; execution provenance incomplete → panel not closable yet |
| Full QRTC vs Base? | Yes if panel completes under comparable semantics |
| Cross-layer memory increment (RAW−GATE)? | Limited yes (env isolate); not pure causal proof |
| Pure gate effect? | **No** — freeze already forbids |
| Capacity confounding? | Param-count confounding **not** supported (identical sd keys); forward-path confounding remains |
| Catastrophic seed part of robustness? | **Yes** if admissible |
| t95 still pre-frozen primary? | **Yes** |
| Change statistic after seeing outcomes? | **NO** |

---

## AUDIT 12 — BASE1026

`model_epoch_3.pth` keys (**FACT**): `model`, `optimizer` only.  
No scheduler / scaler / RNG / dataloader state.

**BASE1026_RECOVERY_MODE = `POLICY_FRESH_RESTART_IF_PANEL_CONTINUES`**

- Exact bit-resume: **not** supported (missing RNG / dataloader chronology; AMP N/A)
- If original A1 is ever rescued: preserve `INTERRUPTED__HOST_REBOOT` lineage on disk + **fresh restart seed1026 from epoch0**
- Not outcome-driven: cell never produced formal test metrics

---

## AUDIT 13 — Prior claims

See `A1_PRIOR_CLAIM_REAUDIT_TABLE.md`.

---

## STOP/GO (no execution)

**A1_FULL_CHAIN_REAUDIT_TERMINAL = `HOLD__PROVENANCE_AND_PRE_POST_PATCH_COMPARABILITY_UNRESOLVED`**

See also: `A1_AUTHORITATIVE_STATUS_AFTER_ADVERSARIAL_REAUDIT.md`

Unresolved before any GPU:
1. **Gate1 FINAL binding** — elevate PARTIAL traceback evidence to FULL (or accept permanent insufficiency → route B)
2. **Gate2** — science-equivalence of pre/post harness without recoverable historical script bytes
3. **Gate3** — BASE1026 fresh-restart policy already recommended if panel continues
4. Operator choice: rescue original A1 vs STOP and optional post-hoc A1-R (not default-authorized)

```
A1_RESUME_AUTHORIZED = false
A2 = NOT_AUTHORIZED
A3 = NOT_AUTHORIZED
GPU = DO_NOT_TOUCH
```

### Erratum to prior adversarial pass
Prior label RAW1024 = ADMISSIBLE__WITH_OPERATIONAL_INCIDENTS… conflated lineage cleanliness with contract-bound implementation identity. Corrected 2026-10-02T09:35Z.