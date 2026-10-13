# QRTC-HR vs Clean — full test filtered rank-pair diagnosis

**Generated (UTC):** 2026-05-07T18:06:40.440691+00:00  
**Triples:** 6438 (two filtered ranks each: tail prediction / head prediction)

## Pair-level outcomes (tail ∪ head; Δ = QRTC − Clean rank)

| Category | Count |
|----------|------:|
| Improved (Δ < 0) | 3627 |
| Worsened (Δ > 0) | 3304 |
| Unchanged (Δ = 0) | 5945 |

## Triple-level net (Δtail + Δhead)

| Category | Count |
|----------|------:|
| Net improved (< 0) | 2779 |
| Net worsened (> 0) | 2339 |
| Net unchanged (= 0) | 1320 |

## Mean shifts (QRTC − Clean)

| Side | Mean Δrank | Median Δrank | P95 Δ | P99 Δ |
|------|------------|--------------|-------|-------|
| tail | 0.2252 | 0.0000 | 5.0000 | 23.0000 |
| head | 10.1083 | 0.0000 | 109.0000 | 1227.0500 |

**Interpretation:** negative mean Δ ⇒ average rank improves under QRTC on that side.

## Hit@1 gain / loss counts (per side, triple-level)

| Side | Gain (was not 1 → becomes 1) | Loss (was 1 → no longer 1) |
|------|------------------------------|-----------------------------|
| tail | 244 | 230 |
| head | 542 | 309 |

## Hit@10 gain / loss counts (crossing the top-10 boundary)

| Side | Gain (>10 → ≤10) | Loss (≤10 → >10) |
|------|-------------------|-------------------|
| tail | 67 | 99 |
| head | 362 | 252 |

## Large moves (|Δrank| ≥ 50)

| Side | Large improve (Δ ≤ −50) | Large worsen (Δ ≥ +50) |
|------|--------------------------|-------------------------|
| tail | 13 | 12 |
| head | 505 | 511 |

## MR / tail risk

- Mean combined Δ per triple (Δtail+Δhead): **10.3335** — divide by 2 to align with average-rank-over-pairs intuition.
- Among triples with **positive** combined Δ, the **largest 1%** of those triples account for **0.362** of the total positive MR-increase mass (**concentration of worseners**).

## Relation-level mean Δ (sorted by |mean Δtail|+|mean Δhead|)

| relation_id | n | mean Δtail | mean Δhead |
|------------|---:|-----------:|-----------:|
| 13 | 6438 | 0.2252 | 10.1083 |

Full table: `relation_mean_delta.tsv`

### Top triples by combined MR pressure (largest Δtail+Δhead)

- idx=5860 (h,t,r)=(21278,30936,13) Δtail=6 Δhead=8108 sum=8114.0
- idx=4276 (h,t,r)=(17053,30942,13) Δtail=-12 Δhead=7775 sum=7763.0
- idx=3567 (h,t,r)=(19043,31180,13) Δtail=-39 Δhead=7542 sum=7503.0
- idx=853 (h,t,r)=(28975,30902,13) Δtail=-12 Δhead=6802 sum=6790.0
- idx=3208 (h,t,r)=(12147,30936,13) Δtail=22 Δhead=6413 sum=6435.0
- idx=6225 (h,t,r)=(25459,30895,13) Δtail=0 Δhead=5438 sum=5438.0
- idx=4968 (h,t,r)=(18574,30997,13) Δtail=-1 Δhead=5219 sum=5218.0
- idx=1407 (h,t,r)=(28097,30998,13) Δtail=38 Δhead=4744 sum=4782.0
- idx=5595 (h,t,r)=(17936,30895,13) Δtail=1 Δhead=4725 sum=4726.0
- idx=1891 (h,t,r)=(13350,31177,13) Δtail=-3 Δhead=4682 sum=4679.0

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
