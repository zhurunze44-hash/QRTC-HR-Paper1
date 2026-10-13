import os
import inspect
from types import MethodType
from collections.abc import Sequence
from decorator import decorator
import copy
import math
import types
import inspect

import torch
from torch import nn
from torch import autograd
from biopathnet.raa_query_init import load_raa_anchor_cache, fuse_query_init

from torch_scatter import scatter_add

from torchdrug import core, layers, utils, data
from torchdrug.layers import functional
from torchdrug.core import Registry as R

from . import layer
from . import qrtc_common
from .evidence_router import RelationGuidedEvidenceRouter
from .mokgr_length_router import MoKGRLengthRouter
from .local_context_prior import HeadLocalContextEncoder, HeadLocalContextCacheProvider


@R.register("model.NBFNet")
class NeuralBellmanFordNetwork(nn.Module, core.Configurable):

    def __init__(self, input_dim, hidden_dims, num_relation=None, symmetric=False,
                 message_func="distmult", aggregate_func="pna", short_cut=False, layer_norm=False, activation="relu",
                 concat_hidden=False, num_mlp_layer=2, dependent=True, remove_one_hop=False,
                 num_beam=10, path_topk=10,
                 use_evidence_router=False,
                 router_hidden_dim=64,
                 router_temperature=1.0,
                 router_residual_init=-2.0,
                 router_type_vocab_cap=64, edge_gate=False, gate_hidden_dim=None,
                 mokgr_l_enable=False,
                 mokgr_l_min_hop=2,
                 mokgr_l_max_hop=None,
                 mokgr_l_num_experts=3,
                 mokgr_l_temperature=1.1):
        super(NeuralBellmanFordNetwork, self).__init__()
        if not isinstance(hidden_dims, Sequence):
            hidden_dims = [hidden_dims]
        if num_relation is None:
            double_relation = 1
        else:
            num_relation = int(num_relation)
            double_relation = num_relation * 2
        self.dims = [input_dim] + list(hidden_dims)
        self.num_relation = num_relation
        self.symmetric = symmetric
        self.short_cut = short_cut
        self.concat_hidden = concat_hidden
        self.remove_one_hop = remove_one_hop
        self.num_beam = num_beam
        self.path_topk = path_topk
        self.use_evidence_router = use_evidence_router
        self.collect_router_debug = os.environ.get("BIOPATHNET_COLLECT_ROUTER_DEBUG", "0") == "1"
        self.print_router_debug = os.environ.get("BIOPATHNET_PRINT_ROUTER_DEBUG", "0") == "1"
        self._last_router_debug = None
        self.use_rg_min_post = False
        self.rg_min_post_router = None
        self._last_rg_min_debug = None
        self._rg_min_rel_probe_done = False
        self.local_context_enable = os.environ.get("BIOPATHNET_LOCAL_CONTEXT_ENABLE", "0") == "1"
        self.local_context_dim = int(os.environ.get("BIOPATHNET_LOCAL_CONTEXT_DIM", "64"))
        self.local_context_hidden_dim = int(os.environ.get("BIOPATHNET_LOCAL_CONTEXT_HIDDEN_DIM", "64"))
        self.local_context_max_neighbor = int(os.environ.get("BIOPATHNET_LOCAL_CONTEXT_MAX_NEIGHBOR", "16"))
        self.proto_use_local_context = os.environ.get("BIOPATHNET_PROTO_USE_LOCAL_CONTEXT", "0") == "1"
        self.local_context_encoder = None
        self.local_context_cache = None
        self._last_local_context_debug = None

        self.edge_gate = edge_gate
        self.gate_hidden_dim = gate_hidden_dim if gate_hidden_dim is not None else self.dims[0]
        self.mokgr_l_enable = mokgr_l_enable
        self.mokgr_l_min_hop = int(mokgr_l_min_hop)
        self.mokgr_l_max_hop = None if mokgr_l_max_hop is None else int(mokgr_l_max_hop)
        self.mokgr_l_num_experts = int(mokgr_l_num_experts)
        self.mokgr_l_temperature = float(mokgr_l_temperature)
        self._last_mokgr_l_debug = None
        self.layers = nn.ModuleList()
        conv_cls = layer.QueryAwareGeneralizedRelationalConv if edge_gate else layer.GeneralizedRelationalConv
        for i in range(len(self.dims) - 1):
            kwargs = dict(
                input_dim=self.dims[i],
                output_dim=self.dims[i + 1],
                num_relation=double_relation,
                query_input_dim=self.dims[0],
                message_func=message_func,
                aggregate_func=aggregate_func,
                layer_norm=layer_norm,
                activation=activation,
                dependent=dependent,
            )
            if edge_gate:
                kwargs["gate_hidden_dim"] = self.gate_hidden_dim
            self.layers.append(conv_cls(**kwargs))
        feature_dim = hidden_dims[-1] * (len(hidden_dims) if concat_hidden else 1) + input_dim
        self.query = nn.Embedding(double_relation, input_dim)
        self.cp_acc_enable = os.getenv("BIOPATHNET_CPACC_ENABLE", "0") == "1"
        self.cp_acc_threshold = float(os.getenv("BIOPATHNET_CPACC_THRESH", "0.30"))
        self.cp_accuracy_tensor = None
        self.cp_accuracy_layers = None
        self.cp_accuracy_gate = None
        self._last_cp_acc_debug = None
        if self.cp_acc_enable:
            self.cp_accuracy_layers = nn.ModuleList()
            for i in range(len(self.dims) - 1):
                self.cp_accuracy_layers.append(layer.CPAccuracyGeneralizedRelationalConv(
                    input_dim=self.dims[i],
                    output_dim=self.dims[i + 1],
                    num_relation=double_relation,
                    query_input_dim=self.dims[0],
                    message_func=message_func,
                    aggregate_func=aggregate_func,
                    layer_norm=layer_norm,
                    activation=activation,
                    dependent=dependent,
                    unmasked_tensor=None,
                ))
            self.cp_accuracy_gate = nn.GRU(self.dims[-1] * 2, self.dims[-1], batch_first=True)
        self.m1_hop_alloc_enable = os.getenv("M1_HOP_ALLOC_ENABLE", "0") == "1"
        self.m1_print_debug = os.getenv("M1_HOP_ALLOC_DEBUG", "0") == "1"
        self._last_m1_hop_debug = None
        if self.m1_hop_alloc_enable and self.concat_hidden:
            raise ValueError("M1_HOP_ALLOC_ENABLE currently requires concat_hidden=False")
        if self.m1_hop_alloc_enable and self.use_evidence_router:
            raise ValueError("M1_HOP_ALLOC_ENABLE currently requires use_evidence_router=False")
        self.m1_hop_logits = nn.Linear(input_dim, len(self.layers))
        self.m1_shared_hop_logits = nn.Parameter(torch.zeros(len(self.layers)))
        self.m1_hop_mode = os.environ.get("M1_HOP_MODE", "rel")  # base|shared|rel
        self.hopfilm_enable = os.environ.get("HOPFILM_ENABLE", "0") == "1"
        self.hopfilm_hidden_dim = int(os.environ.get("HOPFILM_HIDDEN_DIM", "64"))
        self.hopfilm_gamma_scale = float(os.environ.get("HOPFILM_GAMMA_SCALE", "0.10"))
        self.hopfilm_beta_scale = float(os.environ.get("HOPFILM_BETA_SCALE", "0.10"))
        self.hopfilm_mlp = nn.Sequential(
            nn.Linear(len(hidden_dims), self.hopfilm_hidden_dim),
            nn.GELU(),
        )
        self.hopfilm_gamma = nn.Linear(self.hopfilm_hidden_dim, len(hidden_dims) * hidden_dims[0])
        self.hopfilm_beta = nn.Linear(self.hopfilm_hidden_dim, len(hidden_dims) * hidden_dims[0])
        self._hopfilm_freeze_done = False
        nn.init.zeros_(self.m1_hop_logits.weight)
        nn.init.zeros_(self.m1_hop_logits.bias)
        self.epb_enable = os.getenv("EPB_ENABLE", "0") == "1"
        self.epb_num_policy = 4
        self.epb_alpha = float(os.getenv("EPB_ALPHA", "0.5"))
        self.epb_alpha_rel = {}
        self.epb_debug_once = os.getenv("EPB_DEBUG_ONCE", "0") == "1"
        _epb_alpha_rel_env = os.getenv("EPB_ALPHA_REL", "").strip()
        if _epb_alpha_rel_env:
            for _spec in _epb_alpha_rel_env.split(","):
                _spec = _spec.strip()
                if not _spec:
                    continue
                _rid, _aval = _spec.split(":", 1)
                self.epb_alpha_rel[int(_rid)] = float(_aval)
        self._last_epb_debug = None
        self.epb_enable_only_qr = {int(x.strip()) for x in os.getenv("EPB_ENABLE_ONLY_QR", "").split(",") if x.strip()}
        self.epb_disable_qr = {int(x.strip()) for x in os.getenv("EPB_DISABLE_QR", "").split(",") if x.strip()}
        if self.epb_enable and not self.m1_hop_alloc_enable:
            raise ValueError("EPB_ENABLE currently requires M1_HOP_ALLOC_ENABLE=1")
        self.epb_router = nn.Sequential(
            nn.Linear(input_dim, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, self.epb_num_policy),
        )
        _epb_bank = torch.zeros(self.epb_num_policy, len(self.layers))
        _epb_bank[0, 0] = 1.0
        _epb_bank[1, -1] = 1.0
        _epb_bank[2, :] = 1.0 / len(self.layers)
        _mid = len(self.layers) // 2
        _epb_bank[3, max(0, _mid - 1): min(len(self.layers), _mid + 1)] = 1.0
        if _epb_bank[3].sum() > 0:
            _epb_bank[3] = _epb_bank[3] / _epb_bank[3].sum()
        self.register_buffer("epb_policy_bank", _epb_bank)
        self.unified_main_enable = os.getenv("UNIFIED_MAIN_ENABLE", "0") == "1"
        self.unified_epb_enable = os.getenv("UNIFIED_EPB_ENABLE", "0") == "1"
        self.unified_cpacc_enable = os.getenv("UNIFIED_CPACC_ENABLE", "0") == "1"
        self.unified_cpacc_abstain_enable = os.getenv("UNIFIED_CPACC_ABSTAIN_ENABLE", "0") == "1"
        self.unified_delta_scale = float(os.getenv("UNIFIED_DELTA_SCALE", "0.10"))
        self._last_unified_debug = None
        self.unified_lambda_init = float(os.getenv("UNIFIED_LAMBDA_INIT", "0.0"))
        self.unified_train_only = os.getenv("UNIFIED_TRAIN_ONLY", "0") == "1"
        self.unified_cpacc_train_only = os.getenv("UNIFIED_CPACC_TRAIN_ONLY", "0") == "1"
        self.epb_router_train_only = os.getenv("EPB_ROUTER_TRAIN_ONLY", "0") == "1"
        self.f8_direct_delta_enable = os.getenv("F8_DIRECT_DELTA_ENABLE", "0") == "1"
        self.f8_direct_train_only = os.getenv("F8_DIRECT_TRAIN_ONLY", "0") == "1"
        self.f8_direct_alpha = float(os.getenv("F8_DIRECT_ALPHA", "1.0"))
        self.f8_inst_gate_enable = os.getenv("F8_INST_GATE_ENABLE", "0") == "1"
        self.f8_inst_gate_train_only = os.getenv("F8_INST_GATE_TRAIN_ONLY", "0") == "1"
        self.f8_inst_alpha = float(os.getenv("F8_INST_ALPHA", "1.0"))
        self.qces_enable = os.getenv("QCES_ENABLE", "0") == "1"
        self.qces_topk = int(os.getenv("QCES_TOPK", "4"))
        self.qces_debug = os.getenv("QCES_DEBUG", "0") == "1"
        self._last_qces_debug = None
        self.qces_learnable = os.getenv("QCES_LEARNABLE", "0") == "1"
        self.qces_delta_scale = float(os.getenv("QCES_DELTA_SCALE", "0.10"))
        self.qces_rel_logit = nn.Linear(input_dim, self.query.num_embeddings)
        nn.init.zeros_(self.qces_rel_logit.weight)
        nn.init.zeros_(self.qces_rel_logit.bias)
        self._unified_freeze_done = False
        self.unified_lambda = nn.Parameter(torch.full((1,), self.unified_lambda_init))
        self.epb_residual_mlp = nn.Sequential(
            nn.Linear(input_dim * 3, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, input_dim),
        )
        self.cpacc_gate_mlp = nn.Sequential(
            nn.Linear(input_dim * 4, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, 1),
        )
        self.f8_direct_logits = nn.Parameter(torch.zeros(len(hidden_dims)))
        self.f8_inst_delta_logits = nn.Parameter(torch.zeros(len(hidden_dims)))
        self.f8_inst_gate = nn.Linear(len(hidden_dims), 1)
        self.f8_score_res_enable = os.getenv("F8_SCORE_RES_ENABLE", "0") == "1"
        self.f8_score_train_only = os.getenv("F8_SCORE_TRAIN_ONLY", "0") == "1"
        self.f8_score_alpha = float(os.getenv("F8_SCORE_ALPHA", "1.0"))
        self.f8_score_res = nn.Linear(feature_dim, 1)
        nn.init.zeros_(self.f8_score_res.weight)
        nn.init.zeros_(self.f8_score_res.bias)
        self.family_ctx_enable = os.getenv("FAMILY_CTX_ENABLE", "0") == "1"
        self.family_ctx_train_only = os.getenv("FAMILY_CTX_TRAIN_ONLY", "0") == "1"
        self.family_ctx_alpha = float(os.getenv("FAMILY_CTX_ALPHA", "1.0"))
        self.family_ctx_risk_gate_enable = os.getenv("FAMILY_CTX_RISK_GATE_ENABLE", "0") == "1"
        self.family_ctx_risk_proto_min = float(os.getenv("FAMILY_CTX_RISK_PROTO_MIN", "0.5"))
        self.family_ctx_risk_gate_floor = float(os.getenv("FAMILY_CTX_RISK_GATE_FLOOR", "0.25"))
        self.family_ctx_cand_risk_enable = os.getenv("FAMILY_CTX_CAND_RISK_ENABLE", "0") == "1"
        self.family_ctx_cand_risk_proto_min = float(os.getenv("FAMILY_CTX_CAND_RISK_PROTO_MIN", "0.5"))
        self.family_ctx_cand_risk_gate_floor = float(os.getenv("FAMILY_CTX_CAND_RISK_GATE_FLOOR", "0.25"))
        self.family_ctx_wsa_enable = bool(int(os.getenv("FAMILY_CTX_WSA_ENABLE", "0")))
        self.family_ctx_wsa_accept_disable = bool(int(os.getenv("FAMILY_CTX_WSA_ACCEPT_DISABLE", "0")))
        if os.getenv("FAMILY_CTX_PRINT_RUNTIME_CONFIG", "0") == "1":
            print("FAMILY_CTX_RUNTIME_CONFIG",
                  "enable=", int(self.family_ctx_enable),
                  "wsa_enable=", int(self.family_ctx_wsa_enable),
                  "risk_gate=", int(self.family_ctx_risk_gate_enable),
                  "cand_risk=", int(self.family_ctx_cand_risk_enable),
                  "wsa_accept_disable=", int(self.family_ctx_wsa_accept_disable))
        self.family_ctx_wsa_init_support = float(os.getenv("FAMILY_CTX_WSA_INIT_SUPPORT", "0.25"))
        self.family_ctx_wsa_warmup_ratio = float(os.getenv("FAMILY_CTX_WSA_WARMUP_RATIO", "0.15"))
        self.family_ctx_wsa_warmup_steps = int(os.getenv("FAMILY_CTX_WSA_WARMUP_STEPS", "0"))
        self.family_ctx_wsa_q_low = float(os.getenv("FAMILY_CTX_WSA_Q_LOW", "0.90"))
        self.family_ctx_wsa_q_high = float(os.getenv("FAMILY_CTX_WSA_Q_HIGH", "1.20"))
        self.family_ctx_wsa_c_low = float(os.getenv("FAMILY_CTX_WSA_C_LOW", "0.95"))
        self.family_ctx_wsa_c_high = float(os.getenv("FAMILY_CTX_WSA_C_HIGH", "1.30"))
        self.family_ctx_wsa_accept_power = float(os.getenv("FAMILY_CTX_WSA_ACCEPT_POWER", "1.5"))
        self.family_ctx_wsa_ema_momentum = float(os.getenv("FAMILY_CTX_WSA_EMA_MOMENTUM", "0.95"))
        self.family_ctx_evidence_family_enable = os.getenv("FAMILY_CTX_EVIDENCE_FAMILY_ENABLE", "0") == "1"
        self.family_ctx_evidence_exclude_query = os.getenv("FAMILY_CTX_EVIDENCE_EXCLUDE_QUERY", "1") == "1"
        self.register_buffer("family_ctx_proto_sep_ema", torch.tensor(1.0))
        self.register_buffer("family_ctx_cand_sep_ema", torch.tensor(1.0))
        self.family_ctx_num_families = int(os.getenv("FAMILY_CTX_NUM_FAMILIES", "4"))
        self.family_ctx_family_emb = nn.Embedding(self.family_ctx_num_families, self.dims[0])
        self.family_ctx_hop_gate = nn.Linear(self.dims[0] * 4, 1)
        self.family_ctx_proto_mlp = nn.Sequential(
            nn.Linear(self.dims[0] * 3, self.dims[0]),
            nn.ReLU(),
            nn.Linear(self.dims[0], self.dims[0]),
        )
        self.family_ctx_film = nn.Sequential(
            nn.Linear(self.dims[0] * 5, self.dims[0]),
            nn.ReLU(),
            nn.Linear(self.dims[0], self.dims[0] * 2),
        )
        nn.init.zeros_(self.family_ctx_hop_gate.weight)
        nn.init.zeros_(self.family_ctx_hop_gate.bias)
        nn.init.zeros_(self.family_ctx_proto_mlp[2].weight)
        nn.init.zeros_(self.family_ctx_proto_mlp[2].bias)
        nn.init.zeros_(self.family_ctx_film[2].weight)
        nn.init.zeros_(self.family_ctx_film[2].bias)
        self.register_buffer("family_ctx_family_id_table", self._build_family_id_table(), persistent=False)
        self._last_family_ctx_debug = None
        self._last_family_ctx_aux = None
        nn.init.zeros_(self.f8_inst_gate.weight)
        nn.init.constant_(self.f8_inst_gate.bias, -2.0)
        nn.init.zeros_(self.epb_residual_mlp[2].weight)
        nn.init.zeros_(self.epb_residual_mlp[2].bias)
        nn.init.zeros_(self.cpacc_gate_mlp[2].weight)
        nn.init.constant_(self.cpacc_gate_mlp[2].bias, -4.0)
        if self.family_ctx_train_only:
            for _n, _p in self.named_parameters():
                _p.requires_grad = (_n.startswith("family_ctx_hop_gate.") or _n.startswith("family_ctx_proto_mlp.") or _n.startswith("family_ctx_film.") or _n.startswith("family_ctx_family_emb."))
            self._unified_freeze_done = True
        elif self.f8_score_train_only:
            for _n, _p in self.named_parameters():
                _p.requires_grad = _n.startswith("f8_score_res.")
            self._unified_freeze_done = True
        elif self.f8_inst_gate_train_only:
            for _n, _p in self.named_parameters():
                _p.requires_grad = (_n == "f8_inst_delta_logits") or _n.startswith("f8_inst_gate.")
            self._unified_freeze_done = True
        elif self.f8_direct_train_only:
            for _n, _p in self.named_parameters():
                _p.requires_grad = (_n == "f8_direct_logits")
            self._unified_freeze_done = True
        elif self.epb_router_train_only:
            for _n, _p in self.named_parameters():
                _p.requires_grad = _n.startswith("epb_router.")
            self._unified_freeze_done = True
        elif self.unified_train_only:
            for _n, _p in self.named_parameters():
                _p.requires_grad = _n.startswith("epb_residual_mlp.") or _n.startswith("cpacc_gate_mlp.")
            self._unified_freeze_done = True
        elif self.unified_cpacc_train_only:
            for _n, _p in self.named_parameters():
                _p.requires_grad = _n.startswith("cpacc_gate_mlp.")
            self._unified_freeze_done = True
        self.srp_enable = os.getenv("SRP_ENABLE", "0") == "1"
        self.srp_qc_enable = os.getenv("SRP_QC_ENABLE", "0") == "1"
        self.srp_alpha = float(os.getenv("SRP_ALPHA", "0.02"))
        _srp_num_layer = len(self.layers) if hasattr(self, "layers") else len(hidden_dims)
        self.soft_path_prior = nn.Parameter(torch.zeros(double_relation, _srp_num_layer, input_dim))
        self._srp_last_stats = None
        nn.init.normal_(self.soft_path_prior, mean=0.0, std=1e-3)

        self.srp_query_gate = nn.Sequential(
            nn.Linear(input_dim, input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, _srp_num_layer),
        )
        nn.init.zeros_(self.srp_query_gate[2].weight)
        nn.init.constant_(self.srp_query_gate[2].bias, 2.0)
        self.srp_router = nn.ModuleList([
            nn.Linear(self.dims[0], 3 * self.dims[0]) for _ in range(len(self.layers))
        ])
        for _m in self.srp_router:
            nn.init.zeros_(_m.weight)
            nn.init.zeros_(_m.bias)

        self.raa_enable = os.getenv("RAA_ENABLE", "0") == "1"
        self.raa_alpha = float(os.getenv("RAA_ALPHA", "0.1"))
        self.raa_cache_pt = os.getenv("RAA_CACHE_PT", "")
        self._raa_pack = None
        self._raa_last_stats = None
        self._raa_entity_weight = None
        self.mlp = layers.MLP(feature_dim, [feature_dim] * (num_mlp_layer - 1) + [1])

        # Sandbox: candidate-conditioned QRTC readout (env-gated at init). Default OFF.
        self.qrtc_cand_readout_on = os.environ.get("QRTC_CAND_READOUT_ENABLE", "0") == "1"
        self.qrtc_cand_readout_beta = float(os.environ.get("QRTC_CAND_READOUT_BETA", "0.35"))
        self.qrtc_cand_readout_in_scale = float(os.environ.get("QRTC_CAND_READOUT_INPUT_SCALE", "0.5"))
        self.qrtc_cand_readout_tanh_scale = float(os.environ.get("QRTC_CAND_READOUT_TANH_SCALE", "3.0"))
        self.qrtc_cand_readout_train_only = os.environ.get("QRTC_CAND_READOUT_TRAIN_ONLY", "0") == "1"
        if self.qrtc_cand_readout_on:
            # Tail path embedding width is last GNN layer dim, not dims[0] (query input dim).
            _tail_dim = int(hidden_dims[-1])
            self.qrtc_cand_tail_dim = _tail_dim
            _nr = int(self.query.num_embeddings)
            # Compact gate: L2 distance of each candidate tail state vs positive + QRTC usage (per batch, broadcast).
            _gin = 1 + _nr
            self.qrtc_cand_gate_mlp = nn.Linear(_gin, 1)
            nn.init.normal_(self.qrtc_cand_gate_mlp.weight, std=0.05)
            nn.init.zeros_(self.qrtc_cand_gate_mlp.bias)
        else:
            self.qrtc_cand_gate_mlp = None
            self.qrtc_cand_tail_dim = int(hidden_dims[-1])

        # RICS-CS v1: relation-interaction and context-sensitive score adapter.
        # Default OFF. When enabled, the last layer is zero-initialized so the
        # initial behavior is exactly the clean NBFNet score.
        self.rics_enable = os.getenv("RICS_ENABLE", "0") == "1"
        self.rics_alpha = float(os.getenv("RICS_ALPHA", "0.1"))
        self.rics_print_debug = os.getenv("RICS_PRINT_DEBUG", "0") == "1"
        _rics_allow_raw = os.getenv("RICS_ALLOW_REL_IDS", "").strip()
        self.rics_allow_rel_ids = tuple(
            int(x.strip()) for x in _rics_allow_raw.split(",") if x.strip()
        )
        self.rics_center_delta = os.getenv("RICS_CENTER_DELTA", "0") == "1"
        self.rics_explicit_inverse_gate = os.getenv("RICS_EXPLICIT_INVERSE_GATE", "0") == "1"
        self.rics_base_rel_id = int(os.getenv("RICS_BASE_REL_ID", "7"))
        self.rics_delta = None
        self._rics_debug_printed = False
        self._last_rics_debug = None
        if self.rics_enable:
            self.rics_delta = nn.Sequential(
                nn.Linear(feature_dim + input_dim, feature_dim),
                nn.ReLU(),
                nn.Linear(feature_dim, 1),
            )
            nn.init.zeros_(self.rics_delta[-1].weight)
            nn.init.zeros_(self.rics_delta[-1].bias)
        self.rics_train_only = os.getenv("RICS_TRAIN_ONLY", "0") == "1"
        if self.rics_train_only:
            if not self.rics_enable:
                raise ValueError("RICS_TRAIN_ONLY=1 requires RICS_ENABLE=1")
            for _n, _p in self.named_parameters():
                _p.requires_grad = _n.startswith("rics_delta.")
        if self.local_context_enable:
            self.local_context_encoder = HeadLocalContextEncoder(
                num_relation=double_relation,
                relation_dim=self.dims[0],
                context_dim=self.local_context_dim,
                hidden_dim=self.local_context_hidden_dim,
                use_relation_hist=True,
            )
        if self.use_evidence_router:
            if self.concat_hidden:
                raise ValueError("use_evidence_router currently requires concat_hidden=False")
            self.evidence_router = RelationGuidedEvidenceRouter(
                query_dim=self.dims[0],
                hop_dims=self.dims[1:],
                expert_dim=self.dims[-1],
                type_vocab_cap=router_type_vocab_cap,
                router_hidden_dim=router_hidden_dim,
                router_temperature=router_temperature,
                residual_init=router_residual_init,
                local_context_enable=(self.local_context_enable and self.proto_use_local_context),
                local_context_dim=self.local_context_dim,
            )
        else:
            self.evidence_router = None
            self.use_rg_min_post = os.environ.get("RG_MIN_ENABLE", "0") == "1"
            self.rg_min_post_router = None
            self._last_rg_min_debug = None
            self._rg_min_rel_probe_done = False
            if self.use_rg_min_post:
                if self.use_evidence_router:
                    raise ValueError("RG_MIN_ENABLE requires use_evidence_router=False")
                if self.concat_hidden:
                    raise ValueError("RG_MIN_ENABLE currently requires concat_hidden=False")
                if self.symmetric:
                    raise ValueError("RG_MIN_ENABLE currently requires symmetric=False")
                from biopathnet.relation_guided_router_min_post import RelationGuidedEvidenceRouterMinPost
                _rg_hidden = int(os.environ.get("RG_MIN_ROUTER_HIDDEN_DIM", str(max(32, self.dims[0]))))
                _rg_gamma = float(os.environ.get("RG_MIN_GAMMA", "0.1"))
                self.rg_min_post_router = RelationGuidedEvidenceRouterMinPost(
                    query_dim=self.dims[0],
                    hop_dims=self.dims[1:],
                    residual_gamma=_rg_gamma,
                    router_hidden_dim=_rg_hidden,
                )
                if os.environ.get("BIOPATHNET_PRINT_ROUTER_DEBUG", "0") == "1":
                    print(
                        "RG_MIN_POST_ON "
                        f"use_rg_min_post={self.use_rg_min_post} "
                        f"router_cls={type(self.rg_min_post_router).__name__} "
                        f"hidden={_rg_hidden} gamma={_rg_gamma}"
                    )

        if self.mokgr_l_enable:
            if self.concat_hidden:
                raise ValueError("mokgr_l_enable currently requires concat_hidden=False")
            if self.symmetric:
                raise ValueError("mokgr_l_enable currently requires symmetric=False")
            _num_hops = len(self.layers)
            _max_hop = _num_hops if self.mokgr_l_max_hop is None else self.mokgr_l_max_hop
            self.mokgr_l_router = MoKGRLengthRouter(
                query_dim=self.dims[0],
                num_hops=_num_hops,
                min_hop=self.mokgr_l_min_hop,
                max_hop=_max_hop,
                num_experts=self.mokgr_l_num_experts,
                temperature=self.mokgr_l_temperature,
            )
        else:
            self.mokgr_l_router = None

        # QRTC_MINIMAL_PATCH_V6
        self.qrtc_enable = os.environ.get("QRTC_ENABLE", "0") == "1"
        self.qrtc_use_memory = os.environ.get("QRTC_USE_MEMORY", "1") == "1"
        self.qrtc_topk = int(os.environ.get("QRTC_TOPK", "4"))
        self.qrtc_collect_debug = os.environ.get("QRTC_DEBUG", "0") == "1"

        self.qrtc_hidden_dim = self.query.weight.shape[1]
        self.qrtc_init_memory = nn.Parameter(torch.zeros(self.qrtc_hidden_dim))
        self._last_qrtc_debug_layers = []
        # QRTC_TRAIN_ONLY_FORCE_UNFREEZE_V1
        if os.environ.get("QRTC_TRAIN_ONLY", "0") == "1":
            _qrtc_keep = ("qrtc_init_memory", "qrtc_precedent_mlp", "qrtc_gate_mlp", "qrtc_usage_mlp")
            for _name, _param in self.named_parameters():
                _param.requires_grad = any(_k in _name for _k in _qrtc_keep)


        self.qrtc_precedent_mlp = nn.Sequential(
            nn.Linear(self.qrtc_hidden_dim * 2 + 1, self.qrtc_hidden_dim),
            nn.ReLU(),
            nn.Linear(self.qrtc_hidden_dim, 1),
        )
        self.qrtc_gate_mlp = nn.Sequential(
            nn.Linear(self.qrtc_hidden_dim * 3, self.qrtc_hidden_dim),
            nn.ReLU(),
            nn.Linear(self.qrtc_hidden_dim, 1),
        )
        self.qrtc_usage_mlp = nn.Sequential(
            nn.Linear(self.qrtc_hidden_dim * 2 + 1, self.qrtc_hidden_dim),
            nn.ReLU(),
            nn.Linear(self.qrtc_hidden_dim, 1),
        )
        nn.init.zeros_(self.qrtc_usage_mlp[0].weight)
        nn.init.zeros_(self.qrtc_usage_mlp[0].bias)
        nn.init.zeros_(self.qrtc_usage_mlp[2].weight)
        nn.init.constant_(self.qrtc_usage_mlp[2].bias, 8.0)
        self._install_qrtc_message_wrappers()

        # QRTC_TRAIN_ONLY_PATCH_V1
        if os.environ.get("QRTC_TRAIN_ONLY", "0") == "1":
            for _n, _p in self.named_parameters():
                if not _n.startswith("qrtc_"):
                    _p.requires_grad = False


        # RICS_FINAL_TRAIN_ONLY_FREEZE_END_OF_INIT:
        # Must run after all optional modules, including qrtc_* modules, are created.
        if getattr(self, "rics_train_only", False):
            for _n, _p in self.named_parameters():
                _p.requires_grad = _n.startswith("rics_delta.")

        if self.qrtc_cand_readout_on and self.qrtc_cand_readout_train_only and self.qrtc_cand_gate_mlp is not None:
            for _n, _p in self.named_parameters():
                _p.requires_grad = _n.startswith("qrtc_cand_gate_mlp")
            _tr = [_n for _n, _p in self.named_parameters() if _p.requires_grad]
            print("QRTC_CAND_READOUT_TRAIN_ONLY trainable =", _tr)

    def _apply_qrtc_candidate_readout(self, feature, output, r_index):
        """Per-candidate gate on tail hidden before mlp; uses pos-tail contrast + query + QRTC usage."""
        if self.qrtc_cand_gate_mlp is None or (not self.qrtc_cand_readout_on):
            return feature
        if not self.qrtc_enable:
            return feature
        _H = int(getattr(self, "qrtc_cand_tail_dim", self.dims[-1]))
        if feature.size(-1) <= _H or feature.size(1) < 2:
            return feature
        base = feature[..., :_H]
        qpart = feature[..., _H:]
        bsz, n_cand, _ = base.shape
        pos_ref = base[:, :1, :]
        diff = (base - pos_ref).norm(dim=-1, keepdim=True)
        _nr = int(self.query.num_embeddings)
        usage = output.get("qrtc_rel_usage_prev", None)
        if usage is None:
            ufeat = base.new_zeros(bsz, n_cand, _nr)
        else:
            if usage.dim() == 1:
                usage = usage.unsqueeze(0)
            usage = usage.to(device=base.device, dtype=base.dtype)
            if usage.size(0) == 1 and bsz > 1:
                usage = usage.expand(bsz, -1)
            elif usage.size(0) != bsz:
                return feature
            if usage.size(-1) < _nr:
                usage = torch.cat(
                    [usage, usage.new_zeros(bsz, _nr - usage.size(-1))],
                    dim=-1,
                )
            elif usage.size(-1) > _nr:
                usage = usage[..., :_nr]
            ufeat = usage.unsqueeze(1).expand(bsz, n_cand, -1)
        gate_in = torch.cat([diff, ufeat], dim=-1)
        if os.environ.get("QRTC_CAND_READOUT_DEBUG", "0") == "1" and (not getattr(self, "_qrtc_cand_gi_once", False)):
            self._qrtc_cand_gi_once = True
            print(
                "QRTC_CAND_GATE_IN",
                "shape=",
                tuple(gate_in.shape),
                "diff_std_cand=",
                float(diff.squeeze(-1).std(dim=1, unbiased=False).mean().cpu()),
            )
        _logit = self.qrtc_cand_gate_mlp(gate_in * self.qrtc_cand_readout_in_scale)
        _logit = _logit - _logit.mean(dim=1, keepdim=True)
        gate = (
            0.62 + 0.38 * torch.tanh(_logit * self.qrtc_cand_readout_tanh_scale)
        ).clamp(min=0.35, max=0.98)
        beta = self.qrtc_cand_readout_beta
        scale = (1.0 - beta) + beta * gate
        new_base = base * scale
        if os.environ.get("QRTC_CAND_READOUT_DEBUG", "0") == "1" and (not getattr(self, "_qrtc_cand_dbg_once", False)):
            self._qrtc_cand_dbg_once = True
            gv = gate.detach().squeeze(-1)
            print(
                "QRTC_CAND_READOUT_DEBUG",
                "logit_std_cand=",
                float(_logit.squeeze(-1).std(dim=1, unbiased=False).mean().cpu()),
                "gate_mean=",
                float(gv.mean().cpu()),
                "gate_std_cand=",
                float(gv.std(dim=1, unbiased=False).mean().cpu()),
                "gate_minmax=",
                float(gv.min().cpu()),
                float(gv.max().cpu()),
                "scale_mean=",
                float(scale.detach().mean().cpu()),
            )
        return torch.cat([new_base, qpart], dim=-1)

    def build_local_context_cache_once(self, graph):
        if (not self.local_context_enable) or (self.local_context_cache is not None):
            return

        edge_list = getattr(graph, "edge_list", None)
        if edge_list is None or edge_list.size(-1) < 3:
            raise ValueError("local context cache requires graph.edge_list with at least 3 columns")

        edge_list3 = edge_list[:, :3]
        num_node = int(graph.num_node)
        num_relation = int(getattr(graph, "num_relation", self.query.num_embeddings))

        cache = HeadLocalContextCacheProvider(
            num_node=num_node,
            num_relation=num_relation,
            max_neighbor=self.local_context_max_neighbor,
        )
        cache.build_from_edge_list(edge_list3)
        self.local_context_cache = cache

    def get_local_context_batch(self, h_index, device):
        if (not self.local_context_enable) or (self.local_context_cache is None):
            return None
        return self.local_context_cache.get_batch(h_index, device=device)
    def _maybe_build_local_context(self, graph, h_index, relation_query):
        if (not self.local_context_enable) or (not self.proto_use_local_context):
            return None, {}

        self.build_local_context_cache_once(graph)
        ctx_batch = self.get_local_context_batch(h_index=h_index, device=relation_query.device)
        relation_weight = self.query.weight
        neighbor_rel_emb = relation_weight[ctx_batch["neighbor_rel_ids"]]
        neighbor_dir_onehot = torch.nn.functional.one_hot(
            ctx_batch["neighbor_dir_ids"], num_classes=2
        ).float()

        local_context, local_aux = self.local_context_encoder(
            relation_emb=relation_query,
            rel_hist_in=ctx_batch["rel_hist_in"],
            rel_hist_out=ctx_batch["rel_hist_out"],
            neighbor_rel_emb=neighbor_rel_emb,
            neighbor_dir_onehot=neighbor_dir_onehot,
            neighbor_mask=ctx_batch["neighbor_mask"],
        )
        return local_context, local_aux

    def _srp_router_mix(self, layer_id, query, prior):
        logits = self.srp_router[layer_id](query)  # [B, 3D]
        bsz, dim = prior.shape
        logits = logits.view(bsz, dim, 3)          # [B, D, 3]
        pi = torch.softmax(logits, dim=-1)         # [B, D, 3]

        mixed = (
            pi[..., 1] * (0.5 * prior) +
            pi[..., 2] * prior
        )

        if os.getenv("SRP_ROUTER_SMOKE", "0") == "1":
            done = getattr(self, "_srp_router_smoke_done", set())
            if layer_id not in done:
                mean_pi = pi.mean(dim=(0, 1)).detach().cpu().tolist()
                print(f"SRP_ROUTER_SMOKE layer={layer_id} mean_pi={mean_pi}")
                done = set(done)
                done.add(layer_id)
                self._srp_router_smoke_done = done

        return mixed

    def remove_easy_edges(self, graph, h_index, t_index, r_index=None):
        if self.remove_one_hop:
            h_index_ext = torch.cat([h_index, t_index], dim=-1)
            t_index_ext = torch.cat([t_index, h_index], dim=-1)
            if r_index is not None:
                any = -torch.ones_like(h_index_ext)
                pattern = torch.stack([h_index_ext, t_index_ext, any], dim=-1)
            else:
                pattern = torch.stack([h_index_ext, t_index_ext], dim=-1)
        else:
            if r_index is not None:
                pattern = torch.stack([h_index, t_index, r_index], dim=-1)
            else:
                pattern = torch.stack([h_index, t_index], dim=-1)
        pattern = pattern.flatten(0, -2)
        edge_index = graph.match(pattern)[0]
        edge_mask = ~functional.as_mask(edge_index, graph.num_edge)
        return graph.edge_mask(edge_mask)

    def negative_sample_to_tail(self, h_index, t_index, r_index):
        # convert p(h | t, r) to p(t' | h', r')
        # h' = t, r' = r^{-1}, t' = h
        
        # in case of classical KG setting, new_h_index consists of half h (half batch_size, num_neg +1 ) and half t
        # bcs of how the data is ordered in predict (task.py)
        # new_t_index: half neg_t, half neg_h
        # new_r_index: half r, half r + num_relation (for inverse relation)
        # constructing basically (pos_h, r, neg_t) and (pos_t, r-1, neg_h)
        
        is_t_neg = (h_index == h_index[:, [0]]).all(dim=-1, keepdim=True)

        # if True (h_index = pos_h_index), get the h_index, else t_index
        new_h_index = torch.where(is_t_neg, h_index, t_index)
        # if True (h_index = pos_h_index), get the t_index, else h_index
        new_t_index = torch.where(is_t_neg, t_index, h_index)
        # if True (h_index = pos_h_index), get the r_index, else r_index + num_relation (for inverse relation)
        new_r_index = torch.where(is_t_neg, r_index, r_index + self.num_relation)
        return new_h_index, new_t_index, new_r_index

    def as_relational_graph(self, graph, self_loop=True):
        # add self loop
        # convert homogeneous graphs to knowledge graphs with 1 relation
        edge_list = graph.edge_list
        edge_weight = graph.edge_weight
        if self_loop:
            node_in = node_out = torch.arange(graph.num_node, device=self.device)
            loop = torch.stack([node_in, node_out], dim=-1)
            edge_list = torch.cat([edge_list, loop])
            edge_weight = torch.cat([edge_weight, torch.ones(graph.num_node, device=self.device)])
        relation = torch.zeros(len(edge_list), 1, dtype=torch.long, device=self.device)
        edge_list = torch.cat([edge_list, relation], dim=-1)
        graph = type(graph)(edge_list, edge_weight=edge_weight, num_node=graph.num_node,
                            num_relation=1, meta_dict=graph.meta_dict, **graph.data_dict)
        return graph

    #@utils.cached

    def _build_cp_relation_filter_once(self, graph):
        cache = getattr(self, "_cp_relation_filter_cache", None)
        if cache is not None:
            return cache

        edge_list = getattr(graph, "edge_list", None)
        if edge_list is None or edge_list.size(-1) < 3:
            return None

        edge_list3 = edge_list[:, :3].detach().cpu().long()
        src = edge_list3[:, 0].tolist()
        rel = edge_list3[:, 2].tolist()
        if not rel:
            return None

        num_rel = max(rel) + 1
        rel_sets = {}
        for s, r in zip(src, rel):
            rel_sets.setdefault(s, set()).add(r)

        support = [0 for _ in range(num_rel)]
        co = [[0 for _ in range(num_rel)] for _ in range(num_rel)]

        for rs in rel_sets.values():
            rs = sorted(rs)
            for r in rs:
                support[r] += 1
            for r in rs:
                for r2 in rs:
                    co[r][r2] += 1

        acc_thr = float(os.environ.get("BIOPATHNET_CP_ACC_THRESH", "0.30"))
        compat = torch.zeros(num_rel, num_rel, dtype=torch.bool)
        for r in range(num_rel):
            compat[r, r] = True
            if support[r] <= 0:
                continue
            for r2 in range(num_rel):
                if co[r][r2] / support[r] >= acc_thr:
                    compat[r, r2] = True

        cache = {"compat": compat.to(edge_list.device)}
        self._cp_relation_filter_cache = cache
        return cache

    def _maybe_cp_filter_graph(self, graph, r_index):
        if os.environ.get("BIOPATHNET_CP_POOL_ENABLE", "0") != "1":
            return graph

        cache = self._build_cp_relation_filter_once(graph)
        if cache is None or r_index is None:
            return graph

        compat = cache["compat"]
        qrels = r_index.detach().view(-1).long()
        qrels = qrels[(qrels >= 0) & (qrels < compat.size(0))]
        if qrels.numel() == 0:
            return graph

        allowed = compat[qrels.unique()].any(dim=0)
        edge_rel = graph.edge_list[:, 2].long().clamp(min=0, max=compat.size(0) - 1)
        edge_mask = allowed[edge_rel]

        keep_n = int(edge_mask.long().sum().item())
        min_keep = int(os.environ.get("BIOPATHNET_CP_MIN_KEEP_EDGES", "1024"))
        if keep_n < min_keep:
            self._last_cp_pool_debug = {
                "enabled": True,
                "kept_edges": keep_n,
                "kept_ratio": float(edge_mask.float().mean().item()) if edge_mask.numel() > 0 else 0.0,
                "fallback_full_graph": True,
            }
            return graph

        self._last_cp_pool_debug = {
            "enabled": True,
            "kept_edges": keep_n,
            "kept_ratio": float(edge_mask.float().mean().item()),
            "fallback_full_graph": False,
        }
        return graph.edge_mask(edge_mask)




        # QRTC_TRAIN_ONLY_FINALIZE_V2
        if os.environ.get("QRTC_TRAIN_ONLY", "0") == "1":
            _qrtc_keep = ("qrtc_init_memory", "qrtc_precedent_mlp", "qrtc_gate_mlp", "qrtc_usage_mlp")
            for _n, _p in self.named_parameters():
                _p.requires_grad = any(_k in _n for _k in _qrtc_keep)
            _trainable = [_n for _n, _p in self.named_parameters() if _p.requires_grad]
            print("QRTC_TRAIN_ONLY_TRAINABLE =", _trainable)

    def _install_qrtc_message_wrappers(self):
        for layer in self.layers:
            if getattr(layer, "_qrtc_message_wrapped", False):
                continue
            if not hasattr(layer, "message"):
                continue

            _orig_message = layer.message
            _sig = inspect.signature(_orig_message)

            def _wrapped_message(layer_self, *m_args, _orig=_orig_message, _sig=_sig, **m_kwargs):
                message = _orig(*m_args, **m_kwargs)
                _qrtc_state = getattr(layer_self, "_qrtc_state", None)
                if _qrtc_state is None or (not _qrtc_state.get("enabled", False)):
                    return message

                edge_type = None
                _graph = None
                try:
                    bound = _sig.bind_partial(*m_args, **m_kwargs)
                    edge_type = bound.arguments.get("edge_type", None)
                    _graph = bound.arguments.get("graph", None)
                except Exception:
                    edge_type = None
                    _graph = None
                if edge_type is None:
                    edge_type = m_kwargs.get("edge_type", None)
                if _graph is None:
                    _graph = m_kwargs.get("graph", None)
                if _graph is None and len(m_args) >= 1:
                    _graph = m_args[0]
                if edge_type is None and len(m_args) >= 4:
                    edge_type = m_args[3]
                if edge_type is None and _graph is not None and hasattr(_graph, "edge_list"):
                    try:
                        edge_type = _graph.edge_list[:, 2]
                    except Exception:
                        edge_type = None
                if edge_type is None:
                    return message

                _batch_size = int(_qrtc_state["query_rel_emb"].size(0))
                _gate_full = qrtc_common.compute_qrtc_relation_gate(
                    _qrtc_state, int(_qrtc_state["num_relation"]), _batch_size
                )
                if _gate_full is None:
                    return message
                _gate = _gate_full[edge_type]
                # QRTC_LIVE_GRAD_PROBE_V2
                if os.environ.get("QRTC_LIVE_GRAD_PROBE", "0") == "1" and (not hasattr(self, "_qrtc_live_grad_probe_fired")):
                    self._qrtc_live_grad_probe_fired = True
                    print("QRTC_PROBE_GATE_REQUIRES_GRAD =", bool(_gate.requires_grad))
                    print("QRTC_PROBE_MESSAGE_IN_REQUIRES_GRAD =", bool(message.requires_grad))
                if message.size(0) != _gate.size(0):
                    _pad_rows = message.size(0) - _gate.size(0)
                    if _pad_rows > 0:
                        _pad = torch.ones(_pad_rows, _gate.size(1), _gate.size(2), device=_gate.device, dtype=_gate.dtype)
                        _gate = torch.cat([_gate, _pad], dim=0)
                message = message * _gate

                _msg_strength = message.detach().abs().mean(dim=-1)
                _msg_strength_main = _msg_strength[:edge_type.size(0)]
                _rel_usage = scatter_add(
                    _msg_strength_main,
                    edge_type,
                    dim=0,
                    dim_size=_qrtc_state["num_relation"],
                )
                _qrtc_state["rel_usage_next"] = _rel_usage.transpose(0, 1).contiguous()
                # QRTC_DUMP_GATE_STATS_V3_UNCOND
                if os.environ.get("QRTC_DUMP_GATE_STATS", "0") == "1":
                    _gate_scalar_dump = _gate.detach().squeeze(-1)
                    _lid = int(_qrtc_state.get("layer_id", -1))
                    _usem = int(bool(_qrtc_state.get("use_memory", False)))
                    _pnorm = float(_qrtc_state["precedent_memory"].detach().norm(dim=-1).mean().cpu())
                    _mean = float(_gate_scalar_dump.mean().cpu())
                    _std = float(_gate_scalar_dump.std(unbiased=False).cpu())
                    _gmin = float(_gate_scalar_dump.min().cpu())
                    _gmax = float(_gate_scalar_dump.max().cpu())
                    print(f"QRTC_GATE_STATS layer={_lid} use_memory={_usem} mean={_mean:.6f} std={_std:.6f} min={_gmin:.6f} max={_gmax:.6f} precedent_norm={_pnorm:.6f}")
                    _pt_ids = _qrtc_state.get("precedent_topk_ids", None)
                    _pt_w = _qrtc_state.get("precedent_topk_weights", None)
                    if _pt_ids is not None and _pt_w is not None:
                        try:
                            _ids0 = _pt_ids[0].tolist()
                            _w0 = [round(float(x), 6) for x in _pt_w[0].tolist()]
                            print(f"QRTC_PRECEDENT_TOPK layer={_lid} ids={_ids0} weights={_w0}")
                        except Exception:
                            pass
                if _qrtc_state.get("collect_debug", False):
                    _gate_scalar = _gate.detach().squeeze(-1)
                    # QRTC_DUMP_GATE_STATS_V2
                    if os.environ.get("QRTC_DUMP_GATE_STATS", "0") == "1":
                        _lid = int(_qrtc_state.get("layer_id", -1))
                        _usem = int(bool(_qrtc_state.get("use_memory", False)))
                        _pnorm = float(_qrtc_state["precedent_memory"].detach().norm(dim=-1).mean().cpu())
                        _mean = float(_gate_scalar.mean().cpu())
                        _std = float(_gate_scalar.std(unbiased=False).cpu())
                        _gmin = float(_gate_scalar.min().cpu())
                        _gmax = float(_gate_scalar.max().cpu())
                        print(f"QRTC_GATE_STATS layer={_lid} use_memory={_usem} mean={_mean:.6f} std={_std:.6f} min={_gmin:.6f} max={_gmax:.6f} precedent_norm={_pnorm:.6f}")
                        _pt_ids = _qrtc_state.get("precedent_topk_ids", None)
                        _pt_w = _qrtc_state.get("precedent_topk_weights", None)
                        if _pt_ids is not None and _pt_w is not None:
                            try:
                                _ids0 = _pt_ids[0].tolist()
                                _w0 = [round(float(x), 6) for x in _pt_w[0].tolist()]
                                print(f"QRTC_PRECEDENT_TOPK layer={_lid} ids={_ids0} weights={_w0}")
                            except Exception:
                                pass
                    _rel_gate_sum = scatter_add(
                        _gate_scalar,
                        edge_type,
                        dim=0,
                        dim_size=_qrtc_state["num_relation"],
                    )
                    _rel_gate_cnt = scatter_add(
                        torch.ones_like(_gate_scalar),
                        edge_type,
                        dim=0,
                        dim_size=_qrtc_state["num_relation"],
                    ).clamp(min=1.0)
                    _rel_gate_mean = (_rel_gate_sum / _rel_gate_cnt).transpose(0, 1).contiguous()

                    _ktop = min(3, _rel_gate_mean.size(-1))
                    _prom_vals, _prom_ids = _rel_gate_mean.topk(k=_ktop, dim=-1)
                    _supp_vals, _supp_ids = (-_rel_gate_mean).topk(k=_ktop, dim=-1)

                    _qrtc_state["debug"] = {
                        "layer_id": int(_qrtc_state["layer_id"]),
                        "precedent_topk_ids": _qrtc_state.get("precedent_topk_ids"),
                        "precedent_topk_weights": _qrtc_state.get("precedent_topk_weights"),
                        "promoted_topk_ids": _prom_ids.detach().cpu(),
                        "promoted_topk_gates": _prom_vals.detach().cpu(),
                        "suppressed_topk_ids": _supp_ids.detach().cpu(),
                        "suppressed_topk_gates": (-_supp_vals).detach().cpu(),
                    }

                return message

            layer.message = MethodType(_wrapped_message, layer)
            layer._qrtc_message_wrapped = True

    def _qrtc_build_precedent_memory(self, query_rel_emb, rel_usage_prev, relation_table):
        batch_size = query_rel_emb.size(0)
        if (not self.qrtc_enable) or (not self.qrtc_use_memory) or (rel_usage_prev is None):
            precedent_memory = self.qrtc_init_memory.unsqueeze(0).expand(batch_size, -1)
            return precedent_memory, None, None

        k = min(self.qrtc_topk, rel_usage_prev.size(-1))
        topk_usage, topk_ids = rel_usage_prev.topk(k=k, dim=-1)
        topk_rel_emb = relation_table[topk_ids]

        q = query_rel_emb.unsqueeze(1).expand(-1, k, -1)
        u = topk_usage.unsqueeze(-1)
        att_input = torch.cat([q, topk_rel_emb, u], dim=-1)
        att_logit = self.qrtc_precedent_mlp(att_input).squeeze(-1)
        att_weight = torch.softmax(att_logit, dim=-1)
        precedent_memory = (att_weight.unsqueeze(-1) * topk_rel_emb).sum(dim=1)
        return precedent_memory, topk_ids, att_weight

    def _qrtc_prepare_layer_state(self, layer_id, query_rel_emb, relation_table, rel_usage_prev):
        precedent_memory, topk_ids, topk_weights = self._qrtc_build_precedent_memory(
            query_rel_emb, rel_usage_prev, relation_table
        )
        return {
            "enabled": self.qrtc_enable,
            "use_memory": self.qrtc_use_memory,
            "layer_id": layer_id,
            "query_rel_emb": query_rel_emb,
            "precedent_memory": precedent_memory,
            "relation_table": relation_table,
            "gate_mlp": self.qrtc_gate_mlp,
            "usage_mlp": self.qrtc_usage_mlp,
            "num_relation": relation_table.size(0),
            "collect_debug": self.qrtc_collect_debug,
            "precedent_topk_ids": topk_ids.detach().cpu() if topk_ids is not None else None,
            "precedent_topk_weights": topk_weights.detach().cpu() if topk_weights is not None else None,
        }

    def _qrtc_finalize_layer_state(self, layer_state):
        rel_usage_prev = layer_state.get("rel_usage_next", None)
        debug = layer_state.get("debug", None)
        return rel_usage_prev, debug


    def _build_cp_accuracy_tensor_once(self, graph):
        if (not self.cp_acc_enable) or self.cp_accuracy_tensor is not None:
            return
        from collections import defaultdict
        device = graph.edge_list.device
        edge_cpu = graph.edge_list.detach().cpu()
        edge_head = edge_cpu[:, 0].long().tolist()
        edge_rel = edge_cpu[:, 2].long().tolist()
        num_rel = int(max(edge_rel)) + 1 if edge_rel else 0
        node_to_rels = defaultdict(set)
        for h, r in zip(edge_head, edge_rel):
            node_to_rels[h].add(r)
        relation2neighbors = {r: defaultdict(int) for r in range(num_rel)}
        for rels in node_to_rels.values():
            rels = frozenset(sorted(rels))
            for r in rels:
                relation2neighbors[r][rels] += 1
        neighbor_num = [sum(relation2neighbors[r].values()) for r in range(num_rel)]
        acc = torch.zeros(num_rel, num_rel, dtype=torch.bool, device=device)
        thr = float(self.cp_acc_threshold)
        for r in range(num_rel):
            if neighbor_num[r] <= 0:
                continue
            for r2 in range(num_rel):
                co = 0
                for rels, cnt in relation2neighbors[r].items():
                    if r2 in rels:
                        co += cnt
                if co / neighbor_num[r] > thr:
                    acc[r, r2] = True
        self.cp_accuracy_tensor = acc
        for layer in self.cp_accuracy_layers:
            layer.unmasked_tensor = acc
        self._last_cp_acc_tensor_stats = {'shape': tuple(acc.shape), 'true_n': int(acc.sum().item()), 'row_true': [int(x) for x in acc.sum(dim=1).detach().cpu().tolist()]}
        if os.getenv('BIOPATHNET_CPACC_DEBUG', '0') == '1':
            print('[CPACC_TENSOR]', self._last_cp_acc_tensor_stats)

    def _qces_build_allow_rel_from_query(self, query_rel_emb, relation_table, query_rel_id=None):
        sim = torch.matmul(query_rel_emb, relation_table.t()).view(-1)
        delta = self.qces_rel_logit(query_rel_emb).view(-1) if self.qces_learnable else None
        if delta is not None:
            sim = sim + self.qces_delta_scale * torch.tanh(delta)
        k = min(max(int(self.qces_topk), 1), int(sim.numel()))
        topk = torch.topk(sim, k=k).indices
        allow = torch.zeros(sim.size(0), dtype=torch.bool, device=sim.device)
        allow[topk] = True
        qid = None if query_rel_id is None else int(query_rel_id)
        total_rel = int(relation_table.size(0))
        base_rel = total_rel // 2 if total_rel % 2 == 0 else total_rel
        deny_base = {7}
        deny_ids = set()
        for d in deny_base:
            if 0 <= d < total_rel:
                deny_ids.add(d)
            inv_d = d + base_rel
            if base_rel < total_rel and 0 <= inv_d < total_rel:
                deny_ids.add(inv_d)
        if qid is not None and qid in deny_ids:
            deny_ids.remove(qid)
        if deny_ids:
            deny_idx = torch.tensor(sorted(deny_ids), device=allow.device, dtype=torch.long)
            allow[deny_idx] = False
        if qid is not None and 0 <= qid < allow.numel():
            allow[qid] = True
        if (not bool(allow.any())) and qid is not None and 0 <= qid < allow.numel():
            allow[qid] = True
        qces_aux = None
        if self.qces_learnable and qid is not None and 0 <= qid < sim.numel():
            qces_aux = torch.nn.functional.softplus(-sim[qid])
            if deny_ids:
                deny_idx_aux = torch.tensor(sorted(deny_ids), device=sim.device, dtype=torch.long)
                qces_aux = qces_aux + torch.nn.functional.softplus(sim[deny_idx_aux]).mean()
            if hasattr(self, "_last_qces_aux_terms") and self._last_qces_aux_terms is not None:
                self._last_qces_aux_terms.append(qces_aux)
        stats = {"topk": int(k), "query_rel_id": qid, "learnable": int(self.qces_learnable), "delta_abs_mean": 0.0 if delta is None else float(delta.abs().mean().detach().cpu().item()), "qces_aux": 0.0 if qces_aux is None else float(qces_aux.detach().cpu().item()), "allowed_n": int(allow.sum().item()), "allowed_ids": torch.nonzero(allow, as_tuple=False).view(-1).detach().cpu().tolist(), "deny_ids": sorted(deny_ids)}
        return allow, stats

    def _qces_mask_graph_for_query(self, graph, boundary_i, query_i, relation_table, query_rel_id=None):
        if not self.qces_enable:
            return graph, {"enabled": 0}
        num_relation = int(relation_table.size(0))
        edge_rel = graph.edge_list[:, 2].long().clamp(min=0, max=num_relation - 1)
        allow, stats = self._qces_build_allow_rel_from_query(query_rel_emb=query_i, relation_table=relation_table, query_rel_id=query_rel_id)
        edge_mask = allow[edge_rel]
        masked_edge_n = int(edge_mask.sum().item())
        masked_graph = graph.edge_mask(edge_mask) if bool(edge_mask.any()) else graph
        with masked_graph.graph():
            masked_graph.query = query_i
        if boundary_i is not None:
            with masked_graph.node():
                masked_graph.boundary = boundary_i
        stats.update({"edge_n": int(edge_rel.numel()), "masked_edge_n": masked_edge_n, "fallback_full_graph": int(masked_edge_n <= 0)})
        return masked_graph, stats

    def _unified_hop_summary(self, hiddens):
        if len(hiddens) == 1:
            return hiddens[0]
        return torch.stack(hiddens, dim=0).mean(dim=0)

    def _unified_prior_mask(self, r_index):
        _spec = os.getenv('UNIFIED_CPACC_QR_ONLY', '').strip()
        if not _spec:
            return torch.ones(r_index.size(0), 1, device=r_index.device, dtype=self.query.weight.dtype)
        _allow = {int(x.strip()) for x in _spec.split(',') if x.strip()}
        _mask = torch.tensor([1.0 if int(x) in _allow else 0.0 for x in r_index.detach().cpu().tolist()], device=r_index.device, dtype=self.query.weight.dtype)
        return _mask.unsqueeze(-1)

    def _apply_unified_module(self, h_base, hiddens, query, r_index):
        if not self.unified_main_enable:
            self._last_unified_debug = {'enabled': 0}
            return h_base
        hop_summary = self._unified_hop_summary(hiddens)
        node_query = query.unsqueeze(0).expand(h_base.size(0), -1, -1)
        delta_h_raw = torch.zeros_like(h_base)
        delta_h = torch.zeros_like(h_base)
        if self.unified_epb_enable:
            z_delta = torch.cat([h_base, hop_summary, node_query], dim=-1)
            delta_h_raw = self.epb_residual_mlp(z_delta)
            delta_h = self.unified_delta_scale * torch.tanh(delta_h_raw)
            _force_delta_alpha = float(os.getenv('UNIFIED_FORCE_DELTA_ALPHA', '0.0'))
            if _force_delta_alpha > 0:
                delta_h = delta_h + _force_delta_alpha * torch.tanh(hop_summary - h_base)
        g_soft = torch.ones(h_base.size(0), h_base.size(1), 1, device=h_base.device, dtype=h_base.dtype)
        g_prior = torch.ones(1, h_base.size(1), 1, device=h_base.device, dtype=h_base.dtype)
        if self.unified_cpacc_enable:
            z_gate = torch.cat([h_base, hop_summary, node_query, delta_h], dim=-1)
            g_soft = torch.sigmoid(self.cpacc_gate_mlp(z_gate))
            g_prior = self._unified_prior_mask(r_index).unsqueeze(0).to(dtype=h_base.dtype)
        g = g_soft * g_prior
        _lambda = self.unified_lambda.view(1, 1, 1)
        _force_lambda = os.getenv('UNIFIED_FORCE_LAMBDA', '').strip()
        if _force_lambda:
            _lambda = torch.tensor(float(_force_lambda), device=h_base.device, dtype=h_base.dtype).view(1, 1, 1)
        h_final = h_base + _lambda * g * delta_h
        self._last_unified_debug = {
            'enabled': 1,
            'epb_enable': int(bool(self.unified_epb_enable)),
            'cpacc_enable': int(bool(self.unified_cpacc_enable)),
            'delta_norm_mean': float(delta_h.detach().norm(dim=-1).mean().item()),
            'g_soft_mean': float(g_soft.detach().mean().item()),
            'g_prior_mean': float(g_prior.detach().mean().item()),
            'g_mean': float(g.detach().mean().item()),
            'h_base_norm_mean': float(h_base.detach().norm(dim=-1).mean().item()),
            'h_final_norm_mean': float(h_final.detach().norm(dim=-1).mean().item()),
            'applied_delta_norm_mean': float((_lambda * g * delta_h).detach().norm(dim=-1).mean().item()),
            'lambda_mean': float(_lambda.detach().mean().item()),
        }
        if os.getenv('UNIFIED_PRINT_DEBUG', '0') == '1':
            print('UNIFIED_DEBUG =', self._last_unified_debug)
        return h_final

    def bellmanford(self, graph, h_index, r_index, separate_grad=False):
        graph = self._maybe_cp_filter_graph(graph, r_index)
        # r_index.shape - [batch_size]
        # query.shape - [batch_size, hidden_dim]
        base_query = self.query(r_index)
        if self.srp_enable:
            prior = self.soft_path_prior[r_index]  # [B, L, D]
            if self.srp_qc_enable and os.getenv("SRP_QC_SMOKE", "0") == "1":
                gate = torch.sigmoid(self.srp_query_gate(base_query)).unsqueeze(-1)  # [B, L, 1]
                print(
                    "[SRP_QC_SMOKE]",
                    "gate_mean=", float(gate.mean().item()),
                    "gate_std=", float(gate.std().item()) if gate.numel() > 1 else 0.0,
                )
            layer_queries = [
                base_query + self.srp_alpha * self._srp_router_mix(i, base_query, prior[:, i, :])
                for i in range(len(self.layers))
            ]
        else:
            layer_queries = [base_query] * len(self.layers)

        query = layer_queries[0]
        index = h_index.unsqueeze(-1).expand_as(query)
        # intialize the source node with query embedding
        # boundary.shape - [#num_nodes, batch_size, hidden_dim]
        # to insert node features here
        boundary = torch.zeros(graph.num_node, *query.shape, device=self.device)
        boundary.scatter_add_(0, index.unsqueeze(0), query.unsqueeze(0)) #
        with graph.graph():
            graph.query = layer_queries[0]
        with graph.node():
            graph.boundary = boundary #

        hiddens = []
        step_graphs = []
        layer_input = boundary
        if self.cp_acc_enable and self.cp_accuracy_tensor is None:
            self._build_cp_accuracy_tensor_once(graph)
        query_relations_accuracy = r_index.clone().unsqueeze(1) if self.cp_acc_enable else None
        cp_acc_debug_layers = []
        rel_usage_prev = None
        self._last_qrtc_debug_layers = []
        self._last_qces_debug = []
        self._last_qces_aux_terms = []
        relation_table = self.query.weight

        for i, layer in enumerate(self.layers):
            graph.query = layer_queries[i]
            # Default QRTC + DistMult uses fused-compatible path in layer.py (no graph.requires_grad).
            # QRTC_FORCE_MESSAGE_PATH=1 restores scatter/message reference (debug only).
            _force_message_path = os.environ.get("QRTC_FORCE_MESSAGE_PATH", "0") == "1"
            if separate_grad:
                step_graph = graph.clone().requires_grad_()
            elif self.qrtc_enable and _force_message_path and (not self.qces_enable):
                step_graph = graph.clone().requires_grad_()
            else:
                step_graph = graph
            # calculate hidden units - propagate (source) node embedding one step out
            if self.qrtc_enable and (not self.qces_enable):
                layer._qrtc_state = self._qrtc_prepare_layer_state(
                    layer_id=i,
                    query_rel_emb=layer_queries[i],
                    relation_table=relation_table,
                    rel_usage_prev=rel_usage_prev,
                )
            if self.qces_enable:
                qces_outputs = []
                qces_layer_stats = []
                for _b in range(layer_input.shape[1]):
                    _boundary = getattr(graph, "boundary", None)
                    if _boundary is not None:
                        _boundary = _boundary[:, _b:_b+1, :]
                    masked_graph, qces_stat = self._qces_mask_graph_for_query(
                        step_graph,
                        boundary_i=_boundary,
                        query_i=layer_queries[i][_b:_b+1],
                        relation_table=relation_table,
                        query_rel_id=int(r_index[_b].item()),
                    )
                    if self.qrtc_enable:
                        layer._qrtc_state = self._qrtc_prepare_layer_state(
                            layer_id=i,
                            query_rel_emb=layer_queries[i][_b:_b+1],
                            relation_table=relation_table,
                            rel_usage_prev=None if rel_usage_prev is None else rel_usage_prev[_b:_b+1],
                        )
                    hidden_i = layer(masked_graph, layer_input[:, _b:_b+1, :])
                    qces_outputs.append(hidden_i)
                    qces_layer_stats.append(qces_stat)
                hidden = torch.cat(qces_outputs, dim=1)
                self._last_qces_debug.append({"layer": int(i), "items": qces_layer_stats})
                if self.qces_debug:
                    print(f"[QCES_DEBUG] layer={int(i)} stats={qces_layer_stats}")
            else:
                hidden = layer(step_graph, layer_input)
            if self.cp_acc_enable and self.cp_accuracy_layers is not None:
                current_cp_qr = query_relations_accuracy
                hidden_acc, query_relations_accuracy = self.cp_accuracy_layers[i](step_graph, layer_input, query_relations=query_relations_accuracy)
                hidden_pre_cpacc = hidden.detach().clone()
                cpacc_applied_col_n = 0
                if os.getenv("BIOPATHNET_CPACC_APPLY", "0") == "1":
                    cpacc_alpha = float(os.getenv("BIOPATHNET_CPACC_ALPHA", "0.5"))
                    only_qr_env = os.getenv("BIOPATHNET_CPACC_ONLY_QR", "").strip()
                    if only_qr_env:
                        only_qr = int(only_qr_env)
                        for _qi in range(layer_input.shape[1]):
                            _qr = current_cp_qr[_qi]
                            if not torch.is_tensor(_qr):
                                _qr = torch.as_tensor(_qr, device=hidden.device)
                            _qr = _qr.view(-1).long()
                            if _qr.numel() == 1 and int(_qr[0].item()) == only_qr:
                                hidden[:, _qi:_qi+1, :] = (1.0 - cpacc_alpha) * hidden[:, _qi:_qi+1, :] + cpacc_alpha * hidden_acc[:, _qi:_qi+1, :]
                                cpacc_applied_col_n += 1
                    else:
                        hidden = (1.0 - cpacc_alpha) * hidden + cpacc_alpha * hidden_acc
                        cpacc_applied_col_n = int(layer_input.shape[1])
                cp_acc_debug_layers.append({
                    "layer_id": i,
                    "pre_fuse_mean_abs": float(hidden_pre_cpacc.abs().mean().item()),
                    "post_fuse_mean_abs": float(hidden.abs().mean().item()),
                    "acc_mean_abs": float(hidden_acc.abs().mean().item()),
                    "same_shape": bool(hidden_acc.shape == hidden.shape),
                    "cpacc_applied_col_n": int(cpacc_applied_col_n),
                    "mask_stats": getattr(self.cp_accuracy_layers[i], "_last_cpacc_stats", None),
                })
            if os.environ.get("QRTC_LIVE_GRAD_PROBE", "0") == "1" and i == 0:
                _probe_flags = {
                    _n: bool(_p.requires_grad)
                    for _n, _p in self.named_parameters()
                    if ("qrtc_init_memory" in _n) or ("qrtc_precedent_mlp" in _n) or ("qrtc_gate_mlp" in _n)
                }
                print("QRTC_PROBE_PARAM_FLAGS =", _probe_flags)
                print("QRTC_PROBE_LAYER_WRAPPED =", bool(getattr(layer, "_qrtc_message_wrapped", False)))
                print("QRTC_PROBE_HIDDEN_REQUIRES_GRAD =", bool(hidden.requires_grad))
            if self.qrtc_enable and hasattr(layer, "_qrtc_state"):
                rel_usage_prev, qrtc_debug = self._qrtc_finalize_layer_state(layer._qrtc_state)
                if self.qrtc_collect_debug and qrtc_debug is not None:
                    self._last_qrtc_debug_layers.append(qrtc_debug)
                delattr(layer, "_qrtc_state")
            if self.short_cut and hidden.shape == layer_input.shape:
                # if short_cut, then add both new with old
                hidden = hidden + layer_input
            hiddens.append(hidden)
            step_graphs.append(step_graph)
            layer_input = hidden

        self._last_cp_acc_debug = cp_acc_debug_layers if self.cp_acc_enable else None
        if self.cp_acc_enable and os.getenv("BIOPATHNET_CPACC_DEBUG", "0") == "1":
            print("[CPACC_DEBUG]", self._last_cp_acc_debug)
        m1_hop_weight = None
        m1_selected_hidden = None
        if self.m1_hop_alloc_enable:
            if self.m1_hop_mode == "base":
                m1_hop_weight = base_query.new_zeros(base_query.size(0), len(self.layers))
                m1_hop_weight[:, -1] = 1.0
            elif self.m1_hop_mode == "shared":
                m1_hop_weight = torch.softmax(self.m1_shared_hop_logits, dim=-1).unsqueeze(0).expand(base_query.size(0), -1)
            elif self.m1_hop_mode == "rel":
                m1_hop_weight = torch.softmax(self.m1_hop_logits(base_query), dim=-1)
            else:
                raise ValueError(f"Unsupported M1_HOP_MODE: {self.m1_hop_mode}")
            if self.epb_enable:
                m1_hop_weight_raw = m1_hop_weight
                epb_policy_logit = self.epb_router(base_query)
                epb_policy_prob = torch.softmax(epb_policy_logit, dim=-1)
                epb_hop_weight = epb_policy_prob @ self.epb_policy_bank.to(epb_policy_prob.dtype)
                epb_alpha = self.epb_alpha
                if self.epb_alpha_rel:
                    epb_alpha = torch.full((m1_hop_weight_raw.size(0), 1), float(self.epb_alpha), dtype=m1_hop_weight_raw.dtype, device=m1_hop_weight_raw.device)
                    for _rid, _aval in self.epb_alpha_rel.items():
                        epb_alpha[(r_index.view(-1) == _rid), 0] = float(_aval)
                if self.epb_debug_once:
                    try:
                        print("EPB_DEBUG_ALPHA_BASE =", float(self.epb_alpha))
                        print("EPB_DEBUG_ALPHA_REL =", dict(self.epb_alpha_rel))
                        print("EPB_DEBUG_REL_IDS =", sorted(set(int(x) for x in r_index.view(-1).detach().cpu().tolist())))
                        _dbg = epb_alpha if torch.is_tensor(epb_alpha) else torch.tensor([float(epb_alpha)], device=m1_hop_weight_raw.device)
                        print("EPB_DEBUG_ALPHA_UNIQ =", sorted(set(round(float(x),4) for x in _dbg.view(-1).detach().cpu().tolist())))
                    except Exception as _e:
                        print("EPB_DEBUG_ERR =", repr(_e))
                    self.epb_debug_once = False
                # EPB_SELECTIVE_APPLY_V1
                _epb_apply_mask = torch.ones(m1_hop_weight_raw.size(0), 1, dtype=m1_hop_weight_raw.dtype, device=m1_hop_weight_raw.device)
                if self.epb_enable_only_qr:
                    _allow = torch.tensor([1.0 if int(x) in self.epb_enable_only_qr else 0.0 for x in r_index.detach().cpu().tolist()], dtype=m1_hop_weight_raw.dtype, device=m1_hop_weight_raw.device).unsqueeze(-1)
                    _epb_apply_mask = _epb_apply_mask * _allow
                if self.epb_disable_qr:
                    _deny = torch.tensor([1.0 if int(x) in self.epb_disable_qr else 0.0 for x in r_index.detach().cpu().tolist()], dtype=m1_hop_weight_raw.dtype, device=m1_hop_weight_raw.device).unsqueeze(-1)
                    _epb_apply_mask = _epb_apply_mask * (1.0 - _deny)
                m1_hop_weight = m1_hop_weight_raw + _epb_apply_mask * epb_alpha * (epb_hop_weight - m1_hop_weight_raw)
                if self.f8_direct_delta_enable:
                    _f8_rel = r_index.view(-1)
                    _f8_mask = ((_f8_rel == 8) | (_f8_rel == 8 + self.num_relation)).to(m1_hop_weight.dtype).unsqueeze(-1)
                    _base_logit = torch.log(m1_hop_weight.clamp_min(1e-12))
                    _delta = self.f8_direct_alpha * self.f8_direct_logits.to(m1_hop_weight.dtype).unsqueeze(0)
                    _f8_weight = torch.softmax(_base_logit + _delta, dim=-1)
                    m1_hop_weight = _f8_mask * _f8_weight + (1.0 - _f8_mask) * m1_hop_weight
                if self.f8_inst_gate_enable:
                    _f8_rel = r_index.view(-1)
                    _f8_mask = ((_f8_rel == 8) | (_f8_rel == 8 + self.num_relation)).to(m1_hop_weight.dtype).unsqueeze(-1)
                    if os.environ.get("F8_BRANCH_PROBE", "0") == "1":
                        print("F8_BRANCH", "rel_ids=", r_index.view(-1).detach().cpu().tolist(), "mask_sum=", float(_f8_mask.sum().item()))
                    _base_logit = torch.log(m1_hop_weight.clamp_min(1e-12))
                    _delta = self.f8_inst_alpha * self.f8_inst_delta_logits.to(m1_hop_weight.dtype).unsqueeze(0)
                    _cand = torch.softmax(_base_logit + _delta, dim=-1)
                    _gate = torch.sigmoid(self.f8_inst_gate(m1_hop_weight.detach())).to(m1_hop_weight.dtype)
                    if os.environ.get("F8_FORCE_GATE1", "0") == "1":
                        _gate = torch.ones_like(_gate)
                    _mix = (1.0 - _gate) * m1_hop_weight + _gate * _cand
                    if os.environ.get("F8_INFER_DEBUG", "0") == "1" and bool((_f8_mask.sum() > 0).item()):
                        _masked = (_f8_mask.squeeze(-1) > 0)
                        _gate_dbg = _gate[_masked].detach().view(-1).cpu().tolist()
                        _cand_dbg = (_cand - m1_hop_weight).abs().max(dim=-1).values[_masked].detach().cpu().tolist()
                        _mix_dbg = (_mix - m1_hop_weight).abs().max(dim=-1).values[_masked].detach().cpu().tolist()
                        print("F8_INFER", "rel_ids=", _f8_rel.detach().cpu().tolist(), "gate=", _gate_dbg, "cand_delta_max=", _cand_dbg, "mix_delta_max=", _mix_dbg)
                    m1_hop_weight = _f8_mask * _mix + (1.0 - _f8_mask) * m1_hop_weight
                m1_hop_weight = m1_hop_weight / m1_hop_weight.sum(dim=-1, keepdim=True).clamp_min(1e-12)
                self._last_epb_debug = {}
                self._last_epb_debug["policy_prob"] = epb_policy_prob.detach()
                self._last_epb_debug["policy_argmax"] = epb_policy_prob.argmax(dim=-1).detach()
                self._last_epb_debug["w_raw"] = m1_hop_weight_raw.detach()
                self._last_epb_debug["w_policy"] = epb_hop_weight.detach()
                self._last_epb_debug["w_final"] = m1_hop_weight.detach()
                # EPB_PRINT_EACH_QUERY_V1
                print("EPB_W_RAW =", m1_hop_weight_raw[0].detach().cpu().tolist())
                print("EPB_PI =", epb_policy_prob[0].detach().cpu().tolist())
                print("EPB_W_POLICY =", epb_hop_weight[0].detach().cpu().tolist())
                print("EPB_W_FINAL =", m1_hop_weight[0].detach().cpu().tolist())
                if os.environ.get("EPB_PRINT_DEBUG", "0") == "1":
                    print("EPB_POLICY_PROB =", epb_policy_prob[0].detach().cpu().tolist())
                    print("EPB_POLICY_ARGMAX =", int(epb_policy_prob[0].argmax().item()))
                    print("EPB_W_RAW =", m1_hop_weight_raw[0].detach().cpu().tolist())
                    print("EPB_W_POLICY =", epb_hop_weight[0].detach().cpu().tolist())
                    print("EPB_W_FINAL =", m1_hop_weight[0].detach().cpu().tolist())
            # === HOPFILM_BEGIN ===
            if self.hopfilm_enable:
                if (not self._hopfilm_freeze_done) and os.environ.get("HOPFILM_TRAIN_ONLY", "0") == "1":
                    for _n, _p in self.named_parameters():
                        if not _n.startswith("hopfilm_"):
                            _p.requires_grad = False
                    self._hopfilm_freeze_done = True
                z = self.hopfilm_mlp(hop_logits)
                _B = z.size(0)
                _L = len(hiddens)
                _D = hiddens[0].size(-1)
                gamma = self.hopfilm_gamma(z).view(_B, _L, _D)
                beta = self.hopfilm_beta(z).view(_B, _L, _D)
                gamma = 1.0 + self.hopfilm_gamma_scale * torch.tanh(gamma)
                beta = self.hopfilm_beta_scale * torch.tanh(beta)
                _new_hiddens = []
                for _l, _h in enumerate(hiddens):
                    _g = gamma[:, _l, :]
                    _b = beta[:, _l, :]
                    while _g.dim() < _h.dim():
                        _g = _g.unsqueeze(-2)
                        _b = _b.unsqueeze(-2)
                    _new_hiddens.append(_g * _h + _b)
                hiddens = _new_hiddens
            # === HOPFILM_END ===
            hidden_stack = torch.stack(hiddens, dim=0)                              # [L, N, B, D]
            hidden_stack = hidden_stack.permute(2, 0, 1, 3).contiguous()           # [B, L, N, D]
            m1_selected_hidden = (hidden_stack * m1_hop_weight.unsqueeze(-1).unsqueeze(-1)).sum(dim=1)
            m1_selected_hidden = m1_selected_hidden.permute(1, 0, 2).contiguous()  # [N, B, D]
            self._last_m1_hop_debug = {"hop_mode": self.m1_hop_mode, "hop_weight": m1_hop_weight.detach()}
            if self.m1_hop_alloc_enable:
                try:
                    print("M1_HOP_WEIGHT =", m1_hop_weight[0].detach().cpu().tolist())
                except Exception as e:
                    print("M1_HOP_DEBUG_PRINT_FAILED =", repr(e))

        # query is [bs, hidden_dim]; node_query is [num_nodes, bs, hidden_dim]
        node_query = query.expand(graph.num_node, -1, -1)
        if self.evidence_router is not None:
            node_type = getattr(graph, "node_type", None)
            if node_type is None:
                node_type = torch.zeros(graph.num_node, dtype=torch.long, device=query.device)
            local_context = None
            local_context_debug = {}
            if self.local_context_enable and self.proto_use_local_context:
                local_context, local_context_debug = self._maybe_build_local_context(
                    graph, h_index, query
                )
            selected_hidden, router_debug = self.evidence_router(
                hiddens=hiddens,
                query=query,
                node_type=node_type,
                h_index=h_index,
                local_context=local_context,
                collect_debug=self.collect_router_debug,
            )
            self._last_router_debug = router_debug
            self._last_local_context_debug = local_context_debug
            if self.print_router_debug:
                try:
                    print("ROUTER_HOP_WEIGHT =", router_debug["hop_weight"][0].detach().cpu().tolist())
                    print("ROUTER_META_WEIGHT =", router_debug["meta_weight"][0].detach().cpu().tolist())
                    print("ROUTER_RESIDUAL_ALPHA =", float(router_debug["residual_alpha"][0].detach().cpu()))
                    if "type_gate_mean" in router_debug:
                        print("ROUTER_TYPE_GATE_MEAN =", float(router_debug["type_gate_mean"][0].detach().cpu()))
                    if "local_context_norm" in router_debug:
                        print("ROUTER_LOCAL_CONTEXT_NORM =", float(router_debug["local_context_norm"][0].detach().cpu()))
                except Exception as e:
                    print("ROUTER_DEBUG_PRINT_FAILED =", repr(e))
            output = torch.cat([selected_hidden, node_query], dim=-1)
        else:
            if self.concat_hidden:
                # jumping connections, from previous layers
                # all hidden concat with node query
                # [num_nodes, batch_size, hidden_dim*7]
                output = torch.cat(hiddens + [node_query], dim=-1)
            else:
                h_base = m1_selected_hidden if m1_selected_hidden is not None else hiddens[-1]
                final_hidden = self._apply_unified_module(h_base, hiddens, base_query, r_index)
                # selected / last output concat with node_query
                # [num_nodes, batch_size, hidden_dim*2]
                output = torch.cat([final_hidden, node_query], dim=-1)
        return {
            "node_feature": output,
            "step_graphs": step_graphs,
            "hop_hidden_states": hiddens,
            "relation_query": base_query,
            "qrtc_rel_usage_prev": rel_usage_prev,
            "layer_queries": layer_queries,
            "m1_hop_weight": m1_hop_weight,
        }

    def forward(self, graph, h_index, t_index, r_index=None, all_loss=None, metric=None):
        if all_loss is not None:
            # train
            # remove both r and r-1 edges 
            # remove edges of other types btw h_index and t_index
            assert graph.num_relation == self.num_relation
            graph = self.remove_easy_edges(graph, h_index, t_index, r_index)

        shape = h_index.shape
        if graph.num_relation:
            # if num_relation > 1
            graph = graph.undirected(add_inverse=True)
            h_index, t_index, r_index = self.negative_sample_to_tail(h_index, t_index, r_index)
            assert (h_index[:, [0]] == h_index).all()
        else:
            # convert to knowledge graph with 1 relation
            graph = self.as_relational_graph(graph)
            h_index = h_index.view(-1, 1)
            t_index = t_index.view(-1, 1)
            r_index = torch.zeros_like(h_index)
            assert (h_index[:, [0]] == h_index).all()

        assert (r_index[:, [0]] == r_index).all()
        # run mp from source to all nodes; all info need to know is source and relation
        # output["node_feature"].shape - [#num_nodes, batch_size, (hidden_dim + query_node_dim)]
        if os.environ.get("F8_GRAD_PROBE", "0") == "1" and not getattr(self, "_f8_grad_probe_done", False):
            _ps = {"f8_direct_logits": self.f8_direct_logits, "f8_inst_delta_logits": self.f8_inst_delta_logits, "f8_inst_gate.weight": self.f8_inst_gate.weight, "f8_inst_gate.bias": self.f8_inst_gate.bias}
            print("F8_NUM_REL", int(self.num_relation))
            for _n, _p in _ps.items():
                print("F8_PROBE_FLAG", _n, "requires_grad=", bool(_p.requires_grad))
                if _p.requires_grad:
                    _p.register_hook(lambda g, _n=_n: print("F8_GRAD_MAX", _n, float(g.detach().abs().max().item())))
            self._f8_grad_probe_done = True
        output = self.bellmanford(graph, h_index[:, 0], r_index[:, 0])
        # transpose to [batch_size, num_neg+1, hidden_dim*2 or hidden_dim*(num_layer+1)]
        feature = output["node_feature"].transpose(0, 1)
        # only get the path embeddings to the true tail and other negative sampled tails
        # feature.shape - [#num_nodes, batch_size,  (hidden_dim + query_node_dim)]
        index = t_index.unsqueeze(-1).expand(-1, -1, feature.shape[-1])
        feature = feature.gather(1, index)
        rg_min_base_feature = feature
        

        if self.rg_min_post_router is not None:
            feature, rg_min_debug = self.rg_min_post_router(
                graph=graph,
                relation_query=output["relation_query"],
                relation_index=r_index[:, 0],
                hop_hidden_states=output["hop_hidden_states"],
                t_index=t_index,
                base_feature=feature,
                collect_debug=self.collect_router_debug,
            )
            self._last_rg_min_debug = rg_min_debug
            if os.environ.get("RG_MIN_REL_PROBE_ENABLE", "0") == "1" and (not self._rg_min_rel_probe_done):
                try:
                    probe_sample_mode = os.environ.get("RG_MIN_REL_PROBE_SAMPLE_MODE", "manual").strip().lower()
                    if probe_sample_mode == "first_multitype":
                        probe_sample_idx = 0
                        probe_scan = []
                        try:
                            if getattr(graph, "node_type", None) is not None:
                                probe_scan_max = min(int(os.environ.get("RG_MIN_REL_PROBE_SCAN_MAX", "32")), int(feature.size(0)))
                                for _probe_i in range(probe_scan_max):
                                    _probe_types = graph.node_type[t_index[_probe_i:_probe_i + 1]].detach().view(-1)
                                    _probe_unique_n = int(torch.unique(_probe_types).numel())
                                    probe_scan.append((_probe_i, _probe_unique_n))
                                    if _probe_unique_n > 1:
                                        probe_sample_idx = _probe_i
                                        break
                        except Exception as e:
                            print("RG_MIN_REL_PROBE_SCAN_FAILED =", repr(e))
                        print("RG_MIN_REL_PROBE_SAMPLE_MODE =", probe_sample_mode)
                        print("RG_MIN_REL_PROBE_SCAN =", probe_scan)
                    else:
                        probe_sample_idx = int(os.environ.get("RG_MIN_REL_PROBE_SAMPLE_IDX", "0"))
                    probe_sample_idx = max(0, min(probe_sample_idx, feature.size(0) - 1))
                    print("RG_MIN_REL_PROBE_SAMPLE_IDX =", probe_sample_idx)
                    probe_base_feature = rg_min_base_feature[probe_sample_idx:probe_sample_idx + 1].detach()
                    probe_t_index = t_index[probe_sample_idx:probe_sample_idx + 1].detach()
                    probe_hop_hidden_states = [h[:, probe_sample_idx:probe_sample_idx + 1, :].detach() for h in output["hop_hidden_states"]]
                    probe_orig_r = int(r_index[probe_sample_idx, 0].item())
                    probe_rel_ids_env = os.environ.get("RG_MIN_REL_PROBE_REL_IDS", "").strip()
                    if probe_rel_ids_env:
                        probe_rel_ids = []
                        for x in probe_rel_ids_env.split(","):
                            x = x.strip()
                            if x:
                                probe_rel_ids.append(int(x))
                    else:
                        probe_rel_ids = [
                            probe_orig_r,
                            0,
                            1,
                            max(0, int(graph.num_relation) // 2),
                            max(0, int(graph.num_relation) - 1),
                        ]
                    probe_rel_ids = [x for x in probe_rel_ids if 0 <= x < int(graph.num_relation)]
                    _seen_probe = set()
                    probe_rel_ids = [x for x in probe_rel_ids if not (x in _seen_probe or _seen_probe.add(x))]
                    probe_rel_ids = probe_rel_ids[: int(os.environ.get("RG_MIN_REL_PROBE_MAX_REL", "5"))]
                    print("RG_MIN_REL_PROBE_ORIG_REL_ID =", probe_orig_r)
                    print("RG_MIN_REL_PROBE_REL_IDS =", probe_rel_ids)
                    try:
                        if getattr(graph, "node_type", None) is None:
                            print("RG_MIN_REL_PROBE_TAIL_TYPE_UNIQUE_N =", "NONE")
                        else:
                            _probe_tail_type = graph.node_type[probe_t_index].detach().view(-1)
                            print("RG_MIN_REL_PROBE_TAIL_TYPE_UNIQUE_N =", int(torch.unique(_probe_tail_type).numel()))
                            print("RG_MIN_REL_PROBE_TAIL_TYPE_FIRST16 =", _probe_tail_type[:16].detach().cpu().tolist())
                    except Exception as e:
                        print("RG_MIN_REL_PROBE_TAIL_TYPE_FAILED =", repr(e))
                    for _probe_rel in probe_rel_ids:
                        _probe_rel_tensor = r_index.new_tensor([_probe_rel])
                        try:
                            _probe_query = self.query(_probe_rel_tensor)
                        except Exception:
                            _probe_query = self.query(_probe_rel_tensor.unsqueeze(-1))
                        if hasattr(_probe_query, 'dim') and _probe_query.dim() == 3 and _probe_query.size(1) == 1:
                            _probe_query = _probe_query[:, 0, :]
                        _, _probe_debug = self.rg_min_post_router(
                            graph=graph,
                            relation_query=_probe_query,
                            relation_index=_probe_rel_tensor,
                            hop_hidden_states=probe_hop_hidden_states,
                            t_index=probe_t_index,
                            base_feature=probe_base_feature,
                            collect_debug=True,
                        )
                        print("RG_MIN_REL_PROBE_REL_ID =", int(_probe_rel))
                        print("RG_MIN_REL_PROBE_EXPERT_WEIGHT =", _probe_debug["expert_weight"][0].detach().cpu().tolist())
                        print("RG_MIN_REL_PROBE_HOP_WEIGHT =", _probe_debug["hop_weight"][0].detach().cpu().tolist())
                        print("RG_MIN_REL_PROBE_TYPE_BIAS_STATS =", _probe_debug["type_bias_stats"][0].detach().cpu().tolist())
                        try:
                            print("RG_MIN_REL_PROBE_TYPE_BIAS_FIRST16 =", _probe_debug["type_bias"][0, :16].detach().cpu().tolist())
                        except Exception as e:
                            print("RG_MIN_REL_PROBE_TYPE_BIAS_FIRST16_FAILED =", repr(e))
                    self._rg_min_rel_probe_done = True
                except Exception as e:
                    print("RG_MIN_REL_PROBE_FAILED =", repr(e))
                    self._rg_min_rel_probe_done = True
            if self.print_router_debug:
                try:
                    print("RG_MIN_EXPERT_WEIGHT =", rg_min_debug["expert_weight"][0].detach().cpu().tolist())
                    print("RG_MIN_HOP_WEIGHT =", rg_min_debug["hop_weight"][0].detach().cpu().tolist())
                    print("RG_MIN_TYPE_BIAS_STATS =", rg_min_debug["type_bias_stats"][0].detach().cpu().tolist())
                except Exception as e:
                    print("RG_MIN_DEBUG_PRINT_FAILED =", repr(e))
        
        if self.family_ctx_enable:
            if self.training:
                self._family_ctx_global_step = getattr(self, '_family_ctx_global_step', 0) + 1
            _rel = r_index[:, 0] if r_index.ndim > 1 else r_index
            _family_id = self._map_relation_to_family_id(_rel)

            # Evidence-family WSA:
            # In tasks such as PC_KEGG withBRG, the query relation can be a single
            # target relation, while QRTC-HR actually reads multi-relation BRG evidence.
            # When enabled, use final QRTC relation-usage to pick the dominant evidence
            # relation family. Fall back to query-family if no mapped evidence family exists.
            _evidence_rel_id = None
            _evidence_family_id = None
            if self.family_ctx_evidence_family_enable:
                try:
                    _usage = output.get("qrtc_rel_usage_prev", None) if isinstance(output, dict) else None
                    if _usage is not None:
                        if _usage.dim() == 1:
                            _usage = _usage.unsqueeze(0)
                        _usage = _usage.to(feature.device)
                        _usage_for_family = _usage.clone()
                        if self.family_ctx_evidence_exclude_query:
                            _q = _rel.view(-1, 1).long().to(_usage_for_family.device)
                            _q = _q.clamp(min=0, max=_usage_for_family.size(1) - 1)
                            _usage_for_family.scatter_(1, _q, -1.0)
                            _qi = _q + int(self.num_relation)
                            _qi = _qi.clamp(min=0, max=_usage_for_family.size(1) - 1)
                            _usage_for_family.scatter_(1, _qi, -1.0)
                        _evidence_rel_id = _usage_for_family.argmax(dim=-1).long()
                        _evidence_family_id = self._map_relation_to_family_id(_evidence_rel_id)
                        _family_id = torch.where(_evidence_family_id != 0, _evidence_family_id, _family_id)
                        if os.getenv("FAMILY_CTX_EVIDENCE_DEBUG", "0") == "1" and (not hasattr(self, "_family_ctx_evidence_debug_fired")):
                            self._family_ctx_evidence_debug_fired = True
                            print("FAMILY_CTX_EVIDENCE_REL_ID_FIRST8 =", _evidence_rel_id[:8].detach().cpu().tolist())
                            print("FAMILY_CTX_EVIDENCE_FAMILY_ID_FIRST8 =", _evidence_family_id[:8].detach().cpu().tolist())
                except Exception as e:
                    if os.getenv("FAMILY_CTX_EVIDENCE_DEBUG", "0") == "1":
                        print("FAMILY_CTX_EVIDENCE_FAMILY_FAILED =", repr(e))

            _active_mask = (_family_id != 0).to(feature.dtype).view(-1, 1, 1)
            if float(_active_mask.max().item()) > 0:
                _hidden_dim = self.dims[0]
                _base_hidden = feature[..., :_hidden_dim]
                _query_part = feature[..., _hidden_dim:]
                _rq = output["relation_query"].unsqueeze(1).expand(-1, feature.size(1), -1)
                _family_emb = self.family_ctx_family_emb(_family_id)
                _family_emb_expand = _family_emb.unsqueeze(1).expand(-1, feature.size(1), -1)
                _hop_feats = []
                for _hop_hidden in output["hop_hidden_states"]:
                    _hop_feature = _hop_hidden.transpose(0, 1)
                    _hop_index = t_index.unsqueeze(-1).expand(-1, -1, _hop_feature.shape[-1])
                    _hop_feature = _hop_feature.gather(1, _hop_index)
                    _hop_feats.append(_hop_feature)
                _hop_stack = torch.stack(_hop_feats, dim=2)
                _gate_in = torch.cat([_hop_stack, _base_hidden.unsqueeze(2).expand(-1, -1, _hop_stack.size(2), -1), _rq.unsqueeze(2).expand(-1, -1, _hop_stack.size(2), -1), _family_emb_expand.unsqueeze(2).expand(-1, -1, _hop_stack.size(2), -1)], dim=-1)
                _hop_logit = self.family_ctx_hop_gate(_gate_in).squeeze(-1)
                _hop_weight = torch.softmax(_hop_logit, dim=2)
                _support = (_hop_stack * _hop_weight.unsqueeze(-1)).sum(dim=2)
                _proto_in = torch.cat([_support, _rq, _family_emb_expand], dim=-1)
                _prototype = self.family_ctx_proto_mlp(_proto_in)
                if _prototype.size(1) > 1:
                    _proto_sep_dist = (_prototype[:, 1:, :] - _prototype[:, :1, :]).pow(2).mean(dim=-1).mean(dim=-1, keepdim=True)
                else:
                    _proto_sep_dist = torch.ones(_prototype.size(0), 1, device=_prototype.device, dtype=_prototype.dtype)
                _risk_gate = torch.ones_like(_proto_sep_dist)
                if self.family_ctx_risk_gate_enable:
                    _risk_gate = (_proto_sep_dist / max(self.family_ctx_risk_proto_min, 1.0e-6)).clamp(min=self.family_ctx_risk_gate_floor, max=1.0)
                _risk_gate = _risk_gate.view(-1, 1, 1)
                if _prototype.size(1) > 1:
                    _cand_proto_sep = (_prototype[:, 1:, :] - _prototype[:, :1, :]).pow(2).mean(dim=-1, keepdim=True)
                else:
                    _cand_proto_sep = _prototype.new_empty(_prototype.size(0), 0, 1)
                _cand_risk_gate = torch.ones(_prototype.size(0), _prototype.size(1), 1, device=_prototype.device, dtype=_prototype.dtype)
                if self.family_ctx_cand_risk_enable and _cand_proto_sep.numel() > 0:
                    _cand_min = _cand_proto_sep.min(dim=1, keepdim=True).values
                    _cand_max = _cand_proto_sep.max(dim=1, keepdim=True).values
                    _cand_span = (_cand_max - _cand_min).clamp_min(1.0e-6)
                    _cand_neg_rel = (_cand_proto_sep - _cand_min) / _cand_span
                    _cand_neg_gate = self.family_ctx_cand_risk_gate_floor + (1.0 - self.family_ctx_cand_risk_gate_floor) * _cand_neg_rel
                    _cand_risk_gate = torch.cat([torch.ones(_prototype.size(0), 1, 1, device=_prototype.device, dtype=_prototype.dtype), _cand_neg_gate], dim=1)
                _film_in = torch.cat([_base_hidden, _support, _prototype, _rq, _family_emb_expand], dim=-1)
                _film = self.family_ctx_film(_film_in)
                _gamma, _beta = _film.chunk(2, dim=-1)

                if self.family_ctx_wsa_enable:
                    _proto_sep_mean = _proto_sep_dist.mean()
                    _cand_sep_mean = _cand_proto_sep.mean() if _cand_proto_sep.numel() > 0 else _proto_sep_mean
                    if self.training:
                        self._family_ctx_update_ema(_proto_sep_mean, _cand_sep_mean)
                    _query_score = _proto_sep_dist / (self.family_ctx_proto_sep_ema + 1.0e-8)
                    _query_accept = self._family_ctx_deadzone_score(
                        _query_score,
                        self.family_ctx_wsa_q_low,
                        self.family_ctx_wsa_q_high,
                    ).view(-1, 1, 1)
                    if _cand_proto_sep.numel() > 0:
                        _cand_score = _cand_proto_sep / (self.family_ctx_cand_sep_ema + 1.0e-8)
                        _cand_accept_neg = self._family_ctx_deadzone_score(
                            _cand_score,
                            self.family_ctx_wsa_c_low,
                            self.family_ctx_wsa_c_high,
                        )
                        _pos_cand_accept = _query_accept.clone()
                        _cand_accept = torch.cat([_pos_cand_accept, _cand_accept_neg], dim=1)
                    else:
                        _cand_score = _prototype.new_empty(_prototype.size(0), 0, 1)
                        _cand_accept = _query_accept.expand(-1, _prototype.size(1), 1)
                    _accept = (_query_accept * _cand_accept).pow(self.family_ctx_wsa_accept_power)
                    if self.family_ctx_wsa_accept_disable:
                        _accept = torch.ones_like(_cand_accept)
                    _wsa_support = _prototype.new_tensor(float(self._family_ctx_support_schedule())).view(1, 1, 1)
                    _effective_alpha = self.family_ctx_alpha * (_wsa_support + (1.0 - _wsa_support) * _accept)
                else:
                    _query_score = _proto_sep_dist
                    _query_accept = _risk_gate
                    _cand_score = _cand_proto_sep
                    _cand_accept = _cand_risk_gate
                    _accept = _risk_gate * _cand_risk_gate
                    _wsa_support = _prototype.new_tensor(0.0).view(1, 1, 1)
                    _effective_alpha = self.family_ctx_alpha * _risk_gate * _cand_risk_gate
                _adapted_hidden = (1.0 + _effective_alpha * _active_mask * _gamma) * _base_hidden + _effective_alpha * _active_mask * _beta
                self._last_family_ctx_aux = {"family_id": _family_id, "active_mask": _active_mask.reshape(_active_mask.size(0), -1).amax(dim=-1), "risk_gate": _risk_gate, "cand_proto_sep": _cand_proto_sep, "cand_risk_gate": _cand_risk_gate[:, 1:, :], "effective_alpha": _effective_alpha, "pos_effective_alpha": _effective_alpha[:, :1, :], "neg_effective_alpha": _effective_alpha[:, 1:, :], "pos_hidden": _adapted_hidden[:, :1, :], "neg_hidden": _adapted_hidden[:, 1:, :], "pos_proto": _prototype[:, :1, :], "neg_proto": _prototype[:, 1:, :]}
                if self.family_ctx_wsa_enable:
                    self._last_family_ctx_aux.update({
                        'wsa_support': _wsa_support.detach(),
                        'query_accept': _query_accept.detach(),
                        'cand_accept': _cand_accept.detach(),
                    })
                feature = torch.cat([_adapted_hidden, _query_part], dim=-1)
                self._last_family_ctx_debug = {"family_id": _family_id.detach(), "active_mask_mean": _active_mask.mean().detach(), "hop_weight": _hop_weight.detach(), "support_norm": _support.norm(dim=-1).mean().detach(), "prototype_norm": _prototype.norm(dim=-1).mean().detach(), "proto_sep_mean": _proto_sep_dist.mean().detach(), "risk_gate_mean": _risk_gate.mean().detach(), "cand_proto_sep_mean": (_cand_proto_sep.mean().detach() if _cand_proto_sep.numel() > 0 else torch.tensor(1.0, device=_prototype.device)), "cand_risk_gate_mean": _cand_risk_gate.mean().detach(), "gamma_absmax": _gamma.abs().max().detach(), "beta_absmax": _beta.abs().max().detach()}
                if _evidence_rel_id is not None:
                    self._last_family_ctx_debug.update({
                        "evidence_rel_id_mean": _evidence_rel_id.to(_prototype.dtype).mean().detach(),
                        "evidence_family_id_mean": _evidence_family_id.to(_prototype.dtype).mean().detach(),
                    })
                if self.family_ctx_wsa_enable:
                    self._last_family_ctx_debug.update({
                        'wsa_enable': torch.tensor(float(self.family_ctx_wsa_enable), device=_prototype.device),
                        'wsa_accept_disable': torch.tensor(float(self.family_ctx_wsa_accept_disable), device=_prototype.device),
                        'wsa_support': _wsa_support.mean().detach(),
                        'query_score_mean': _query_score.mean().detach(),
                        'query_accept_mean': _query_accept.mean().detach(),
                        'cand_score_mean': (_cand_score.mean().detach() if _cand_score.numel() > 0 else torch.tensor(1.0, device=_prototype.device)),
                        'cand_accept_mean': _cand_accept.mean().detach(),
                        'accept_mean': _accept.mean().detach(),
                        'effective_alpha_zero_frac': (_effective_alpha.abs() < 1.0e-12).to(_effective_alpha.dtype).mean().detach(),
                        'proto_sep_ema': self.family_ctx_proto_sep_ema.detach(),
                        'cand_sep_ema': self.family_ctx_cand_sep_ema.detach(),
                    })
            else:
                self._last_family_ctx_aux = None
                self._last_family_ctx_debug = {"family_id": _family_id.detach(), "active_mask_mean": _active_mask.mean().detach()}
        else:
            self._last_family_ctx_aux = None
            self._last_family_ctx_debug = None

        if self.symmetric:
            assert (t_index[:, [0]] == t_index).all()
            r_index = (r_index + self.num_relation) % (self.num_relation * 2)
            output = self.bellmanford(graph, t_index[:, 0], r_index[:, 0])
            inv_feature = output["node_feature"].transpose(0, 1)
            index = h_index.unsqueeze(-1).expand(-1, -1, inv_feature.shape[-1])
            inv_feature = inv_feature.gather(1, index)
            feature = (feature + inv_feature) / 2

        if self.qrtc_cand_gate_mlp is not None and self.qrtc_cand_readout_on and (not self.mokgr_l_enable):
            feature = self._apply_qrtc_candidate_readout(feature, output, r_index)

        if self.mokgr_l_enable:
            hop_hiddens = output["hop_hidden_states"]
            hop_start = max(0, self.mokgr_l_min_hop - 1)
            hop_end = len(hop_hiddens) if self.mokgr_l_max_hop is None else min(len(hop_hiddens), self.mokgr_l_max_hop)
            if hop_start >= hop_end:
                raise ValueError(
                    f"invalid mokgr_l hop window: start={hop_start}, end={hop_end}, total={len(hop_hiddens)}"
                )
            relation_query = output["relation_query"].unsqueeze(1).expand(-1, t_index.size(1), -1)
            hop_features = []
            for hop_hidden in hop_hiddens[hop_start:hop_end]:
                hop_feature = hop_hidden.transpose(0, 1)
                hop_index = t_index.unsqueeze(-1).expand(-1, -1, hop_feature.shape[-1])
                hop_feature = hop_feature.gather(1, hop_index)
                hop_feature = torch.cat([hop_feature, relation_query], dim=-1)
                hop_features.append(hop_feature)
            hop_features = torch.stack(hop_features, dim=2)    # [B, N, H, F]
            hop_logits = self.mlp(hop_features).squeeze(-1)    # [B, N, H]
            hop_weight, mokgr_l_debug = self.mokgr_l_router(output["relation_query"])
            score = (hop_logits * hop_weight.unsqueeze(1)).sum(dim=-1)
            self._last_mokgr_l_debug = mokgr_l_debug
            if self.print_router_debug:
                try:
                    print("MOKGR_L_HOP_WEIGHT =", hop_weight[0].detach().cpu().tolist())
                except Exception as e:
                    print("MOKGR_L_DEBUG_PRINT_FAILED =", repr(e))
        else:
            # one score for each node - [batch_size, num_neg + 1]
            score = self.mlp(feature).squeeze(-1)
        if self.f8_score_res_enable:
            _f8_rel = r_index[:, 0] if r_index.ndim > 1 else r_index
            _f8_mask = ((_f8_rel == 8) | (_f8_rel == 8 + self.num_relation)).to(score.dtype).unsqueeze(-1)
            _delta_score = self.f8_score_alpha * self.f8_score_res(feature).squeeze(-1)
            score = score + _f8_mask * _delta_score
        if self.rics_enable:
            _rics_rel = r_index[:, 0] if r_index.ndim > 1 else r_index
            _rics_query = self.query(_rics_rel).unsqueeze(1).expand(-1, feature.size(1), -1)
            _rics_in = torch.cat([feature, _rics_query], dim=-1)
            _rics_raw = self.rics_delta(_rics_in).squeeze(-1)
            if self.rics_center_delta:
                _rics_raw = _rics_raw - _rics_raw.mean(dim=1, keepdim=True)
            _rics_delta = torch.tanh(_rics_raw)
            if self.rics_allow_rel_ids:
                _allow = torch.tensor(
                    self.rics_allow_rel_ids,
                    device=_rics_rel.device,
                    dtype=_rics_rel.dtype,
                )
                _rics_mask = (_rics_rel.unsqueeze(-1) == _allow.view(1, -1)).any(dim=-1)
                _rics_mask = _rics_mask.to(score.dtype).unsqueeze(-1)
            else:
                _rics_mask = torch.ones(score.size(0), 1, device=score.device, dtype=score.dtype)
            if self.rics_explicit_inverse_gate:
                _rics_inverse_rel_id = int(self.rics_base_rel_id + self.num_relation)
                _rics_inverse_mask = (_rics_rel == _rics_inverse_rel_id).to(score.dtype).unsqueeze(-1)
                _rics_mask = _rics_mask * _rics_inverse_mask
            else:
                _rics_inverse_rel_id = None
                _rics_inverse_mask = torch.ones(score.size(0), 1, device=score.device, dtype=score.dtype)
            score = score + _rics_mask * self.rics_alpha * _rics_delta
            self._last_rics_debug = {
                "enable": 1,
                "alpha": float(self.rics_alpha),
                "allow_rel_ids": list(self.rics_allow_rel_ids),
                "center_delta": bool(self.rics_center_delta),
                "explicit_inverse_gate": bool(self.rics_explicit_inverse_gate),
                "base_rel_id": int(self.rics_base_rel_id),
                "inverse_rel_id": int(_rics_inverse_rel_id) if _rics_inverse_rel_id is not None else None,
                "inverse_mask_mean": float(_rics_inverse_mask.detach().mean().item()),
                "mask_mean": float(_rics_mask.detach().mean().item()),
                "delta_absmax": float(_rics_delta.detach().abs().max().item()),
                "delta_mean": float(_rics_delta.detach().mean().item()),
                "delta_std": float(_rics_delta.detach().std().item()) if _rics_delta.numel() > 1 else 0.0,
                "masked_delta_absmax": float((_rics_mask * _rics_delta).detach().abs().max().item()),
                "masked_delta_mean": float((_rics_mask * _rics_delta).detach().mean().item()),
                "masked_delta_std": float((_rics_mask * _rics_delta).detach().std().item()) if _rics_delta.numel() > 1 else 0.0,
                "score_mean_after": float(score.detach().mean().item()),
            }
            if self.rics_print_debug and (os.getenv("RICS_PRINT_DEBUG_EVERY", "0") == "1" or not self._rics_debug_printed):
                print("RICS_DEBUG =", self._last_rics_debug)
                self._rics_debug_printed = True
        else:
            self._last_rics_debug = None
        return score.view(shape)

    def _build_family_id_table(self):
        num_rel = int(self.num_relation)
        table = torch.zeros(num_rel * 2, dtype=torch.long)
        specs = [
            (os.getenv("FAMILY_CTX_EXPR_IDS", "8"), 1),
            (os.getenv("FAMILY_CTX_CERNA_IDS", ""), 2),
            (os.getenv("FAMILY_CTX_TRANS_IDS", ""), 3),
        ]
        for raw_ids, family_id in specs:
            for x in raw_ids.split(","):
                x = x.strip()
                if not x:
                    continue
                rid = int(x)
                if 0 <= rid < num_rel:
                    table[rid] = family_id
                    table[rid + num_rel] = family_id
        return table

    def _map_relation_to_family_id(self, r_index):
        if r_index.ndim > 1:
            r_index = r_index[:, 0]
        return self.family_ctx_family_id_table[r_index]


    def _family_ctx_deadzone_score(self, x, low, high):
        if high <= low:
            return (x > low).to(x.dtype)
        return ((x - low) / (high - low)).clamp(min=0.0, max=1.0)

    def _family_ctx_support_schedule(self):
        if not self.training:
            return 0.0
        warmup_ratio = max(0.0, min(1.0, self.family_ctx_wsa_warmup_ratio))
        init_support = max(0.0, min(1.0, self.family_ctx_wsa_init_support))
        if warmup_ratio <= 0 or init_support <= 0:
            return 0.0
        explicit_steps = int(getattr(self, 'family_ctx_wsa_warmup_steps', 0))
        if explicit_steps > 0:
            warmup_steps = explicit_steps
        else:
            total_steps = int(getattr(self, 'num_epoch', 0)) * int(getattr(self, 'batch_per_epoch', 0))
            warmup_steps = max(1, int(total_steps * warmup_ratio)) if total_steps > 0 else 1
        global_step = int(getattr(self, '_family_ctx_global_step', 0))
        ratio = min(float(global_step) / float(warmup_steps), 1.0)
        return init_support * (1.0 - ratio)

    def _family_ctx_update_ema(self, proto_sep_mean, cand_sep_mean):
        m = self.family_ctx_wsa_ema_momentum
        proto_val = proto_sep_mean.detach().to(self.family_ctx_proto_sep_ema.device, dtype=self.family_ctx_proto_sep_ema.dtype)
        cand_val = cand_sep_mean.detach().to(self.family_ctx_cand_sep_ema.device, dtype=self.family_ctx_cand_sep_ema.dtype)
        self.family_ctx_proto_sep_ema.mul_(m).add_(proto_val * (1.0 - m))
        self.family_ctx_cand_sep_ema.mul_(m).add_(cand_val * (1.0 - m))

    def visualize(self, graph, h_index, t_index, r_index):
        assert h_index.numel() == 1 and h_index.ndim == 1
        graph = graph.undirected(add_inverse=True)

        output = self.bellmanford(graph, h_index, r_index, separate_grad=True)
        feature = output["node_feature"]
        step_graphs = output["step_graphs"]

        index = t_index.unsqueeze(0).unsqueeze(-1).expand(-1, -1, feature.shape[-1])
        feature = feature.gather(0, index).squeeze(0)
        score = self.mlp(feature).squeeze(-1)

        edge_weights = [graph.edge_weight for graph in step_graphs]
        edge_grads = autograd.grad(score, edge_weights)
        for graph, edge_grad in zip(step_graphs, edge_grads):
            with graph.edge():
                graph.edge_grad = edge_grad
        distances, back_edges = self.beam_search_distance(step_graphs, h_index, t_index, self.num_beam)
        paths, weights = self.topk_average_length(distances, back_edges, t_index, self.path_topk)

        return paths, weights

    @torch.no_grad()
    def beam_search_distance(self, graphs, h_index, t_index, num_beam=10):
        num_node = graphs[0].num_node
        input = torch.full((num_node, num_beam), float("-inf"), device=self.device)
        input[h_index, 0] = 0

        distances = []
        back_edges = []
        for graph in graphs:
            graph = graph.edge_mask(graph.edge_list[:, 0] != t_index)
            node_in, node_out = graph.edge_list.t()[:2]

            message = input[node_in] + graph.edge_grad.unsqueeze(-1)
            msg_source = graph.edge_list.unsqueeze(1).expand(-1, num_beam, -1)

            is_duplicate = torch.isclose(message.unsqueeze(-1), message.unsqueeze(-2)) & \
                           (msg_source.unsqueeze(-2) == msg_source.unsqueeze(-3)).all(dim=-1)
            is_duplicate = is_duplicate.float() - \
                           torch.arange(num_beam, dtype=torch.float, device=self.device) / (num_beam + 1)
            # pick the first occurrence as the previous state
            prev_rank = is_duplicate.argmax(dim=-1, keepdim=True)
            msg_source = torch.cat([msg_source, prev_rank], dim=-1)

            node_out, order = node_out.sort()
            node_out_set = torch.unique(node_out)
            # sort message w.r.t. node_out
            message = message[order].flatten()
            msg_source = msg_source[order].flatten(0, -2)
            size = scatter_add(torch.ones_like(node_out), node_out, dim_size=num_node)
            msg2out = torch.repeat_interleave(size[node_out_set] * num_beam)
            # deduplicate
            is_duplicate = (msg_source[1:] == msg_source[:-1]).all(dim=-1)
            is_duplicate = torch.cat([torch.zeros(1, dtype=torch.bool, device=self.device), is_duplicate])
            message = message[~is_duplicate]
            msg_source = msg_source[~is_duplicate]
            msg2out = msg2out[~is_duplicate]
            size = scatter_add(torch.ones_like(msg2out), msg2out, dim_size=len(node_out_set))

            if not torch.isinf(message).all():
                distance, rel_index = functional.variadic_topk(message, size, k=num_beam)
                abs_index = rel_index + (size.cumsum(0) - size).unsqueeze(-1)
                back_edge = msg_source[abs_index]
                distance = distance.view(len(node_out_set), num_beam)
                back_edge = back_edge.view(len(node_out_set), num_beam, 4)
                distance = scatter_add(distance, node_out_set, dim=0, dim_size=num_node)
                back_edge = scatter_add(back_edge, node_out_set, dim=0, dim_size=num_node)
            else:
                distance = torch.full((num_node, num_beam), float("-inf"), device=self.device)
                back_edge = torch.zeros(num_node, num_beam, 4, dtype=torch.long, device=self.device)

            distances.append(distance)
            back_edges.append(back_edge)
            input = distance

        return distances, back_edges

    def topk_average_length(self, distances, back_edges, t_index, k=10):
        paths = []
        average_lengths = []

        for i in range(len(distances)):
            distance, order = distances[i][t_index].flatten(0, -1).sort(descending=True)
            back_edge = back_edges[i][t_index].flatten(0, -2)[order]
            for d, (h, t, r, prev_rank) in zip(distance[:k].tolist(), back_edge[:k].tolist()):
                if d == float("-inf"):
                    break
                path = [(h, t, r)]
                for j in range(i - 1, -1, -1):
                    h, t, r, prev_rank = back_edges[j][h, prev_rank].tolist()
                    path.append((h, t, r))
                paths.append(path[::-1])
                average_lengths.append(d / len(path))

        if paths:
            average_lengths, paths = zip(*sorted(zip(average_lengths, paths), reverse=True)[:k])

        return paths, average_lengths

def cached(model, debug=False):

    @decorator
    def wrapper(forward, self, *args, **kwargs):

        def equal(x, y):
            if isinstance(x, nn.Parameter):
                x = x.data
            if isinstance(y, nn.Parameter):
                y = y.data
            if type(x) != type(y):
                return False
            if isinstance(x, torch.Tensor):
                return x.shape == y.shape and (x == y).all()
            elif isinstance(x, data.Graph):
                if x.num_node != y.num_node or x.num_edge != y.num_edge or x.num_relation != y.num_relation:
                    return False
                edge_feature = getattr(x, "edge_feature", torch.tensor(0, device=x.device))
                y_edge_feature = getattr(y, "edge_feature", torch.tensor(0, device=y.device))
                if edge_feature.shape != y_edge_feature.shape:
                    return False
                return (x.edge_list == y.edge_list).all() and (x.edge_weight == y.edge_weight).all() \
                       and (edge_feature == y_edge_feature).all()
            else:
                return x == y

        if self.training:
            return forward(self, *args, **kwargs)

        func = inspect.signature(forward)
        func = func.bind(self, *args, **kwargs)
        func.apply_defaults()
        arguments = func.arguments.copy()
        arguments.pop(next(iter(arguments.keys())))

        if hasattr(self, "_forward_cache"):
            hit = True
            message = []
            for k, v in arguments.items():
                if not equal(self._forward_cache[k], v):
                    hit = False
                    message.append("%s: miss" % k)
                    break
                message.append("%s: hit" % k)
            if debug:
                print("[cache] %s" % ", ".join(message))
        else:
            hit = False
            if debug:
                print("[cache] cold start")
        if hit:
            return self._forward_cache["result"]
        else:
            self._forward_cache = {}

        for k, v in arguments.items():
            if isinstance(v, torch.Tensor) or isinstance(v, data.Graph):
                v = v.detach()
            self._forward_cache[k] = v
        result = forward(self, *args, **kwargs)
        self._forward_cache["result"] = result
        return result

    model = copy.copy(model)
    model.forward = types.MethodType(wrapper(model.forward.__func__), model)
    return model


# TODO: faster implemenation of remove
@torch.no_grad()
def remove(graph, edges, ratio=1):
    if ratio == 0:
        return graph
    in_edge = torch.zeros(graph.num_edge, dtype=torch.bool, device=graph.device)
    for edges_ in edges.split(2048):
        if edges.shape[-1] == 3:
            in_edge_ = (graph.edge_list.unsqueeze(0) == edges_.unsqueeze(1)).all(dim=-1).any(dim=0)
        elif edges.shape[-1] == 2:
            in_edge_ = (graph.edge_list[:, :2].unsqueeze(0) == edges_.unsqueeze(1)).all(dim=-1).any(dim=0)
        elif edges.shape[-1] == 1:
            in_edge_ = (graph.edge_list[:, :2].unsqueeze(0) == edges_.unsqueeze(1)).any(dim=-1).any(dim=0)
        else:
            raise ValueError
        in_edge = in_edge | in_edge_
    if ratio < 1:
        in_edge = in_edge & (torch.rand(len(in_edge), device=graph.device) < ratio)
    graph = graph.edge_mask(~in_edge)
    return graph

@R.register("model.MLPScore")
class MLPScore(layers.MLP, core.Configurable):

    def __init__(self, num_entity, num_relation, embedding_dim, hidden_dims, activation="relu", dropout=0,
                 num_feature=3):
        super(MLPScore, self).__init__(embedding_dim * num_feature, hidden_dims, activation, dropout)
        self.num_entity = num_entity
        self.num_relation = num_relation
        self.num_feature = num_feature

        self.entity = nn.Embedding(num_entity, embedding_dim)
        self.relation = nn.Embedding(num_relation, embedding_dim)
        self.entity_norm = nn.LayerNorm(embedding_dim)
        self.relation_norm = nn.LayerNorm(embedding_dim)

        nn.init.kaiming_uniform_(self.entity.weight, a=math.sqrt(5), mode="fan_in")
        nn.init.kaiming_uniform_(self.relation.weight, a=math.sqrt(5), mode="fan_in")

    def forward(self, head, tail, relation, h_index=None, t_index=None, r_index=None, all_loss=None, metric=None):
        head = self.entity_norm(head)
        tail = self.entity_norm(tail)
        relation = self.relation_norm(relation)
        if h_index is not None:
            h = head[h_index]
            r = relation[r_index]
            t = tail[t_index]
        else:
            h = head
            r = relation
            t = tail
        x = torch.cat([h, r, t], dim=-1)
        score = super(MLPScore, self).forward(x)
        score = score.squeeze(-1)
        return score

    def forward_feature(self, feature):
        score = super(MLPScore, self).forward(feature)
        score = score.squeeze(-1)
        return score

    def flip_relation(self, relation):
        # TODO: Is it reasonable?
        return -relation

@R.register("model.NodeEncoder")
class NodeEncoder(nn.Module, core.Configurable):

    def __init__(self, gnn_model, score_model, flip_edge=False):
        super(NodeEncoder, self).__init__()
        self.gnn_model = cached(gnn_model)
        self.score_model = score_model
        self.flip_edge = flip_edge

    def get_undirected(self, graph):
        edge_list = graph.edge_list[:, [1, 0, 2]]
        if graph.num_relation > 1: # knowledge graph
            edge_list[:, 2] += graph.num_relation
            num_relation = graph.num_relation * 2
        else:
            num_relation = graph.num_relation
        edge_list = torch.cat((graph.edge_list, edge_list))
        edge_feature = self.score_model.flip_relation(graph.edge_feature)
        edge_feature = torch.cat((graph.edge_feature, edge_feature))
        return type(graph)(edge_list, edge_feature=edge_feature, num_node=graph.num_node, num_relation=num_relation)

    def forward(self, graph, h_index, t_index, r_index, all_loss=None, metric=None):
        if isinstance(self.score_model.relation, torch.nn.Parameter):
            entity_weight = self.score_model.entity
            relation_weight = self.score_model.relation
        else:
            entity_weight = self.score_model.entity.weight
            relation_weight = self.score_model.relation.weight

        self.gnn_model._raa_entity_weight = entity_weight

        with graph.edge():
            graph.edge_feature = relation_weight[graph.edge_list[:, 2]]
        if all_loss is not None:
            edges = torch.stack((h_index, t_index, r_index), dim=-1).flatten(0, -2)
            graph = remove(graph, edges)
        if self.flip_edge:
            graph = self.get_undirected(graph)

        feature = self.gnn_model(graph, entity_weight, all_loss, metric)["node_feature"]
        if isinstance(self.gnn_model, MLPScore):
            features = [feature[h_index], relation_weight[r_index], feature[t_index]]
            features = torch.cat(features, dim=-1)
            score = self.score_model.forward_feature(features)
        else:
            score = self.score_model(feature, feature, relation_weight, h_index, t_index, r_index,
                                    all_loss, metric)
        
        return score
