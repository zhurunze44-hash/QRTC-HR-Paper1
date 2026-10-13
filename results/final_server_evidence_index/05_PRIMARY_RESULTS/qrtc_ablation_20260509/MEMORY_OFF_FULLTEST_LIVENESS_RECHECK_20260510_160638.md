# MEMORY_OFF_FULLTEST_LIVENESS_RECHECK

Config: config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest_20260510.yaml
Log: paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_20260510.log
Detected PID: 2654

Rule:
- CPU total_ticks increases OR pmon shows PID GPU util: ACTIVE_SILENT_EVAL
- PID gone + no done marker: ABNORMAL_STOP_NEED_DIAGNOSIS
- PID exists but CPU ticks/context switches do not move and pmon cannot attribute GPU util: POSSIBLE_HANG_NEED_SECOND_RECHECK
- TEST_ONLY_EVAL_DONE / metrics / EXIT_CODE:0 in log: FULLTEST_FINISHED_NEED_CLOSURE

## SAMPLE T0
Sun May 10 16:06:38 CST 2026

PID=2654
   PID   PPID     ELAPSED     TIME %CPU %MEM STAT WCHAN                            CMD
  2654   1677    06:24:26 00:00:00  0.0  0.0 Ss   do_wait                          /bin/bash -O extglob -c snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap" && { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE -- cd /root/autodl-tmp/BioPathNet_fresh || exit 1 mkdir -p paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs  LOG="/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_20260510.log" : > "$LOG"  env -u EVAL_VALID_CAP -u EVAL_TEST_CAP \ EVAL_ONLY_SPLIT=test \ QRTC_ENABLE=1 \ QRTC_USE_MEMORY=0 \ QRTC_TOPK=2 \ FAMILY_CTX_ENABLE=0 \ FAMILY_CTX_WSA_ENABLE=0 \ FAMILY_CTX_RISK_GATE_ENABLE=0 \ FAMILY_CTX_CAND_RISK_ENABLE=0 \ QAES_ENABLE=0 \ QAM_ENABLE=0 \ RICS_ENABLE=0 \ WSA_ENABLE=0 \ WSL_ENABLE=0 \ UAEP_ENABLE=0 \ QRDP_M2_ENABLE=0 \ /root/miniconda3/envs/biopathnet_py310_torch201/bin/python script/eval_valid_only.py \   -c /root/autodl-tmp/BioPathNet_fresh/config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest_20260510.yaml \   --gpus '[0]' -s 1024 \   >> "$LOG" 2>&1  echo "EXIT_CODE:$?" >> "$LOG"

### /proc status key lines
State:	S (sleeping)
VmRSS:	    3508 kB
Threads:	1
voluntary_ctxt_switches:	17
nonvoluntary_ctxt_switches:	0

### CPU ticks
utime_ticks=0 stime_ticks=0 total_ticks=0

### IO
syscr: 152
syscw: 13
read_bytes: 0
write_bytes: 0
cancelled_write_bytes: 0

### fd 0/1/2
fd/0 -> socket:[446723456]
fd/1 -> socket:[446723458]
fd/2 -> socket:[446723460]

### wchan
do_wait
### log stat
  File: paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_20260510.log
  Size: 8980      	Blocks: 24         IO Block: 4096   regular file
Device: 900h/2304d	Inode: 1106184786  Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-05-10 10:03:37.829528715 +0800
Modify: 2026-05-10 09:42:32.527512112 +0800
Change: 2026-05-10 09:42:32.527512112 +0800
 Birth: 2026-05-10 09:42:12.350798715 +0800

