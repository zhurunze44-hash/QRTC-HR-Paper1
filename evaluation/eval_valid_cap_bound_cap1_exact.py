import os
import sys
import json
import pprint
import random
import torch
import numpy as np
from torch.utils import data as torch_data

from torchdrug import core
from torchdrug.utils import comm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 关键：必须先 import 这些模块，触发自定义类注册到 Registry
from biopathnet import dataset, layer, model, task, util  # noqa: F401

logger = None

def solver_load_bound(solver, checkpoint, load_optimizer=False):
    global logger
    logger.warning("Load checkpoint from %s" % checkpoint)
    checkpoint = os.path.expanduser(checkpoint)
    state = torch.load(checkpoint, map_location=solver.device)

    if "model" not in state:
        raise KeyError("checkpoint missing 'model' key")

    # 不把 checkpoint 里的图缓冲回灌到当前 solver
    for k in [
        "fact_graph",
        "fact_graph_supervision",
        "graph",
        "train_graph",
        "valid_graph",
        "test_graph",
        "full_valid_graph",
        "full_test_graph",
    ]:
        state["model"].pop(k, None)

    incompatible = solver.model.load_state_dict(state["model"], strict=False)
    logger.warning("missing_keys = %s", list(incompatible.missing_keys))
    logger.warning("unexpected_keys = %s", list(incompatible.unexpected_keys))

    if load_optimizer and "optimizer" in state:
        solver.optimizer.load_state_dict(state["optimizer"])
        for opt_state in solver.optimizer.state.values():
            for k, v in opt_state.items():
                if isinstance(v, torch.Tensor):
                    opt_state[k] = v.to(solver.device)

    comm.synchronize()

def get_num_edge(g):
    if g is None:
        return None
    if hasattr(g, "num_edge"):
        try:
            return int(g.num_edge)
        except Exception:
            pass
    if hasattr(g, "edge_list"):
        try:
            return int(len(g.edge_list))
        except Exception:
            pass
    return None

def main():
    global logger
    args, vars = util.parse_args()
    try:
        _forced = {}
        for _k in list(vars(args).keys()):
            _low = _k.lower()
            if 'cap' in _low and any(x in _low for x in ['valid', 'mini', 'bound', 'eval']):
                setattr(args, _k, 1)
                _forced[_k] = getattr(args, _k)
        print('FORCED_CAP_ARGS =', _forced)
    except Exception as _e:
        print('FORCED_CAP_ARGS_ERROR =', repr(_e))
    cfg = util.load_config(args.config, context=vars)
    working_dir = util.create_working_directory(cfg)

    seed_rank = int(args.seed) + int(comm.get_rank())
    random.seed(int(args.seed))
    np.random.seed(int(args.seed))
    torch.manual_seed(seed_rank)

    logger = util.get_root_logger()
    logger.warning("Working directory: %s", working_dir)
    logger.warning("Config file: %s", args.config)
    logger.warning("Seed: %d", seed_rank)
    logger.warning(pprint.pformat(cfg))

    # 按原始完整配置构建，不改 split
    ds = core.Configurable.load_config_dict(cfg.dataset)
    solver = util.build_solver(cfg, ds)

    if not hasattr(cfg, "checkpoint"):
        raise ValueError("cfg.checkpoint is required")

    solver_load_bound(solver, cfg.checkpoint, load_optimizer=False)

    valid_cap = int(os.environ.get("VALID_CAP", "16"))
    eval_bs = int(os.environ.get("EVAL_BATCH_SIZE", "1"))

    original_valid = solver.valid_set
    cap = min(valid_cap, len(original_valid))
    solver.valid_set = torch_data.Subset(original_valid, list(range(cap)))
    solver.batch_size = eval_bs

    if hasattr(solver.model, "split"):
        solver.model.split = "valid"

    info = {
        "valid_cap_requested": valid_cap,
        "valid_cap_used": cap,
        "eval_batch_size": eval_bs,
        "valid_set_len_after_cap": len(solver.valid_set),
        "fact_graph_num_edge": get_num_edge(getattr(solver.model, "fact_graph", None)),
        "valid_graph_num_edge": get_num_edge(getattr(solver.model, "valid_graph", None)),
        "full_valid_graph_num_edge": get_num_edge(getattr(solver.model, "full_valid_graph", None)),
    }
    logger.warning("BOUND_MINI_VALID_INFO = %s", json.dumps(info, ensure_ascii=False))

    metric = solver.evaluate("valid")
    metric_out = {k: float(v) for k, v in metric.items()}

    out_json = os.path.join(working_dir, "mini_valid_metrics.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(
            {
                "info": info,
                "metric": metric_out,
                "config": args.config,
                "checkpoint": cfg.checkpoint,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    logger.warning("WROTE %s", out_json)
    print(json.dumps(metric_out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
