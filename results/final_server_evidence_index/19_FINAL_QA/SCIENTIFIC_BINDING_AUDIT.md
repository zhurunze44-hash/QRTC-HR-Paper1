# SCIENTIFIC_BINDING_AUDIT

| Item | Verdict |
|------|---------|
| formal source identified | PASS |
| formal config identified | PASS |
| formal checkpoint identified | PASS (except May-02 PC woBRG QRTC ckpt MISSING) |
| primary results bound | PASS |
| 5-seed provenance resolved | PASS (resolved as missing/not A1) |
| cross-dataset provenance resolved | PASS |
| query-level records found | PASS |
| bootstrap reproducible | PASS (query-level; CI close to historical, seed 20260509) |
| parameter count verified | PASS (totals identical; QRTC-module key-set vs CMPB 11620 differs) |
| runtime provenance verified | UNRESOLVED for manuscript full wall-clock; PASS for microbench |
| exact replay verified | UNRESOLVED live; PASS historical log vs table (ABS_DIFF 0) |
| split hashes verified | PASS |
| evaluator bound | PASS |
| LAST_CHANCE authority bound | PASS |
| A1 boundary resolved | PASS |
| no new training executed | PASS |

Overall: PASS with documented gaps (not STOP on core source/results; 5-seed formal panel absent).
