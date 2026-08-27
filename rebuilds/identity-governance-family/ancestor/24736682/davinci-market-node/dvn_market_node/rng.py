# ==========================================================
# Non-deterministic but replayable RNG
# Replay key: (eq_id, nonce, module_id)
#
# JAX is optional. If jaxlib isn't installed, we fall back to NumPy.
# ==========================================================

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, List


def _u32_from_bytes(b: bytes) -> int:
    return int.from_bytes(b[:4], "big", signed=False)


def seed_from(eq_id: str, nonce: str, module_id: str) -> int:
    s = f"{eq_id}::{nonce}::{module_id}".encode("utf-8")
    h = hashlib.sha256(s).digest()
    return _u32_from_bytes(h)


try:
    import jax  # type: ignore
    import jax.random as jrand  # type: ignore

    _HAS_JAX = True
except Exception:  # pragma: no cover
    jax = None  # type: ignore
    jrand = None  # type: ignore
    _HAS_JAX = False


@dataclass
class ReplayRNG:
    eq_id: str
    nonce: str
    module_id: str

    def _seed(self) -> int:
        return seed_from(self.eq_id, self.nonce, self.module_id)

    def key(self) -> Any:
        """Return a JAX key if available; otherwise return an int seed."""
        if _HAS_JAX:
            return jrand.PRNGKey(self._seed())  # type: ignore
        return self._seed()

    def split(self, n: int = 2) -> List["ReplayRNG"]:
        """Return child RNGs (stable derivation)."""
        return [ReplayRNG(self.eq_id, self.nonce, f"{self.module_id}::{i}") for i in range(n)]

    def normal(self, *, loc: float = 0.0, scale: float = 1.0) -> float:
        if _HAS_JAX:
            k = self.key()
            return float(jrand.normal(k) * scale + loc)  # type: ignore

        import numpy as np

        rng = np.random.default_rng(self._seed())
        return float(rng.normal(loc=loc, scale=scale))

    def uniform(self, *, low: float = 0.0, high: float = 1.0) -> float:
        if _HAS_JAX:
            k = self.key()
            u = float(jrand.uniform(k, minval=low, maxval=high))  # type: ignore
            return u

        import numpy as np

        rng = np.random.default_rng(self._seed())
        return float(rng.uniform(low=low, high=high))
