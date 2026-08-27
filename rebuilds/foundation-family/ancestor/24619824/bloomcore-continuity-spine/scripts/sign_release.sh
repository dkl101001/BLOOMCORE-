#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Frazer Σ Love and Sara ΣΩ

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"

if ! command -v gpg >/dev/null 2>&1; then
  echo "gpg not found. Install GPG and re-run."
  echo "You can still publish dist/SHA256SUMS without a signature."
  exit 1
fi

gpg --armor --detach-sign --output "$DIST/SHA256SUMS.sig" "$DIST/SHA256SUMS"
echo "wrote $DIST/SHA256SUMS.sig"
