# withoutBRG — QRTC hard-load + code-path audit + verdict freeze — 2026-05-08

**Scope:** Converge prior **VERDICT D (PARTIAL_TRUST_ONLY)** toward a hardened **A/B/C** decision. No LncTarD-PPI, no retrain, no QRTC formula edits.

---

## Executive summary

| Gate | Result |
|------|--------|
| **QRTC checkpoint hard-load** | **HARDLOAD_PASS** — QRTC-named parameters **fully intersect** (28 keys); `missing_keys` are **`graph` / `fact_graph`** only (runtime graph tensors removed from ckpt like production `solver_load`; **not** QRTC weights). |
| **Code path A vs B** | **CODEPATH_PASS** — listed files **byte-identical** (`sha256` match) between `/root/autodl-tmp/BioPathNet_fresh` and `<REDACTED_SERVER_PATH> |
| **RotatE full valid (no cap)** | **Re-run complete** — **`#valid: 3227`**, new log + metrics in **`ROTATE_WITHOUTBRG_FULL_VALID_REEVAL_NOCAP_STATUS_20260508.md`**. Prior full-valid RotatE card **invalid** due to **`EVAL_VALID_CAP=2`**. |

### Final VERDICT (§五)

**A. TRUST_HARDENED_WITHOUTBRG_RESULTS_USABLE**

All of the following hold:

1. NBFNet Clean/QRTC **full-split** eval was already established in the prior speed/path audit (3227 / 6438; indices ranges).
2. **QRTC hard-load PASS** — no silent drop of QRTC weights; `strict=False` gaps are **non-QRTC graph buffers**.
3. **CODEPATH_PASS** — audited sources match across **A** and **B** roots.
4. **RotatE valid** replaced with a **no-cap** full-valid row.

---

## 一、QRTC-HR checkpoint hard-load 审计

### Config & checkpoint (fixed)

- **Config:** `withoutbrg_formal_rerun_20260507/config/qrtc_hronly_withoutbrg_eval_abs_ckpt_20260508.yaml`
- **Checkpoint:** `withoutbrg_formal_rerun_20260507/qrtc_hronly_train_direct_20260508/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-08-13-35-27-655973/model_epoch_8.pth`

### Procedure

- **Script:** `script/audit_qrtc_ckpt_hardload.py` (read-only; builds model with **`QRTC_ENABLE=1`**, **`QRTC_USE_MEMORY=1`**, **`QRTC_TOPK=2`** before import/instantiation).
- **Checkpoint layout:** top-level keys **`['model', 'optimizer']`** — standard training export.
- **`state['model']`:** `OrderedDict`, **117** keys before hygiene pops.
- **Hygiene pops (aligned with `solver_load`):** remove `fact_graph`, `fact_graph_supervision`, `graph`, `train_graph`, `valid_graph`, `test_graph`, `full_valid_graph`, `full_test_graph` **when present**. For this file, pops hit **`fact_graph`** and **`graph`** only → **115** keys fed into `load_state_dict`.

### `load_state_dict(strict=False)` results

| Field | Value |
|-------|------:|
| **missing_keys** | **2** — `graph`, `fact_graph` |
| **unexpected_keys** | **0** |
| **error_msgs** | **None** |

**Interpretation:** `graph` / `fact_graph` are **large runtime graph tensors**, intentionally stripped before load in production **`eval_valid_only.solver_load`**. They are **not** QRTC MLP / memory parameters.

### QRTC-related key scan

- **Regex (case-insensitive):** `qrtc`, `hop`, `memory`, `readout`, `attention`, `topk`, `precedent`, `gate_mlp`, `usage_mlp`
- **Model QRTC-like keys:** **28**
- **Checkpoint QRTC-like keys:** **28**
- **Intersection:** **28**
- **Missing QRTC-pattern keys:** **0**
- **Unexpected QRTC-pattern keys:** **0**

### Hard-load conclusion token

**`HARDLOAD_PASS`** — meets definition: non-empty missing keys are **only** non-QRTC graph slots removed from checkpoint; **no** QRTC parameter mismatch.

---

