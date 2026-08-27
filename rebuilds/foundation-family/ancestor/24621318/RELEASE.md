# Release Guide — BLOOMFORCE-CORE

## Preflight

```bash
python -m pip install -e ".[dev]"
make lint
make type
make test
make smoke
bash scripts/ship_smoke.sh
```

## Build artifacts

```bash
make build
ls -lah dist/
python -m twine check dist/*
```

## Supply-chain check (optional)

```bash
python -m pip_audit -r <(python -m pip freeze) || true
```

## Tagging

Use `vX.Y.Z` tags aligned to `pyproject.toml`.


## Signed releases

See `docs/SIGNED_RELEASE.md` for SBOM + checksums + signing steps.
