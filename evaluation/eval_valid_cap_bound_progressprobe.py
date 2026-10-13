import faulthandler
import sys
import runpy
import time

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

# ---------- scatter_min ----------
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

# ---------- bellmanford / forward ----------
_ORIG_BELLMANFORD = _bp_model.NBFNet.bellmanford
_ORIG_FORWARD = _bp_model.NBFNet.forward
_ORIG_PREDICT = _bp_task.KnowledgeGraphCompletionBiomed.predict

def _bellmanford_probe(self, *args, **kwargs):
    n = getattr(_bellmanford_probe, "_count", 0) + 1
    _bellmanford_probe._count = n
    t1 = time.time()
    out = _ORIG_BELLMANFORD(self, *args, **kwargs)
    dt = time.time() - t1
    print(f"BELLMANFORD_PROGRESS call={n} sec={dt:.6f} wall={_now():.3f}", flush=True)
    return out

def _forward_probe(self, *args, **kwargs):
    n = getattr(_forward_probe, "_count", 0) + 1
    _forward_probe._count = n
    t1 = time.time()
    out = _ORIG_FORWARD(self, *args, **kwargs)
    dt = time.time() - t1
    if n <= 20 or n in {50, 100, 200, 500, 1000}:
        print(f"FORWARD_PROGRESS call={n} sec={dt:.6f} wall={_now():.3f}", flush=True)
    return out

def _predict_probe(self, *args, **kwargs):
    n = getattr(_predict_probe, "_count", 0) + 1
    _predict_probe._count = n
    t1 = time.time()
    out = _ORIG_PREDICT(self, *args, **kwargs)
    dt = time.time() - t1
    print(f"PREDICT_PROGRESS call={n} sec={dt:.6f} wall={_now():.3f}", flush=True)
    return out

_bp_model.NBFNet.bellmanford = _bellmanford_probe
_bp_model.NBFNet.forward = _forward_probe
_bp_task.KnowledgeGraphCompletionBiomed.predict = _predict_probe

print("PROGRESS_PROBE_ON", flush=True)
runpy.run_path("<REDACTED_SERVER_PATH>", run_name="__main__")
