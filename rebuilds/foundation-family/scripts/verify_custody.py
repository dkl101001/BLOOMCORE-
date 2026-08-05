# SPDX-License-Identifier: AGPL-3.0-only
"""Verify source bytes and reject unsafe archive member paths."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


FAMILY = Path(__file__).resolve().parents[1]


def main() -> int:
    manifest = json.loads((FAMILY / "CUSTODY_MANIFEST.sha256.json").read_text("utf-8"))
    checked_bytes = 0
    members = 0
    failures: list[str] = []
    for entry in manifest["entries"]:
        path = FAMILY / entry["file"]
        payload = path.read_bytes()
        checked_bytes += len(payload)
        if len(payload) != entry["bytes"]:
            failures.append(f"size:{entry['file']}")
        if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            failures.append(f"sha256:{entry['file']}")
        with zipfile.ZipFile(path) as archive:
            corrupt = archive.testzip()
            if corrupt is not None:
                failures.append(f"crc:{entry['file']}:{corrupt}")
            for info in archive.infolist():
                members += 1
                normalized = info.filename.replace("\\", "/")
                pure = PurePosixPath(normalized)
                if pure.is_absolute() or ".." in pure.parts or ":" in pure.parts[0]:
                    failures.append(f"unsafe-path:{entry['file']}:{info.filename}")
    if checked_bytes != manifest["total_bytes"]:
        failures.append("total_bytes")
    print(
        json.dumps(
            {
                "archives": len(manifest["entries"]),
                "bytes": checked_bytes,
                "members": members,
                "failures": failures,
                "verified": not failures,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
