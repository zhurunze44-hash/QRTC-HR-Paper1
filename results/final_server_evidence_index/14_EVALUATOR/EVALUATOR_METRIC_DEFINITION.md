# Evaluator metric definitions

**File:** SOURCE_RESTORE `biopathnet/task.py` `KnowledgeGraphCompletionBiomed.evaluate` ~337–383

Filtered ranking (`self.filtered_ranking`):
`ranking = sum((pos_pred <= pred) & mask, dim=-1) + 1`

- **MR:** `ranking.float().mean()`
- **MRR:** `(1 / ranking.float()).mean()`
- **Hits@K:** `(ranking <= K).float().mean()`
- **AUROC / AP:** computed on a **1:1 pos vs sampled neg** stack (`metrics.area_under_roc` / `area_under_prc`), **not** on the full filtered ranking list.

Formal eval script for PC wBRG QRTC test: `eval_test_metrics_only_20260506.py` (metrics-only, no extra training).
