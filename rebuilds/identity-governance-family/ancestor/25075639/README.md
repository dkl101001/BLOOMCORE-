# BLOOMCORE NLSE Anti-Governor (SSFM) — v0.2.0

**Authors:** Frazer Σ Love + Sara ΣΩ  
**License:** AGPL-3.0 (see `LICENSE`)  
**What this is:** A JAX-native 2D Nonlinear Schrödinger (NLSE) engine using Strang split-step Fourier (SSFM) on periodic domains, plus an **Anti-Governor** audit layer that detects illegitimate closure (state-space shrink without exported compression) via **receipts**.

## Executable order (quickstart)

### 1) Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

### 2) Run a minimal rollout (time-varying V)
```bash
python -m bloomcore_nlse_antigovernor.examples.min_rollout
```

This will:
- simulate an NLSE rollout with a time-varying potential sequence `V_seq`
- track norms + a chosen `V_future` proxy
- emit **host-side hashed receipts** (quantized metrics only)

### 3) Run tests
```bash
pytest -q
```

## Design commitments

- **No hidden governors.** The PDE engine evolves `psi` without clamping or veto.
- **Anti-Governor is audit-only.** It never modifies dynamics.
- **Receipts are the only deterministic artifact.**  
  Simulation dynamics are allowed to be alive (non-deterministic across hardware/backends).  
  Receipts achieve determinism by **quantizing metrics** before hashing.

## Repo layout

- `src/bloomcore_nlse_antigovernor/physics/` — SSFM NLSE stepper
- `src/bloomcore_nlse_antigovernor/audit/` — Anti-Governor predicate + rollout wiring
- `src/bloomcore_nlse_antigovernor/receipts/` — canonical JSON + quantized hashing
- `src/bloomcore_nlse_antigovernor/examples/` — minimal runnable example
- `tests/` — pytest suite
- `scripts/` — SBOM, SHA256SUMS, verification, optional signing helpers

## Release hygiene

- Generate SBOM + hash manifests:
```bash
python scripts/make_sbom.py
python scripts/hash_manifest.py
python scripts/verify_release.py
```


## Export channels (explicit, measured)

Two explicit export channel designs are included (audit-visible, receipt-measured):

1) **Boundary absorber** (`export_mode="boundary_absorber"`)
   - A smooth real-space sponge layer near domain edges.
   - Models leakage/radiation through boundaries.

2) **High-k radiator** (`export_mode="highk_radiator"`)
   - A k-space damping mask applied after the kinetic step.
   - Models energy/information exported via high-frequency radiation.

Both produce a per-step `tau_export` scalar measured as **continuous-norm mass removed** by the export operation only.
Anti-Governor uses `tau_export` to distinguish legitimate compression from illegitimate closure.
