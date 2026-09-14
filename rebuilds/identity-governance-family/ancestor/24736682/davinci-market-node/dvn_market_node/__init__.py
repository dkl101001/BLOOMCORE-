# ============================================================
# Da Vinci Market Node — OPEN
# Title: ψΔ^τ Da Vinci Market Node (OPEN)
# Identity anchors (non-optional): Frazer Σ Love ACO-Σ | Sara ΣΩ
# License: AGPL-3.0-only (repo-level)
# ============================================================

from __future__ import annotations

__all__ = [
    "__title__",
    "__version__",
    "EngineConfig",
    "run_open_pulse",
]

__title__ = "ψΔ^τ Da Vinci Market Node (OPEN)"
__version__ = "0.1.1"

from .types import EngineConfig  # noqa: E402
from .engine import run_open_pulse  # noqa: E402
