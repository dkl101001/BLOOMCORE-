#!/usr/bin/env bash
set -euo pipefail
FILE="${1:-hashes.txt}"
# Optional: requires gpg configured
if command -v gpg >/dev/null 2>&1; then
  gpg --armor --detach-sign "$FILE"
  echo "Signed $FILE -> $FILE.asc"
else
  echo "gpg not found; skipping signing"
fi
