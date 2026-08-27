#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
make lint
make type
make test
make build
python -m twine check dist/*
echo "SHIP_BUILD_OK"
