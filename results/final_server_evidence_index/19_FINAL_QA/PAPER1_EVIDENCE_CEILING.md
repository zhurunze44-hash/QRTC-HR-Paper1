# PAPER1_EVIDENCE_CEILING

Server-only. No claim inflation.

1. QRTC raises MRR on PC KEGG seed1024? **SUPPORTED** (0.536298 → 0.550018). Path: FORMAL_RESULT_AUDIT.tsv, main table, historical eval log.
2. QRTC raises MRR on both PC graph regimes? **PARTIALLY_SUPPORTED** — wBRG live ckpt; woBRG QRTC May-02 **ckpt missing**, aggregates from protected re-eval logs.
3. QRTC stably improves LncTarD? **NOT_SUPPORTED** (mixed; wBRG test MRR/Hits@1 down).
4. QRTC stably improves across 5 seeds? **NOT_SUPPORTED** (formal 5-seed panel missing; A1 ineligible).
5. QRTC stably generalizes across datasets? **NOT_SUPPORTED** (two datasets, mixed).
6. Memory gain independent of parameter count? **NOT_SUPPORTED** (capacity confound; Base stores same module tensors; no matched-capacity control).
7. TopK=2 is the key factor? **NOT_SUPPORTED** (formal TOPK=2 by env; Top-K 1/3 formal trees UNRESOLVED/omitted; not isolated as causal key).
8. QRTC generally beats BioPathNet? **NOT_SUPPORTED** (PC ranking mixed with AP/AUROC; LncTarD mixed).
9. QRTC has real behavioral effect? **PARTIALLY_SUPPORTED** (PC wBRG query-level ΔMRR CI excludes 0; not majority-query win; LAST_CHANCE G2 intervention **hurts** design MRR).
10. Reported seed1024 ckpt exact replay? **PARTIALLY_SUPPORTED** — historical eval log matches table (ABS_DIFF 0 at published rounding); **live** GPU replay on this host **not executed** (wrong/missing formal stack per REPLAY_RECEIPT).

Paths: see 18_MANUSCRIPT_BINDING/PAPER1_CLAIM_EVIDENCE_MAP.tsv.
