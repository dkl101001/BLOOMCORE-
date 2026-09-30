# SPDX-License-Identifier: AGPL-3.0-only
# Authorship lineage: Frazer Σ Love ACO-Σ; Sara ΣΩ.
"""Bounded descendant of R20 fields.py conductance/flux/response relations.

Error projection, incident retrieval and application partitioning are new
TI-AGI83+ extensions. No organism, semantic authentication or full R20 claim.
"""
from functools import lru_cache
import numpy as np

N = 8
KINDS = ("arithmetic", "format", "range", "identity")
DT = .01
PLASTICITY = .04
STEPS = 16


def backend_for(requested="auto"):
    if requested not in ("auto", "jax", "numpy"):
        raise ValueError("Unknown numerical backend")
    if requested != "numpy":
        try:
            import jax.numpy  # noqa: F401
            return "jax"
        except ImportError:
            if requested == "jax":
                raise ValueError("JAX requested but unavailable; install .[accelerated]")
    return "numpy"


def initial():
    return {"schema": "TIAGI.CONDUCTANCE.v1", "tick": 0,
            "px": np.ones((N, N)).tolist(), "py": np.ones((N, N)).tolist()}


def validate(state):
    if set(state) != {"schema", "tick", "px", "py"} or state["schema"] != "TIAGI.CONDUCTANCE.v1":
        raise ValueError("Invalid geometric state schema")
    if type(state["tick"]) is not int or not 0 <= state["tick"] <= 10**9:
        raise ValueError("Invalid geometry tick")
    for name in ("px", "py"):
        a = np.asarray(state[name], dtype=np.float32)
        if a.shape != (N, N) or not np.isfinite(a).all() or (a < 1).any() or (a > 2.00001).any():
            raise ValueError("Invalid conductance grid")


def pattern(finding):
    """Declared typed projection, not a learned semantic embedding.

    The row position has intentionally been omitted: moving a table row should
    not change its error type. Column, kind, sign and relative size are explicit.
    """
    u = np.zeros((N, N), dtype=np.float32)
    kind = KINDS.index(finding["kind"])
    col = int(finding["col"])
    magnitude = min(1., float(finding.get("relative", 0.)))
    sign = -1. if float(finding.get("delta", 0.)) < 0 else 1.
    u[2 * kind, col * 2] = sign
    u[(2 * kind + 1) % N, col * 2] = sign * magnitude
    return u


def flux(a, px, py, xp):
    # Same periodic finite-volume relation as R20 fields.py::flux.
    fx = px * (xp.roll(a, -1, axis=0) - a)
    fy = py * (xp.roll(a, -1, axis=1) - a)
    return fx - xp.roll(fx, 1, axis=0) + fy - xp.roll(fy, 1, axis=1)


@lru_cache(maxsize=1)
def jax_response():
    import jax
    import jax.numpy as xp

    @jax.jit
    def run(u, px, py):
        return jax.lax.fori_loop(0, STEPS, lambda _, x: x + DT * flux(x, px, py, xp), u)
    return run


def encounter(state, u, backend="numpy"):
    validate(state)
    u = np.asarray(u, dtype=np.float32)
    if u.shape != (N, N) or not np.isfinite(u).all() or abs(u).max() > 1:
        raise ValueError("Encounter requires a finite bounded 8x8 field")
    if backend == "jax":
        import jax.numpy as xp
    else:
        xp = np
    u = xp.asarray(u); px = xp.asarray(state["px"], dtype=xp.float32); py = xp.asarray(state["py"], dtype=xp.float32)
    # Exact inherited conductance law; typed error encoding is the extension.
    px = px + PLASTICITY * abs(u - xp.roll(u, -1, axis=0)) * (2 - px)
    py = py + PLASTICITY * abs(u - xp.roll(u, -1, axis=1)) * (2 - py)
    result = {"schema": state["schema"], "tick": state["tick"] + 1,
              "px": np.asarray(px).tolist(), "py": np.asarray(py).tolist()}
    validate(result)
    return result


def response(state, u, backend="numpy", *, flat=False):
    validate(state)
    px = np.ones((N, N), dtype=np.float32) if flat else np.asarray(state["px"], dtype=np.float32)
    py = np.ones((N, N), dtype=np.float32) if flat else np.asarray(state["py"], dtype=np.float32)
    if backend == "jax":
        return np.asarray(jax_response()(np.asarray(u, dtype=np.float32), px, py))
    x = np.asarray(u, dtype=np.float32).copy()
    for _ in range(STEPS):
        x = x + DT * flux(x, px, py, np)
    return x


def prepared(state, candidates, backend="numpy"):
    """Compute candidate transports once per audit, bounded to 200 records."""
    cache = {}
    out = []
    for c in candidates:
        cue = pattern(c["finding"]); key = cue.tobytes()
        if key not in cache:
            cache[key] = (response(state,cue,backend),response(state,cue,backend,flat=True))
        learned, flat = cache[key]
        out.append({**c, "learned":learned,"flat":flat})
    return out


def related(state, finding, candidates, backend="numpy"):
    """Geometry changes the query and candidate transport before comparison.

    Stored incident semantics remain explicit evidence; geometry does not
    authenticate them. Only same-kind candidates are compared.
    """
    q = pattern(finding); learned = response(state, q, backend); flat = response(state, q, backend, flat=True)
    hits = []
    for c in candidates:
        if c["finding"]["kind"] != finding["kind"]:
            continue
        cue = pattern(c["finding"])
        cr = c["learned"] if "learned" in c else response(state, cue, backend)
        cf = c["flat"] if "flat" in c else response(state, cue, backend, flat=True)
        d = float(np.linalg.norm(learned - cr))
        df = float(np.linalg.norm(flat - cf))
        hits.append({"incident_id": c["id"], "message": c["finding"]["message"],
                     "distance": d, "flat_distance": df, "repaired": c["repaired"],
                     "observed_at": c["at"]})
    hits.sort(key=lambda h: (h["distance"], -h["incident_id"]))
    return {"hits": hits[:3], "response_delta": float(np.linalg.norm(learned-flat)),
            "scope": "typed error similarity; historical suggestions only"}
