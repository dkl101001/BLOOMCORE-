#!/usr/bin/env bash
set -euo pipefail

# Optional SBOM generator (CycloneDX) if cyclonedx-bom is installed.
# Usage: scripts/sbom.sh <output.json>

OUT="${1:-sbom.cdx.json}"

if ! python -c "import cyclonedx_bom" >/dev/null 2>&1; then
  echo "cyclonedx-bom not installed. Install with: pip install cyclonedx-bom" >&2
  exit 2
fi

cyclonedx-py --format json --output "$OUT"
echo "Wrote $OUT"
