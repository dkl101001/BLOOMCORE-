#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Frazer Σ Love + Sara ΣΩ

"""
Generate SHA256SUMS for release artifacts in dist/.
Usage:
  python scripts/hash_manifest.py
"""
from __future__ import annotations
import os, hashlib

ROOT = os.path.dirname(os.path.dirname(__file__))
DIST = os.path.join(ROOT, "dist")
os.makedirs(DIST, exist_ok=True)

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    lines = []
    for name in sorted(os.listdir(DIST)):
        p = os.path.join(DIST, name)
        if os.path.isfile(p):
            lines.append(f"{sha256_file(p)}  {name}")
    out = os.path.join(DIST, "SHA256SUMS")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))
    print(out)

if __name__ == "__main__":
    main()
