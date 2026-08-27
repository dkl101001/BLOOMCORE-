# Frazer Σ Love + Sara ΣΩ
#!/usr/bin/env bash
set -euo pipefail

# signs dist/SHA256SUMS using gpg (recommended)
# requires gpg installed + a signing key configured locally.
#
# Usage:
#   bash scripts/sign_release.sh
#
# Output:
#   dist/SHA256SUMS.sig

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"

if ! command -v gpg >/dev/null 2>&1; then
  echo "gpg not found. Install GPG and re-run."
  echo "You can still publish dist/SHA256SUMS without a signature."
  exit 1
fi

gpg --armor --detach-sign --output "$DIST/SHA256SUMS.sig" "$DIST/SHA256SUMS"
echo "wrote $DIST/SHA256SUMS.sig"
