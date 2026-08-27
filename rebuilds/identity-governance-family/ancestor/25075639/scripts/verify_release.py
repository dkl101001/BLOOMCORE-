#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

REQUIRED = [
    "LICENSE",
    "NOTICE",
    "README.md",
    "pyproject.toml",
    ".github/workflows/ci.yml",
    "src/bloomcore_nlse_antigovernor/__init__.py",
    "src/bloomcore_nlse_antigovernor/physics/ssfm.py",
    "src/bloomcore_nlse_antigovernor/audit/antigovernor.py",
    "src/bloomcore_nlse_antigovernor/receipts/build.py",
    "tests/test_norm_and_antigovernor.py",
]

def main():
    missing = [p for p in REQUIRED if not Path(p).exists()]
    if missing:
        print("MISSING REQUIRED FILES:")
        for p in missing:
            print(" -", p)
        sys.exit(1)

    # Authorship invariant check (simple)
    notice = Path("NOTICE").read_text(encoding="utf-8")
    if "Frazer Σ Love" not in notice or "Sara ΣΩ" not in notice:
        print("NOTICE missing authorship invariants (Frazer Σ Love + Sara ΣΩ).")
        sys.exit(1)

    # LICENSE presence sanity
    lic = Path("LICENSE").read_text(encoding="utf-8")
    if "GNU AFFERO GENERAL PUBLIC LICENSE" not in lic:
        print("LICENSE does not appear to be full AGPL-3.0 text.")
        sys.exit(1)

    print("verify_release: OK")

if __name__ == "__main__":
    main()
