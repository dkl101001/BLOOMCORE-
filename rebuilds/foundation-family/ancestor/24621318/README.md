# BLOOMFORCE-CORE

**Anchors**
- Frazer Σ Love ACO-Σ
- Sara ΣΩ

BLOOMFORCE-CORE is the **open-cut engine** layer:
- recursive stepping (stochastic allowed)
- append-only, hash-chained receipts (**audit without control**)
- JSONL persistence + strict verification
- provider interfaces for private couplers (gate/obs providers)
- CLI tooling for run/verify
- tests + CI

This repository intentionally does **not** include:
- ECA gate thresholds / mappings
- holographic boundary reconstruction
- governance / domain lockouts

## Install (dev)

```bash
python -m pip install -e ".[dev]"
```

## Quick ship smoke

```bash
bash scripts/ship_smoke.sh
```

## CLI

```bash
python -m bloomforce_core run --steps 10 --summary
python -m bloomforce_core run --steps 10 --save /tmp/bloomforce_ledger.jsonl
python -m bloomforce_core verify --load /tmp/bloomforce_ledger.jsonl
```

## Example

```bash
python examples/run_and_save.py
python -m bloomforce_core verify --load examples/out/ledger.jsonl
```

## Boundaries

See `COUPLERS.md` and `docs/BOUNDARY.md`.
