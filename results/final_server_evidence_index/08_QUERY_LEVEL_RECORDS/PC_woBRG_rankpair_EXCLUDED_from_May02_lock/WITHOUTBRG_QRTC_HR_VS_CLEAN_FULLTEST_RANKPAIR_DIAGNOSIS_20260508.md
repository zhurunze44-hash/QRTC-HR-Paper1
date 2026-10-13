# QRTC-HR vs Clean — full test filtered rank-pair diagnosis

**Generated (UTC):** 2026-05-08T06:31:36.393097+00:00  
**Triples:** 6438 (two filtered ranks each: tail prediction / head prediction)

## Pair-level outcomes (tail ∪ head; Δ = QRTC − Clean rank)

| Category | Count |
|----------|------:|
| Improved (Δ < 0) | 2135 |
| Worsened (Δ > 0) | 7145 |
| Unchanged (Δ = 0) | 3596 |

## Triple-level net (Δtail + Δhead)

| Category | Count |
|----------|------:|
| Net improved (< 0) | 727 |
| Net worsened (> 0) | 5608 |
| Net unchanged (= 0) | 103 |

## Mean shifts (QRTC − Clean)

| Side | Mean Δrank | Median Δrank | P95 Δ | P99 Δ |
|------|------------|--------------|-------|-------|
| tail | -0.4845 | 0.0000 | 9.0000 | 31.0000 |
| head | 1371.0036 | 632.0000 | 7659.0000 | 7930.6300 |

**Interpretation:** negative mean Δ ⇒ average rank improves under QRTC on that side.

## Hit@1 gain / loss counts (per side, triple-level)

| Side | Gain (was not 1 → becomes 1) | Loss (was 1 → no longer 1) |
|------|------------------------------|-----------------------------|
| tail | 209 | 225 |
| head | 90 | 1005 |

## Hit@10 gain / loss counts (crossing the top-10 boundary)

| Side | Gain (>10 → ≤10) | Loss (≤10 → >10) |
|------|-------------------|-------------------|
| tail | 109 | 126 |
| head | 95 | 2179 |

## Large moves (|Δrank| ≥ 50)

| Side | Large improve (Δ ≤ −50) | Large worsen (Δ ≥ +50) |
|------|--------------------------|-------------------------|
| tail | 43 | 21 |
| head | 419 | 4974 |

## MR / tail risk

- Mean combined Δ per triple (Δtail+Δhead): **1370.5191** — divide by 2 to align with average-rank-over-pairs intuition.
- Among triples with **positive** combined Δ, the **largest 1%** of those triples account for **0.049** of the total positive MR-increase mass (**concentration of worseners**).

## Relation-level mean Δ (sorted by |mean Δtail|+|mean Δhead|)

| relation_id | n | mean Δtail | mean Δhead |
|------------|---:|-----------:|-----------:|
| 0 | 6438 | -0.4845 | 1371.0036 |

Full table: `relation_mean_delta.tsv`

### Top triples by combined MR pressure (largest Δtail+Δhead)

- idx=5127 (h,t,r)=(6511,2244,0) Δtail=2 Δhead=7978 sum=7980.0
- idx=2392 (h,t,r)=(5681,2838,0) Δtail=0 Δhead=7978 sum=7978.0
- idx=3769 (h,t,r)=(6845,1097,0) Δtail=0 Δhead=7973 sum=7973.0
- idx=5515 (h,t,r)=(5601,1097,0) Δtail=0 Δhead=7973 sum=7973.0
- idx=4477 (h,t,r)=(1371,1097,0) Δtail=0 Δhead=7973 sum=7973.0
- idx=3415 (h,t,r)=(6196,1097,0) Δtail=0 Δhead=7973 sum=7973.0
- idx=3844 (h,t,r)=(6508,1097,0) Δtail=0 Δhead=7973 sum=7973.0
- idx=4273 (h,t,r)=(3324,672,0) Δtail=1 Δhead=7971 sum=7972.0
- idx=1995 (h,t,r)=(2773,672,0) Δtail=1 Δhead=7971 sum=7972.0
- idx=2966 (h,t,r)=(6464,959,0) Δtail=0 Δhead=7972 sum=7972.0

## AP/AUROC vs Hits/MRR (qualitative)

- **Hits@1 / MRR** respond to **top-of-list** mass; **Hit@1 gain/loss counts** above quantify directional flips.
- **MR** is a **mean** over **2×N** ranks; **right-tail** worseners can dominate the mean even when **median Δ** is modest — check **large-worsen counts** and **positive-mass concentration**.
- **AP/AUROC** aggregate **sampled pos/neg score pairs** in `KnowledgeGraphCompletionBiomed.evaluate`; they are not equivalent to Hit@K and can move **slightly opposite** when mid-tail scores/calibration change (report as **trade-off**, not contradiction).

## Paper writing guidance

- Claim **filtered top-k / MRR gains** when consistent with aggregate test table; pair-level improved vs worsened counts support whether gains are **broad** or **sparse**.
- Explicitly report **test MR regression** vs Clean and tie to **head vs tail mean Δ** + **relation table** if skewed.
- Do **not** imply uniform improvement; avoid masking **AP/AUROC** deltas.

## Files

- `clean_fulltest_filtered_rankpairs.tsv`
- `qrtc_fulltest_filtered_rankpairs.tsv`
- `matched_rank_delta.tsv`
- `relation_mean_delta.tsv`
- `rankpair_summary.json`
