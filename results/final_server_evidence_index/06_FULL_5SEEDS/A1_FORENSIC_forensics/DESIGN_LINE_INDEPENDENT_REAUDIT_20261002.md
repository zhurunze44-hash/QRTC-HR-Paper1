# Design-line independent re-audit (post RAW1024 knife)

**UTC:** 2026-10-02T08:50:00Z  
**Stance:** defect-first; do not protect prior GPT narrative  
**GPU actions:** none

---

## Executive verdict

The **scientific object** A1 = `{BASE, GATE_ONLY, RAW_QRTC} × seeds{1024…1028}` with frozen launchers / SOURCE_RESTORE / epoch8 endpoint is **internally coherent as a method panel**.

But the **GPT-directed execution line** has real structural defects. Several already bit production (dual drivers, 3600s false FATAL, OOM storm). RAW1024’s ugly MRR is **not** evidence those defects invalidated the winning lineage — the lineage knife still passes — but they **are** evidence the harness was unsafe and needed repair before continuing the remaining 9 cells.

---

## What the GPT line got right

1. Bound method launchers with fail-closed `A1_AUTHORIZED` and explicit QRTC_* disposition.
2. Formal endpoint = `model_epoch_8.pth` + `smoke_skip_valid` (do not silently switch to best-valid / epoch5).
3. Result-blind lineage admissibility (do not INVALID a cell because MRR is ugly).
4. Guardian attach-waiter when panel dies but train lives (correct recovery class).
5. Eval harness repair (writable cwd; JSON metrics; fail-closed extract).

---

## What the GPT line got wrong (or overclaimed)

### P0 — Execution isolation was not actually enforced

- Panel singleton was PID-file only → dual drivers observed (`CELL_BEGIN` ×2 at identical UTC).
- Combined with cold-start retries into an occupied GPU → RAW1024 28× `OutOfMemoryError` before the one successful cold start.
- `wait_existing_train` hard-timeout 3600s ≪ healthy train wall (~5h) → false `FATAL` while trainer live (GATE1024 / RAW1024).

**Fixed in Erratum V2** (flock + stall-only wait + GPU occupancy gate).

### P1 — Mechanism / naming theater (scientific interpretation risk)

Already adjudicated 2026-09-25; still true:

| Protocol claim | SOURCE_RESTORE DistMult+PNA reality |
|----------------|--------------------------------------|
| `QRTC_FEEDBACK_STATE_MODE=canonical_raw` controls compute | **Never read** by Python |
| `QRTC_MEMORY_ALPHA=0.35` shapes gate on A1 path | **No-op** unless `edge_gate=True` (A1 fused path has `edge_gate=False`) |
| `GATE_ONLY` = pure matched-topology gate switch | **Gate + learned `qrtc_init_memory`** (extra params) |
| A1 proves “feedback-state validity” | **False** — A1 is method panel only; A3 still unauthorized |

These do **not** make BASE/GATE/RAW computationally identical under bound launchers (they remain distinct). They **do** forbid selling A1 as a clean feedback-state ablation.

### P1 — Comparison normality is OK for completed cells; panel is incomplete

| Seed | BASE | GATE | RAW | RAW−BASE |
|-----:|-----:|-----:|----:|---------:|
| 1024 | 0.545 | 0.548 | **0.195** | **−0.350** |
| 1025 | 0.549 | 0.547 | 0.546 | −0.003 |

- Contrasts use same dataset `PC_KEGG_0602`, same epoch8 endpoint, bound launchers → **comparison geometry is normal**.
- RAW1024 collapse co-travels with train BCE divergence (ep5 0.476 → ep8 0.559) while RAW1025/BASE/GATE stay ~0.475–0.478 → **not an eval/receipt bug**.
- Historical May-2026 formal RAW1024 MRR≈0.550 used a **different checkpoint** — validates eval stack, not this fresh A1 train.

### P2 — Operator / state hygiene

- Zombie locks claimed RUNNING after host reboot (cleared 2026-10-02).
- `HARNESS_HASH_LOCK` drifted from live scripts (relocked in Erratum V2).
- `STATE.json` `current_cell` fields were stale/conflicting.

---

