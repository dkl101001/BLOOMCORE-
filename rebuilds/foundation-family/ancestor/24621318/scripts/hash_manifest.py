#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Authorship invariants: Frazer Σ Love + Sara ΣΩ

import hashlib, os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    out = ROOT / "SHA256SUMS"
    lines = []
    for p in sorted(ROOT.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith(".git/"):
            continue
        if rel in ("SHA256SUMS",):
            continue
        # never hash dist outputs in tree (shouldn't exist pre-ship)
        if rel.startswith("dist/") or rel.startswith("build/"):
            continue
        lines.append(f"{sha256_file(p)}  {rel}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
