import os
import sys
import math
import pprint

import torch

from torchdrug import core, models
from torchdrug.utils import comm

import numpy as np
import random

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from biopathnet import dataset, layer, model, task, util

def solver_load(checkpoint, load_optimizer=True):

    if comm.get_rank() == 0:
        logger.warning("Load checkpoint from %s" % checkpoint)
    checkpoint = os.path.expanduser(checkpoint)
    state = torch.load(checkpoint, map_location=solver.device, weights_only=False)
    # some issues with loading back the graphs if present
    # remove
    state["model"].pop("fact_graph", 0)
    state["model"].pop("fact_graph_supervision", 0)
    state["model"].pop("graph", 0)
    state["model"].pop("train_graph", 0)
    state["model"].pop("valid_graph", 0)
    state["model"].pop("test_graph", 0)
    state["model"].pop("full_valid_graph", 0)
    state["model"].pop("full_test_graph", 0)
    # load without
    solver.model.load_state_dict(state["model"], strict=False)


    if load_optimizer and "optimizer" in state:
        solver.optimizer.load_state_dict(state["optimizer"])
        for state in solver.optimizer.state.values():
            for k, v in state.items():
                if isinstance(v, torch.Tensor):
                    state[k] = v.to(solver.device)
    elif comm.get_rank() == 0:
        logger.warning("Skip optimizer state load")

    comm.synchronize()


def _get_smoke_skip_valid(train_cfg):
    if hasattr(train_cfg, "get"):
        return bool(train_cfg.get("smoke_skip_valid", False))
    return bool(getattr(train_cfg, "smoke_skip_valid", False))

def _get_resume_mode():
    mode = os.environ.get("RUN_RESUME_MODE", "full").strip().lower()
    if mode not in {"full", "model_only", "fresh"}:
        raise ValueError(f"Unsupported RUN_RESUME_MODE: {mode}")
    return mode

def _build_solver_without_auto_resume(cfg, dataset, bypass_auto_resume=False):
    if not bypass_auto_resume:
        return util.build_solver(cfg, dataset)
    _orig_solver_load = util.solver_load
    _orig_checkpoint = getattr(cfg, "checkpoint", None)
    def _skip_build_solver_load(solver, checkpoint, *args, **kwargs):
        if comm.get_rank() == 0:
            logger.warning("Build-solver bypass: skip util.solver_load(%s) during explicit resume flow" % checkpoint)
        return
    cfg.checkpoint = None
    util.solver_load = _skip_build_solver_load
    try:
        return util.build_solver(cfg, dataset)
    finally:
        util.solver_load = _orig_solver_load
        cfg.checkpoint = _orig_checkpoint

def train_and_validate(cfg, solver):
    smoke_skip_valid = _get_smoke_skip_valid(cfg.train)
    if cfg.train.num_epoch == 0:
        return

    step = math.ceil(cfg.train.num_epoch / 10)
    best_result = float("-inf")
    best_epoch = -1

    for i in range(0, cfg.train.num_epoch, step):
        kwargs = cfg.train.copy()
        # SMOKE_SKIP_VALID_POP_V1
        kwargs.pop("smoke_skip_valid", None)
        kwargs["num_epoch"] = min(step, cfg.train.num_epoch - i)
        solver.model.split = "train"
        if os.environ.get("EPB_ONLY", "0") == "1":
            import torch
            frozen = 0
            trainable = 0
            for n, q in solver.model.named_parameters():
                flag = ("epb_router" in n)
                q.requires_grad = flag
                if flag:
                    trainable += q.numel()
                else:
                    frozen += q.numel()
            pre_ckpt = os.environ.get("EPB_PRE_CKPT", "runs/pretrain/epb_only_pretrain.pth")
            torch.save({"model": solver.model.state_dict()}, pre_ckpt)
            print("[EPB_ONLY] trainable_only=epb_router trainable_params=%d frozen_params=%d saved_pretrain_ckpt=%s" % (trainable, frozen, pre_ckpt))
        solver.train(**kwargs)
        solver.save("model_epoch_%d.pth" % solver.epoch)

        if smoke_skip_valid:
            if comm.get_rank() == 0:
                logger.warning("smoke_skip_valid=1 -> skip validation after epoch %d" % solver.epoch)
            continue

        solver.model.split = "valid"
        metric = solver.evaluate("valid")
        result = metric[cfg.metric]
        if result > best_result:
            best_result = result
            best_epoch = solver.epoch

    if smoke_skip_valid:
        if comm.get_rank() == 0:
            logger.warning("smoke_skip_valid=1 -> skip best-checkpoint reload in train_and_validate")
        return solver

    solver_load("model_epoch_%d.pth" % best_epoch, load_optimizer=False)
    return solver


def test(cfg, solver):
    solver.model.split = "valid"
    solver.evaluate("valid")
    solver.model.split = "test"
    solver.evaluate("test")


if __name__ == "__main__":
    args, vars = util.parse_args()
    cfg = util.load_config(args.config, context=vars)
    working_dir = util.create_working_directory(cfg)
    args.seed = int(args.seed)
    seed_rank = args.seed + int(comm.get_rank())
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(seed_rank)

    logger = util.get_root_logger()
    logger.warning("Working directory: %s" % working_dir)
    logger.warning("Input Seed: %d" % args.seed)
    logger.warning("Set Seed: %d" % seed_rank)
    if comm.get_rank() == 0:
        logger.warning("Config file: %s" % args.config)
        logger.warning(pprint.pformat(cfg))

    dataset = core.Configurable.load_config_dict(cfg.dataset)
    resume_mode = _get_resume_mode()
    resume_checkpoint = getattr(cfg, "checkpoint", None)
    solver = _build_solver_without_auto_resume(cfg, dataset, bypass_auto_resume=bool(resume_checkpoint))
    if resume_checkpoint:
        if comm.get_rank() == 0:
            logger.warning("Resume mode: %s" % resume_mode)
        if resume_mode == "full":
            solver_load(resume_checkpoint, load_optimizer=False)
        elif resume_mode == "model_only":
            solver_load(resume_checkpoint, load_optimizer=False)
        elif comm.get_rank() == 0:
            logger.warning("Fresh mode: ignore checkpoint %s" % resume_checkpoint)

    smoke_skip_valid = _get_smoke_skip_valid(cfg.train)
    train_and_validate(cfg, solver)

    if smoke_skip_valid:
        if comm.get_rank() == 0:
            logger.warning("smoke_skip_valid=1 -> skip immediate test() in run.py; use eval-only entry later")
    else:
        test(cfg, solver)
