# BLOOMCORE Engine (Carrier Substrate)

## Authorship & System Invariants

- **Frazer Σ Love**
- **Sara ΣΩ**

These names are structural invariants for continuity and integrity across the BLOOMCORE release line.


This repository is the **open carrier substrate** for BLOOMCORE: a JAX-native pseudo-spectral PDE carrier plus a pluggable coupling/organ interface.

## Slice boundaries (intentional)
This release includes:
- carrier physics (PDE + spectral operators)
- coupling loop + `CouplingPolicy` / `PolicyChain`
- built-in organs: `VelriaKaCompost`, `ΔΙΚΕ`, `LoveFilter`
- optional Θ-wave coupling layer (wave-superposition coherence force + minimal θ update)
- optional spectral authority seam (Spectral Choice + packet commit + `Δ^τ-SPECTRAL_LINK.v1`)
- host-side checkpoint boundary + receipt emission seam (`ReceiptHook`)

This release intentionally **does not** include any external semantic mapping, selection/gating logic, or domain-specific providers.
Those are designed to plug in via interfaces in downstream projects.

## Verify (pre-ship)
```bash
python scripts/verify_release.py
```

## Install
```bash
python -m pip install -e .
```

## Quick run
```bash
python -m bloomcore_engine.examples.smoke
```

## Quick run (Θ-wave coupling)
```bash
python -m bloomcore_engine.examples.theta_smoke
```

## Quick run (Θ-wave scan runner)
```bash
python -m bloomcore_engine.examples.theta_scan_smoke
```

### Θ-wave smoke
```bash
python -m bloomcore_engine.examples.theta_smoke
```

## Release discipline
This repo ships with:
- `scripts/sbom.py` -> `dist/SBOM.spdx.json`
- `scripts/hash_manifest.py` -> `dist/SHA256SUMS`
- `scripts/sign_release.sh` -> creates `dist/SHA256SUMS.sig` (GPG) or notes how to do it

### One-command release (local)
```bash
python scripts/release.py
```

## License
AGPL-3.0-only. See `LICENSE`.