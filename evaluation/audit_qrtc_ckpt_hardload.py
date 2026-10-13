#!/usr/bin/env python3
"""One-off read-only QRTC checkpoint strictness audit (does not train)."""
from __future__ import annotations

import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Must match QRTC eval; parameters instantiate only when model builds.
os.environ["QRTC_ENABLE"] = "1"
os.environ["QRTC_USE_MEMORY"] = "1"
os.environ["QRTC_TOPK"] = "2"
for _k in (
    "EVAL_VALID_CAP",
    "EVAL_TEST_CAP",
    "VALID_CAP",
    "TEST_CAP",
    "CAP",
    "DEBUG",
    "SMOKE",
    "SAMPLE",
    "SUBSET",
):
    os.environ.pop(_k, None)

import copy
import logging
import torch
from biopathnet import util

# Import after env: builds NBFNet with QRTC modules
import script.eval_valid_only as eval_valid_only  # noqa: E402

_log = logging.getLogger("audit_qrtc_ckpt")
_log.setLevel(logging.WARNING)
if not _log.handlers:
    _log.addHandler(logging.StreamHandler())
eval_valid_only.logger = _log  # load_dataset_and_solver uses module-level logger
from script.eval_valid_only import build_solver  # noqa: E402
from torchdrug import core as td_core  # noqa: E402

QRTC_RE = re.compile(
    r"qrtc|QRTC|hop|memory|readout|attention|topk|precedent|gate_mlp|usage_mlp",
    re.IGNORECASE,
)


def _filter_qrtc_keys(keys):
    return [k for k in keys if QRTC_RE.search(k)]


