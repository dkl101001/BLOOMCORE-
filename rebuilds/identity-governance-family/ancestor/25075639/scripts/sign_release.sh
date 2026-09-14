#!/usr/bin/env bash
set -euo pipefail

# Optional signing helper.
# If gpg is available and a key is configured, sign SHA256SUMS -> SHA256SUMS.asc
# This script does NOT enforce determinism in dynamics; it signs the deterministic artifact outputs.

if ! command -v gpg >/dev/null 2>&1; then
  echo "gpg not found; skipping signing."
  exit 0
fi

if [[ ! -f SHA256SUMS ]]; then
  echo "SHA256SUMS not found. Run: python scripts/hash_manifest.py"
  exit 1
fi

gpg --armor --detach-sign --output SHA256SUMS.asc SHA256SUMS
echo "Wrote SHA256SUMS.asc"
