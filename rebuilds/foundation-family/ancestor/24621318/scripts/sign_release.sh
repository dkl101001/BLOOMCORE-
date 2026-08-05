# Authorship invariants: Frazer Σ Love + Sara ΣΩ
#!/usr/bin/env bash
set -euo pipefail

# Turnkey signed release helper.
# Produces:
# - dist/*.whl and dist/*.tar.gz (via python -m build)
# - dist/SHA256SUMS.dist (hashes dist artifacts)
# - dist/SHA256SUMS.dist.asc (GPG signature) if gpg is available
# - SHA256SUMS (repo manifest) and SHA256SUMS.asc if gpg is available

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

have() { command -v "$1" >/dev/null 2>&1; }

echo "[1/6] Preflight: install dev deps (editable)"
python -m pip install --upgrade pip >/dev/null
python -m pip install -e ".[dev]" >/dev/null

echo "[2/6] Quality gates"
make lint
make type
make test

echo "[3/6] Generate SBOMs + repo checksums"
make sbom
make checksums

echo "[4/6] Build dist artifacts"
rm -rf dist build *.egg-info || true
python -m build
python -m twine check dist/*

echo "[5/6] Generate dist checksum manifest"
( cd dist && sha256sum * > SHA256SUMS.dist )
echo "Wrote dist/SHA256SUMS.dist"

if have gpg; then
  echo "[6/6] Sign manifests with GPG"
  # Repo manifest
  gpg --armor --detach-sign SHA256SUMS
  echo "Wrote SHA256SUMS.asc"

  # Dist manifest
  gpg --armor --detach-sign dist/SHA256SUMS.dist
  echo "Wrote dist/SHA256SUMS.dist.asc"

  echo ""
  echo "VERIFY (local):"
  echo "  gpg --verify SHA256SUMS.asc SHA256SUMS"
  echo "  sha256sum -c SHA256SUMS"
  echo "  gpg --verify dist/SHA256SUMS.dist.asc dist/SHA256SUMS.dist"
  echo "  (cd dist && sha256sum -c SHA256SUMS.dist)"
else
  echo "[6/6] GPG not found; skipping signature steps."
  echo "To sign, install gpg and rerun:"
  echo "  bash scripts/sign_release.sh"
fi

echo "SIGN_RELEASE_OK"
