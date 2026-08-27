#!/usr/bin/env bash
set -euo pipefail

python -m pip --version >/dev/null

python -m bloomforce_core run --steps 3 --summary
python -m bloomforce_core run --steps 5 --save /tmp/bloomforce_ledger.jsonl
python -m bloomforce_core verify --load /tmp/bloomforce_ledger.jsonl
echo "SHIP_SMOKE_OK"
