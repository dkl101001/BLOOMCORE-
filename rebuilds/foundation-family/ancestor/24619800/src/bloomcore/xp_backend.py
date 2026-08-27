from __future__ import annotations

"""CPU backend helpers (NumPy only).

Authorship invariants:
- Frazer Σ Love ACO-Σ
- Sara ΣΩ
"""

from dataclasses import dataclass
from typing import Any
import numpy as np


@dataclass(frozen=True)
class XPBackend:
    """Tiny abstraction layer over NumPy.

    This repo is *CPU-only* by design. The abstraction exists so the math reads
    consistently and can be extended elsewhere without changing call sites.
    """
    xp: Any = np  # keep attribute name used in the sketch

    def array(self, x, dtype=None):
        return np.array(x, dtype=dtype)

    def zeros(self, shape, dtype=float):
        return np.zeros(shape, dtype=dtype)

    def zeros_like(self, x):
        return np.zeros_like(x)

    def norm(self, x) -> float:
        return float(np.linalg.norm(x))

    def dot(self, a, b):
        return np.dot(a, b)

    def matmul(self, a, b):
        return np.matmul(a, b)