## 二、代码路径一致性审计（A vs B）

**A** = `/root/autodl-tmp/BioPathNet_fresh`  
**B** = `<REDACTED_SERVER_PATH>

### sha256 / identity table

| File (relative to repo root) | A exists | B exists | identical |
|------------------------------|----------|----------|-------------|
| `script/eval_valid_only.py` | yes | yes | **yes** |
| `biopathnet/model.py` | yes | yes | **yes** |
| `biopathnet/layer.py` | yes | yes | **yes** |
| `script/run.py` | yes | yes | **yes** |
| `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/scripts/dump_fulltest_filtered_ranks_20260506.py` | yes | yes | **yes** |
| `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/scripts/run_withoutbrg_clean_direct_eval_20260508.sh` | yes | yes | **yes** |
| `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/scripts/run_withoutbrg_qrtc_hronly_direct_eval_20260508.sh` | yes | yes | **yes** |
| `paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/scripts/run_withoutbrg_fulltest_rankpair_20260508.sh` | yes | yes | **yes** |

**Representative:** sizes and mtimes match pairwise (e.g. `eval_valid_only.py` **15605** bytes, mtime **2026-05-08 13:20:20 +0800** on both).

### Code-path conclusion token

**`CODEPATH_PASS`**

---

## 三、RotatE withoutBRG full valid — 去 cap 重跑

See dedicated card:

**`ROTATE_WITHOUTBRG_FULL_VALID_REEVAL_NOCAP_STATUS_20260508.md`**

**Log:** `rotate_withoutbrg_eval_workdir_20260508/full_valid_nocap_reeval_20260508.log`

Key proof lines: **`#valid: 3227`**, no **`EVAL_VALID_CAP`**, **`EXIT_CODE:0`**.

---

## 四、是否需要受保护版 QRTC full test 重跑

**Decision: 不需要（默认）。**

| Condition | Status |
|-----------|--------|
| Hard-load PASS | **Yes** |
| Codepath PASS | **Yes** |
| Optional protected wrapper + rerun | **Not executed** — gates (1)(2) satisfied; **no** evidence requiring a second full-test pass to fix trust. |

If a future run wants belt-and-suspenders, a wrapper may **print env**, **run strictness audit**, and **exit 2/3** on QRTC/cap failures — **out of scope** for this freeze step.

---

## 五、最终 VERDICT（冻结）

**A. TRUST_HARDENED_WITHOUTBRG_RESULTS_USABLE**

---

## 六、回传格式（对用户 §六）

1. **总 VERDICT:** **A. TRUST_HARDENED_WITHOUTBRG_RESULTS_USABLE**
2. **QRTC hard-load:** **HARDLOAD_PASS**（QRTC 参数无缺失；缺 **`graph`/`fact_graph`** 为预期图张量剥离）。
3. **missing/unexpected 摘要:** missing **2** (`graph`, `fact_graph`)；unexpected **0**。
4. **QRTC key 交集:** model **28**，ckpt **28**，交集 **28**。
5. **Codepath:** **CODEPATH_PASS**，上表 **sha256** 全一致。
6. **RotatE full valid no-cap:** 完成；指标见 **`ROTATE_WITHOUTBRG_FULL_VALID_REEVAL_NOCAP_STATUS_20260508.md`**（MR **1485.03**，MRR **0.0167032**，等）。
7. **受保护 QRTC full test 重跑:** **不需要**。
8. **PC_KEGG 总结表:** **允许**写入此次 withoutBRG 数字 **作为 hardened 记录**，但必须标注为 **withoutBRG 语境下的相对 Clean 退化 / 边界现象**（尤其 QRTC-HR aggregate MR↑、head-rank 压力），**禁止**表述为相对主线的“提升”或未经核验的增益叙事。

---

## Artifacts

| Artifact | Path |
|------------|------|
| Hard-load audit script | `script/audit_qrtc_ckpt_hardload.py` |
| RotatE no-cap log | `rotate_withoutbrg_eval_workdir_20260508/full_valid_nocap_reeval_20260508.log` |

---

*Audit completed 2026-05-08.*
