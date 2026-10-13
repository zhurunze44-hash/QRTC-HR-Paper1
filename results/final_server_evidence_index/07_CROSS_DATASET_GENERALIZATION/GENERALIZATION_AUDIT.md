# GENERALIZATION_AUDIT

Answers from **disk**, not from manuscript spin.

1. **How many distinct biomedical datasets were actually run formally?**  
   **Two:** PC KEGG (PC_KEGG_0602) and LncTarD-PPI. No third formal biomedical dataset tree found.

2. **Which are independent tasks?**  
   PC KEGG pathway completion vs LncTarD lncRNA–target-style completion are **different biomedical tasks**. wBRG vs woBRG are **graph regimes of the same split files**, not new datasets. Not transfer learning (train on A, test on B).

3. **Where is QRTC positive?**  
   PC KEGG wBRG and woBRG: test MRR/Hits@1/Hits@10 up (wBRG AP/AUROC down; wBRG test MR worse). LncTarD woBRG: tiny +MRR, mixed Hits.

4. **Mixed?**  
   LncTarD wBRG test: AP/AUROC/Hits@10/MR up; **Hits@1 and MRR down**.

5. **Negative?**  
   LncTarD wBRG MRR/Hits@1. PC wBRG test MR. Query-level: not majority-query improvement (Win/Tie/Loss 3627/5945/3304).

6. **Broad generalization?**  
   **Not supported.** Two datasets, seed1024, mixed LncTarD.

7. **Dataset-dependent effect?**  
   **Supported as description of existing tables.**

8. **Post-hoc favorable dataset selection?**  
   LncTarD **was run and reported mixed**. No hidden third positive dataset found. Risk remains that only two datasets exist (limited search), not that negatives were deleted from the main table.

9. **Unreported negative datasets?**  
   **No additional completed formal dataset found** to hide. RotatE baselines exist but are not QRTC negatives. Top-K 1/3 formal trains: UNRESOLVED/omitted per CMPB.

Do not call wBRG/woBRG “cross-dataset generalization.”
