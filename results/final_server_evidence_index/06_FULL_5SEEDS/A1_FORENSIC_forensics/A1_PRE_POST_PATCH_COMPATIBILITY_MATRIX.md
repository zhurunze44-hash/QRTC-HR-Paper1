# A1 Pre/Post Patch Compatibility Matrix
UTC: 2026-10-02T09:40:20Z

| # | Dimension | Same for pre-6 vs future V2? | Evidence |
|---|-----------|------------------------------|----------|
| 1 | scientific source semantics | **UNRESOLVED→not YES** | Sep import only PARTIALLY_BOUND; V2 adds scrub |
| 2 | model architecture | LIKELY YES | same YAML/SOURCE_RESTORE freeze SHA |
| 3 | trainable parameter set | LIKELY YES | identical sd keys BASE/GATE/RAW |
| 4 | initialization semantics | LIKELY YES if same source | source binding incomplete |
| 5 | optimizer | YES | Adam 5e-3 frozen |
| 6 | LR/scheduler | YES | None scheduler |
| 7 | dataset splits | YES | PC_KEGG_0602 SHA sealed |
| 8 | batching | YES | batch 16 |
| 9 | negatives | YES | 512 |
| 10 | epoch endpoint | YES | epoch8 + smoke_skip_valid |
| 11 | evaluation implementation | LIKELY YES | eval py SHA unchanged since Sep25 |
| 12 | metric implementation | LIKELY for completed (JSON); V2 extractor differs | extract rewritten Oct2 |
| 13 | seed semantics | PARTIAL | SEED_CONTRACT PARTIALLY_BOUND |
| 14 | method-factor semantics | LIKELY YES | ENABLE/MEMORY/TOPK launchers unchanged |
| 15 | no outcome-dependent diffs | YES for design | V2 patches not outcome-selected for metrics of completed |

## Verdict
**PRE_POST_PATCH_PANEL_COMPATIBILITY = UNRESOLVED**

Cannot certify YES. Therefore front6+back9 **must not** be stitched into one confirmatory primary under current evidence.
