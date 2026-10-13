# LncTarD-PPI QRTC-HR only withBRG Formal Epoch8 Full Test Status - 2026-05-08

## Verdict

VERDICT=LNCTARDPPI_QRTC_HRONLY_WITHBRG_FORMAL_EPOCH8_FULLTEST_PASS

## Evidence

- #test=609 expected from log
- Evaluate on test
- EXIT_CODE=0
- Full metrics present
- No automatic rank-pair started

## Log

/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/qrtc_hronly_withbrg_formal_epoch8_fulltest_20260508.log

## Metrics

```
          'metric': ('mr', 'mrr', 'hits@1', 'hits@3', 'hits@10', 'hits@100',
                     'hits@20', 'hits@50', 'auroc', 'ap'),
00:43:25   ap: 0.90108
00:43:25   auroc: 0.894475
00:43:25   hits@1: 0.0829228
00:43:25   hits@10: 0.395731
00:43:25   hits@100: 0.784072
00:43:25   hits@20: 0.514778
00:43:25   hits@3: 0.192939
00:43:25   hits@50: 0.674877
00:43:25   mr: 82.8292
00:43:25   mrr: 0.1793
```

## Watch log

/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/autoshutdown_after_qrtc_fulltest_20260508.log

## Next step

After reboot / next login, compare Clean vs QRTC and decide whether to run rank-pair.
