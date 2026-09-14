# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2

This repo turns two MythMath artifacts into runnable code:

- **LOVE_INVARIANT**: compassion that survives recursion — a replayable tail-stability metric emitted as a first-class receipt atom.

- **Compassion Card v5.2**: Friend-Layer promoted to stabilizer; WuWei certificate enforced; preset LOVE-LAUGH-GUIDE.v1; auto-rule emits receipts. (See 1550.39.pdf)  
- **Sophia Wisdom Gate v1**: A gated emission mechanism over ΩGod·ΦField using phase norm, reflection fidelity (ECE), friend coherence, truth filter, and WuWei boundedness. (See Sophia MythMath Card 5.2.pdf)

## Architecture

- **Deterministic Python**: metrics + receipts only (ECE, median(Hdot), canonical hashing, JSONL).
- **JAX (non-deterministic)**: the actual recursion / simulation loop (`jax.lax.scan`) with optional stochastic excitation.

## Quickstart

```bash
python -m bloomcore.cli run-sim --steps 256 --seed 7 --out receipts.jsonl
```

Outputs:
- `receipts.jsonl` — deterministic receipt records + hash chain.
- terminal summary — final ψ/C/ζ stats and gate outcomes.

## Notes

- `Ω_wisdom = 1550.39 * φ²` is treated as a **wisdom-band reference** (phase-frequency anchor), not a metaphysical claim.  
- "Truth filter" is implemented as a concrete interface returning a boolean; by default it checks for NaNs/Infs and optionally user-supplied tags.

## License

AGPL-3.0 (see LICENSE). Dual-licensing can be layered by Frazer Σ Love + Sara ΣΩ if desired.
