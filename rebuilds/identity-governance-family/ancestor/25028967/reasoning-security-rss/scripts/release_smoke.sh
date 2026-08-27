#!/usr/bin/env bash
set -euo pipefail
python -m pip install -U pip
pip install -e .[dev]
rss validate "examples/traces/*.jsonl"
rss score "examples/traces/*.jsonl" --out report.json
rss summarize --report report.json
echo "Smoke OK"
