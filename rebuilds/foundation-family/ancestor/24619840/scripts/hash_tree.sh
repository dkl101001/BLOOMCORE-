#!/usr/bin/env bash
set -euo pipefail

# Usage: scripts/hash_tree.sh <path>
# Writes SHA256SUMS for all files under <path> (excluding .git, __pycache__, .venv, dist, build).

ROOT="${1:-.}"
OUT="${2:-SHA256SUMS}"

cd "$ROOT"

# Build file list deterministically
FILES=$(find . -type f   -not -path './.git/*'   -not -path './.venv/*'   -not -path './**/__pycache__/*'   -not -path './**/*.pyc'   -not -path './**/*.pyo'   -not -path './**/*.pyd'   -not -path './**/.pytest_cache/*'   -not -path './**/dist/*'   -not -path './**/build/*'   | LC_ALL=C sort)

: > "$OUT"
while IFS= read -r f; do
  sha256sum "$f" >> "$OUT"
done <<< "$FILES"

echo "Wrote $OUT"
