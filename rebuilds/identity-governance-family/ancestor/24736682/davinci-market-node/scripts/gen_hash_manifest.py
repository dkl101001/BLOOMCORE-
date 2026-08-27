#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
from typing import Iterable

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "ENV",
    "env",
    "__pycache__",
    "build",
    "dist",
    ".pytest_cache",
}

EXCLUDE_FILES = {
    "HASHES.sha256",
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def iter_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if p.name in EXCLUDE_FILES:
            continue
        if str(rel).endswith(".pyc"):
            continue
        yield p

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="HASHES.sha256")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.out)

    rows = []
    for p in sorted(iter_files(root), key=lambda x: str(x)):
        rel = str(p.relative_to(root))
        rows.append(f"{sha256_file(p)}  {rel}")

    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} hashes -> {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
