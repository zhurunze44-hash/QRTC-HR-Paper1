# LAST_CHANCE_AUTHORITY_SUMMARY

Do **not** use `_QUARANTINE_*` receipts as authority (stale mixed / pre-repair).

## G0 PASS

- `receipts/G0_LIVE_RECEIPT.json`
- `receipts/G0_ASSET_LOCK_RECEIPT.json`
- `00_AUTHORITY/G0_AUTHORITY_LOCK.md`  
SHA256: see bundle copies under `16_LAST_CHANCE/`.

Closeout: G0 RAW replay PASS (LNC/PC); assets `LIVE_SHA_MATCH_SEALED`.

## G1 practical_signal=true

- `03_G1_INTERVENTION/G1_SUMMARY.json`  
LNC zero-update |ΔMRR| = **0.003561404759472429** (closeout: 0.0035614).

## G2 NOT_SELECTED

- `04_G2_DIAGNOSIS/G2_SUMMARY.json` / `CANDIDATE_FREEZE.json`  
scale-matched g*A ΔMRR = **-0.010520068313048952**.

## G3 SKIPPED_NOT_SELECTED

- `05_G3_CORRECTED/G3_SUMMARY.json`

## FINAL

`CLOSED__NO_INVESTMENT_SIGNAL__REPAIR_RERUN_VERIFIED`  
Source: `receipts/AUDIT_CLOSEOUT_FINAL_20261003.json` and `07_DECISION/CLOSEOUT.md`.

## INTEGRITY 35/35

**MISSING as a named 35-item checklist file.** Closeout `integrity_checks_pass` lists **7** bullets, not 35. This bundle does not fabricate a 35/35 receipt.

TRAINING_AUTHORIZED remains false. CMPB writing-only. A1 STOP unchanged.
