
import os
import sys
import json
import math
import pprint
import random
import numpy as np
import torch

from torchdrug import core
from torchdrug.utils import comm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from biopathnet import dataset, layer, model, task, util


def model_only_load(checkpoint, solver, logger):
    if comm.get_rank() == 0:
        logger.warning("Load checkpoint from %s" % checkpoint)
    checkpoint = os.path.expanduser(checkpoint)
    state = torch.load(checkpoint, map_location=solver.device)

    # mirror public run.py style
    state["model"].pop("fact_graph_supervision", 0)
    state["model"].pop("graph", 0)
    state["model"].pop("train_graph", 0)
    state["model"].pop("valid_graph", 0)
    state["model"].pop("test_graph", 0)
    state["model"].pop("full_valid_graph", 0)
    state["model"].pop("full_test_graph", 0)

    missing, unexpected = solver.model.load_state_dict(state["model"], strict=False)
    if comm.get_rank() == 0:
        logger.warning("missing_keys = %s" % list(missing))
        logger.warning("unexpected_keys = %s" % list(unexpected))
    comm.synchronize()


def unwrap_task_model(solver):
    m = solver.model
    if hasattr(m, "module"):
        m = m.module
    return m


def get_soft_path_prior_param(solver):
    task_model = unwrap_task_model(solver)
    return task_model.model.soft_path_prior


def freeze_except_soft_path_prior(solver, logger):
    total_n = 0
    trainable_n = 0
    frozen_n = 0
    trainable_names = []
    frozen_names = []

    for name, p in solver.model.named_parameters():
        total_n += p.numel()
        if name.endswith("model.soft_path_prior") or "model.soft_path_prior" in name:
            p.requires_grad_(True)
            trainable_n += p.numel()
            trainable_names.append(name)
        else:
            p.requires_grad_(False)
            frozen_n += p.numel()
            frozen_names.append(name)

    old_opt = solver.optimizer
    opt_cls = old_opt.__class__
    defaults = dict(old_opt.defaults)
    trainable_params = [p for p in solver.model.parameters() if p.requires_grad]
    solver.optimizer = opt_cls(trainable_params, **defaults)

    logger.warning("FREEZE_REPORT total_n=%d trainable_n=%d frozen_n=%d" % (total_n, trainable_n, frozen_n))
    logger.warning("TRAINABLE_NAMES = %s" % trainable_names[:20])
    logger.warning("FROZEN_NAME_SAMPLE = %s" % frozen_names[:20])

    return {
        "total_param_n": int(total_n),
        "trainable_param_n": int(trainable_n),
        "frozen_param_n": int(frozen_n),
        "trainable_names": trainable_names,
        "frozen_name_sample": frozen_names[:20],
        "optimizer_class": opt_cls.__name__,
        "optimizer_defaults": defaults,
    }


def tensor_stats(x):
    return {
        "shape": list(x.shape),
        "mean": float(x.mean().item()),
        "std": float(x.std().item()),
        "norm": float(x.norm().item()),
        "max_abs": float(x.abs().max().item()),
    }


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

    ckpt = os.environ.get("SRP_SMOKE_CHECKPOINT", "").strip()
    smoke_epoch = int(os.environ.get("SRP_SMOKE_NUM_EPOCH", "1"))

    cfg_ckpt = ""
    try:
        cfg_ckpt = str(getattr(cfg, "checkpoint", "") or "").strip()
    except Exception:
        try:
            cfg_ckpt = str(cfg.get("checkpoint", "") or "").strip()
        except Exception:
            cfg_ckpt = ""

    load_ckpt = ckpt or cfg_ckpt

    dataset_obj = core.Configurable.load_config_dict(cfg.dataset)

    # util.build_solver() always calls solver_load(cfg.checkpoint) in this codebase.
    # We must bypass that full checkpoint / optimizer load, then do model-only load manually.
    _orig_solver_load = util.solver_load
    def _no_ckpt_solver_load(solver, checkpoint):
        logger.warning("BYPASS solver_load during build_solver (checkpoint=%r)" % (checkpoint,))
        return
    util.solver_load = _no_ckpt_solver_load
    try:
        solver = util.build_solver(cfg, dataset_obj)
    finally:
        util.solver_load = _orig_solver_load

    if load_ckpt:
        model_only_load(load_ckpt, solver, logger)
    else:
        logger.warning("SRP_SMOKE_CHECKPOINT empty and cfg.checkpoint empty; will train from current init")

    freeze_report = freeze_except_soft_path_prior(solver, logger)

    prior_before = get_soft_path_prior_param(solver).detach().cpu().clone()
    logger.warning("PRIOR_BEFORE = %s" % tensor_stats(prior_before))

    solver.model.split = "train"
    solver.train(num_epoch=smoke_epoch)

    prior_after = get_soft_path_prior_param(solver).detach().cpu().clone()
    delta = prior_after - prior_before

    after_stats = tensor_stats(prior_after)
    delta_stats = tensor_stats(delta)
    ratio = 0.0
    if after_stats["norm"] > 0:
        ratio = float(delta_stats["norm"] / after_stats["norm"])

    logger.warning("PRIOR_AFTER = %s" % after_stats)
    logger.warning("PRIOR_DELTA = %s" % delta_stats)
    logger.warning("PRIOR_DELTA_OVER_AFTER_NORM = %.8f" % ratio)

    solver.save("model_epoch_srp_prior_smoke.pth")

    solver.model.split = "valid"
    metric = solver.evaluate("valid")

    report = {
        "asset": "srp_prior_only_learnability_smoke",
        "working_dir": working_dir,
        "checkpoint_loaded": ckpt,
        "smoke_epoch": smoke_epoch,
        "freeze_report": freeze_report,
        "prior_before": tensor_stats(prior_before),
        "prior_after": after_stats,
        "prior_delta": delta_stats,
        "prior_delta_over_after_norm": ratio,
        "valid_metric": {k: float(v) for k, v in metric.items()},
        "saved_checkpoint": os.path.join(working_dir, "model_epoch_srp_prior_smoke.pth"),
    }

    report_path = os.path.join(working_dir, "SRP_PRIOR_SMOKE_REPORT.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    latest_path = os.path.join(working_dir, "SRP_LATEST_CHECKPOINT.txt")
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(report["saved_checkpoint"] + "\n")

    logger.warning("WROTE %s" % report_path)
    logger.warning("WROTE %s" % latest_path)
