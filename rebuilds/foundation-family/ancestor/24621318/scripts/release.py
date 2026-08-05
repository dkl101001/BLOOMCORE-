#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Authorship invariants: Frazer Σ Love + Sara ΣΩ
"""Release builder for BLOOMFORCE-CORE.

Pre-ship gate:
- Runs scripts/verify_release.py and fails fast if the repo violates the
  AGPL GitHub-ready shipment schema.

Outputs (created under dist/):
- dist/bloomforce-core-src-<UTCSTAMP>.zip   (source archive, clean)
- dist/SBOM.cdx.json                        (copied from sbom/)
- dist/SBOM.spdx.json                       (copied from sbom/)
- dist/SHA256SUMS                           (copied from root SHA256SUMS)

This script is intentionally conservative and domain-neutral.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DIST = ROOT / "dist"
SBOM_DIR = ROOT / "sbom"

EXCLUDE_PREFIXES = (
    ".git/",
    ".venv/",
    "venv/",
    "__pycache__/",
    "dist/",
    "build/",
)

EXCLUDE_SUFFIXES = (
    ".pyc",
)

def run(cmd: list[str]) -> None:
    subprocess.check_call(cmd, cwd=str(ROOT))

def utc_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S", time.gmtime())

def should_include(rel: str) -> bool:
    # normalize to forward slashes
    rel = rel.replace(os.sep, "/")
    for p in EXCLUDE_PREFIXES:
        if rel.startswith(p):
            return False
    for s in EXCLUDE_SUFFIXES:
        if rel.endswith(s):
            return False
    # exclude egg-info anywhere
    if ".egg-info/" in rel:
        return False
    return True

def build_source_zip(out_path: pathlib.Path) -> None:
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in ROOT.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(ROOT).as_posix()
            if not should_include(rel):
                continue
            z.write(p, arcname=rel)

def main() -> int:
    # 1) Pre-ship gate: fail fast
    run([sys.executable, str(SCRIPTS / "verify_release.py")])

    # 2) Ensure dist/ is clean
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    # 3) Generate SBOMs (writes into sbom/)
    run([sys.executable, str(SCRIPTS / "sbom_gen.py")])

    # 4) Update SHA256SUMS at repo root (excluding dist/)
    run([sys.executable, str(SCRIPTS / "hash_manifest.py")])

    # 5) Build source zip
    src_zip = DIST / f"bloomforce-core-src-{utc_stamp()}.zip"
    build_source_zip(src_zip)

    # 6) Copy SBOMs + SHA256SUMS into dist
    if (SBOM_DIR / "sbom.cdx.json").exists():
        shutil.copy2(SBOM_DIR / "sbom.cdx.json", DIST / "SBOM.cdx.json")
    if (SBOM_DIR / "sbom.spdx.json").exists():
        shutil.copy2(SBOM_DIR / "sbom.spdx.json", DIST / "SBOM.spdx.json")
    if (ROOT / "SHA256SUMS").exists():
        shutil.copy2(ROOT / "SHA256SUMS", DIST / "SHA256SUMS")

    print(f"Wrote: {src_zip.relative_to(ROOT)}")
    print("Wrote: dist/SBOM.cdx.json (if present)")
    print("Wrote: dist/SBOM.spdx.json (if present)")
    print("Wrote: dist/SHA256SUMS (if present)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
