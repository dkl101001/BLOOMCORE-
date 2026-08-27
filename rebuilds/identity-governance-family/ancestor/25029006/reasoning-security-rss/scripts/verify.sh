#!/usr/bin/env bash
set -euo pipefail
HASHFILE="${1:-hashes.txt}"
if [ ! -f "$HASHFILE" ]; then
  echo "Missing $HASHFILE" >&2
  exit 1
fi
python - <<'PY'
import sys, hashlib
from pathlib import Path
hashfile = Path(sys.argv[1])
ok = True
for line in hashfile.read_text(encoding="utf-8").splitlines():
    if not line.strip(): 
        continue
    h, path = line.split("  ", 1)
    p = Path(path)
    if not p.exists():
        print("MISSING", path)
        ok = False
        continue
    hh = hashlib.sha256(p.read_bytes()).hexdigest()
    if hh != h:
        print("MISMATCH", path)
        ok = False
print("OK" if ok else "FAIL")
sys.exit(0 if ok else 2)
PY "$HASHFILE"
