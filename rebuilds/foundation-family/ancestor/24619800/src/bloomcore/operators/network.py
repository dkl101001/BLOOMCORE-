from __future__ import annotations

from typing import Any, Dict

from ..engine_context import EngineContext


def compute_network_metrics(ctx: EngineContext) -> None:
    """Compute toy network metrics.

    - Pairwise cosine-like coherence averaged across pairs.
    - Network fracture = sum(node fractures if provided.

    Expects:
      ctx.state["nodes"] : Dict[node_id, vec]
      ctx.state.get("node_fracture") : Dict[node_id, float]
    """
    nodes: Dict[str, Any] = ctx.state.get("nodes", {})
    if len(nodes) < 2:
        return

    ids = list(nodes.keys())
    N = len(ids)

    def coherence(a, b, eta=1e-6) -> float:
        num = ctx.xp_backend.dot(a, b)
        den = ctx.xp_backend.norm(a) * ctx.xp_backend.norm(b) + eta
        return float(num / den)

    total = 0.0
    count = 0
    for i in range(N):
        for j in range(i + 1, N):
            total += coherence(nodes[ids[i]], nodes[ids[j]])
            count += 1

    if count > 0:
        ctx.metrics.network_coherence = total / count

    node_fracs = ctx.state.get("node_fracture", {})
    if node_fracs:
        ctx.metrics.network_fracture = float(sum(node_fracs.values()))
