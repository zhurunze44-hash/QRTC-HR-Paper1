# script to load the trained model
# first, evaluates on the validation and full test set
# then evaluates on the validation and test_pred.txt
# finally predicts for test_pred.txt
# to double check with performances seen during training if all loaded correctly
import os
import faulthandler
import sys
import pprint

import torch

from torchdrug import core
from torchdrug.utils import comm
from torch.utils import data as torch_data
from torchdrug import data, core, utils
import pandas as pd
import copy
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from biopathnet import dataset, layer, model, task, util
import numpy as np


def solver_load(checkpoint, solver, load_optimizer=True):

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


    skip_opt = os.environ.get("EVAL_SKIP_OPTIMIZER_LOAD", "0") == "1"
    if load_optimizer and not skip_opt:
        solver.optimizer.load_state_dict(state["optimizer"])
        for state in solver.optimizer.state.values():
            for k, v in state.items():
                if isinstance(v, torch.Tensor):
                    state[k] = v.to(solver.device)
    elif load_optimizer and skip_opt:
        print("EVAL_SKIP_OPTIMIZER_LOAD=1 -> skip optimizer state load")

    comm.synchronize()


def build_solver(cfg, _dataset, train_set, valid_set, test_set):
    cfg.task.model.num_relation = _dataset.num_relation
    _task = core.Configurable.load_config_dict(cfg.task)
    cfg.optimizer.params = _task.parameters()
    optimizer = core.Configurable.load_config_dict(cfg.optimizer)
    if "scheduler" in cfg:
        cfg.scheduler.optimizer = optimizer
        scheduler = core.Configurable.load_config_dict(cfg.scheduler)
    else:
        scheduler = None
    return core.Engine(_task, train_set, valid_set, test_set, optimizer, scheduler, **cfg.engine)

def load_vocab(dataset, vocab_file):
    entity_mapping = {}
    with open(vocab_file, "r") as fin:
        for line in fin:
            k, v = line.strip().split("\t")
            entity_mapping[k] = v
    entity_vocab = [entity_mapping[t] for t in dataset.entity_vocab]
    relation_vocab = ["%s (%d)" % (t[t.rfind("/") + 1:].replace("_", " "), i)
                      for i, t in enumerate(dataset.relation_vocab)]

    return entity_vocab, relation_vocab

@torch.no_grad()
def get_prediction(cfg, solver, relation_vocab, dataset):
    test_set = solver.test_set

    dataloader = data.DataLoader(test_set, solver.batch_size, sampler=None, num_workers=solver.num_worker)
    model = solver.model

    model.eval()
    preds = []
    targets = []
    masks = []
    
    for ith, batch in enumerate(dataloader):

        if solver.device.type == "cuda":
            batch = utils.cuda(batch, device=solver.device)
        logger.warning("Predicting batch %s" % ith)
        pred, (mask, target) = model.predict_and_target(batch)
        
        preds.append(pred)
        targets.append(target)
        masks.append(mask)
    
    pred = utils.cat(preds)
    mask = utils.cat(masks)
    pred = pred[mask].detach().cpu()
    mask = mask.detach().cpu()
    target = utils.cat(targets).detach().cpu()

    # get nodes
    nodes = dataset.entity_vocab
    
    # get prediction nodes
    nodes_mask = np.broadcast_to(nodes, tuple(np.array(mask.shape))) # broadcast nodes to mask shape
    pred_nodes = nodes_mask[mask] # mask out unwanted

    # get query nodes
    trans_target = torch.transpose(torch.flip(torch.transpose(target, 0, 1), [0]), 0,1) # flip target
    idx = torch.reshape(trans_target, (-1,)).cpu().numpy() # reshape to 1D
    target_nodes = np.array(nodes)[idx] # get nodes from index
    rep_times = np.sum(mask.cpu().numpy(), axis=2).reshape(mask.shape[0]*mask.shape[1]) # get number of times to repeat
    query_node = np.repeat(target_nodes, rep_times) # repeat nodes
    
    # test_relation
    testset_relation =  [relation_vocab[i].split(" ")[0] for i in [x.numpy()[2] for x in solver.test_set]] # get relation from testset
    rels = np.column_stack((testset_relation, ['rev_' + s for s in testset_relation])) # get both relation and relation^(-1)
    query_rel = np.repeat(rels, rep_times) # repeat relations
    
    
    df = {"query_node": query_node,
          'query_relation':query_rel,
          "pred_node": pred_nodes,
          "probability": pred}

    df = pd.DataFrame(df)
    df = df.drop_duplicates()
    logger.warning("Done")
    return df

def merge_with_entity_vocab(df, dataset, entity_vocab, relation_vocab):
    # get head nodes
    
    lookup = pd.DataFrame(list(zip( dataset.entity_vocab, entity_vocab)), columns =['short', 'long'])

    df = pd.merge(df, lookup, how="left", left_on="query_node", right_on="short", sort=False)
    df = pd.merge(df, lookup, how="left", left_on="pred_node", right_on="short", sort=False)
    return df


