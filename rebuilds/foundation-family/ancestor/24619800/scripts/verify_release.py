#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Frazer Σ Love + Sara ΣΩ

"""Release verifier (fail-fast).

Asserts:
  1) Required files exist (LICENSE, NOTICE, workflow, etc.)
  2) Authorship invariants are present: "Frazer Σ Love" and "Sara ΣΩ"

Designed to be domain-neutral: checks packaging, not domain semantics.

Run from repo root:
  python scripts/verify_release.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


INVARIANTS = ("Frazer Σ Love", "Sara ΣΩ")


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    message: str


def repo_root_from_script(script_file: Path) -> Path:
    # scripts/verify_release.py -> repo root
    return script_file.resolve().parent.parent


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def must_exist(root: Path, rel: str) -> CheckResult:
    p = root / rel
    if p.exists() and p.is_file():
        return CheckResult(True, f"OK: exists: {rel}")
    return CheckResult(False, f"MISSING: {rel}")


def must_contain_all(root: Path, rel: str, needles: Iterable[str]) -> CheckResult:
    p = root / rel
    if not p.exists():
        return CheckResult(False, f"MISSING (cannot check contents): {rel}")
    data = read_text(p)
    missing = [n for n in needles if n not in data]
    if missing:
        return CheckResult(False, f"INVARIANT MISSING in {rel}: {', '.join(missing)}")
    return CheckResult(True, f"OK: invariants present in {rel}")


def main() -> int:
    script_file = Path(__file__)
    root = repo_root_from_script(script_file)

    required_files = [
        "README.md",
        "LICENSE",
        "NOTICE",
        "pyproject.toml",
        ".github/workflows/ci.yml",
        # visible mirror for dotfolder-hostile unzip tools
        "github_workflows/ci.yml",
        "scripts/sign_release.sh",
        "scripts/hash_manifest.py",
        "scripts/sbom.py",
        "scripts/release.py",
        "scripts/verify_release.py",
    ]

    results: list[CheckResult] = [must_exist(root, rel) for rel in required_files]

    invariant_files = [
        "NOTICE",
        "README.md",
        "pyproject.toml",
        ".github/workflows/ci.yml",
        "github_workflows/ci.yml",
        "scripts/sign_release.sh",
        "scripts/verify_release.py",
    ]
    results.extend(must_contain_all(root, rel, INVARIANTS) for rel in invariant_files)

    ok = all(r.ok for r in results)
    for r in results:
        stream = sys.stdout if r.ok else sys.stderr
        stream.write(r.message + "\n")

    if ok:
        print("PASS: release packaging invariants satisfied.")
        return 0

    print("FAIL: release packaging invariants not satisfied.", file=sys.stderr)
    print("Tip: run `ls -a .github/workflows` to confirm dotfolders are present.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
