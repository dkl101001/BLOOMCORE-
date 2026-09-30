# SPDX-License-Identifier: AGPL-3.0-only
"""Verify exact release custody and app-source equality before clean tests."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TAG = "ti-agi83-plus-v0.2.0"
ARCHIVE_SHA = "96fb198f3f5fad321fe5d5da09d0e0bf1986d4bf095b5a5d5753595b4573897a"


def verify(destination=None):
    archive = HERE / (TAG + ".zip")
    if hashlib.sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA:
        raise ValueError("Release archive digest mismatch")
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("Archive CRC failure")
        for name in z.namelist():
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or path.parts[0] != TAG:
                raise ValueError("Unexpected archive path")
        manifest = json.loads(z.read(TAG + "/MANIFEST.sha256.json"))
        expected = {TAG + "/" + k for k in manifest["files"]} | {TAG + "/MANIFEST.sha256.json"}
        if set(z.namelist()) != expected or len(z.namelist()) != len(expected):
            raise ValueError("Archive member set mismatch")
        for name, digest in manifest["files"].items():
            if hashlib.sha256(z.read(TAG + "/" + name)).hexdigest() != digest:
                raise ValueError("Manifest mismatch: " + name)
            if hashlib.sha256((ROOT / "demos/ti-agi83-plus" / name).read_bytes()).hexdigest() != digest:
                raise ValueError("Published app source differs from package: " + name)
        if destination is not None:
            z.extractall(destination)
    return {"status": "PASS", "archiveSha256": ARCHIVE_SHA, "hashedFiles": len(manifest["files"])}


if __name__ == "__main__":
    print(json.dumps(verify(Path(sys.argv[1]) if len(sys.argv) > 1 else None)))
