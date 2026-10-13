#!/usr/bin/env python3
"""
Read-only first-batch probe for LncTarD-PPI Clean withBRG formal train assert failure.
No training, no backward. Replicates KnowledgeGraphCompletionBiomed train index layout.
"""
from __future__ import annotations

import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import torch
from torch.utils import data as torch_data

from torchdrug import core

from biopathnet import util
import biopathnet.dataset  # noqa: F401 — register datasets.biomedical
import biopathnet.task  # noqa: F401 — register tasks.KnowledgeGraphCompletionBiomed
import biopathnet.model  # noqa: F401 — register model.NBFNet


def _rel_set(path: str) -> set[str]:
    rels: set[str] = set()
    with open(path, "r") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                rels.add(parts[1])
    return rels


def _head_tail_types(path: str, inv_entity_vocab: dict, node_type: torch.Tensor) -> tuple[Counter, Counter]:
    """Map first column = head type, third = tail type using entity_types-backed node_type."""
    hc: Counter = Counter()
    tc: Counter = Counter()
    with open(path, "r") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                continue
            ht, _, ttok = parts[0], parts[1], parts[2]
            if ht in inv_entity_vocab:
                hi = inv_entity_vocab[ht]
                if 0 <= hi < len(node_type):
                    hc[int(node_type[hi].item())] += 1
            if ttok in inv_entity_vocab:
                ti = inv_entity_vocab[ttok]
                if 0 <= ti < len(node_type):
                    tc[int(node_type[ti].item())] += 1
    return hc, tc


