# MEMORY_OFF_FULLTEST_MONITOR_STATUS

## 0. Time / Host
Sun May 10 16:05:26 CST 2026
autodl-container-16vw4zvw9r-9e9e4658

## 1. Target
Target: PC_KEGG withBRG QRTC-HR memory_off full test
Config: config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest_20260510.yaml
Log: paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_20260510.log

## 2. GPU
Sun May 10 16:05:26 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 595.58.03              Driver Version: 595.58.03      CUDA Version: 13.2     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA RTX PRO 6000 Blac...    On  |   00000000:5A:00.0 Off |                  Off |
| N/A   58C    P0            347W /  600W |    4661MiB /  97887MiB |     99%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A            2669      C   ...net_py310_torch201/bin/python       4652MiB |
+-----------------------------------------------------------------------------------------+

## 3. Relevant processes
2654 /bin/bash -O extglob -c snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap" && { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE -- cd /root/autodl-tmp/BioPathNet_fresh || exit 1 mkdir -p paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs  LOG="/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_20260510.log" : > "$LOG"  env -u EVAL_VALID_CAP -u EVAL_TEST_CAP \ EVAL_ONLY_SPLIT=test \ QRTC_ENABLE=1 \ QRTC_USE_MEMORY=0 \ QRTC_TOPK=2 \ FAMILY_CTX_ENABLE=0 \ FAMILY_CTX_WSA_ENABLE=0 \ FAMILY_CTX_RISK_GATE_ENABLE=0 \ FAMILY_CTX_CAND_RISK_ENABLE=0 \ QAES_ENABLE=0 \ QAM_ENABLE=0 \ RICS_ENABLE=0 \ WSA_ENABLE=0 \ WSL_ENABLE=0 \ UAEP_ENABLE=0 \ QRDP_M2_ENABLE=0 \ /root/miniconda3/envs/biopathnet_py310_torch201/bin/python script/eval_valid_only.py \   -c /root/autodl-tmp/BioPathNet_fresh/config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest_20260510.yaml \   --gpus '[0]' -s 1024 \   >> "$LOG" 2>&1  echo "EXIT_CODE:$?" >> "$LOG"
2669 /root/miniconda3/envs/biopathnet_py310_torch201/bin/python script/eval_valid_only.py -c /root/autodl-tmp/BioPathNet_fresh/config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest_20260510.yaml --gpus [0] -s 1024
48810 /bin/bash -O extglob -c snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap" && { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE -- cd /root/autodl-tmp/BioPathNet_fresh || exit 1  LOG="paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_20260510.log" CFG="config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest_20260510.yaml" OUT="paper1_q2_sci_package_20260428/qrtc_ablation_20260509/MEMORY_OFF_FULLTEST_MONITOR_STATUS_$(date +%Y%m%d_%H%M%S).md"  { echo "# MEMORY_OFF_FULLTEST_MONITOR_STATUS" echo echo "## 0. Time / Host" date hostname echo echo "## 1. Target" echo "Target: PC_KEGG withBRG QRTC-HR memory_off full test" echo "Config: $CFG" echo "Log: $LOG" echo echo "## 2. GPU" nvidia-smi || true echo echo "## 3. Relevant processes" pgrep -af "pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest|eval_valid_only.py|script/run.py|eval_test_metrics_only" || echo "NO_RELEVANT_PROCESS_FOUND" echo echo "## 4. Config sanity" if [ -f "$CFG" ]; then   echo "CFG_EXISTS=YES"   grep -nE "path:|include_factgraph|checkpoint:|num_negative|batch_size|num_epoch|smoke_skip_valid|EVAL_VALID_CAP|test|valid|output_dir" "$CFG" || true else   echo "CFG_EXISTS=NO" fi echo echo "## 5. Log file status" if [ -f "$LOG" ]; then   echo "LOG_EXISTS=YES"   stat "$LOG"   echo   echo "### Start / progress markers"   grep -nE "Evaluate on test|Evaluate on valid|#test|#valid|TEST_ONLY_EVAL_DONE|VALID_ONLY_EVAL_DONE|average|mrr|mr|hits|auroc|ap|Traceback|RuntimeError|CUDA out of memory|out of memory|Killed|EXIT_CODE" "$LOG" | tail -80 || true   echo   echo "### Last 120 log lines"   tail -120 "$LOG" else   echo "LOG_EXISTS=NO" fi echo echo "## 6. Quick verdict rule" echo "- If process exists + log mtime is recent + no Traceback/OOM/Killed: RUNNING_NORMAL_OR_PROGRESSING" echo "- If TEST_ONLY_EVAL_DONE / metrics / EXIT_CODE:0 appear: FULLTEST_FINISHED_NEED_CLOSURE" echo "- If no process + no completion marker: ABNORMAL_STOP_NEED_DIAGNOSIS" echo "- If process exists but log mtime stale for >30min: POSSIBLE_HANG_NEED_RECHECK" } | tee "$OUT"  echo echo "WROTE_MONITOR_STATUS=$OUT"
48825 /bin/bash -O extglob -c snap=$(command cat <&3) && builtin shopt -s extglob && builtin eval -- "$snap" && { builtin set +u 2>/dev/null || true; builtin eval "${__CURSOR_SANDBOX_ENV_RESTORE:-}" 2>/dev/null; builtin export PWD="$(builtin pwd)"; builtin shopt -s expand_aliases 2>/dev/null; builtin eval "$1"; }; COMMAND_EXIT_CODE=$?; dump_bash_state >&4; builtin exit $COMMAND_EXIT_CODE -- cd /root/autodl-tmp/BioPathNet_fresh || exit 1  LOG="paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_20260510.log" CFG="config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest_20260510.yaml" OUT="paper1_q2_sci_package_20260428/qrtc_ablation_20260509/MEMORY_OFF_FULLTEST_MONITOR_STATUS_$(date +%Y%m%d_%H%M%S).md"  { echo "# MEMORY_OFF_FULLTEST_MONITOR_STATUS" echo echo "## 0. Time / Host" date hostname echo echo "## 1. Target" echo "Target: PC_KEGG withBRG QRTC-HR memory_off full test" echo "Config: $CFG" echo "Log: $LOG" echo echo "## 2. GPU" nvidia-smi || true echo echo "## 3. Relevant processes" pgrep -af "pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest|eval_valid_only.py|script/run.py|eval_test_metrics_only" || echo "NO_RELEVANT_PROCESS_FOUND" echo echo "## 4. Config sanity" if [ -f "$CFG" ]; then   echo "CFG_EXISTS=YES"   grep -nE "path:|include_factgraph|checkpoint:|num_negative|batch_size|num_epoch|smoke_skip_valid|EVAL_VALID_CAP|test|valid|output_dir" "$CFG" || true else   echo "CFG_EXISTS=NO" fi echo echo "## 5. Log file status" if [ -f "$LOG" ]; then   echo "LOG_EXISTS=YES"   stat "$LOG"   echo   echo "### Start / progress markers"   grep -nE "Evaluate on test|Evaluate on valid|#test|#valid|TEST_ONLY_EVAL_DONE|VALID_ONLY_EVAL_DONE|average|mrr|mr|hits|auroc|ap|Traceback|RuntimeError|CUDA out of memory|out of memory|Killed|EXIT_CODE" "$LOG" | tail -80 || true   echo   echo "### Last 120 log lines"   tail -120 "$LOG" else   echo "LOG_EXISTS=NO" fi echo echo "## 6. Quick verdict rule" echo "- If process exists + log mtime is recent + no Traceback/OOM/Killed: RUNNING_NORMAL_OR_PROGRESSING" echo "- If TEST_ONLY_EVAL_DONE / metrics / EXIT_CODE:0 appear: FULLTEST_FINISHED_NEED_CLOSURE" echo "- If no process + no completion marker: ABNORMAL_STOP_NEED_DIAGNOSIS" echo "- If process exists but log mtime stale for >30min: POSSIBLE_HANG_NEED_RECHECK" } | tee "$OUT"  echo echo "WROTE_MONITOR_STATUS=$OUT"

