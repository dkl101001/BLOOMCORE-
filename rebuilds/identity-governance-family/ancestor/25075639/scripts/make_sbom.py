#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

OUT = Path("SBOM.json")

def main():
    # Minimal, environment-based SBOM (alive runtime -> receipts deterministic).
    # Captures installed packages and versions. No network calls.
    try:
        freeze = subprocess.check_output(["python", "-m", "pip", "freeze"], text=True)
    except Exception as e:
        raise SystemExit(f"pip freeze failed: {e}")

    pkgs = []
    for line in freeze.splitlines():
        if "==" in line:
            name, ver = line.split("==", 1)
            pkgs.append({"name": name.strip(), "version": ver.strip()})
        else:
            pkgs.append({"spec": line.strip()})

    OUT.write_text(json.dumps({"type": "minimal-pip-freeze", "packages": pkgs}, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