def main() -> None:
    cfg_path = os.path.join(
        ROOT,
        "config/knowledge_graph/biomedical/lnctardppi_clean_withbrg_formal_seed1024_20260508.yaml",
    )
    if not os.path.isfile(cfg_path):
        raise FileNotFoundError(cfg_path)

    cfg = util.load_config(cfg_path, context={"gpus": [0]})

    print("=== CONFIG AUDIT (key fields) ===")
    print("dataset.path:", cfg.dataset.get("path"))
    print("dataset.include_factgraph:", cfg.dataset.get("include_factgraph"))
    print("task.class:", cfg.task.get("class"))
    print("task.model.class:", cfg.task.model.get("class"))
    print("task.model.hidden_dims:", cfg.task.model.get("hidden_dims"))
    print("task.model.symmetric:", cfg.task.model.get("symmetric", "<absent>"))
    print("task.num_negative:", cfg.task.get("num_negative"))
    print("task.strict_negative:", cfg.task.get("strict_negative"))
    print("task.heterogeneous_negative:", cfg.task.get("heterogeneous_negative"))
    print("task.adversarial_temperature:", cfg.task.get("adversarial_temperature"))
    print("engine.batch_size:", cfg.engine.get("batch_size"))
    print("train.num_epoch:", cfg.train.get("num_epoch"))
    print("train.smoke_skip_valid:", cfg.train.get("smoke_skip_valid"))
    print("train.batch_per_epoch:", cfg.train.get("batch_per_epoch", "<absent>"))
    print("checkpoint (top-level):", getattr(cfg, "checkpoint", "<absent>"))

    data_path = os.path.expanduser(str(cfg.dataset.path))
    print("\n=== DATA FILES (first 20 lines each) ===")
    for name in ("train1.txt", "train2.txt", "valid.txt", "test.txt"):
        p = os.path.join(data_path, name)
        print(f"\n--- {name} ---")
        if not os.path.isfile(p):
            print("MISSING")
            continue
        with open(p, "r") as f:
            for i, line in enumerate(f):
                if i >= 20:
                    break
                print(line.rstrip("\n"))

    print("\n=== RELATION SETS PER SPLIT ===")
    r_train1 = _rel_set(os.path.join(data_path, "train1.txt"))
    r_train2 = _rel_set(os.path.join(data_path, "train2.txt"))
    r_valid = _rel_set(os.path.join(data_path, "valid.txt"))
    r_test = _rel_set(os.path.join(data_path, "test.txt"))
    print("train1 n_rel:", len(r_train1))
    print("train2 n_rel:", len(r_train2), "subset of train1?", r_train2 <= r_train1)
    print("valid n_rel:", len(r_valid), "subset of train1?", r_valid <= r_train1)
    print("test n_rel:", len(r_test), "subset of train1?", r_test <= r_train1)
    print("valid vs train2 same set?", r_valid == r_train2)
    print("test vs train2 same set?", r_test == r_train2)

    if not torch.cuda.is_available():
        print("\n[WARN] CUDA not available; solver may fail.")
    dataset = core.Configurable.load_config_dict(cfg.dataset)
    train_set, valid_set, test_set = dataset.split()
    g = dataset.graph
    node_type = g.node_type

    inv = dataset.inv_entity_vocab
    missing_train2 = []
    with open(os.path.join(data_path, "train2.txt"), "r") as f:
        for line in f:
            h, _r, t = line.rstrip("\n").split("\t")[:3]
            if h not in inv:
                missing_train2.append(("h", h))
            if t not in inv:
                missing_train2.append(("t", t))
    print("\n=== ENTITY VOCAB (train2 rows missing from inv_entity_vocab) ===")
    print("missing count:", len(missing_train2), "sample:", missing_train2[:5])

    hc2, tc2 = _head_tail_types(os.path.join(data_path, "train2.txt"), inv, node_type)
    hcv, tcv = _head_tail_types(os.path.join(data_path, "valid.txt"), inv, node_type)
    print("\n=== NODE TYPE ID HISTOGRAMS (type id -> count) train2 head/tail ===")
    print("train2 head:", dict(hc2.most_common(20)))
    print("train2 tail:", dict(tc2.most_common(20)))
    print("valid head:", dict(hcv.most_common(20)))
    print("valid tail:", dict(tcv.most_common(20)))

    print("\n=== BUILD SOLVER (load graphs + task; no train) ===")
    solver = util.build_solver(cfg, dataset)
    task = solver.model
    task.eval()
    bs = int(cfg.engine.batch_size)
    loader = torch_data.DataLoader(
        train_set, batch_size=bs, shuffle=False, num_workers=0,
    )
    batch = next(iter(loader))
    print("raw batch tensor shape:", tuple(batch.shape))
    print("raw batch dtype:", batch.dtype, "device:", batch.device)

    def _dict_get(d, idx: int):
        if isinstance(d, (list, tuple)):
            if 0 <= idx < len(d):
                return d[idx]
            return f"<oob {idx}>"
        if idx in d:
            return d[idx]
        k = str(idx)
        if k in d:
            return d[k]
        return f"<missing {idx}>"

    def tok_triplet(row):
        h, t, r = int(batch[row, 0]), int(batch[row, 1]), int(batch[row, 2])
        return _dict_get(dataset.entity_vocab, h), _dict_get(dataset.entity_vocab, t), _dict_get(dataset.relation_vocab, r)

    print("\nfirst 5 triplets (h_name, t_name, r_name):")
    for i in range(min(5, batch.shape[0])):
        print(i, tok_triplet(i))

    pos_h_index, pos_t_index, pos_r_index = batch.t()
    with torch.no_grad():
        neg_index = task._strict_negative(pos_h_index, pos_t_index, pos_r_index)
    num_neg = int(cfg.task.num_negative)
    h_index = pos_h_index.unsqueeze(-1).repeat(1, num_neg + 1)
    t_index = pos_t_index.unsqueeze(-1).repeat(1, num_neg + 1)
    r_index = pos_r_index.unsqueeze(-1).repeat(1, num_neg + 1)
    bsz = len(pos_h_index)
    half = bsz // 2
    t_index[:half, 1:] = neg_index[:half]
    h_index[half:, 1:] = neg_index[half:]

    print("\n=== INDEX TENSOR SHAPES ===")
    print("h_index", tuple(h_index.shape))
    print("t_index", tuple(t_index.shape))
    print("r_index", tuple(r_index.shape))

    def row_all_same(x, name):
        ok = (x[:, 1:] == x[:, :1]).all(dim=1)
        return ok

    h_same = row_all_same(h_index, "h")
    t_same = row_all_same(t_index, "t")
    r_same = row_all_same(r_index, "r")
    print("\nrows where h constant across columns:", int(h_same.sum()), "/", bsz)
    print("rows where t constant across columns:", int(t_same.sum()), "/", bsz)
    print("rows where r constant across columns:", int(r_same.sum()), "/", bsz)

    sym_expect_t = (t_index[:, [0]] == t_index).all(dim=1)
    failed_t = ~sym_expect_t
    n_fail = int(failed_t.sum())
    print("\nrows failing assert (t_index[:, [0]] == t_index).all(dim=1):", n_fail)
    if n_fail:
        ev, rv = dataset.entity_vocab, dataset.relation_vocab
        idxs = torch.nonzero(failed_t, as_tuple=False).view(-1)[:8]
        print("sample row indices:", idxs.tolist())
        for ri in idxs[:3]:
            r = int(ri)
            print(f"\n--- FAIL ROW {r} ---")
            ph, pt, pr = int(pos_h_index[r]), int(pos_t_index[r]), int(pos_r_index[r])
            print("positive (h, r, t):", _dict_get(ev, ph), _dict_get(rv, pr), _dict_get(ev, pt))
            negs = t_index[r, 1:11].tolist()
            print("first 10 negative tail ids:", negs)
            print("first 10 neg tail names:", [_dict_get(ev, int(x)) for x in negs])
            print("head id/name:", ph, _dict_get(ev, ph), "type:", int(node_type[ph]))
            print("pos tail id/name:", pt, _dict_get(ev, pt), "type:", int(node_type[pt]))

    print("\n=== NEGATIVE SAMPLING MODE (train batch layout) ===")
    print(f"rows [0, {half}) : corrupt TAIL (t varies on negatives); pos (h,r) fixed")
    print(f"rows [{half}, {bsz}) : corrupt HEAD (h varies); pos tail t fixed")
    print("model symmetric=True expects t_index identical in every column for ALL rows -> incompatible with first half.")

    m_sym = bool(getattr(task.model, "symmetric", False))
    print("\nmodel.symmetric:", m_sym)
    print("NBFNet assert would fire on any tail-corruption row when symmetric=True.")


if __name__ == "__main__":
    main()
