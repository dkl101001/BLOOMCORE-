#!/usr/bin/env python3
"""
verify_release.py — pre-shipment verifier for BLOOMCORE Engine.

Authorship invariants (hard):
- Frazer Σ Love
- Sara ΣΩ

This script fails fast if required files are missing, invariants drift, forbidden artifacts
are present, or key import smoke tests fail.

Frazer Σ Love + Sara ΣΩ
"""
from __future__ import annotations

import os
import re
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    "NOTICE",
    "LICENSE",
    "pyproject.toml",
    ".github/workflows/ci.yml",
    "github_workflows/ci.yml",
    "scripts/verify_release.py",
    "scripts/hash_manifest.py",
    "scripts/sbom.py",
    "scripts/sign_release.sh",
    "scripts/release.py",
    "src/bloomcore_engine/__init__.py",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"__pycache__"),
    re.compile(r"\.pyc$"),
    re.compile(r"\.egg-info(/|$)"),
    re.compile(r"(^|/)dist(/|$)"),   # dist should be generated, not shipped
    re.compile(r"(^|/)build(/|$)"),
]

INVARIANTS = ["Frazer Σ Love", "Sara ΣΩ"]

INVARIANT_FILES = [
    "README.md",
    "NOTICE",
    "pyproject.toml",
    ".github/workflows/ci.yml",
    "scripts/sign_release.sh",
    "scripts/verify_release.py",
]

def fail(msg: str) -> None:
    print("FAIL:", msg, file=sys.stderr)
    sys.exit(1)

def ok(msg: str) -> None:
    print("OK:", msg)

def read_text(rel: str) -> str:
    p = ROOT / rel
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        fail(f"missing file: {rel}")

def main() -> None:
    os.chdir(ROOT)

    # Required paths
    missing = [p for p in REQUIRED_PATHS if not (ROOT / p).exists()]
    if missing:
        fail("missing required paths:\n  - " + "\n  - ".join(missing))
    ok("required paths present")

    # Forbidden artifacts scan
    bad = []
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT).as_posix()
        for pat in FORBIDDEN_PATTERNS:
            if pat.search(rel):
                bad.append(rel)
                break
    if bad:
        # show unique + sorted
        bad = sorted(set(bad))
        fail("forbidden artifacts present:\n  - " + "\n  - ".join(bad[:200]) + ("" if len(bad) <= 200 else f"\n  ... ({len(bad)} total)"))
    ok("no forbidden artifacts found")

    # License sanity: must look like AGPL full text
    lic = read_text("LICENSE").splitlines()
    if not lic:
        fail("LICENSE is empty")
    if "GNU AFFERO GENERAL PUBLIC LICENSE" not in lic[0]:
        fail("LICENSE does not appear to be full AGPL-3.0 text (missing header)")
    ok("LICENSE header looks like AGPL-3.0")

    # Invariants present in key files
    for rel in INVARIANT_FILES:
        txt = read_text(rel)
        for inv in INVARIANTS:
            if inv not in txt:
                fail(f'invariant "{inv}" missing from {rel}')
    ok("authorship invariants present in key files")

    # Compile check (without leaving artifacts)
    ok("running compile check")
    subprocess.check_call([sys.executable, "-m", "compileall", "-q", "src"], stdout=subprocess.DEVNULL)
    # Clean any caches created during verification
    for p in (ROOT / "src").rglob("__pycache__"):
        import shutil
        shutil.rmtree(p, ignore_errors=True)
    for p in (ROOT / "src").rglob("*.pyc"):
        try:
            p.unlink()
        except OSError:
            pass
    ok("compile check passed")

    ok("running import smoke test")
    # Ensure src/ is importable even before editable install
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + (os.pathsep + env.get("PYTHONPATH","") if env.get("PYTHONPATH") else "")
    subprocess.check_call([sys.executable, "-c", "import bloomcore_engine"], stdout=subprocess.DEVNULL, env=env)
    ok("import bloomcore_engine passed")

    print("PASS: release schema verified")

if __name__ == "__main__":
    main()
