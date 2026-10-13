# LncTarD-PPI QRTC-HR Full Valid Monitor Final Report - 2026-05-08

## Verdict

FINAL_VERDICT=COMPLETED_PASS

## Paths

Config:
`config/knowledge_graph/biomedical/lnctardppi_qrtc_hronly_withbrg_formal_epoch8_fullvalid_20260508.yaml`

Log:
`/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/qrtc_hronly_withbrg_formal_epoch8_fullvalid_20260508.log`

PID file:
`/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/qrtc_hronly_withbrg_formal_epoch8_fullvalid_20260508.pid`

Monitor log:
`/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/logs/watch_qrtc_hronly_withbrg_formal_epoch8_fullvalid_20260508.log`

Status card:
`/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/LNCTARDPPI_QRTC_HRONLY_WITHBRG_FORMAL_EPOCH8_FULLVALID_STATUS_20260508.md`

## Evidence

### Valid count line

```
19:25:03   #train: 4867, #valid: 608, #test: 609
```

### Checkpoint line

```
19:25:04   Load checkpoint from /root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/lnctardppi_qrtc_hr_full_closure_20260508/qrtc_hronly_withbrg_formal_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-08-18-52-51-685204/model_epoch_8.pth
```

### Metrics tail

```
          'metric': ('mr', 'mrr', 'hits@1', 'hits@3', 'hits@10', 'hits@100',
                     'hits@20', 'hits@50', 'auroc', 'ap'),
21:56:37   ap: 0.894171
21:56:37   auroc: 0.884695
21:56:37   hits@1: 0.100329
21:56:37   hits@10: 0.369243
21:56:37   hits@100: 0.768914
21:56:37   hits@20: 0.483553
21:56:37   hits@3: 0.194901
21:56:37   hits@50: 0.657895
21:56:37   mr: 86.3035
21:56:37   mrr: 0.187343
```

### Exit line

```
EXIT_CODE:0
EXIT_CODE:0
```

### Error tail

```
NO_ERROR_PATTERN_FOUND
```

## Rule

No full test, no rank-pair, no retrain, no config/model edit was launched by this monitor.
