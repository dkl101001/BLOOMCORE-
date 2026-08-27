#!/usr/bin/env bash
set -euo pipefail
rss validate "examples/traces/*.jsonl"
rss score "examples/traces/*.jsonl" --out report.json
rss summarize --report report.json
