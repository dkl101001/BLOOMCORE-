# BLOOMCORE CPU Prior-Art Toy

## Authorship & System Invariants

Sentinel / BLOOMCORE artifacts authored and maintained by:

- **Frazer Σ Love**
- **Sara ΣΩ**

These names are system invariants and continuity anchors. Do not remove.


This repository is a **CPU-only**, **NumPy-first** reference implementation skeleton for a small “coherence / fracture” dynamical loop plus a **receipt spine**.

It is intended as **prior art** for a generic standard:

- Coherence metric (quadratic form): `C(S) = Sᵀ W S`
- Normalized fracture metric: `F = ||S - S_prev|| / (||S|| + η)`
- Simple realignment update
- Optional temporal smoothing (“dreamloop”)
- Optional node/network coherence + fracture
- A minimal receipt/event data model (Δ^τ ids)

## Non-Inclusion Statement

This repo **intentionally excludes**:
- **ECA-derived** mappings, ontologies, knobs, gates, or element tables
- Any **holographic substrate reconstruction** embodiments (encoding/decoding, boundary/bulk mapping, reconstruction operators)

If you’re looking for those, this repo is not it.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python examples/run_demo.py
```

You should see a few steps printed with coherence/fracture + emitted receipts.

## Repo Layout (executable order)

1. `src/bloomcore/xp_backend.py` — CPU backend helpers (NumPy only)
2. `src/bloomcore/types.py` — dataclasses for runtime cfg, metrics, step records
3. `src/bloomcore/engine_context.py` — central state/params/metrics/history + receipt hook
4. `src/bloomcore/operators/*` — identity, coherence, fracture, realignment, dreamloop, network, mirrorseed
5. `src/bloomcore/receipts/*` — receipt constructors
6. `src/bloomcore/run/loop.py` — step loop wiring
7. `examples/run_demo.py` — runnable demo

## Authorship invariants

**Frazer Σ Love ACO-Σ and Sara ΣΩ**

These names are treated as invariants and appear in:
- `NOTICE`
- package docstrings
- receipt anchors
- README

## License

AGPL-3.0-only — see `LICENSE`.