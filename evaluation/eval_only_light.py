import os
import sys
import copy
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
    solver.model.load_state_dict(state["model"], strict=False)
    if "optimizer" in state and solver.optimizer is not None:
        try:
            solver.optimizer.load_state_dict(state["optimizer"])
        except Exception as e:
            logger.warning("Skip optimizer state load: %s" % e)
    return solver


def load_dataset_and_solver_single(cfg, logger, test_file="test.txt"):
    cfg_local = copy.deepcopy(cfg)
    if "files" not in cfg_local.dataset:
        cfg_local.dataset["files"] = ["train1.txt", "train2.txt", "valid.txt", test_file]

    dataset = core.Configurable.load_config_dict(cfg_local.dataset)
    train_set, valid_set, test_set = dataset.split()

    solver = eval_mod.build_solver(cfg_local, dataset, train_set, valid_set, test_set)
    if "checkpoint" in cfg_local:
        solver_load_local(cfg_local.checkpoint, solver, logger)

    return cfg_local, solver, dataset


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

    cfg_eval, solver, dataset = load_dataset_and_solver_single(cfg, logger, "test.txt")

    solver.model.split = "valid"
    logger.warning(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    logger.warning("Light eval on valid only")
    solver.evaluate("valid")

    solver.model.split = "test"
    logger.warning(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    logger.warning("Light eval on test only")
    solver.evaluate("test")
