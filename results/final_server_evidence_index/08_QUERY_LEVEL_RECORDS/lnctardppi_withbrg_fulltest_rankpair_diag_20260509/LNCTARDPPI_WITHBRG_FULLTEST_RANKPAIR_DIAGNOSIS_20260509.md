# QRTC-HR vs Clean — full test filtered rank-pair diagnosis

**Generated (UTC):** 2026-05-09T04:41:05.591058+00:00  
**Triples:** 609 (two filtered ranks each: tail prediction / head prediction)

## Pair-level outcomes (tail ∪ head; Δ = QRTC − Clean rank)

| Category | Count |
|----------|------:|
| Improved (Δ < 0) | 555 |
| Worsened (Δ > 0) | 491 |
| Unchanged (Δ = 0) | 172 |

## Triple-level net (Δtail + Δhead)

| Category | Count |
|----------|------:|
| Net improved (< 0) | 323 |
| Net worsened (> 0) | 261 |
| Net unchanged (= 0) | 25 |

## Mean shifts (QRTC − Clean)

| Side | Mean Δrank | Median Δrank | P95 Δ | P99 Δ |
|------|------------|--------------|-------|-------|
| tail | -9.6749 | 0.0000 | 77.0000 | 226.1600 |
| head | 0.1987 | 0.0000 | 38.0000 | 112.0000 |

**Interpretation:** negative mean Δ ⇒ average rank improves under QRTC on that side.

## Hit@1 gain / loss counts (per side, triple-level)

| Side | Gain (was not 1 → becomes 1) | Loss (was 1 → no longer 1) |
|------|------------------------------|-----------------------------|
| tail | 8 | 21 |
| head | 14 | 18 |

## Hit@10 gain / loss counts (crossing the top-10 boundary)

| Side | Gain (>10 → ≤10) | Loss (≤10 → >10) |
|------|-------------------|-------------------|
| tail | 21 | 20 |
| head | 37 | 25 |

## Large moves (|Δrank| ≥ 50)

| Side | Large improve (Δ ≤ −50) | Large worsen (Δ ≥ +50) |
|------|--------------------------|-------------------------|
| tail | 58 | 45 |
| head | 22 | 24 |

## MR / tail risk

- Mean combined Δ per triple (Δtail+Δhead): **-9.4762** — divide by 2 to align with average-rank-over-pairs intuition.
- Among triples with **positive** combined Δ, the **largest 1%** of those triples account for **0.133** of the total positive MR-increase mass (**concentration of worseners**).

## Relation-level mean Δ (sorted by |mean Δtail|+|mean Δhead|)

| relation_id | n | mean Δtail | mean Δhead |
|------------|---:|-----------:|-----------:|
| 12 | 7 | -283.4286 | 60.5714 |
| 9 | 28 | 21.8571 | -3.8929 |
| 8 | 228 | -12.5965 | -1.3772 |
| 7 | 247 | -7.3684 | 1.1579 |
| 11 | 52 | 0.3846 | -6.3846 |
| 10 | 47 | 3.2340 | 3.5319 |

Full table: `relation_mean_delta.tsv`

### Top triples by combined MR pressure (largest Δtail+Δhead)

- idx=394 (h,t,r)=(15904,5718,9) Δtail=611 Δhead=0 sum=611.0
- idx=328 (h,t,r)=(16132,15114,8) Δtail=533 Δhead=-17 sum=516.0
- idx=562 (h,t,r)=(16535,5678,11) Δtail=376 Δhead=-1 sum=375.0
- idx=474 (h,t,r)=(16725,7034,7) Δtail=360 Δhead=3 sum=363.0
- idx=21 (h,t,r)=(1056,15878,11) Δtail=355 Δhead=3 sum=358.0
- idx=429 (h,t,r)=(15824,4632,10) Δtail=234 Δhead=5 sum=239.0
- idx=353 (h,t,r)=(16307,3452,10) Δtail=0 Δhead=231 sum=231.0
- idx=254 (h,t,r)=(16454,5202,8) Δtail=228 Δhead=2 sum=230.0
- idx=15 (h,t,r)=(16594,3131,8) Δtail=205 Δhead=-3 sum=202.0
- idx=459 (h,t,r)=(16773,2859,8) Δtail=-3 Δhead=190 sum=187.0

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
