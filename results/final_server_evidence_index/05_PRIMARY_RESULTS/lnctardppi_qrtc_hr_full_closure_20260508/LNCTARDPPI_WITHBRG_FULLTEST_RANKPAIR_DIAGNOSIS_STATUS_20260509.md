# LncTarD-PPI withBRG — full-test rank-pair diagnosis (Clean vs QRTC-HR) — 2026-05-09

**VERDICT=LNCTARDPPI_WITHBRG_FULLTEST_RANKPAIR_DIAGNOSIS_PASS**

## Scope

- **Split:** full **test** only (`#test=609`), **filtered** ranking, **no** cap / smoke / subset eval flags.
- **Configs:**  
  - Clean: `config/knowledge_graph/biomedical/lnctardppi_clean_withbrg_formal_epoch8_fulltest_20260508.yaml`  
  - QRTC: `config/knowledge_graph/biomedical/lnctardppi_qrtc_hronly_withbrg_formal_epoch8_fulltest_20260508.yaml`
- **Data path override for dumper:** `PC_KEGG_DATA_ROOT=/root/autodl-tmp/BioPathNet_fresh/data/lnctardppi` (script requirement; **not** PC_KEGG data).
- **QRTC env (dump qrtc):** `QRTC_ENABLE=1`, `QRTC_USE_MEMORY=1`, `QRTC_TOPK=2`; all other toggles **0** per protocol.
- **Log:** `logs/lnctardppi_withbrg_fulltest_rankpair_diag_20260509.log` — ends with `EXIT_CODE:0` (outer bash); no `Traceback` / `RuntimeError` / CUDA OOM / `AssertionError` / `killed` / `NaN`.

## Output directory

`paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/lnctardppi_withbrg_fulltest_rankpair_diag_20260509/`

## PASS checklist

| Artifact | Status |
|----------|--------|
| `clean_fulltest_filtered_rankpairs.tsv` | **Present**; **609** triple rows (+ header) |
| `qrtc_fulltest_filtered_rankpairs.tsv` | **Present**; **609** triple rows (+ header) |
| `matched_rank_delta.tsv` | **Present** |
| `relation_mean_delta.tsv` | **Present** |
| `rankpair_summary.json` | **Present** |
| Diagnosis MD | **`LNCTARDPPI_WITHBRG_FULLTEST_RANKPAIR_DIAGNOSIS_20260509.md`** |

## Pair-level (Δ = QRTC − Clean rank; tail ∪ head, 1218 pairs)

| Outcome | Count |
|---------|------:|
| Improved (Δ < 0) | **555** |
| Worsened (Δ > 0) | **491** |
| Unchanged (Δ = 0) | **172** |

## Triple-level net (Δtail + Δhead)

| Outcome | Count |
|---------|------:|
| Net improved (< 0) | **323** |
| Net worsened (> 0) | **261** |
| Net unchanged (= 0) | **25** |

## Mean shifts & MR interpretation

- **Mean Δtail:** **−9.67** (negative ⇒ average **tail** rank improves under QRTC).
- **Mean Δhead:** **+0.20** (slight average **head** rank **worsening** vs Clean).
- **Mean combined (Δtail+Δhead) per triple:** **−9.48** — consistent with **lower test MR** for QRTC vs Clean in the aggregate table; improvement is **tail-driven**; head side is **near neutral on average**.
- **Median Δtail / Δhead:** both **0** — mass of changes at small ranks; **mean MR** still moves because of **asymmetric tail/head means** and **right-tail** moves (see P95/P99 in diagnosis MD).
- **Head vs tail long-tail outliers:** largest **positive** combined-pressure triples include **tail-only** large worsening (e.g. idx 394, Δtail=611) and **head-only** worsening (e.g. idx 353, Δhead=231, Δtail=0); see `rankpair_summary.json` `top10_triples_by_positive_mr_delta_sum` and `relation_mean_delta.tsv` (e.g. relation **9** mean Δtail **+**, relation **12** strong negative mean Δtail with offsetting head).

## Hit@1 / Hit@10 boundary counts (triple-level)

- **Hit@1 tail:** gain **8**, loss **21** → net **loss** of top-1 tail hits under QRTC (aligns with **lower test MRR / Hits@1**).
- **Hit@1 head:** gain **14**, loss **18** → small net loss.
- **Hit@10 tail:** gain **21**, loss **20** (roughly balanced).
- **Hit@10 head:** gain **37**, loss **25** → net **gain** on head @10 (aligns with **higher test Hits@10/20/50/100** in aggregate table).

## Aggregate alignment

- **Test MR:** QRTC **lower** than Clean — supported by **negative mean Δtail** dominating **slightly positive mean Δhead**.
- **Test MRR / Hits@1:** QRTC **lower** — supported by **Hit@1 loss > gain** on both sides in rank-pair, despite many strict rank **improvements** in the mid/long tail.
- **Test AP / AUROC:** QRTC **higher** — consistent with **score-pair** / calibration shifts not identical to rank@K (see diagnosis MD “AP/AUROC vs Hits/MRR”).

## Reference

Full narrative + file list: `LNCTARDPPI_WITHBRG_FULLTEST_RANKPAIR_DIAGNOSIS_20260509.md`  
Machine-readable stats: `rankpair_summary.json`
