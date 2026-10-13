# QRTC HR-only fused withBRG — full test metrics summary

- Generated: 2026-05-06T22:15:03+08:00
- Monitored PID: 82347
- Test log: `/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/logs/qrtc_hronly_fused_withbrg_formal_epoch8_full_test_metrics_only_20260506.log`
- Status: **SUCCESS** (metrics or TEST_METRICS_ONLY_EVAL_DONE)

## Parsed test metrics

```
22:10:25   ap: 0.986643
22:10:25   auroc: 0.985724
22:10:25   hits@1: 0.460158
22:10:25   hits@10: 0.730429
22:10:25   hits@100: 0.907891
22:10:25   hits@20: 0.793103
22:10:25   hits@3: 0.592498
22:10:25   hits@50: 0.866418
22:10:25   mr: 126.234
22:10:25   mrr: 0.550018
22:10:25   TEST_METRICS_ONLY_EVAL_DONE -> exit before prediction phase
```

## Log tail (after last Evaluate on test)

```
15:28:10   Evaluate on test
/root/miniconda3/envs/biopathnet_py310_torch201/lib/python3.10/site-packages/torch/functional.py:554: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /pytorch/aten/src/ATen/native/TensorShape.cpp:4322.)
  return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]
W0506 15:28:25.216000 82347 site-packages/torch/utils/cpp_extension.py:2425] TORCH_CUDA_ARCH_LIST is not set, all archs for visible cards are included for compilation. 
W0506 15:28:25.216000 82347 site-packages/torch/utils/cpp_extension.py:2425] If this is not desired, please set os.environ['TORCH_CUDA_ARCH_LIST'] to specific architectures.
22:10:25   ------------------------------
22:10:25   ap: 0.986643
22:10:25   auroc: 0.985724
22:10:25   hits@1: 0.460158
22:10:25   hits@10: 0.730429
22:10:25   hits@100: 0.907891
22:10:25   hits@20: 0.793103
22:10:25   hits@3: 0.592498
22:10:25   hits@50: 0.866418
22:10:25   mr: 126.234
22:10:25   mrr: 0.550018
22:10:25   TEST_METRICS_ONLY_EVAL_DONE -> exit before prediction phase
```
