# QRTC-HR vs Clean — full test filtered rank-pair diagnosis

**Generated (UTC):** 2026-05-09T08:33:07.363828+00:00  
**Triples:** 609 (two filtered ranks each: tail prediction / head prediction)

## Pair-level outcomes (tail ∪ head; Δ = QRTC − Clean rank)

| Category | Count |
|----------|------:|
| Improved (Δ < 0) | 526 |
| Worsened (Δ > 0) | 456 |
| Unchanged (Δ = 0) | 236 |

## Triple-level net (Δtail + Δhead)

| Category | Count |
|----------|------:|
| Net improved (< 0) | 306 |
| Net worsened (> 0) | 276 |
| Net unchanged (= 0) | 27 |

## Mean shifts (QRTC − Clean)

| Side | Mean Δrank | Median Δrank | P95 Δ | P99 Δ |
|------|------------|--------------|-------|-------|
| tail | -1.6798 | 0.0000 | 41.2000 | 211.5200 |
| head | -0.4548 | 0.0000 | 27.6000 | 73.6000 |

**Interpretation:** negative mean Δ ⇒ average rank improves under QRTC on that side.

## Hit@1 gain / loss counts (per side, triple-level)

| Side | Gain (was not 1 → becomes 1) | Loss (was 1 → no longer 1) |
|------|------------------------------|-----------------------------|
| tail | 12 | 10 |
| head | 9 | 16 |

## Hit@10 gain / loss counts (crossing the top-10 boundary)

| Side | Gain (>10 → ≤10) | Loss (≤10 → >10) |
|------|-------------------|-------------------|
| tail | 10 | 18 |
| head | 20 | 20 |

## Large moves (|Δrank| ≥ 50)

| Side | Large improve (Δ ≤ −50) | Large worsen (Δ ≥ +50) |
|------|--------------------------|-------------------------|
| tail | 32 | 26 |
| head | 12 | 14 |

## MR / tail risk

- Mean combined Δ per triple (Δtail+Δhead): **-2.1346** — divide by 2 to align with average-rank-over-pairs intuition.
- Among triples with **positive** combined Δ, the **largest 1%** of those triples account for **0.139** of the total positive MR-increase mass (**concentration of worseners**).

## Relation-level mean Δ (sorted by |mean Δtail|+|mean Δhead|)

| relation_id | n | mean Δtail | mean Δhead |
|------------|---:|-----------:|-----------:|
| 5 | 7 | -176.4286 | -18.1429 |
| 3 | 47 | -0.2979 | -6.2553 |
| 2 | 28 | -1.0357 | 4.8571 |
| 1 | 228 | 4.0351 | -0.7500 |
| 0 | 247 | -3.2146 | 0.7368 |
| 4 | 52 | 2.4808 | -0.0577 |

Full table: `relation_mean_delta.tsv`

### Top triples by combined MR pressure (largest Δtail+Δhead)

- idx=593 (h,t,r)=(73,725,1) Δtail=456 Δhead=1 sum=457.0
- idx=99 (h,t,r)=(602,401,1) Δtail=323 Δhead=0 sum=323.0
- idx=314 (h,t,r)=(602,66,1) Δtail=323 Δhead=0 sum=323.0
- idx=432 (h,t,r)=(1195,856,1) Δtail=315 Δhead=5 sum=320.0
- idx=457 (h,t,r)=(2528,2167,1) Δtail=292 Δhead=0 sum=292.0
- idx=254 (h,t,r)=(1699,1084,1) Δtail=229 Δhead=1 sum=230.0
- idx=440 (h,t,r)=(30,1133,4) Δtail=212 Δhead=1 sum=213.0
- idx=92 (h,t,r)=(674,1722,0) Δtail=206 Δhead=2 sum=208.0
- idx=467 (h,t,r)=(2423,614,1) Δtail=150 Δhead=5 sum=155.0
- idx=407 (h,t,r)=(73,2386,0) Δtail=148 Δhead=-1 sum=147.0

## AP/AUROC vs Hits/MRR (qualitative)

- **Hits@1 / MRR** respond to **top-of-list** mass; **Hit@1 gain/loss counts** above quantify directional flips.
- **MR** is a **mean** over **2×N** ranks; **right-tail** worseners can dominate the mean even when **median Δ** is modest — check **large-worsen counts** and **positive-mass concentration**.
- **AP/AUROC** aggregate **sampled pos/neg score pairs** in `KnowledgeGraphCompletionBiomed.evaluate`; they are not equivalent to Hit@K and can move **slightly opposite** when mid-tail scores/calibration change (report as **trade-off**, not contradiction).

## Paper writing guidance

- Claim **filtered top-k / MRR gains** when consistent with aggregate test table; pair-level improved vs worsened counts support whether gains are **broad** or **sparse**.
- Explicitly report **test MR regression** vs Clean and tie to **head vs tail mean Δ** + **relation table** if skewed.
- Do **not** imply uniform improvement; avoid masking **AP/AUROC** deltas.

## LncTarD-PPI withoutBRG — aggregate MR / MRR / Hits direction (recomputed ranks, *n*=609)

Values from `dump_*_meta.json` (`recomputed` block; filtered ranking).

| Metric | Clean | QRTC | Direction |
|--------|------:|-----:|-----------|
| MR (mean over tail∪head ranks) | 87.272 | 86.204 | **↓ QRTC better** |
| MRR (mean over inverse ranks) | 0.1836 | 0.1845 | **↑ QRTC better** |
| MR_tail | 117.153 | 115.473 | **↓ QRTC better** |
| MR_head | 57.391 | 56.936 | **↓ QRTC better** |
| MRR_tail | 0.1705 | 0.1740 | **↑ QRTC better** |
| MRR_head | 0.1967 | 0.1949 | **↓ QRTC worse** (small head-MRR trade-off) |
| Hits@1 (eval tensor) | 0.09360 | 0.08949 | Clean slightly higher on aggregated Hits@1 |

**Interpretation:** MR and aggregate MRR **improve** under QRTC on this full test; **head-side MRR** is slightly lower while **tail-side MRR** rises — report as **head vs tail decomposition**, not a single scalar story.

## Head / tail long-tail outliers (when interpreting MR or MRR)

From `rankpair_summary.json`: **p99 Δtail ≈ 212**, **p99 Δhead ≈ 74** rank units (QRTC − Clean). Tail prediction exhibits **heavier extreme deltas** than head — consistent with **tail-side long-tail outliers** driving residual MR sensitivity even when mean Δtail is negative. Use **large_improve / large_worsen** counts per side and **relation_id** table (esp. relation **5**) for mechanistic wording.

## Files

- `clean_fulltest_filtered_rankpairs.tsv`
- `qrtc_fulltest_filtered_rankpairs.tsv`
- `matched_rank_delta.tsv`
- `relation_mean_delta.tsv`
- `rankpair_summary.json`