## 4. Config sanity
CFG_EXISTS=YES
1:# PC_KEGG withBRG — QRTC memory_off ablation — full test only (no cap).
2:# Run: script/eval_valid_only.py with EVAL_ONLY_SPLIT=test + env contract (QRTC_* + module disables).
3:# Do not set EVAL_VALID_CAP / EVAL_TEST_CAP for formal metrics.
5:checkpoint: /root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_seed1024_epoch8/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-09-16-53-28-980276/model_epoch_8.pth
7:output_dir: paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_eval_20260510
11:  path: /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602
12:  include_factgraph: yes
26:  num_negative: 512
40:  batch_size: 16
43:  smoke_skip_valid: yes
44:  num_epoch: 8

## 5. Log file status
LOG_EXISTS=YES
  File: paper1_q2_sci_package_20260428/qrtc_ablation_20260509/logs/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_20260510.log
  Size: 8980      	Blocks: 24         IO Block: 4096   regular file
Device: 900h/2304d	Inode: 1106184786  Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-05-10 10:03:37.829528715 +0800
Modify: 2026-05-10 09:42:32.527512112 +0800
Change: 2026-05-10 09:42:32.527512112 +0800
 Birth: 2026-05-10 09:42:12.350798715 +0800

### Start / progress markers
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

