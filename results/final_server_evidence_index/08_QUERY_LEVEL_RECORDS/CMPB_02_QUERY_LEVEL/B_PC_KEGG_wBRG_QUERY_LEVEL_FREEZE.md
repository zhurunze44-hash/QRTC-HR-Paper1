# B_PC_KEGG_wBRG query-level freeze (authoritative)

- n_pairs = 12876
- ΔMRR observed = 0.013720
- Bootstrap 95% CI = [0.00995, 0.01742] (B=10000 lineage in paper1_statistical_evidence_20260509; supports positive)
- Rank Win / Tie / Loss = **3627 / 5945 / 3304**
- Correction: interrupt memo had Tie/Loss swapped (3627/3304/5945). Correct is 3627/5945/3304.
- Fraction: win=0.282, tie=0.462, loss=0.257
- Mean +ΔRR = 0.1868 (n=3627); mean −ΔRR = -0.1516 (n=3304)
- Locked prose: aggregate short-list MRR gain arises from an **asymmetric redistribution of ranks**, not a majority-query improvement.
- Bootstrap scope freeze: 95% percentile CI for test-query sampling uncertainty conditional on frozen checkpoints; not training-seed uncertainty.
- Forbidden phrases: most queries improve; majority-query improvement; broadly positive per-query effect.
