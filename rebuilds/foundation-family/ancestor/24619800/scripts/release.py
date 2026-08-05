#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Frazer Σ Love and Sara ΣΩ

"""
Local release helper:
- builds SBOM
- zips source tree into dist/
- writes SHA256SUMS for dist/
"""
from __future__ import annotations
import os, zipfile, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(__file__))
DIST = os.path.join(ROOT, "dist")
os.makedirs(DIST, exist_ok=True)

def run(cmd):
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)

def zip_repo(out_name: str) -> str:
    out_path = os.path.join(DIST, out_name)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(ROOT):
            if os.path.abspath(root).startswith(os.path.abspath(DIST)):
                continue
            for fn in files:
                if fn.endswith(".pyc"):
                    continue
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, ROOT)
                z.write(p, rel)
    return out_path

def main():
    run([sys.executable, "scripts/sbom.py"])
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    zip_repo(f"bloomcore-continuity-spine-src-{ts}.zip")
    run([sys.executable, "scripts/hash_manifest.py"])
    print("ok")

if __name__ == "__main__":
    main()
