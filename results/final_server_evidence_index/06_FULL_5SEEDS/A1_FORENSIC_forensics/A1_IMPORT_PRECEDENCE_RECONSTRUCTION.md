# A1 Import Precedence Reconstruction
UTC: 2026-10-02T09:40:20Z

## Cold-start launcher (method bound)
```
exec python /.../QRTC_HR_SOURCE_RESTORE_20260908/script/run.py -c CFG --gpus '[0]' -s SEED
```

## Resolution order at process start
1. `sys.path[0]` = `.../SOURCE_RESTORE/script` (directory containing run.py)
2. standard site / stdlib entries
3. `run.py` L14: `sys.path.append(dirname(dirname(__file__)))` → **SOURCE_RESTORE root at END**
4. After `create_working_directory`: `os.chdir(unique_timestamp_workdir)` under `runs/<cell>/...`

## Critical implication
Because the authority root is **appended**, not `insert(0)`, any earlier `biopathnet` on `sys.path` / `PYTHONPATH` would win.

## What we can prove
- Formal env has **no** site-packages `biopathnet` now.
- Completed-cell exception stacks that mention biopathnet resolve **only** under SOURCE_RESTORE (never WORK/worktree/site-packages/biopathnet).
- SOURCE_RESTORE scientific file SHAs match `SOURCE_IDENTITY_FREEZE` (20260924); mtimes May-2026 (unchanged during A1).

## What we cannot prove
- Quiet winning processes never logged `module.__file__`.
- Historical ambient `PYTHONPATH` at Sep 25–30.
- Therefore **no cell reaches FULLY_BOUND__SOURCE_RESTORE**.
