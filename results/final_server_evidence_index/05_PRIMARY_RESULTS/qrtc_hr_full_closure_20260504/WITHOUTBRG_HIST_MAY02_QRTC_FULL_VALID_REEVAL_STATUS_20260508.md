# Historical May-02 withoutBRG QRTC — protected full valid re-eval — 2026-05-08

## Status

**PASS** — `EXIT_CODE:0`，preflight `HARDLOAD_PASS`（QRTC-pattern missing/unexpected = **0**），`#valid=3227`。

## Environment

- **Conda:** `biopathnet_py310_torch201`

## Protocol

| Requirement | Recorded |
|-------------|----------|
| Split | `valid` |
| `#valid` | **3227** |
| Checkpoint | `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/pc_kegg_qrtc_hronly_withoutbrg_mem_formal_seed1024_epoch8_batch16_neg512/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-02-14-41-05-535438/model_epoch_8.pth` |
| Config | `withoutbrg_formal_rerun_20260507/config/pc_kegg_hist_may02_qrtc_epoch8_EVAL_PROTECTED_ARBITRATION_20260508.yaml` |
| Dataset | `/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602` |
| Cap / subset / smoke | **无**（启动脚本扫描 + 环境清理） |
| QRTC | `QRTC_ENABLE=1` `QRTC_USE_MEMORY=1` `QRTC_TOPK=2` |
| Anti-modules | 全部为 **0**（见仲裁卡） |

## Paths

| Item | Path |
|------|------|
| Log | `logs/hist_may02_qrtc_protected_full_valid_arbitration_20260508.log` |
| Launcher | `scripts/run_hist_may02_qrtc_protected_arbitration_eval_20260508.sh valid` |

## Hard-load（摘录）

- `missing_keys`: `graph`, `fact_graph`（非 QRTC；与历史 eval 一致）
- `unexpected_keys`: **0**
- QRTC-pattern missing/unexpected: **0**

## Metrics（full valid）

| Metric | Value |
|--------|------:|
| AP | 0.952 |
| AUROC | 0.948784 |
| Hits@1 | 0.328633 |
| Hits@3 | 0.435699 |
| Hits@10 | 0.559498 |
| Hits@20 | 0.626278 |
| Hits@50 | 0.724202 |
| Hits@100 | 0.787729 |
| MR | 263.658 |
| MRR | 0.406578 |

## Retention

**FORMAL_TRUSTED** — withoutBRG QRTC **valid** 权威行（与 `WITHOUTBRG_QRTC_AUTHORITY_ARBITRATION_20260508.md` 一致）。
