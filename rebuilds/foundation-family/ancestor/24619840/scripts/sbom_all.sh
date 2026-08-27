#!/usr/bin/env bash
set -euo pipefail

# Optional SBOM generator for both subprojects if cyclonedx-bom is installed.
# Usage: scripts/sbom_all.sh <output_dir>

OUTDIR="${1:-sbom}"
mkdir -p "$OUTDIR"

if ! python -c "import cyclonedx_bom" >/dev/null 2>&1; then
  echo "cyclonedx-bom not installed. Install with: pip install cyclonedx-bom" >&2
  exit 2
fi

( cd sentinel_lite_kernel && cyclonedx-py --format json --output "../$OUTDIR/kernel.sbom.cdx.json" )
( cd sentinel_executor_lite && cyclonedx-py --format json --output "../$OUTDIR/executor.sbom.cdx.json" )

echo "Wrote $OUTDIR/kernel.sbom.cdx.json"
echo "Wrote $OUTDIR/executor.sbom.cdx.json"
