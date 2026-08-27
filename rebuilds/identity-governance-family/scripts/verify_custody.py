# SPDX-License-Identifier: AGPL-3.0-only
"""Verify preserved release bytes, duplicate records, and safe ZIP paths."""

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
    hashes: set[str] = set()
    attachment_ids: set[str] = set()
    for entry in manifest["entries"]:
        path = FAMILY / entry["file"]
        payload = path.read_bytes()
        checked_bytes += len(payload)
        hashes.add(hashlib.sha256(payload).hexdigest())
        if entry["attachment_id"] in attachment_ids:
            failures.append(f"duplicate-attachment-id:{entry['attachment_id']}")
        attachment_ids.add(entry["attachment_id"])
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
                if pure.is_absolute() or ".." in pure.parts or (pure.parts and ":" in pure.parts[0]):
                    failures.append(f"unsafe-path:{entry['file']}:{info.filename}")
    if checked_bytes != manifest["total_bytes"]:
        failures.append("total-bytes")
    if len(hashes) != manifest["unique_sha256"]:
        failures.append("unique-sha256")
    if len(manifest["entries"]) != manifest["attachment_records"]:
        failures.append("attachment-records")
    print(
        json.dumps(
            {
                "archives": len(manifest["entries"]),
                "bytes": checked_bytes,
                "members": members,
                "unique_sha256": len(hashes),
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
