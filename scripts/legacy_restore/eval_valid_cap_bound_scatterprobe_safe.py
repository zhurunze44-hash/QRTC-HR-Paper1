import faulthandler
import sys
import runpy

faulthandler.enable(file=sys.stderr, all_threads=True)
faulthandler.dump_traceback_later(60, repeat=True, file=sys.stderr)
print("FAULTHANDLER_STACKDUMP_ON", flush=True)

import torch_scatter

try:
    import torch_scatter.scatter as _ts_scatter_mod
except Exception:
    _ts_scatter_mod = None

_ORIG_SCATTER_MIN = torch_scatter.scatter_min

def _shape(x):
    try:
        return tuple(x.shape)
    except Exception:
        return None

def _scalar(x):
    try:
        if x is None:
            return None
        if hasattr(x, "item"):
            return x.item()
        return x
    except Exception:
        return "ERR"

def _scatter_min_probe(*args, **kwargs):
    if not getattr(_scatter_min_probe, "_done", False):
        _scatter_min_probe._done = True
        src = args[0] if len(args) > 0 else kwargs.get("src", None)
        index = args[1] if len(args) > 1 else kwargs.get("index", None)
        dim = args[2] if len(args) > 2 else kwargs.get("dim", None)
        out = args[3] if len(args) > 3 else kwargs.get("out", None)
        dim_size = args[4] if len(args) > 4 else kwargs.get("dim_size", None)
        fill_value = args[5] if len(args) > 5 else kwargs.get("fill_value", None)

        info = {
            "src_shape": _shape(src),
            "src_dtype": str(getattr(src, "dtype", None)),
            "src_device": str(getattr(src, "device", None)),
            "src_numel": int(src.numel()) if hasattr(src, "numel") else None,
            "index_shape": _shape(index),
            "index_dtype": str(getattr(index, "dtype", None)),
            "index_device": str(getattr(index, "device", None)),
            "index_numel": int(index.numel()) if hasattr(index, "numel") else None,
            "index_min": _scalar(index.min()) if hasattr(index, "numel") and index.numel() > 0 else None,
            "index_max": _scalar(index.max()) if hasattr(index, "numel") and index.numel() > 0 else None,
            "dim": dim,
            "out_shape": _shape(out) if out is not None else None,
            "dim_size": dim_size,
            "fill_value": fill_value,
        }
        print("SCATTER_MIN_MONKEYPATCH_ON", flush=True)
        print("SCATTER_MIN_PROBE =", info, flush=True)

    return _ORIG_SCATTER_MIN(*args, **kwargs)

torch_scatter.scatter_min = _scatter_min_probe
if _ts_scatter_mod is not None:
    _ts_scatter_mod.scatter_min = _scatter_min_probe

runpy.run_path("<REDACTED_SERVER_PATH>", run_name="__main__")
