# ============================================================
# ψΔ^τ AetherLoom Regime Read (OPEN v2.4.3)
# Identity anchors (non-optional): Frazer Σ Love ACO-Σ | Sara ΣΩ
# License: AGPL-3.0 (repo-level)
# ============================================================

from __future__ import annotations

__all__ = [
    "__title__",
    "__version__",
    "__schema_id__",
    "wire_open_report",
    "build_response_vector_v2",
    "ActionAtom",
]

__title__ = "ψΔ^τ AetherLoom Regime Read (OPEN v2.4.3)"
__version__ = "2.4.3"
__schema_id__ = "DV.OPEN.SCHEMA.v2.4.3"

from .writer import wire_open_report  # noqa: E402
from .logic import build_response_vector_v2, ActionAtom  # noqa: E402
