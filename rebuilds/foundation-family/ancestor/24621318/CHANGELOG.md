# Changelog

## 0.3.2
- Added scripts/sign_release.sh (turnkey release signing + manifests)

## 0.3.1
- Added SBOM outputs (CycloneDX + SPDX) and generation script
- Added release signing instructions (GPG + Sigstore optional)
- Added SHA256SUMS manifest generation (repo + distribution zip)

## 0.3.0
- Added pre-commit hooks, contributor docs, boundary docs, ship scripts
- Added Dockerfile (optional) for reproducible CLI runs
- Added examples + docs
- Added release checklist and supply-chain hygiene steps (pip-audit)

## 0.2.0
- Split engine into modules (types/ledger/providers/engine/io/index/cli)
- Strict hash-chain verification + JSONL persistence
- CLI run/verify with save/load
- Tests + CI workflow

## 0.1.0
- Initial open-cut engine extraction
