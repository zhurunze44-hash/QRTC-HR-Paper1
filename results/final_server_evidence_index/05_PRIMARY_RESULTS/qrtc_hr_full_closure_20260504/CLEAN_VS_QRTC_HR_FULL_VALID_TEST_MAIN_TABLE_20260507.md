# Clean vs QRTC-HR (withBRG) — full valid / full test main table

**Frozen:** 2026-05-07  
**Dataset:** PC_KEGG_0602 (`include_factgraph`: yes)  
**Protocol:** explicit checkpoint `model_epoch_8.pth`; seed **1024**; batch 16; neg 512; epoch 8  
**Models:** Clean NBFNet withBRG vs QRTC-HR fused withBRG (formal epoch8 ckpt).

---

## 1. Source artifacts

| Run | Valid evidence | Test evidence |
|-----|----------------|---------------|
| **Clean withBRG** | `CLEAN_WITHBRG_EPOCH8_FULL_VALID_STATUS_20260504.md`, log `clean_withbrg_epoch8_FULL_VALID_20260504.log` | `CLEAN_WITHBRG_EPOCH8_FULL_TEST_STATUS_20260504.md`, log `clean_withbrg_epoch8_FULL_TEST_20260504.log` |
| **QRTC-HR withBRG** | `QRTC_HRONLY_FUSED_WITHBRG_FULL_VALID_MONITOR_SUMMARY_20260506.md`, log `logs/qrtc_hronly_fused_withbrg_formal_epoch8_full_valid_nocap_20260506.log` | `QRTC_HRONLY_FUSED_WITHBRG_FULL_TEST_METRICS_SUMMARY_20260506.md`, log `logs/qrtc_hronly_fused_withbrg_formal_epoch8_full_test_metrics_only_20260506.log` |

---

## 2. Full validation metrics

| Metric | Clean | QRTC-HR | Δ (QRTC − Clean) |
|--------|------:|--------:|------------------:|
| AP | 0.988077 | 0.987018 | −0.001059 |
| AUROC | 0.986829 | 0.985864 | −0.000965 |
| Hits@1 | 0.427022 | 0.445460 | +0.018438 |
| Hits@3 | 0.572358 | 0.579641 | +0.007283 |
| Hits@10 | 0.712581 | 0.720948 | +0.008367 |
| Hits@20 | 0.782770 | 0.788813 | +0.006043 |
| Hits@50 | 0.863960 | 0.864735 | +0.000775 |
| Hits@100 | 0.904865 | 0.905485 | +0.000620 |
| MR | 126.674 | 123.395 | −3.279 |
| MRR | 0.524037 | 0.536668 | +0.012631 |

**Valid read:** Ranking-heavy summaries (Hits@1/3/10, MRR) favor QRTC-HR; AP/AUROC slightly lower; **MR improves on valid.**

---

## 3. Full test metrics

| Metric | Clean | QRTC-HR | Δ (QRTC − Clean) |
|--------|------:|--------:|------------------:|
| AP | 0.988616 | 0.986643 | −0.001973 |
| AUROC | 0.987207 | 0.985724 | −0.001483 |
| Hits@1 | 0.440975 | 0.460158 | +0.019183 |
| Hits@3 | 0.580304 | 0.592498 | +0.012194 |
| Hits@10 | 0.724371 | 0.730429 | +0.006058 |
| Hits@20 | 0.793336 | 0.793103 | −0.000233 |
| Hits@50 | 0.866107 | 0.866418 | +0.000311 |
| Hits@100 | 0.908046 | 0.907891 | −0.000155 |
| MR | 121.068 | 126.234 | +5.166 |
| MRR | 0.536298 | 0.550018 | +0.013720 |

**Test read:** Same broad pattern as valid for **top-heavy ranking** (Hits@1/3/10, MRR ↑); AP/AUROC slightly ↓; **MR worsens on test** despite MR improvement on valid — suggests shifted tail behavior / split-specific outliers rather than a uniform monotone improvement.

---

## 4. One-line synthesis

**Ranking-positive but mixed:** QRTC-HR consistently lifts early retrieval (Hits@1–10, MRR) on both splits while sacrificing small margins on AP/AUROC; **MR improves on valid but degrades on test**, flagging **generalization of tail ranks** as the primary tension for prose and optional follow-up (outside current freeze scope).