## Is the design line itself “the problem” for RAW1024=0.195?

**No, not as lineage invalidity.**

Independent 8-check knife on winning workdir `2026-09-27-04-47-10-225368`:

| Check | Verdict |
|-------|---------|
| C1 fresh init | PASS |
| C2 exclusive writer (workdir) | PASS |
| C3 8-epoch continuous / no OOM in winner | PASS |
| C4 contract bind | PASS |
| C5 same lineage ep1–8 | PASS (PID probe weak; lineage unique) |
| C6 epoch8 not overwritten | PASS |
| C7 eval only this epoch8 | PASS |
| C8 no cherry-pick among metrics | PASS |

**Final:** `ADMISSIBLE__FRESH_COMPLETED_LINEAGE`  
Interim label before knife was correctly `HOLD__EXECUTION_CONTAMINATION_REQUIRES_LINEAGE_ADJUDICATION` — **not** immediate INVALID.

So 0.195 **must enter** the 5-seed primary panel. Do not invent rerun because it is ugly. Do not switch endpoint to epoch5.

**Yes, as program risk:** GPT line overstated mechanism identity and shipped an unsafe orchestrator. That raised execution-accident background and burned GPU on OOM retries — but the completed scientific lineage still stands.

---

## Mistaken-run checklist

| Hypothesis | Finding |
|------------|---------|
| Wrong dataset / split | Excluded (`PC_KEGG_0602`, counts match) |
| Eval loaded wrong ckpt | Excluded (receipt/eval log → winning epoch8 SHA) |
| Receipt bleed / `mr`/`mrr` regex | Excluded (JSON metrics path) |
| Resume from failed attempt weights | Excluded (0 `.pth` in 29 siblings; no Load checkpoint) |
| Cherry-pick among completed MRRs | Excluded (exactly one metrics JSON) |
| Mis-compare vs historical 0.55 | Different checkpoint generation — not a bug, but easy narrative trap |
| Dual-eval produced alternate score | Orphan eval dir `09-52-10` empty; one metrics file |

---

## What remains unauthorized

- GPU re-eval of epoch5/epoch8 for RAW1024
- BASE1026 resume (still `INTERRUPTED__HOST_REBOOT` until explicit policy)
- Restarting the 15-run panel without operator command
- Relabeling A1 as feedback-state validity / SCI2 upgrade decision based on two seeds alone

---

## Closeout of remaining hygiene (same UTC session)

| Item | Action |
|------|--------|
| Stale `PANEL_LIVE_STATUS.json` still `RUNNING` | Rewritten → `PAUSED__RAW1024_LINEAGE_ADJUDICATED__HARNESS_V2` |
| Stale `STATE.json` `a1_status` / conflicting `current_cell` | Rewritten to PAUSED; RAW1024 = ADMISSIBLE |
| `gpu_foreign_occupant_mib` ignored `self=` / did not exclude cell trainers | Fixed to exclude `train_pids`; hash lock + Erratum V2 table updated |
| Harness hash lock | All 7 scripts MATCH |

Panel remains paused. No GPU / no BASE1026 resume / no panel restart from this closeout.


---

## Final end-to-end pass (2026-10-02T09:00Z)

Additional defects found and fixed after the first Erratum V2 stamp:

1. **P0** Guardian `A1_PANEL_FLOCK` probe always false-held (FD0 vs FD7) → permanently blocked unattended restart — **fixed**.
2. **P1** Guardian stall-bounce during GPU/existing-train waits — **fixed** (phase-aware skip + log heartbeat).
3. **P1** `a1_train_shim.py` unlocked + path scrub missing — **fixed** (hash-locked + SOURCE_RESTORE scrub).
4. **P1** extract metrics panel-wide newest fallback (cross-cell poison) — **fixed** (cell-scoped + refuse).
5. **P2** over-broad `pgrep`, eval without GPU gate, waiter GLOG duplex — **fixed**.

Verification: 8/8 hash MATCH; flock probe OK; extract RAW1024 MRR OK; cross-cell REFUSE; SKIP_COMPLETE on completed cells; C1–C8 spot OK; panel remains PAUSED; no GPU train/eval launched.
