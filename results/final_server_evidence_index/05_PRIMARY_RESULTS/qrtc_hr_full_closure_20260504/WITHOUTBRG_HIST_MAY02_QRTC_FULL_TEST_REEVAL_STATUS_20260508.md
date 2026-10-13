# Historical May-02 withoutBRG QRTC — protected full test re-eval — 2026-05-08

## Status

**PASS** — `EXIT_CODE:0`，preflight `HARDLOAD_PASS`（QRTC-pattern missing/unexpected = **0**），`#test=6438`。

## Environment

- **Conda:** `biopathnet_py310_torch201`

## Protocol

| Requirement | Recorded |
|-------------|----------|
| Split | `test` |
| `#test` | **6438** |
| Checkpoint | 与 valid 相同（May-02 `model_epoch_8.pth`） |
| Config | 与 valid 相同 |

## Paths

| Item | Path |
|------|------|
| Log | `logs/hist_may02_qrtc_protected_full_test_arbitration_20260508.log` |
| Launcher | `scripts/run_hist_may02_qrtc_protected_arbitration_eval_20260508.sh test` |

## Hard-load（摘录）

- 与 valid 运行相同：`HARDLOAD_PASS: non-QRTC missing/unexpected only`

## Metrics（full test）

| Metric | Value |
|--------|------:|
| AP | 0.952694 |
| AUROC | 0.949748 |
| Hits@1 | 0.341799 |
| Hits@3 | 0.448975 |
| Hits@10 | 0.574324 |
| Hits@20 | 0.640727 |
| Hits@50 | 0.728332 |
| Hits@100 | 0.789997 |
| MR | 261.621 |
| MRR | 0.419978 |

## Retention

**FORMAL_TRUSTED** — withoutBRG QRTC **test** 权威行（与 `WITHOUTBRG_QRTC_AUTHORITY_ARBITRATION_20260508.md` 一致）。
