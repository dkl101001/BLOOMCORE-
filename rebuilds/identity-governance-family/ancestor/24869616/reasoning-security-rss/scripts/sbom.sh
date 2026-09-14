#!/usr/bin/env bash
set -euo pipefail
# Minimal SBOM: dependency freeze snapshot (sufficient for lightweight auditing)
python -m pip freeze > sbom.txt
echo "Wrote sbom.txt"
