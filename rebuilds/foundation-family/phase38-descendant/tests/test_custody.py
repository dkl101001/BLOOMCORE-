# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import json
from pathlib import Path


FAMILY = Path(__file__).resolve().parents[2]


def test_all_preserved_source_bytes_match_manifest():
    manifest = json.loads((FAMILY / "CUSTODY_MANIFEST.sha256.json").read_text("utf-8"))
    total = 0
    for entry in manifest["entries"]:
        payload = (FAMILY / entry["file"]).read_bytes()
        total += len(payload)
        assert len(payload) == entry["bytes"]
        assert hashlib.sha256(payload).hexdigest() == entry["sha256"]
    assert total == manifest["total_bytes"] == 272681
