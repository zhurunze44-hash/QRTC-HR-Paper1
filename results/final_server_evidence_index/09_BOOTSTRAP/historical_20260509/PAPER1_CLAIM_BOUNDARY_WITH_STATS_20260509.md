# Paper 1 — Claim boundary with rank-pair statistics — 2026-05-09

This document separates **per-query rank-pair evidence** (paired ranks, MRR, Hits@K transitions, bootstrap CIs, sign tests) from **global ranking metrics** reported by eval (AP, AUROC, dataset-level MR/MRR/Hits@K). **Never** imply that rank-pair \(p\)-values validate biology or clinical utility.

---

## Claims that can be drafted (with explicit binding)

1. **PC_KEGG withBRG — paired ranking shifts on the exported full-test rank-pair slice (`block B`).**  
   - **Support:** Bootstrap 95% CIs favor **positive** \(\Delta\)MRR and \(\Delta\)Hits@1–10; sign test on discordant rank moves favors improvements (\(p \approx 1.1×10^{-4}\)); Wilcoxon on \(\Delta RR\) is highly significant.  
   - **Binding files:** `paper1_rankpair_bootstrap_ci_20260509.tsv` (rows `B_PC_KEGG_withBRG`, metrics `delta_mrr`, `delta_hits@1`–`@10`), `paper1_rankpair_statistical_tests_20260509.tsv`.

2. **PC_KEGG withBRG — MR / Hits@ larger K are not uniformly backed by paired evidence.**  
   - **Support:** Bootstrap **mixed** for \(\Delta\)MR and for \(\Delta\)Hits@20–100 despite gains at small K.  
   - **Binding:** same CI table rows for block B.

3. **LncTarD-PPI withBRG — mean paired rank improves on this diagnostic export (`block C`).**  
   - **Support:** Observed \(\Delta\)MR is negative and bootstrap CI for \(\Delta\)MR lies entirely below 0 (favorable to QRTC under “lower is better”).  
   - **Binding:** CI + tests TSV rows `C_LncTarD-PPI_withBRG`.

4. **Side-heterogeneity on PC_KEGG withoutBRG rank-pair diagnostics (`block A`) — head vs tail.**  
   - **Support:** `paper1_rankpair_side_breakdown_summary_20260509.tsv` shows **TAIL** mean \(\Delta\)MR slightly negative vs **HEAD** massively positive (harmful).  
   - **Binding:** side breakdown TSV + hit-transition tables.

---

## Claims that must be weakened

| Weak form | Why |
|-----------|-----|
| “QRTC-HR improves retrieval across the board on PC_KEGG.” | MR \(\Delta\) is **not** CI-supported positive; large-K Hits mixed. |
| “Rank-pair statistics prove QRTC-HR’s AP/AUROC story.” | AP/AUROC were **not** recomputed here; rank-pair stats address **paired rank/MRR/Hits** only. |
| “withoutBRG rank-pair confirms the May-02 trusted metrics.” | Dump aligns with **2026-05-08** eval wiring per diagnosis card; **authority lock** references **May-02** checkpoint for tables—**do not merge**. |
| “LncTarD shows the same clear gain as PC_KEGG.” | Block C: sign test \(p≈0.051\); MRR/Hits CIs **mixed**; \(n=609\) triples. |

---

## Claims that are **disallowed** (for this evidence package)

1. Any statement that **equates** rank-pair \(p\)-values with **biological** or **clinical** validation.  
2. Any statement that **rank-pair MR** replaces or **re-proves** **global** MR from eval logs **without** citing the eval source.  
3. Using **block A** numbers to **support** or **attack** the **May-02 withoutBRG QRTC** frozen table without an explicit **checkpoint / YAML alignment** paragraph.  
4. “Uniform improvement on all K / all sides” for any block—contradicted by TSVs (esp. B larger K, A head side, D mixed CIs).  
5. Citing **May-08 bad-rerun** checkpoint metrics from the authority lock as trusted outcomes—still **forbidden** by `PC_KEGG_WITHOUTBRG_QRTC_AUTHORITY_LOCK_STATUS_20260508.md`.

---

## One-sentence paper-ready framings (per block)

| Block | Suggested sentence (bounded) |
|-------|----------------------------|
| **A** | On the **2026-05-08–wired** withoutBRG rank-pair diagnostic, paired rank movements are **dominated by head-side degradation** despite slight tail-side improvements—this artifact **must not** be read as evaluating the May-02 authoritative checkpoint. |
| **B** | On the frozen PC_KEGG withBRG full-test rank-pair export, paired **MRR** and **Hits@1–10** shift in QRTC-HR’s favor with bootstrap support, while **mean rank** and larger-K Hits show **mixed** paired evidence consistent with tail-sensitive metrics. |
| **C** | On LncTarD-PPI withBRG, paired **mean rank** improves with a fully negative bootstrap CI for \(\Delta\)MR, but **MRR / Hits** lack consistent CI support and discordant-rank symmetry is **not** significant at \(\alpha=0.05\). |
| **D** | On LncTarD-PPI withoutBRG, paired effects are **small** with bootstrap intervals **straddling zero** for most metrics despite a modest excess of per-pair rank improvements—report cautiously given \(n\). |

---

## Discussion items — acknowledge trade-offs explicitly

1. **Mean rank vs top-heavy metrics:** When MRR/Hits@small-K improve but \(\Delta\)MR is unfavorable or ambiguous, describe **sensitivity of MR to heavy-tail moves** rather than forcing a single-direction story.  
2. **Head vs tail prediction sides:** Especially PC_KEGG withoutBRG diagnostic—**do not** collapse to a scalar “better/worse” without side context.  
3. **Checkpoint alignment:** Separate paragraphs for **table metrics** (freeze / arbitration) vs **rank-pair dumps** (YAML dated pipeline).  
4. **External validity:** LncTarD \(n\) is modest; treat statistics as **supporting qualitative pattern**, not replication of PC_KEGG magnitude.

---

## Statistical ↔ metric mapping cheat sheet

| Evidence type | Supports | Does **not** automatically support |
|---------------|----------|-------------------------------------|
| Rank-pair \(\Delta\)MR / \(\Delta\)MRR / \(\Delta\)Hits@K | Paired movement on evaluated triples’ filtered ranks | Global AP, AUROC, or eval MR unless tied to same checkpoint + full eval |
| Bootstrap CI “yes” on \(\Delta\)Hits@K | Direction of paired hit-indicator changes | Certainty on rare relations or unseen entities |
| Sign test \(p\) | Asymmetry of improve vs worsen moves among non-ties | Practical significance or domain correctness |

---

*Generated as documentation-only audit support — 2026-05-09.*
