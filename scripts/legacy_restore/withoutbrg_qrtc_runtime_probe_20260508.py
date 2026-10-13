#!/usr/bin/env python3
"""
Minimal runtime probe: does not modify model formulas; reloads process per variant.
Checks QRTC env, module presence, weight stats, forward debug, score separation Clean vs QRTC.
"""
from __future__ import annotations

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _bootstrap_env(variant: str) -> None:
    os.environ.pop("EVAL_VALID_CAP", None)
    os.environ.pop("EVAL_TEST_CAP", None)
    if variant == "clean":
        os.environ["QRTC_ENABLE"] = "0"
        os.environ.pop("QRTC_USE_MEMORY", None)
        os.environ.pop("QRTC_TOPK", None)
    else:
        os.environ["QRTC_ENABLE"] = "1"
        os.environ["QRTC_USE_MEMORY"] = "1"
        os.environ["QRTC_TOPK"] = "2"
    os.environ["QRTC_DEBUG"] = "1"
    os.environ["WORLD_SIZE"] = "1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", choices=("clean", "qrtc"))
    args = ap.parse_args()

    _bootstrap_env(args.variant)
    os.chdir(REPO)
    if REPO not in sys.path:
        sys.path.insert(0, REPO)

    import copy
    import logging
    import numpy as np
    import torch
    from torchdrug import core as td_core
    from torchdrug import utils

    import script.eval_valid_only as evo

    evo.logger = logging.getLogger("probe")
    evo.logger.addHandler(logging.StreamHandler())
    evo.logger.setLevel(logging.WARNING)

    from script.eval_valid_only import build_solver, solver_load  # noqa: E402

    cfg_rel = (
        "paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/"
        "withoutbrg_formal_rerun_20260507/config/clean_withoutbrg_eval_abs_ckpt_20260508_020728.yaml"
    )
    ckpt_clean = (
        "/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/"
        "qrtc_hr_full_closure_20260504/withoutbrg_formal_rerun_20260507/clean_train_out/"
        "KnowledgeGraphCompletionBiomed/biomedical/NBFNet/2026-05-08-02-07-31-368798/"
        "model_epoch_8.pth"
    )
    ckpt_qrtc = (
        "/root/autodl-tmp/BioPathNet_fresh/paper1_q2_sci_package_20260428/"
        "qrtc_hr_full_closure_20260504/withoutbrg_formal_rerun_20260507/"
        "qrtc_hronly_train_direct_20260508/KnowledgeGraphCompletionBiomed/biomedical/"
        "NBFNet/2026-05-08-13-35-27-655973/model_epoch_8.pth"
    )

    from biopathnet import util  # noqa: E402

    cfg_path = os.path.join(REPO, cfg_rel)
    cfg = util.load_config(cfg_path, context={"gpus": [0]})
    cfg = copy.deepcopy(cfg)
    cfg.pop("checkpoint", None)
    cfg.dataset["files"] = ["train1.txt", "train2.txt", "valid.txt", "test.txt"]
    _dataset = td_core.Configurable.load_config_dict(cfg.dataset)
    train_set, valid_set, test_set = _dataset.split()
    os.environ["EVAL_SKIP_OPTIMIZER_LOAD"] = "1"
    solver = build_solver(cfg, _dataset, train_set, valid_set, test_set)

    ckpt = ckpt_clean if args.variant == "clean" else ckpt_qrtc
    solver_load(ckpt, solver)

    # TorchDrug Engine.model is the task module (KnowledgeGraphCompletionBiomed).
    task_mod = solver.model
    nbf = task_mod.model

    print("=== VARIANT ===", args.variant, flush=True)
    print(
        "QRTC_ENABLE",
        os.environ.get("QRTC_ENABLE"),
        "QRTC_USE_MEMORY",
        os.environ.get("QRTC_USE_MEMORY"),
        "QRTC_TOPK",
        os.environ.get("QRTC_TOPK"),
        flush=True,
    )
    print("nbf.qrtc_enable", getattr(nbf, "qrtc_enable", None), flush=True)
    print("nbf.qrtc_use_memory", getattr(nbf, "qrtc_use_memory", None), flush=True)
    print("nbf.qrtc_topk", getattr(nbf, "qrtc_topk", None), flush=True)

    qrtc_names = [n for n, _ in nbf.named_parameters() if "qrtc" in n.lower()]
    print("num QRTC-named params:", len(qrtc_names), flush=True)
    if qrtc_names:
        flats = []
        for n in qrtc_names:
            t = dict(nbf.named_parameters())[n].detach().float().cpu().numpy().ravel()
            flats.append(t)
        cat = np.concatenate(flats)
        print(
            "QRTC param aggregate norm(L2):",
            float(np.linalg.norm(cat)),
            "mean",
            float(cat.mean()),
            "std",
            float(cat.std()),
            flush=True,
        )
        print("any nan/inf in QRTC params:", bool(np.isnan(cat).any() or np.isinf(cat).any()), flush=True)

    from torchdrug import data as td_data

    bs = min(8, len(valid_set))
    loader = td_data.DataLoader(valid_set, batch_size=bs, num_workers=0)

    batch = next(iter(loader))
    batch = utils.cuda(batch, device=solver.device)
    task_mod.eval()
    with torch.no_grad():
        pred = task_mod.predict(batch)

    pred_cpu = pred.detach().cpu().float()
    print(
        "predict tensor shape",
        tuple(pred.shape),
        "mean abs",
        float(pred_cpu.abs().mean()),
        "std",
        float(pred_cpu.std()),
        flush=True,
    )
    print("predict finite:", bool(torch.isfinite(pred).all().item()), flush=True)

    dbg = getattr(nbf, "_last_qrtc_debug_layers", None)
    print("len(_last_qrtc_debug_layers):", 0 if dbg is None else len(dbg), flush=True)
    if dbg:
        print("sample debug keys:", list(dbg[0].keys()) if isinstance(dbg[0], dict) else type(dbg[0]), flush=True)

    # Heuristic: QRTC path should populate debug layers when QRTC_DEBUG=1 and QRTC enabled
    if args.variant == "qrtc":
        ok_dbg = len(dbg) > 0 if dbg is not None else False
        print("QRTC_DEBUG layers populated:", ok_dbg, flush=True)
    else:
        print("QRTC_DEBUG layers populated (expect false for clean):", bool(dbg), flush=True)


if __name__ == "__main__":
    main()
