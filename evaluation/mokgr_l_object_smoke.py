import types
import torch

from biopathnet.model import NeuralBellmanFordNetwork


class DummyGraph:
    def __init__(self, num_relation):
        self.num_relation = num_relation

    def undirected(self, add_inverse=True):
        return self


def main():
    torch.manual_seed(1234)

    model = NeuralBellmanFordNetwork(
        input_dim=32,
        hidden_dims=[32, 32, 32, 32, 32, 32],
        num_relation=13,
        message_func="distmult",
        aggregate_func="pna",
        short_cut=True,
        layer_norm=True,
        dependent=True,
        symmetric=False,
        edge_gate=True,
        gate_hidden_dim=None,
        mokgr_l_enable=True,
        mokgr_l_min_hop=2,
        mokgr_l_max_hop=6,
        mokgr_l_num_experts=3,
        mokgr_l_temperature=1.1,
    )
    model.eval()

    batch_size = 2
    num_nodes = 12
    num_neg = 3
    hidden_dim = 32
    num_hops = 6

    h_index = torch.tensor([
        [1, 1, 1],
        [2, 2, 2],
    ], dtype=torch.long)

    t_index = torch.tensor([
        [3, 4, 5],
        [6, 7, 8],
    ], dtype=torch.long)

    r_index = torch.tensor([
        [0, 0, 0],
        [1, 1, 1],
    ], dtype=torch.long)

    node_feature = torch.randn(num_nodes, batch_size, hidden_dim + hidden_dim)
    hop_hidden_states = [torch.randn(num_nodes, batch_size, hidden_dim) for _ in range(num_hops)]
    relation_query = torch.randn(batch_size, hidden_dim)

    def fake_bellmanford(self, graph, h_index_, r_index_, separate_grad=False):
        return {
            "node_feature": node_feature,
            "step_graphs": [],
            "hop_hidden_states": hop_hidden_states,
            "relation_query": relation_query,
            "layer_queries": [relation_query for _ in range(num_hops)],
        }

    model.bellmanford = types.MethodType(fake_bellmanford, model)

    graph = DummyGraph(num_relation=13)
    score = model(graph, h_index, t_index, r_index)

    debug = model._last_mokgr_l_debug
    print("score_shape =", tuple(score.shape))
    print("score_finite =", bool(torch.isfinite(score).all().item()))
    if debug is None:
        print("mokgr_l_debug = NONE")
    else:
        hop_weight = debug["hop_weight"].detach().cpu()
        print("MOKGR_L_HOP_WEIGHT_SHAPE =", tuple(hop_weight.shape))
        print("MOKGR_L_HOP_WEIGHT_ROW0 =", hop_weight[0].tolist())
        print("MOKGR_L_HOP_WEIGHT_SUM_ROW0 =", float(hop_weight[0].sum().item()))
        topk = debug["topk_indices"].detach().cpu()
        print("MOKGR_L_TOPK_ROW0 =", topk[0].tolist())


if __name__ == "__main__":
    main()
