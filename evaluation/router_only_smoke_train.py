import os
import ast
import time
import random
import argparse
from pathlib import Path

import numpy as np
import torch
from torchdrug import core

from biopathnet import util
from biopathnet import dataset as dataset_module
from biopathnet import task as task_module
from biopathnet import model as model_module


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True)
    parser.add_argument("--gpus", required=True, help='e.g. "[0]"')
    parser.add_argument("-s", "--seed", type=int, default=1024)
    args = parser.parse_args()

    set_seed(args.seed)

    gpus = ast.literal_eval(args.gpus)
    if isinstance(gpus, int):
        gpus = [gpus]

    cfg = util.load_config(args.config, context=vars(args))
    cfg.engine.gpus = gpus

    dataset = core.Configurable.load_config_dict(cfg.dataset)

    # 关键：旧 checkpoint 只加载 model，不恢复 optimizer
    os.environ["BIOPATHNET_SKIP_OPTIMIZER_LOAD"] = "1"

    solver = util.build_solver(cfg, dataset)

    trainable_names = []
    frozen_names = []

    for name, p in solver.model.named_parameters():
        trainable = name.startswith("model.evidence_router") or name.startswith("model.mlp")
        p.requires_grad_(trainable)
        if trainable:
            trainable_names.append(name)
        else:
            frozen_names.append(name)

    # 重建 optimizer，只优化 router + mlp
    cfg.optimizer.params = [p for p in solver.model.parameters() if p.requires_grad]
    solver.optimizer = core.Configurable.load_config_dict(cfg.optimizer)

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_dir = Path(cfg.output_dir) / "router_only_smoke" / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    print("===== ROUTER-ONLY SMOKE =====")
    print("out_dir =", out_dir)
    print("trainable_param_n =", sum(p.numel() for p in solver.model.parameters() if p.requires_grad))
    print("frozen_param_n =", sum(p.numel() for p in solver.model.parameters() if not p.requires_grad))
    print("trainable_names =")
    for x in trainable_names:
        print("  ", x)

    # 小烟雾训练：先按当前 cfg.train 跑
    train_cfg = dict(cfg.train)
    print("train_cfg =", train_cfg)
    solver.train(**train_cfg)

    ckpt_path = out_dir / "router_only_smoke_last.pth"
    torch.save({
        "model": solver.model.state_dict(),
        "optimizer": solver.optimizer.state_dict(),
    }, ckpt_path)

    probe_cfg_path = out_dir / "router_only_smoke_probe.yaml"
    base_text = Path(args.config).read_text(encoding="utf-8")
    new_text = base_text.replace(str(cfg.checkpoint), str(ckpt_path))
    probe_cfg_path.write_text(new_text, encoding="utf-8")

    (out_dir / "TRAINABLE_NAMES.txt").write_text("\n".join(trainable_names) + "\n", encoding="utf-8")
    (out_dir / "FROZEN_NAMES_HEAD.txt").write_text("\n".join(frozen_names[:200]) + "\n", encoding="utf-8")

    print("CKPT =", ckpt_path)
    print("PROBE_CFG =", probe_cfg_path)


if __name__ == "__main__":
    main()
