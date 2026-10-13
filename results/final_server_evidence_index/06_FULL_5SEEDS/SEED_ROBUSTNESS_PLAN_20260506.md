# Seed / robustness plan — Q2

**Primary anchor:** seed **1024** — all formal withBRG Clean & QRTC-HR trains published to date.

---

## Gap

- **No multi-seed aggregation** exists for full valid/test metrics.
- Ranking deltas vs Clean (especially **Hits@1**) could shift materially under another initialization.

---

## Candidates

| Seed | Role |
|------|------|
| **1024** | Primary (frozen main table) |
| **2025** | Secondary draw — easy to remember |
| **3407** | ML-common alternate |

Pick **one** extra seed for Q2 unless budget allows two.

---

## Cost model (order of magnitude)

Each additional **full formal train** (8 epochs, batch16 neg512, withBRG):

- **GPU wall-clock:** ~**4–6 hours** historical band on large GPU for QRTC-HR train log window — treat as **~1 GPU-night** inclusive of jitter + compile.
- **Full valid:** ~**1–1.5 hours** (logged ~1h16 for Clean withBRG reference).
- **Full test:** ~**6–8 hours** wall-clock class observed for metrics-only heavy eval — **plan watchdog + logs**.

**Total per seed duplicate:** ~ **2 GPU-days** conservative if train+valid+test sequential.

---

## Minimum viable robustness

1. **withBRG QRTC-HR formal repeat** at **seed 2025** **only** (Clean optional if budget tight — but reviewer symmetry favors **both**).  
2. Report **mean ± spread** only if **≥2 seeds** complete matching protocol.

---

## Fallback if budget capped

- **Deterministic cap64 valid-only** for auxiliary seeds — **cannot replace** full-test claims but supports engineering sanity.
