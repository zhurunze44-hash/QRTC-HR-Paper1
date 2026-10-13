# METHOD_IDENTITY_AUDIT

**Authority code root:** `<REDACTED_SERVER_PATH>  
**Not authority:** `QRTC_HR_WORK_20260908/biopathnet` (OPT-1/2 engineering copy; SHA differs for model.py/layer.py/qrtc_common.py)  
**Binding:** `SOURCE_IDENTITY_FREEZE.json`, `IMPLEMENTATION_IDENTITY.json`  
**No training in this audit.** Line numbers from SOURCE_RESTORE files on 2026-10-05.

## Formal identity

**FORMAL_METHOD_IDENTITY=RELATION_GATE_PLUS_CROSS_LAYER_RELATION_USAGE_MEMORY**

Confirmed as fused DistMult QRTC-HR (`QRTC_MINIMAL_PATCH_V6` / MESSAGE_GATED / TOPK=2 on formal env).

---

### 1. Relation gate before or after aggregation?

**File:** `layer.py` **Class:** `GeneralizedRelationalConv` **Function:** `message_and_aggregate` **Lines:** 140–171

Excerpt:

```
if use_fused_qrtc:
    relation_bf = relation_input.view(...)
    gate_rb = qrtc_common.compute_qrtc_relation_gate(...)
    if gate_rb is not None:
        relation_bf = relation_bf * gate_rb
        relation_input = relation_bf.reshape(...)
...
update = functional.generalized_rspmm(adjacency, relation_input, input, ...)
```

**判定:** Gate scales DistMult relation features **before** RSPMM aggregation.

### 2. Does the gate actually change the message relation feature?

**File:** `qrtc_common.py` **Function:** `compute_qrtc_relation_gate` **Lines:** 21–35

```
gate_in = torch.cat([q, r, c], dim=-1)
return torch.sigmoid(gate_mlp(gate_in))
```

Then `relation_bf = relation_bf * gate_rb` (layer.py 150).

**判定:** YES. Per-(relation, batch) sigmoid gate multiplies `relation_bf` used as DistMult relation input.

### 3. How is usage statistic defined?

**File:** `qrtc_common.py` **Function:** `accumulate_qrtc_rel_usage_chunked` **Lines:** 58–92

```
edge_msg = edge_rel * edge_inp
strength = edge_msg.detach().abs().mean(dim=-1)
acc = acc + scatter_add(strength, edge_type[sl], ...)
qrtc_state["rel_usage_next"] = acc.transpose(0, 1)
```

**判定:** Detached mean-abs DistMult edge-message strength, scattered by relation ID. `qrtc_usage_mlp` is **not** used on this fused path.

### 4. Usage from current or previous propagation layer?

Usage is written to `rel_usage_next` during the current layer fused MAA (`layer.py` 155–162). `model.py` `_qrtc_finalize_layer_state` (991–994) returns `rel_usage_next` as `rel_usage_prev` for the **next** layer. Layer 0 uses `qrtc_init_memory` when `rel_usage_prev is None`.

**判定:** Usage is computed from the **current** layer’s (post-gate) messages; memory for layer ℓ uses **previous** layer usage (or init).

### 5. How is memory constructed?

**File:** `model.py` **Function:** `_qrtc_build_precedent_memory` **Lines:** 954–970

```
topk_usage, topk_ids = rel_usage_prev.topk(k=k, dim=-1)
topk_rel_emb = relation_table[topk_ids]
att_logit = self.qrtc_precedent_mlp(cat[q, topk_rel_emb, u])
att_weight = softmax(...)
precedent_memory = (att_weight * topk_rel_emb).sum(dim=1)
```

If memory off or no prev usage: `precedent_memory = qrtc_init_memory` expanded over batch.

**判定:** Attention-weighted sum of Top-K **relation embeddings**.

### 6. Does memory feed the next layer?

**File:** `qrtc_common.py` gate uses `precedent_memory` in concat (lines 26–35). Next layer’s `_qrtc_prepare_layer_state` rebuilds memory from previous usage.

**判定:** YES. Memory enters the next layer’s relation gate.

### 7. Top-K selects relation IDs or stages?

`rel_usage_prev.topk` over the relation dimension; `relation_table[topk_ids]`.

**判定:** **Relation IDs**, not propagation stages.

### 8. Formal TOPK = 2?

**File:** `model.py` line 469: `self.qrtc_topk = int(os.environ.get("QRTC_TOPK", "4"))`  
Formal train/eval **environment contract** sets `QRTC_TOPK=2` (IMPLEMENTATION_IDENTITY / ablation YAML comments). Code default if unset is **4**.

**判定:** Formal results: TOPK=2 by env contract. Code getenv default 4 is a footgun, not the formal setting.

### 9. Terminal readout residual path?

`QRTC_CAND_READOUT_ENABLE` default `"0"` (`model.py` 347). Formal identity freeze: cand-readout OFF.

**判定:** Formal path has **no** terminal residual readout. Optional code exists but is off.

### 10. s_base + Delta s in formal results?

Formal fused path uses native last-layer MLP score. Residual/delta heads exist behind unused flags (`qces`, `f8_score_res`, cand readout).

**判定:** **NO** for formal Table II–IV.

### 11. Candidate state mixer in formal results?

**判定:** **NO** (cand-readout / mixer flags off). `UNRESOLVED` only if a historical YAML secretly enabled it — inspected formal YAMLs put QRTC flags in **shell env**, documented as CAND_READOUT=0 FORCE_MESSAGE=0.

### 12. Final scorer native last-layer MLP?

IMPLEMENTATION_IDENTITY: `score = mlp(gather(cat(h_L, query), t_index))`. Consistent with NBFNet last-layer concat-query MLP.

**判定:** YES.

### 13. What gated/init (memory_off) actually turns off?

Ablation YAML: `QRTC_ENABLE=1 QRTC_USE_MEMORY=0 QRTC_TOPK=2`.  
`_qrtc_build_precedent_memory`: if not `qrtc_use_memory`, always `qrtc_init_memory`. Gate MLP still runs.

**判定:** Turns off **cross-layer usage memory / Top-K precedent**. Does **not** remove gate or `qrtc_init_memory`. Not a pure-gate ablation. Historical A1 label `GATE_ONLY` is the same class.

### 14. Extra trainable components vs Base?

Always instantiated: `qrtc_init_memory`, `qrtc_precedent_mlp`, `qrtc_gate_mlp`, `qrtc_usage_mlp` (and possibly unused cpacc). Base (`QRTC_ENABLE=0`) still **stores** these tensors; they are not used in the forward if disabled.

**Formal-active extra vs Base forward:** `qrtc_gate_mlp` + `qrtc_precedent_mlp` + `qrtc_init_memory`. `qrtc_usage_mlp` inactive on fused DistMult path.

---

Uncertainties: WORK vs RESTORE SHA mismatch is documented, not guessed. Pair-KG routers in the same files are **not** on the formal YAML path.
