# LncTarD-PPI QRTC Full Test — Launcher First-Attempt Audit — 2026-05-08

## Verdict tag

**FIRST_LAUNCH_FAIL_SUPERSEDED_BY_CONDA_RETRY**

## What failed (first attempt)

- **Symptom:** `ModuleNotFoundError: No module named 'torchdrug'`
- **Root cause:** The first `nohup` launcher invoked **system Python** because **`conda activate biopathnet_py310_torch201` was missing** from the full-test run wrapper.
- **What this is not:** This is **not** a QRTC model failure, **not** an `eval_valid_only.py` logic failure, **not** a checkpoint load failure, and **not** a dataset path failure.

## Fix applied (superseding launch)

- `source /root/miniconda3/etc/profile.d/conda.sh`
- `conda activate biopathnet_py310_torch201`
- `export WORLD_SIZE=1`
- `set +e` / `set -e` around `python script/eval_valid_only.py` so `EXIT_CODE` is always emitted even on failure.

## Authoritative run for results

- **Treat as current valid full test:** the **conda-corrected** background run whose log shows **`Load checkpoint`** then **`Evaluate on test`** (post-retry timeline).
- **Do not** treat the superseded first segment as the eval outcome.

## Auditing rule for mixed logs

If the full-test log file ever contains **both** the early `ModuleNotFoundError: torchdrug` block **and** a later successful-looking tail:

- The **final full-test status card must not** scan the entire mixed file and declare **FAIL** solely from that **early superseded** segment.
- **PASS/FAIL** for the formal full test must be judged from the **current effective run** (from the post-retry **`Load checkpoint` / `Evaluate on test`** anchor onward), including **metrics** and **`EXIT_CODE:0`**.

## Scope

No rank-pair, no retrain, no eval config edit as part of this note.
