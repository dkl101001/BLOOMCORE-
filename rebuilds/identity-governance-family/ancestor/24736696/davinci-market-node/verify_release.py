#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def parse_manifest(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Bad manifest line: {line!r}")
        digest = parts[0]
        rel = " ".join(parts[1:])
        rows.append((digest, rel))
    return rows

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hashes", default="HASHES.sha256")
    ap.add_argument("--root", default=".")
    ap.add_argument("--sbom", default=None)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    manifest_path = Path(args.hashes)

    if not manifest_path.exists():
        raise SystemExit(f"Missing manifest: {manifest_path}")

    manifest = parse_manifest(manifest_path.read_text(encoding="utf-8"))
    if not manifest:
        raise SystemExit("Manifest empty")

    failures = []
    for expected, rel in manifest:
        p = root / rel
        if not p.exists():
            failures.append(f"MISSING {rel}")
            continue
        got = sha256_file(p)
        if got.lower() != expected.lower():
            failures.append(f"BADHASH {rel} expected={expected} got={got}")

    if args.sbom:
        sbom_path = Path(args.sbom)
        if not sbom_path.exists():
            failures.append(f"MISSING_SBOM {sbom_path}")
        else:
            try:
                doc = json.loads(sbom_path.read_text(encoding="utf-8"))
                if not isinstance(doc, dict):
                    failures.append("SBOM_NOT_OBJECT")
                else:
                    if "spdxVersion" not in doc:
                        failures.append("SBOM_MISSING_spdxVersion")
                    if "packages" not in doc:
                        failures.append("SBOM_MISSING_packages")
            except Exception as e:
                failures.append(f"SBOM_PARSE_ERROR {e!r}")

    if failures:
        print("VERIFY FAILED")
        for f in failures:
            print(" -", f)
        return 2

    print(f"VERIFY OK ({len(manifest)} files)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
