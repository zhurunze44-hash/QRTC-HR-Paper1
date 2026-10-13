#!/usr/bin/env python3
"""Diagnostic: first N triples of capped valid_set — unfiltered tail rank (NOT filtered protocol)."""
from __future__ import annotations

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True, help="hist_qrtc|curr_qrtc|curr_clean")
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--cfg", required=True)
    ap.add_argument("--n", type=int, default=20)
    args = ap.parse_args()

    os.chdir(REPO)
    sys.path.insert(0, REPO)
    os.environ["WORLD_SIZE"] = "1"
    os.environ["EVAL_SKIP_OPTIMIZER_LOAD"] = "1"
    os.environ["EVAL_VALID_CAP"] = "64"
    os.environ["EVAL_ONLY_SPLIT"] = "valid"

    if args.variant == "curr_clean":
        os.environ["QRTC_ENABLE"] = "0"
    else:
        os.environ["QRTC_ENABLE"] = "1"
        os.environ["QRTC_USE_MEMORY"] = "1"
        os.environ["QRTC_TOPK"] = "2"

    import copy
    import torch
    from torchdrug import core as td_core
    from torchdrug import utils

    import script.eval_valid_only as evo
    import logging

    evo.logger = logging.getLogger("ranks")
    evo.logger.addHandler(logging.StreamHandler())
    evo.logger.setLevel(logging.ERROR)

    from script.eval_valid_only import build_solver, solver_load  # noqa: E402
    from biopathnet import util  # noqa: E402

    cfg = util.load_config(args.cfg, context={"gpus": [0]})
    cfg = copy.deepcopy(cfg)
    cfg.pop("checkpoint", None)
    cfg.dataset["files"] = ["train1.txt", "train2.txt", "valid.txt", "test.txt"]
    _dataset = td_core.Configurable.load_config_dict(cfg.dataset)
    train_set, valid_set, test_set = _dataset.split()

    # replicate eval_valid_only cap
    cap = 64
    idx = getattr(valid_set, "indices", None)
    if isinstance(idx, range):
        valid_set.indices = range(idx.start, min(idx.start + cap, idx.stop))

    solver = build_solver(cfg, _dataset, train_set, valid_set, test_set)
    solver_load(args.ckpt, solver)

    task = solver.model
    device = solver.device

    print("variant", args.variant, "n_valid_after_cap", len(valid_set), flush=True)

    rows = []
    for i in range(min(args.n, len(valid_set))):
        batch = valid_set[i].unsqueeze(0).to(device)
        with torch.no_grad():
            pred = task.predict(batch)
        # pred [1, 2, num_entity] tail channel 0
        t_scores = pred[0, 0].float()
        h_idx, t_idx, r_idx = batch[0].tolist()
        score_true = t_scores[t_idx].item()
        # unfiltered rank: count entities with strictly higher score + 1
        rank = int((t_scores > score_true).sum().item()) + 1
        rows.append((i, int(h_idx), int(t_idx), int(r_idx), rank))

    print("idx h t r unfiltered_tail_rank", flush=True)
    for row in rows:
        print(*row, flush=True)


if __name__ == "__main__":
    main()
