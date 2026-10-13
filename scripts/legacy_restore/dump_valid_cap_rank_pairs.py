import os
import sys
import json
import random
import pprint
import torch
import numpy as np
from torch.utils import data as torch_data

from torchdrug import core, utils
from torchdrug.utils import comm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from biopathnet import dataset, layer, model, task, util  # noqa: F401

logger = None


def solver_load_bound(solver, checkpoint, load_optimizer=False):
    global logger
    logger.warning("Load checkpoint from %s" % checkpoint)
    checkpoint = os.path.expanduser(checkpoint)
    state = torch.load(checkpoint, map_location=solver.device)
    if "model" not in state:
        raise KeyError("checkpoint missing 'model' key")

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
    comm.synchronize()


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

    ds = core.Configurable.load_config_dict(cfg.dataset)
    solver = util.build_solver(cfg, ds)

    if not hasattr(cfg, "checkpoint"):
        raise ValueError("cfg.checkpoint is required")

    solver_load_bound(solver, cfg.checkpoint, load_optimizer=False)

    valid_cap = int(os.environ.get("VALID_CAP", "32"))
    eval_bs = int(os.environ.get("EVAL_BATCH_SIZE", "1"))

    original_valid = solver.valid_set
    cap = min(valid_cap, len(original_valid))
    solver.valid_set = torch_data.Subset(original_valid, list(range(cap)))
    solver.batch_size = eval_bs

    if hasattr(solver.model, "split"):
        solver.model.split = "valid"

    model_obj = solver.model
    model_obj.eval()

    out_jsonl = os.path.join(working_dir, "valid_cap_rank_dump.jsonl")
    out_summary = os.path.join(working_dir, "valid_cap_rank_summary.json")

    dataloader = torch_data.DataLoader(
        solver.valid_set,
        batch_size=solver.batch_size,
        shuffle=False,
        num_workers=solver.num_worker,
    )

    all_rank = []
    row_offset = 0

    with open(out_jsonl, "w", encoding="utf-8") as f:
        with torch.no_grad():
            for batch in dataloader:
                if solver.device.type == "cuda":
                    batch = utils.cuda(batch, device=solver.device)

                pred = model_obj.predict(batch, all_loss=None, metric={})
                mask, target = model_obj.target(batch)

                pos_pred = pred.gather(-1, target.unsqueeze(-1))
                if model_obj.filtered_ranking:
                    ranking = torch.sum((pos_pred <= pred) & mask, dim=-1) + 1
                else:
                    ranking = torch.sum(pos_pred <= pred, dim=-1) + 1

                pred_cpu = pred.detach().cpu()
                pos_score = pos_pred.squeeze(-1).detach().cpu()
                ranking_cpu = ranking.detach().cpu()
                batch_cpu = batch.detach().cpu()

                bs = len(batch_cpu)
                for i in range(bs):
                    cap_row = row_offset + i
                    try:
                        global_index = int(original_valid.indices[cap_row])
                    except Exception:
                        global_index = cap_row

                    h, t, r = [int(x) for x in batch_cpu[i].tolist()]
                    tail_rank = int(ranking_cpu[i, 0])
                    head_rank = int(ranking_cpu[i, 1])
                    rec = {
                        "cap_row": cap_row,
                        "global_index": global_index,
                        "head": h,
                        "tail": t,
                        "relation": r,
                        "tail_rank": tail_rank,
                        "head_rank": head_rank,
                        "tail_pos_score": float(pos_score[i, 0]),
                        "head_pos_score": float(pos_score[i, 1]),
                    }
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    all_rank.extend([tail_rank, head_rank])

                row_offset += bs

    rank = torch.tensor(all_rank, dtype=torch.float32)
    summary = {
        "valid_cap_requested": valid_cap,
        "valid_cap_used": cap,
        "eval_batch_size": eval_bs,
        "num_rank_values": int(rank.numel()),
        "mr": float(rank.mean()),
        "mrr": float((1.0 / rank).mean()),
        "hits@1": float((rank <= 1).float().mean()),
        "hits@3": float((rank <= 3).float().mean()),
        "hits@10": float((rank <= 10).float().mean()),
        "hits@20": float((rank <= 20).float().mean()),
        "hits@50": float((rank <= 50).float().mean()),
        "hits@100": float((rank <= 100).float().mean()),
        "config": args.config,
        "checkpoint": cfg.checkpoint,
        "rank_dump_jsonl": out_jsonl,
    }

    with open(out_summary, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    logger.warning("WROTE %s", out_jsonl)
    logger.warning("WROTE %s", out_summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