last 30 lines:
                          'path': '/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602',
                          'verbose': 1},
              'indices': range(1910075, 1916513)},
 'train_set': {'class': 'dataset.Subset',
               'dataset': {'class': 'datasets.biomedical',
                           'entity_files': None,
                           'fact_as_train': False,
                           'files': ['train1.txt', 'train2.txt', 'valid.txt',
                                     'test.txt'],
                           'include_factgraph': True,
                           'path': '/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602',
                           'verbose': 1},
               'indices': range(1884146, 1906848)},
 'valid_set': {'class': 'dataset.Subset',
               'dataset': {'class': 'datasets.biomedical',
                           'entity_files': None,
                           'fact_as_train': False,
                           'files': ['train1.txt', 'train2.txt', 'valid.txt',
                                     'test.txt'],
                           'include_factgraph': True,
                           'path': '/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602',
                           'verbose': 1},
               'indices': range(1906848, 1910075)}}
09:42:17   Load checkpoint from /root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-09-16-53-28-980276/model_epoch_8.pth
09:42:18   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
09:42:18   Evaluate on test
/root/miniconda3/envs/biopathnet_py310_torch201/lib/python3.10/site-packages/torch/functional.py:554: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /pytorch/aten/src/ATen/native/TensorShape.cpp:4322.)
  return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]
W0510 09:42:32.529000 2669 site-packages/torch/utils/cpp_extension.py:2425] TORCH_CUDA_ARCH_LIST is not set, all archs for visible cards are included for compilation. 
W0510 09:42:32.529000 2669 site-packages/torch/utils/cpp_extension.py:2425] If this is not desired, please set os.environ['TORCH_CUDA_ARCH_LIST'] to specific architectures.

### nvidia-smi compute apps
2669, /root/miniconda3/envs/biopathnet_py310_torch201/bin/python, 4652 MiB

### nvidia-smi pmon short sample
# gpu         pid   type     sm    mem    enc    dec    jpg    ofa     fb   ccpm    command 
# Idx           #    C/G      %      %      %      %      %      %     MB     MB    name 
    0       2669     C     98     61      -      -      -      -   4652      0    python         
    0       2669     C     98     61      -      -      -      -   4652      0    python         
    0       2669     C     98     61      -      -      -      -   4652      0    python         

## sleep 90s before second sample

## SAMPLE T1
Sun May 10 16:08:10 CST 2026

PID=2654
   PID   PPID     ELAPSED     TIME %CPU %MEM STAT WCHAN                            CMD
  2654   1677    06:25:58 00:00:00  0.0  0.0 Ss   do_wait                          /bin/bash -O extglob -c snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap" && { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE -- cd /root/autodl-tmp/BioPathNet_fresh || exit 1 mkdir -p paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs  LOG="/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_20260510.log" : > "$LOG"  env -u EVAL_VALID_CAP -u EVAL_TEST_CAP \ EVAL_ONLY_SPLIT=test \ QRTC_ENABLE=1 \ QRTC_USE_MEMORY=0 \ QRTC_TOPK=2 \ FAMILY_CTX_ENABLE=0 \ FAMILY_CTX_WSA_ENABLE=0 \ FAMILY_CTX_RISK_GATE_ENABLE=0 \ FAMILY_CTX_CAND_RISK_ENABLE=0 \ QAES_ENABLE=0 \ QAM_ENABLE=0 \ RICS_ENABLE=0 \ WSA_ENABLE=0 \ WSL_ENABLE=0 \ UAEP_ENABLE=0 \ QRDP_M2_ENABLE=0 \ /root/miniconda3/envs/biopathnet_py310_torch201/bin/python script/eval_valid_only.py \   -c /root/autodl-tmp/BioPathNet_fresh/config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest_20260510.yaml \   --gpus '[0]' -s 1024 \   >> "$LOG" 2>&1  echo "EXIT_CODE:$?" >> "$LOG"

### /proc status key lines
State:	S (sleeping)
VmRSS:	    3508 kB
Threads:	1
voluntary_ctxt_switches:	17
nonvoluntary_ctxt_switches:	0

### CPU ticks
utime_ticks=0 stime_ticks=0 total_ticks=0

### IO
syscr: 152
syscw: 13
read_bytes: 0
write_bytes: 0
cancelled_write_bytes: 0

