import json
import os
import sys
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

    print("Fetching a tiny valid batch...")
    valid_loader = solver.valid_loader
    batch = next(iter(valid_loader))
    batch = core.batch_to_device(batch, solver.device)
    
    kg_task = solver.model
    kg_task.eval()
    
    h_index = batch["graph"].edge_list[:4, 0]
    t_index = batch["graph"].edge_list[:4, 1]
    r_index = batch["graph"].edge_list[:4, 2]
    
    print("Running forward pass (should be extremely fast)...")
    results = []
    with torch.no_grad():
        preds = kg_task.model(kg_task.fact_graph, h_index, t_index, r_index)
        for i in range(len(h_index)):
            pos_t = t_index[i].item()
            pos_score = preds[i, pos_t].item()
            top_scores, top_indices = torch.topk(preds[i], 20)
            negatives = []
            for score, idx in zip(top_scores.tolist(), top_indices.tolist()):
                if idx != pos_t:
                    negatives.append({"neg_t": idx, "neg_score": round(score, 4), "delta": round(score - pos_score, 4)})
            results.append({"query_h": h_index[i].item(), "query_r": r_index[i].item(), "pos_t": pos_t, "pos_score": round(pos_score, 4), "top_negatives": negatives[:8]})
    
    out_file = "hard_negatives_dump.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Success! Dumped hard negatives to {out_file}")

if __name__ == "__main__":
    main()
