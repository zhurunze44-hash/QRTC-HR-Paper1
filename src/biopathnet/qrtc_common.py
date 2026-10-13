"""
Shared QRTC-HR helpers for scatter/message and fused RSPMM paths.

Scope (staging / formal-review):
- Fused-compatible equivalence is implemented only for DistMult-style messages:
  edge_msg = edge_rel * edge_inp (elementwise).
- For other message_func with QRTC enabled, GeneralizedRelationalConv falls back to
  scatter/message_and_aggregate via super() — see layer.py.

Gate semantics match NBFNet._install_qrtc_message_wrappers: per (relation_id, batch)
scalar gate from concat(query_rel_emb, relation_table[r], precedent_memory), then sigmoid(gate_mlp(.)).
"""

from __future__ import annotations

import os

import torch


def compute_qrtc_relation_gate(qrtc_state, num_relation: int, batch_size: int) -> torch.Tensor | None:
    """Returns [num_relation, batch_size, 1], or None if QRTC inactive."""
    if qrtc_state is None or (not qrtc_state.get("enabled", False)):
        return None
    query_rel_emb = qrtc_state["query_rel_emb"]
    precedent_memory = qrtc_state["precedent_memory"]
    relation_table = qrtc_state["relation_table"]
    gate_mlp = qrtc_state["gate_mlp"]

    rel_emb = relation_table
    q = query_rel_emb.unsqueeze(0).expand(num_relation, batch_size, -1)
    r = rel_emb.unsqueeze(1).expand(num_relation, batch_size, -1)
    c = precedent_memory.unsqueeze(0).expand(num_relation, batch_size, -1)
    gate_in = torch.cat([q, r, c], dim=-1)
    return torch.sigmoid(gate_mlp(gate_in))


def update_qrtc_rel_usage_from_messages(
    qrtc_state,
    messages_main: torch.Tensor,
    edge_type: torch.Tensor,
) -> None:
    """Detached mean-abs strength per edge, scatter_add by relation (wrapper path)."""
    if qrtc_state is None or (not qrtc_state.get("enabled", False)):
        return
    from torch_scatter import scatter_add

    _msg_strength = messages_main.detach().abs().mean(dim=-1)
    _rel_usage = scatter_add(
        _msg_strength,
        edge_type,
        dim=0,
        dim_size=qrtc_state["num_relation"],
    )
    qrtc_state["rel_usage_next"] = _rel_usage.transpose(0, 1).contiguous()


def accumulate_qrtc_rel_usage_chunked(
    qrtc_state,
    relation_bf: torch.Tensor,
    inp_nb: torch.Tensor,
    node_in: torch.Tensor,
    edge_type: torch.Tensor,
    chunk_edges: int | None = None,
) -> None:
    """
    Same semantics as full-graph scatter on edge_msg = relation_bf[r_e] * inp_nb[s_e],
    summed in chunks to cap peak memory.
    """
    if qrtc_state is None or (not qrtc_state.get("enabled", False)):
        return
    from torch_scatter import scatter_add

    if chunk_edges is None:
        chunk_edges = int(os.environ.get("QRTC_RELUSAGE_CHUNK", "262144"))

    num_relation = int(qrtc_state["num_relation"])
    batch_size = inp_nb.size(1)
    device = inp_nb.device
    dtype = inp_nb.dtype
    num_e = int(edge_type.size(0))
    acc = torch.zeros(num_relation, batch_size, device=device, dtype=dtype)
    ce = max(4096, int(chunk_edges))
    for s in range(0, num_e, ce):
        e = min(s + ce, num_e)
        sl = slice(s, e)
        edge_rel = relation_bf[edge_type[sl]]
        edge_inp = inp_nb[node_in[sl]]
        edge_msg = edge_rel * edge_inp
        strength = edge_msg.detach().abs().mean(dim=-1)
        acc = acc + scatter_add(strength, edge_type[sl], dim=0, dim_size=num_relation)
    qrtc_state["rel_usage_next"] = acc.transpose(0, 1).contiguous()