def main():
    ap = argparse.ArgumentParser(description="QRTC checkpoint strict load_state_dict audit")
    ap.add_argument(
        "-c",
        "--config",
        default=None,
        help="Eval YAML (absolute or repo-relative). Default: May-08 withoutBRG QRTC eval config.",
    )
    ap.add_argument(
        "--exit-on-qrtc-mismatch",
        action="store_true",
        help="Exit 2 if any QRTC-pattern key is missing or unexpected after load_state_dict(strict=False).",
    )
    args = ap.parse_args()

    cfg_rel = (
        "paper1_q2_sci_package_20260428/qrtc_hr_full_closure_20260504/"
        "withoutbrg_formal_rerun_20260507/config/qrtc_hronly_withoutbrg_eval_abs_ckpt_20260508.yaml"
    )
    cfg_arg = args.config or cfg_rel
    cfg_path = cfg_arg if os.path.isabs(cfg_arg) else os.path.join(REPO, cfg_arg)
    context = {"gpus": [0]}
    cfg = util.load_config(cfg_path, context=context)

    ckpt_path = cfg.checkpoint
    if not os.path.isabs(ckpt_path):
        ckpt_path = os.path.join(REPO, ckpt_path)
    ckpt_path = os.path.expanduser(ckpt_path)

    print("=== CONFIG ===", flush=True)
    print(cfg_path, flush=True)
    print("checkpoint:", ckpt_path, flush=True)
    print("exists:", os.path.isfile(ckpt_path), flush=True)

    # Build solver without loading ckpt (avoid load_dataset_and_solver vocab_file global)
    cfg_build = copy.deepcopy(cfg)
    cfg_build.pop("checkpoint", None)
    cfg_local = copy.deepcopy(cfg_build)
    if "files" not in cfg_local.dataset:
        cfg_local.dataset["files"] = [
            "train1.txt",
            "train2.txt",
            "valid.txt",
            "test.txt",
        ]
    _dataset = td_core.Configurable.load_config_dict(cfg_local.dataset)
    train_set, valid_set, test_set = _dataset.split()
    solver = build_solver(cfg_local, _dataset, train_set, valid_set, test_set)

    raw = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    print("\n=== CHECKPOINT TOP-LEVEL KEYS ===", flush=True)
    if isinstance(raw, dict):
        print(list(raw.keys()), flush=True)
    else:
        print(type(raw), flush=True)

    # Mirror solver_load preprocessing
    if not isinstance(raw, dict) or "model" not in raw:
        print("HARDLOAD_INCONCLUSIVE: unexpected checkpoint structure", flush=True)
        sys.exit(1)

    state_model = raw["model"]
    print("\n=== CKPT state['model'] type ===", type(state_model), flush=True)
    if isinstance(state_model, dict):
        print("len(state['model'] keys):", len(state_model), flush=True)
    else:
        print("state['model'] is not a dict", flush=True)

    popped = []
    for key in (
        "fact_graph",
        "fact_graph_supervision",
        "graph",
        "train_graph",
        "valid_graph",
        "test_graph",
        "full_valid_graph",
        "full_test_graph",
    ):
        if isinstance(state_model, dict) and key in state_model:
            state_model.pop(key)
            popped.append(key)
    print("popped non-tensor graph keys:", popped, flush=True)

    model = solver.model
    model_keys = list(model.state_dict().keys())
    ckpt_keys = list(state_model.keys()) if isinstance(state_model, dict) else []

    print("\n=== MODEL state_dict len ===", len(model_keys), flush=True)
    print("=== CKPT model dict len (after pop) ===", len(ckpt_keys), flush=True)

    # strict=False with capture (PyTorch returns IncompatibleKeys)
    load_out = model.load_state_dict(state_model, strict=False)
    missing = list(getattr(load_out, "missing_keys", []) or [])
    unexpected = list(getattr(load_out, "unexpected_keys", []) or [])
    err_msgs = getattr(load_out, "error_msgs", None)

    print("\n=== load_state_dict(strict=False) ===", flush=True)
    print("missing_keys count:", len(missing), flush=True)
    if missing:
        for k in missing:
            print("  MISSING:", k, flush=True)
    print("unexpected_keys count:", len(unexpected), flush=True)
    if unexpected:
        for k in unexpected:
            print("  UNEXPECTED:", k, flush=True)
    print("error_msgs:", err_msgs, flush=True)

    mk_q = _filter_qrtc_keys(missing)
    uk_q = _filter_qrtc_keys(unexpected)
    print("\n=== QRTC-pattern in missing ===", len(mk_q), flush=True)
    for k in mk_q:
        print("  ", k, flush=True)
    print("=== QRTC-pattern in unexpected ===", len(uk_q), flush=True)
    for k in uk_q:
        print("  ", k, flush=True)

    model_q = set(_filter_qrtc_keys(model_keys))
    ckpt_q = set(_filter_qrtc_keys(ckpt_keys))
    inter = model_q & ckpt_q
    only_model = model_q - ckpt_q
    only_ckpt = ckpt_q - model_q

    print("\n=== QRTC-key intersection ===", flush=True)
    print("model QRTC-like keys:", len(model_q), flush=True)
    print("checkpoint QRTC-like keys:", len(ckpt_q), flush=True)
    print("intersection:", len(inter), flush=True)
    if only_model:
        print("only in model (no matching ckpt key):", len(only_model), flush=True)
        for k in sorted(only_model)[:80]:
            print("  ", k, flush=True)
        if len(only_model) > 80:
            print("  ...", flush=True)
    if only_ckpt:
        print("only in checkpoint (no matching model key):", len(only_ckpt), flush=True)
        for k in sorted(only_ckpt)[:80]:
            print("  ", k, flush=True)
        if len(only_ckpt) > 80:
            print("  ...", flush=True)

    # Verdict
    print("\n=== VERDICT_LINE ===", flush=True)
    if mk_q or uk_q:
        print("HARDLOAD_FAIL: QRTC-related keys in missing/unexpected", flush=True)
    elif len(missing) == 0 and len(unexpected) == 0:
        print("HARDLOAD_PASS: missing_keys=0 unexpected_keys=0", flush=True)
    elif not mk_q and not uk_q and (missing or unexpected):
        print(
            "HARDLOAD_PASS: non-QRTC missing/unexpected only (review list above)",
            flush=True,
        )
    else:
        print("HARDLOAD_INCONCLUSIVE", flush=True)

    if args.exit_on_qrtc_mismatch:
        if mk_q or uk_q:
            print("PREFLIGHT_EXIT:2 QRTC keys missing or unexpected", flush=True)
            sys.exit(2)


if __name__ == "__main__":
    main()
