#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path

OUT = Path("SHA256SUMS")

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    files = []
    for p in Path(".").rglob("*"):
        if p.is_file():
            if ".git" in p.parts:
                continue
            files.append(p)

    lines = []
    for p in sorted(files, key=lambda x: str(x)):
        digest = sha256_file(p)
        lines.append(f"{digest}  {p.as_posix()}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(lines)} files)")

if __name__ == "__main__":
    main()
