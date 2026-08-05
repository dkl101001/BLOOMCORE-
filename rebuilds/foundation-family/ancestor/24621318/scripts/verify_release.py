#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Authorship invariants: Frazer Σ Love + Sara ΣΩ

import os, sys, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    "NOTICE",
    "LICENSE",
    "pyproject.toml",
    ".github/workflows/ci.yml",
    "github_workflows/ci.yml",
    "scripts/verify_release.py",
    "scripts/sign_release.sh",
]

FORBIDDEN_SUBSTRINGS = ["__pycache__", ".pyc", ".pyo", ".egg-info", "dist/", "build/"]

INVARIANTS = ["Frazer Σ Love", "Sara ΣΩ"]

INVARIANT_FILES = [
    "README.md",
    "NOTICE",
    "pyproject.toml",
    ".github/workflows/ci.yml",
    "github_workflows/ci.yml",
    "scripts/sign_release.sh",
    "scripts/verify_release.py",
]

def die(msg: str, code: int = 2):
    print(f"[FAIL] {msg}")
    sys.exit(code)

def ok(msg: str):
    print(f"[OK] {msg}")

def read_text(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace")

def main():
    os.chdir(ROOT)

    # required paths
    missing = [p for p in REQUIRED_PATHS if not (ROOT / p).exists()]
    if missing:
        die("Missing required paths: " + ", ".join(missing))

    # license header check
    lic_head = (ROOT / "LICENSE").read_text(encoding="utf-8", errors="replace").splitlines()[:5]
    if not any("GNU AFFERO GENERAL PUBLIC LICENSE" in ln for ln in lic_head):
        die("LICENSE does not look like full AGPL-3.0 text (missing AGPL header in first lines).")
    ok("LICENSE header looks like AGPL.")

    # invariants
    for rel in INVARIANT_FILES:
        txt = read_text(rel)
        for inv in INVARIANTS:
            if inv not in txt:
                die(f'Invariant "{inv}" missing from {rel}')
    ok("Authorship invariants present where required.")

    # forbidden artifacts scan
    bad = []
    for p in ROOT.rglob("*"):
        rel = p.as_posix().replace(str(ROOT.as_posix())+"/","")
        if p.is_dir():
            continue
        for s in FORBIDDEN_SUBSTRINGS:
            if s in rel:
                bad.append(rel)
                break
    if bad:
        die("Forbidden artifacts present: " + ", ".join(sorted(set(bad))[:50]))
    ok("No forbidden artifacts detected.")

    # compile + import smoke (best effort)
    try:
        subprocess.check_call([sys.executable, "-m", "compileall", "-q", "src"])
        ok("compileall OK")
    except Exception as e:
        die(f"compileall failed: {e}")

    pkg = None
    # attempt import module name from src
    src = ROOT / "src"
    if src.exists():
        pkgs = [p.name for p in src.iterdir() if p.is_dir() and (p/"__init__.py").exists()]
        if pkgs:
            pkg = pkgs[0]
    if not pkg:
        die("Could not detect package under src/ for import smoke test.")
    try:
        subprocess.check_call([sys.executable, "-c", f"import {pkg}"])
        ok(f"import {pkg} OK")
    except Exception as e:
        die(f"import smoke test failed for {pkg}: {e}")

    print("[PASS] Release schema verified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
