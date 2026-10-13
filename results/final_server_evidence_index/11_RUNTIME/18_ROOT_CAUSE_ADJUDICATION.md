# 18 Root Cause Adjudication (sealed with real PC-KEGG)

**Classification: `ALGORITHM_DOMINANT`**  
**Refined forward label: `ALGORITHM_DOMINANT_WITH_OPTIMIZABLE_ON_PATH_OVERHEAD`**

Primary workload: real_pc_kegg
- R_WRAPPER = **1.0017** → wrapper / QRTC-off backbone debt **ABSENT / NEGLIGIBLE**
- R_QRTC = **1.4706** → QRTC-on incremental cost **MATERIAL (~47%)**
- R_TOTAL = **1.4731**
- MESSAGE_CALL_RATIO = **both_zero_fused_path**
- PROPAGATION_CALL_RATIO = **1.0**
- MAA_RATIO = **1.0** → **DUPLICATE_PROPAGATION = FALSE**

## Synthetic (secondary)
- R_WRAPPER≈0.999 · R_QRTC≈1.212 · R_TOTAL≈1.211

## Closed suspicions
1. `_install_qrtc_message_wrappers` causing backbone re-run / duplicate propagation → **CLOSED (ABSENT)**
2. Historical multi-× epoch slowdown fully explained by 1.47× forward → **NOT CLOSED** (needs fwd / fwd+bwd / val decomposition)

## Top 5 (QRTC-on path)
1. `accumulate_qrtc_rel_usage_chunked` rematerializes DistMult edge messages in Python chunks
2. `compute_qrtc_relation_gate` expands R×B×d + gate MLP each layer (**algorithmic**)
3. Unconditional precedent topk `.detach().cpu()` sync in `_qrtc_prepare_layer_state` (**engineering**)
4. R_wrapper≈1.00 (QRTC-off ≈ BioPathNet; wrappers off fused hot path)
5. R_qrtc≈1.47; maa_ratio=1.0 (no duplicate propagation)

## Contract
- Shared backbone = YES  
- Readout-only = **NO** (gate inside message passing)  
- B≡C scores = YES; D differs intentionally