### Last 120 log lines
EVAL_JIT_WARMUP: importing torchdrug.layers.functional (rspmm CUDA extension)...
EVAL_JIT_WARMUP: done.
paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_eval_20260510/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-10-09-42-14-980473
09:42:14   Working directory: paper1_q2_sci_package_20260428/qrtc_ablation_20260509/pc_kegg_withbrg_qrtc_memory_off_epoch8_fulltest_eval_20260510/KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-10-09-42-14-980473
09:42:14   Config file: /root/autodl-tmp/BioPathNet_fresh/config/q2_sci_pc_kegg_20260428/pc_kegg_qrtc_ablation_memory_off_withbrg_epoch8_fulltest_20260510.yaml
Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:   0%|          | 0/1884146 [00:00<?, ?it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:   6%|▌         | 113764/1884146 [00:00<00:01, 1137597.69it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  13%|█▎        | 239638/1884146 [00:00<00:01, 1208838.81it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  20%|█▉        | 367808/1884146 [00:00<00:01, 1242093.88it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  26%|██▋       | 495899/1884146 [00:00<00:01, 1257408.80it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  33%|███▎      | 624489/1884146 [00:00<00:00, 1267660.32it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  40%|███▉      | 753173/1884146 [00:00<00:00, 1274174.47it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  47%|████▋     | 881911/1884146 [00:00<00:00, 1278483.02it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  54%|█████▎    | 1009777/1884146 [00:00<00:00, 1278530.04it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  60%|██████    | 1137631/1884146 [00:00<00:00, 1263500.04it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  67%|██████▋   | 1264625/1884146 [00:01<00:00, 1265462.16it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  74%|███████▍  | 1393662/1884146 [00:01<00:00, 1273034.86it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  81%|████████  | 1522687/1884146 [00:01<00:00, 1278236.70it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  88%|████████▊ | 1651651/1884146 [00:01<00:00, 1281673.62it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt:  95%|█████████▍| 1780583/1884146 [00:01<00:00, 1283970.77it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train1.txt: 100%|██████████| 1884146/1884146 [00:01<00:00, 1268833.76it/s]
Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train2.txt:   0%|          | 0/22702 [00:00<?, ?it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/train2.txt: 100%|██████████| 22702/22702 [00:00<00:00, 1327668.95it/s]
Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/valid.txt:   0%|          | 0/3227 [00:00<?, ?it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/valid.txt: 100%|██████████| 3227/3227 [00:00<00:00, 1291755.97it/s]
Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/test.txt:   0%|          | 0/6438 [00:00<?, ?it/s]Loading /root/autodl-tmp/BioPathNet_fresh/data/PC_KEGG_0602/test.txt: 100%|██████████| 6438/6438 [00:00<00:00, 1305246.00it/s]
09:42:16   biomedical(
  #entity: 31410
  #relation: 14
  #triplet: 1916513
)
09:42:16   #train: 22702, #valid: 3227, #test: 6438
09:42:17   Preprocess training set
09:42:17   {'batch_size': 16,
 'class': 'core.Engine',
 'gpus': [0],
 'gradient_interval': 1,
 'log_interval': 100,
 'logger': 'logging',
 'num_worker': 0,
 'optimizer': {'amsgrad': False,
               'betas': (0.9, 0.999),
               'capturable': False,
               'class': 'optim.Adam',
               'decoupled_weight_decay': False,
               'differentiable': False,
               'eps': 1e-08,
               'foreach': None,
               'fused': None,
               'lr': 0.005,
               'maximize': False,
               'weight_decay': 0},
 'scheduler': None,
 'task': {'adversarial_temperature': 1,
          'class': 'tasks.KnowledgeGraphCompletionBiomed',
          'criterion': 'bce',
          'fact_ratio': None,
          'filtered_ranking': True,
          'full_batch_eval': False,
          'margin': 6,
          'metric': ('mr', 'mrr', 'hits@1', 'hits@3', 'hits@10', 'hits@100',
                     'hits@20', 'hits@50', 'auroc', 'ap'),
          'model': {'activation': 'relu',
                    'aggregate_func': 'pna',
                    'class': 'model.NBFNet',
                    'concat_hidden': False,
                    'dependent': True,
                    'edge_gate': False,
                    'gate_hidden_dim': None,
                    'hidden_dims': [32, 32, 32, 32, 32, 32],
                    'input_dim': 32,
                    'layer_norm': True,
                    'message_func': 'distmult',
                    'mokgr_l_enable': False,
                    'mokgr_l_max_hop': None,
                    'mokgr_l_min_hop': 2,
                    'mokgr_l_num_experts': 3,
                    'mokgr_l_temperature': 1.1,
                    'num_beam': 10,
                    'num_mlp_layer': 2,
                    'num_relation': tensor(14),
                    'path_topk': 10,
                    'remove_one_hop': False,
                    'router_hidden_dim': 64,
                    'router_residual_init': -2.0,
                    'router_temperature': 1.0,
                    'router_type_vocab_cap': 64,
                    'short_cut': True,
                    'symmetric': False,
                    'use_evidence_router': False},
          'num_negative': 512,
          'sample_weight': False,
          'strict_negative': True},
 'test_set': {'class': 'dataset.Subset',
              'dataset': {'class': 'datasets.biomedical',
                          'entity_files': None,
                          'fact_as_train': False,
                          'files': ['train1.txt', 'train2.txt', 'valid.txt',
                                    'test.txt'],
                          'include_factgraph': True,
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

## 6. Quick verdict rule
- If process exists + log mtime is recent + no Traceback/OOM/Killed: RUNNING_NORMAL_OR_PROGRESSING
- If TEST_ONLY_EVAL_DONE / metrics / EXIT_CODE:0 appear: FULLTEST_FINISHED_NEED_CLOSURE
- If no process + no completion marker: ABNORMAL_STOP_NEED_DIAGNOSIS
- If process exists but log mtime stale for >30min: POSSIBLE_HANG_NEED_RECHECK
