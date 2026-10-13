import faulthandler
import sys
import runpy
import time
import inspect

faulthandler.enable(file=sys.stderr, all_threads=True)
faulthandler.dump_traceback_later(60, repeat=True, file=sys.stderr)
print("FAULTHANDLER_STACKDUMP_ON", flush=True)

import torch
import torch_scatter
from biopathnet import model as _bp_model
from biopathnet import task as _bp_task

try:
    import torch_scatter.scatter as _ts_scatter_mod
except Exception:
    _ts_scatter_mod = None

_t0 = time.time()

def _now():
    return time.time() - _t0

# scatter_min probe
_ORIG_SCATTER_MIN = torch_scatter.scatter_min
def _scatter_min_probe(*args, **kwargs):
    n = getattr(_scatter_min_probe, "_count", 0) + 1
    _scatter_min_probe._count = n
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    t1 = time.time()
    out = _ORIG_SCATTER_MIN(*args, **kwargs)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    dt = time.time() - t1
    if n <= 20 or n in {50, 100, 200, 500, 1000, 2000, 5000, 10000}:
        print(f"SCATTER_MIN_PROGRESS call={n} sec={dt:.6f} wall={_now():.3f}", flush=True)
    return out

torch_scatter.scatter_min = _scatter_min_probe
if _ts_scatter_mod is not None:
    _ts_scatter_mod.scatter_min = _scatter_min_probe

# generic class patcher
def _patch_method(cls, method_name, tag):
    orig = getattr(cls, method_name, None)
    if not callable(orig):
        return False

    def wrapped(self, *args, __orig=orig, __tag=tag, **kwargs):
        n = getattr(wrapped, "_count", 0) + 1
        wrapped._count = n
        t1 = time.time()
        out = __orig(self, *args, **kwargs)
        dt = time.time() - t1
        if n <= 20 or n in {50, 100, 200, 500, 1000}:
            print(f"{__tag} call={n} sec={dt:.6f} wall={_now():.3f}", flush=True)
        return out

    setattr(cls, method_name, wrapped)
    return True

model_hits = []
for name, obj in vars(_bp_model).items():
    if inspect.isclass(obj):
        has_bf = callable(getattr(obj, "bellmanford", None))
        has_fw = callable(getattr(obj, "forward", None))
        if has_bf and has_fw:
            _patch_method(obj, "bellmanford", f"BELLMANFORD_PROGRESS[{name}]")
            _patch_method(obj, "forward", f"FORWARD_PROGRESS[{name}]")
            model_hits.append(name)

task_hits = []
for name, obj in vars(_bp_task).items():
    if inspect.isclass(obj):
        has_pred = callable(getattr(obj, "predict", None))
        if has_pred:
            _patch_method(obj, "predict", f"PREDICT_PROGRESS[{name}]")
            task_hits.append(name)

print("PROGRESS_PROBE_GENERIC_ON", flush=True)
print("MODEL_PATCHED =", model_hits, flush=True)
print("TASK_PATCHED =", task_hits, flush=True)

runpy.run_path("<REDACTED_SERVER_PATH>", run_name="__main__")
