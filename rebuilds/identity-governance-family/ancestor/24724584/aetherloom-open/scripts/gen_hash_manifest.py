#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
from typing import Iterable

DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "venv",
    "ENV",
    "env",
    "__pycache__",
    "build",
    "dist",
    "*.egg-info",
}

DEFAULT_EXCLUDE_FILES = {
    "HASHES.sha256",
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def is_excluded(rel: str) -> bool:
    parts = rel.split(os.sep)
    if any(p in DEFAULT_EXCLUDES for p in parts):
        return True
    return False

def iter_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(root))
            if is_excluded(rel):
                continue
            if p.name in DEFAULT_EXCLUDE_FILES:
                continue
            if rel.startswith("dist/") or rel.startswith("build/"):
                continue
            yield p

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repo root to hash")
    ap.add_argument("--out", default="HASHES.sha256", help="Output manifest path")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.out)

    rows = []
    for p in sorted(iter_files(root), key=lambda x: str(x)):
        rel = str(p.relative_to(root))
        digest = sha256_file(p)
        rows.append(f"{digest}  {rel}")

    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} hashes -> {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
