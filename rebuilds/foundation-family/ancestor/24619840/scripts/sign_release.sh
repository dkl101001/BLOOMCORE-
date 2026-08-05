#!/usr/bin/env bash
set -euo pipefail

# Usage: scripts/sign_release.sh <artifact.zip>
# Produces: <artifact.zip>.sha256 and optional minisign signature if installed.

ZIP="${1:?zip path required}"

sha256sum "$ZIP" > "${ZIP}.sha256"

if command -v minisign >/dev/null 2>&1; then
  if [[ -z "${MINISIGN_SECRET_KEY:-}" ]]; then
    echo "minisign present but MINISIGN_SECRET_KEY not set; skipping signature." >&2
    exit 0
  fi
  minisign -S -s "$MINISIGN_SECRET_KEY" -m "$ZIP"
  echo "Wrote ${ZIP}.minisig"
else
  echo "minisign not installed; wrote ${ZIP}.sha256 only."
fi
