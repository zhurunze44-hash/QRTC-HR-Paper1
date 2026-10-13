import os
import sys
import copy
import time
import torch

from torchdrug import core
from torchdrug.utils import comm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from biopathnet import util

import script.eval_and_predict as eval_mod


def solver_load_local(checkpoint, solver, logger):
    checkpoint = os.path.expanduser(checkpoint)
    logger.warning("Load checkpoint from %s" % checkpoint)
    state = torch.load(checkpoint, map_location=torch.device("cpu"))
    model_state = state["model"] if isinstance(state, dict) and "model" in state else state
    solver.model.load_state_dict(model_state, strict=False)
    if isinstance(state, dict) and "optimizer" in state and solver.optimizer is not None:
        try:
            solver.optimizer.load_state_dict(state["optimizer"])
        except Exception as e:
            logger.warning("Skip optimizer state load: %s" % e)
    return solver


def cap_subset(subset_obj, cap):
    if cap is None or cap <= 0:
        return subset_obj

    # torchdrug / dataset.Subset 路径
    if hasattr(subset_obj, "indices"):
        new_subset = copy.copy(subset_obj)
        idx = subset_obj.indices
        if isinstance(idx, range):
            idx = list(idx)
        else:
            idx = list(idx)
        new_subset.indices = idx[:cap]
        return new_subset

    # fallback
    from torch.utils.data import Subset
    return Subset(subset_obj, list(range(min(cap, len(subset_obj)))))


def build_solver_for_mini_valid(cfg, logger, valid_cap, test_file="test.txt"):
    cfg_local = copy.deepcopy(cfg)
    if "files" not in cfg_local.dataset:
        cfg_local.dataset["files"] = ["train1.txt", "train2.txt", "valid.txt", test_file]

    dataset = core.Configurable.load_config_dict(cfg_local.dataset)
    train_set, valid_set, test_set = dataset.split()

    valid_set = cap_subset(valid_set, valid_cap)

    logger.warning("Mini valid cap = %d" % valid_cap)
    logger.warning("Mini valid actual size = %d" % len(valid_set))

    solver = eval_mod.build_solver(cfg_local, dataset, train_set, valid_set, test_set)
    if "checkpoint" in cfg_local:
        solver_load_local(cfg_local.checkpoint, solver, logger)

    return solver


if __name__ == "__main__":
    args, vars = util.parse_args()
    cfg = util.load_config(args.config, context=vars)
    working_dir = util.create_working_directory(cfg)
    print(working_dir)

    torch.manual_seed(args.seed + comm.get_rank())

    logger = util.get_root_logger()
    logger.warning("Working directory: %s" % working_dir)
    if comm.get_rank() == 0:
        logger.warning("Config file: %s" % args.config)

    valid_cap = int(os.environ.get("VALID_CAP", "16"))
    solver = build_solver_for_mini_valid(cfg, logger, valid_cap, "test.txt")

    solver.model.split = "valid"
    logger.warning(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    logger.warning("Mini valid only evaluation start")
    start = time.time()
    metric = solver.evaluate("valid")
    elapsed = time.time() - start
    logger.warning("Mini valid elapsed_sec = %.2f" % elapsed)
    logger.warning("Mini valid metric = %s" % metric)
