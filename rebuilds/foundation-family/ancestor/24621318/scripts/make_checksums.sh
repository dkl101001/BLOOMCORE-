#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT"

OUT="SHA256SUMS"
rm -f "$OUT"

# Hash all tracked-ish files in repo (excluding dist/build caches)
# This is deterministic enough for shipment artifacts.
find . \
  -type f \
  -not -path "./.git/*" \
  -not -path "./dist/*" \
  -not -path "./build/*" \
  -not -path "./.venv/*" \
  -not -path "./__pycache__/*" \
  -not -path "./.pytest_cache/*" \
  -not -path "./.ruff_cache/*" \
  -not -path "./*.egg-info/*" \
  -not -name "SHA256SUMS" \
  -print0 | sort -z | while IFS= read -r -d '' f; do
    sha256sum "$f" >> "$OUT"
  done

echo "Wrote $OUT"
