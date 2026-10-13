# PAPER1_RESULT_PROVENANCE_FINAL — Forensic Freeze

**UTC:** 2026-09-08T15:42:00Z  
**Status:** **FROZEN** — do not reinterpret as readout-only without a new binding case  
**Authority PDF:** `../00_submission_authority/QRTC_HR_SUBMITTED_MANUSCRIPT.pdf`  
**PDF SHA256:** `c568124e9b6ce72c596f2a06610763d855fe34335634c34b6ebd906073417993`  
**Local PDF binding:** `SUBMISSION_PDF_LOCAL_BINDING = PASS`

---

## Frozen status board

```
PAPER1_RESULT_PROVENANCE =
  PASS__TABLE_RESULTS_BOUND

PAPER1_CLAIM_AUDIT =
  CASE_B__HARD_READOUT_ONLY_CLAIM_CONFIRMED

PAPER1_IMPLEMENTATION =
  QRTC_MINIMAL_PATCH_V6
  MESSAGE_GATED_RELATION_CONDITIONED_REASONING
  TOPK=2

PAPER1_MANUSCRIPT_IMPLEMENTATION_CONSISTENCY =
  FAIL__SUBSTANTIVE_MISMATCH

PAPER1_ENVIRONMENT_CONSISTENCY =
  FAIL__MANUSCRIPT_ENVIRONMENT_MISMATCH

PAPER1_ENVIRONMENT_PROVENANCE =
  FAIL__MANUSCRIPT_ENVIRONMENT_MISMATCH

READOUT_ONLY_IMPLEMENTATION_WITH_MATCHING_TABLE_RESULTS =
  NOT_FOUND

PROVENANCE_METHOD_VERDICT (legacy / still valid) =
  FAIL__PAPER1_RESULTS_BOUND_TO_MESSAGE_GATED_IMPLEMENTATION

QRTC_RUNTIME_OPT2 =
  PAUSED__CASE_B_METHOD_MISMATCH

QRTC_HR_PAIRKG_IDENTITY =
  HOLD__PENDING_PAPER1_METHOD_RECONCILIATION

NBFNet_PAIRKG =
  AUTHORIZED

BioPathNet_PAIRKG =
  AUTHORIZED
```

---

## What each field means (frozen interpretation)

| Field | Meaning |
|-------|---------|
| `PASS__TABLE_RESULTS_BOUND` | Table II (and LncTarD companion) scalars bind to formal fused QRTC runs / ckpts / configs / logs. Numbers have asset support. |
| `CASE_B__HARD_READOUT_ONLY_CLAIM_CONFIRMED` | Submitted PDF repeatedly claims scoring-stage readout only + fixed propagation (abstract→methods→Fig.1). Case A revoked permanently for this PDF SHA. |
| `QRTC_MINIMAL_PATCH_V6` + message-gated | Result-generating algorithm: relation gate inside message passing + memory/state + hop routing; formal env `QRTC_ENABLE=1 USE_MEMORY=1 TOPK=2`. |
| `FAIL__SUBSTANTIVE_MISMATCH` | Manuscript algorithm ≠ result-generating algorithm. Controlled “identical propagation / same generated states” interpretation is **invalid**. |
| `FAIL__MANUSCRIPT_ENVIRONMENT_MISMATCH` | PDF claims PyTorch 2.8.0 / CUDA 12.8; formal runs bind to `biopathnet_py310_torch201` (PyTorch 2.0.1 lineage). **Separate** from method mismatch; does **not** invalidate Table binding. |
| `NOT_FOUND` | No readout-only / cand-readout-only lineage reproduces Table II. |
| Pair-KG HOLD on QRTC-HR | Name currently maps to two scientific objects; do not put empirical message-gated code into Pair-KG main table as “Paper-1 QRTC-HR transport” until Path A or B reconciles identity. |

---

## Explicit separations (do not collapse)

1. **Result numbers** — likely genuine / provenance-bound.  
2. **Algorithm description** — materially inaccurate vs execution.  
3. **Controlled readout-only interpretation** — invalid for current tables.  
4. **Environment description** — manuscript ≠ run env; independent FAIL.  
5. **Not alleged:** data fabrication / fake metrics. Do not escalate language that way.

---

## Binding fingerprint (Table II core; unchanged from audit)

| Setting | Clean MRR | QRTC MRR |
|---------|-----------|----------|
| PC-KEGG withBRG | 0.536298 | 0.550018 |
| PC-KEGG withoutBRG | 0.405033 | 0.419978 |

Full chain: `../03_PAPER1_RESULT_PROVENANCE_AUDIT/PAPER1_RESULT_PROVENANCE_AUDIT.md`  
Formal QRTC contract: `QRTC_ENABLE=1`, `QRTC_USE_MEMORY=1`, `QRTC_TOPK=2`, cand-readout off, fused DistMult message path (`QRTC_FORCE_MESSAGE_PATH=0`).

---

## Two scientific objects (must not be blurred)

**Manuscript QRTC-HR**

- Fixed BioPathNet-style propagation  
- Post-propagation Top-L readout + residual score  
- Claimed controlled comparison on same generated states  

**Empirical QRTC implementation (Table-bound)**

- Relation-conditioned gate inside message passing  
- Memory / state mechanism  
- Hop/state routing + scoring  
- Patch marker: `QRTC_MINIMAL_PATCH_V6`

---

## Reconciliation policy (frozen preference)

**Preferred Path A:** revise manuscript to describe the true message-gated method (when revision window allows). Keep assets; do **not** rewrite code to match old text.

**Path B:** implement true readout-only QRTC-HR and **retrain/reevaluate**. Current Table II–IV **cannot** support that new method.

Until Path A or B completes:

- Do not treat OPT/runtime work as repairing Paper-1 claims.  
- Do not enter QRTC-HR into Pair-KG formal main comparison as Paper-1 transport.  
- NBFNet / BioPathNet Pair-KG work may continue.

---

## Forbidden reinterpretations

- Reverting this freeze to HOLD / Case A because “maybe wording only.”  
- Claiming Table II proves a readout-only controlled experiment.  
- Changing formal code toward manuscript text to “save” the paper narrative.  
- Using environment mismatch to doubt Table binding, or using Table binding to ignore environment FAIL.