def test(cfg, solver):
    solver.model.split = "valid"
    solver.evaluate("valid")
    solver.model.split = "test"
    solver.evaluate("test")
    
def load_dataset_and_solver(cfg, test_file):
    cfg_local = copy.deepcopy(cfg)
    if 'files' not in cfg_local.dataset:
        cfg_local.dataset['files'] = ['train1.txt', 'train2.txt', 'valid.txt', test_file]
    _dataset = core.Configurable.load_config_dict(cfg_local.dataset)
    train_set, valid_set, test_set = _dataset.split()

    def _cap_runtime_subset(subset, env_name):
        raw = os.environ.get(env_name, "0")
        try:
            cap = int(raw)
        except Exception:
            cap = 0
        if cap <= 0:
            return subset

        idx = getattr(subset, "indices", None)
        if isinstance(idx, range):
            new_idx = range(idx.start, min(idx.start + cap, idx.stop))
            subset.indices = new_idx
            print(f"{env_name}={cap} -> runtime_subset.indices = {new_idx}")
            return subset

        if isinstance(idx, list):
            subset.indices = idx[:cap]
            print(f"{env_name}={cap} -> runtime_subset.indices(list) = {len(subset.indices)}")
            return subset

        try:
            return subset[:cap]
        except Exception:
            print(f"{env_name}={cap} -> runtime subset cap skipped (unsupported type)")
            return subset

    valid_set = _cap_runtime_subset(valid_set, "EVAL_VALID_CAP")
    test_set = _cap_runtime_subset(test_set, "EVAL_TEST_CAP")
    
    if comm.get_rank() == 0:
        logger.warning(_dataset)
        logger.warning("#train: %d, #valid: %d, #test: %d" % (len(train_set), len(valid_set), len(test_set)))
    
    solver = build_solver(cfg_local, _dataset, train_set, valid_set, test_set)
    if "checkpoint" in cfg_local:
        solver_load(cfg_local.checkpoint, solver)
    
    entity_vocab, relation_vocab = load_vocab(_dataset, vocab_file)
    return cfg_local, solver, _dataset, entity_vocab, relation_vocab
        
if __name__ == "__main__":
    args, vars = util.parse_args()
    faulthandler.enable()
    _fh_sec = int(os.environ.get("EVAL_FAULTHANDLER_TIMEOUT", "0"))
    if _fh_sec > 0:
        faulthandler.dump_traceback_later(_fh_sec, repeat=False)
    cfg = util.load_config(args.config, context=vars)
    def _maybe_cap_subset(cfg_obj, key, env_name):
        raw = __import__('os').environ.get(env_name, '0')
        try:
            cap = int(raw)
        except Exception:
            cap = 0
        if cap <= 0:
            return
        node = cfg_obj.get(key) if isinstance(cfg_obj, dict) else getattr(cfg_obj, key, None)
        if node is None:
            return
        idx = node.get('indices') if isinstance(node, dict) else getattr(node, 'indices', None)
        if isinstance(idx, range):
            new_idx = range(idx.start, min(idx.start + cap, idx.stop))
            if isinstance(node, dict):
                node['indices'] = new_idx
            else:
                node.indices = new_idx
            print(f"{env_name}={cap} -> {key}.indices = {new_idx}")
    _maybe_cap_subset(cfg, 'valid_set', 'EVAL_VALID_CAP')
    _maybe_cap_subset(cfg, 'test_set', 'EVAL_TEST_CAP')
    working_dir = util.create_working_directory(cfg)
    print(working_dir)
    # get entity names
    if 'entity_files' in cfg.dataset:
        vfile = cfg.dataset.entity_files[1]
    else:
        vfile = "entity_names.txt"
    vocab_file = os.path.join(os.path.dirname(__file__), cfg.dataset.path, vfile)
    vocab_file = os.path.abspath(vocab_file)

    torch.manual_seed(args.seed + comm.get_rank())

    logger = util.get_root_logger()
    logger.warning("Working directory: %s" % working_dir)
    if comm.get_rank() == 0:
        logger.warning("Config file: %s" % args.config)
        #logger.warning(pprint.pformat(cfg))

    # Test phase
    cfg_eval, solver_eval, _dataset_eval, entity_vocab_eval, relation_vocab_eval = load_dataset_and_solver(cfg, 'test.txt')
    test(cfg_eval, solver_eval)

    # Prediction phase
    cfg_pred, solver, _dataset, entity_vocab, relation_vocab = load_dataset_and_solver(cfg, 'test_pred.txt')
    test(cfg_pred, solver)

    logger.warning(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    logger.warning("Starting link prediction")
    logger.warning("------------------------------")
    
    df = get_prediction(cfg_pred, solver, relation_vocab, _dataset)
    df = merge_with_entity_vocab(df, _dataset, entity_vocab, relation_vocab)
    df = df.sort_values(['query_node', 'query_relation', 'probability'], ascending=[True, False, False])
    
    logger.warning("Link prediction done")
    logger.warning("Saving to file")
    df.to_csv(os.path.join(working_dir, "predictions.csv"), index=False, sep="\t")
    logger.warning("Done")
    logger.warning("------------------------------")