### fd 0/1/2
fd/0 -> socket:[446723456]
fd/1 -> socket:[446723458]
fd/2 -> socket:[446723460]

### wchan
do_wait
### log stat
  File: paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_20260510.log
  Size: 8980      	Blocks: 24         IO Block: 4096   regular file
Device: 900h/2304d	Inode: 1106184786  Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-05-10 10:03:37.829528715 +0800
Modify: 2026-05-10 09:42:32.527512112 +0800
Change: 2026-05-10 09:42:32.527512112 +0800
 Birth: 2026-05-10 09:42:12.350798715 +0800

last 30 lines:
                          'path': '/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602',
                          'verbose': 1},
              'indices': range(1910075, 1916513)},
 'train_set': {'class': 'dataset.Subset',
               'dataset': {'class': 'datasets.biomedical',
                           'entity_files': None,
                           'fact_as_train': False,
                           'files': ['train1.txt', 'train2.txt', 'valid.txt',
                                     'test.txt'],
                           'include_factgraph': True,
                           'path': '/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602',
                           'verbose': 1},
               'indices': range(1884146, 1906848)},
 'valid_set': {'class': 'dataset.Subset',
               'dataset': {'class': 'datasets.biomedical',
                           'entity_files': None,
                           'fact_as_train': False,
                           'files': ['train1.txt', 'train2.txt', 'valid.txt',
                                     'test.txt'],
                           'include_factgraph': True,
                           'path': '/root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602',
                           'verbose': 1},
               'indices': range(1906848, 1910075)}}
09:42:17   Load checkpoint from /root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-09-16-53-28-980276/model_epoch_8.pth
09:42:18   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
09:42:18   Evaluate on test
/root/miniconda3/envs/biopathnet_py310_torch201/lib/python3.10/site-packages/torch/functional.py:554: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /pytorch/aten/src/ATen/native/TensorShape.cpp:4322.)
  return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]
W0510 09:42:32.529000 2669 site-packages/torch/utils/cpp_extension.py:2425] TORCH_CUDA_ARCH_LIST is not set, all archs for visible cards are included for compilation. 
W0510 09:42:32.529000 2669 site-packages/torch/utils/cpp_extension.py:2425] If this is not desired, please set os.environ['TORCH_CUDA_ARCH_LIST'] to specific architectures.

### nvidia-smi compute apps
2669, /root/miniconda3/envs/biopathnet_py310_torch201/bin/python, 4652 MiB

### nvidia-smi pmon short sample
# gpu         pid   type     sm    mem    enc    dec    jpg    ofa     fb   ccpm    command 
# Idx           #    C/G      %      %      %      %      %      %     MB     MB    name 
    0       2669     C     98     60      -      -      -      -   4652      0    python         
    0       2669     C     98     61      -      -      -      -   4652      0    python         
    0       2669     C     98     61      -      -      -      -   4652      0    python         

## Completion / error markers
3:paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_eval_20260510/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-10-09-42-14-980473
4:09:42:14   Working directory: paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_eval_20260510/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-10-09-42-14-980473
15:09:42:16   #train: 22702, #valid: 3227, #test: 6438
26:               'capturable': False,
38:          'class': 'tasks.KnowledgeGraphCompletionBiomed',
44:          'metric': ('mr', 'mrr', 'hits@1', 'hits@3', 'hits@10', 'hits@100',
45:                     'hits@20', 'hits@50', 'auroc', 'ap'),
70:                    'router_type_vocab_cap': 64,
83:                          'include_factgraph': True,
93:                           'include_factgraph': True,
103:                           'include_factgraph': True,
107:09:42:17   Load checkpoint from /root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-09-16-53-28-980276/model_epoch_8.pth
109:09:42:18   Evaluate on test
110:/root/miniconda3/envs/biopathnet_py310_torch201/lib/python3.10/site-packages/torch/functional.py:554: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /pytorch/aten/src/ATen/native/TensorShape.cpp:4322.)
