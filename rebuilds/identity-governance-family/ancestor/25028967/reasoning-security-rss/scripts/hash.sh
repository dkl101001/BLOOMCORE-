#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-hashes.txt}"
export OUT="$OUT"
# Hash repository files (excluding venv, git, caches)
python - <<'PY'
import os, hashlib
from pathlib import Path
root = Path(".")
ignore = {".git", ".venv", "venv", "__pycache__", "dist", "build", ".pytest_cache"}
paths = []
for p in root.rglob("*"):
    if p.is_dir(): 
        continue
    parts = set(p.parts)
    if parts & ignore:
        continue
    if p.name in {"hashes.txt"}:
        continue
    paths.append(p)
paths.sort()
with open(os.environ.get("OUT","hashes.txt"), "w", encoding="utf-8") as f:
    for p in paths:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        f.write(f"{h}  {p.as_posix()}\n")
PY
echo "Wrote $OUT"
