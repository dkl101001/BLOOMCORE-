#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Frazer Σ Love + Sara ΣΩ

"""
Generate a minimal SPDX JSON SBOM for this repo without external tools.

This is a pragmatic OSS-friendly SBOM that lists:
- the project package itself
- runtime dependencies (declared + best-effort import versions if installed)

Usage:
  python scripts/sbom.py
"""
from __future__ import annotations
import json, os, sys, hashlib, datetime
import importlib.metadata as im

ROOT = os.path.dirname(os.path.dirname(__file__))
DIST = os.path.join(ROOT, "dist")
os.makedirs(DIST, exist_ok=True)

PROJECT_NAME = "bloomcore-engine"
PROJECT_VERSION = "0.1.0"
DEPENDENCIES = ["jax", "jaxlib", "numpy"]

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def pkg_version(name: str) -> str | None:
    try:
        return im.version(name)
    except Exception:
        return None

def main() -> None:
    created = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    packages = []
    packages.append({
        "SPDXID": "SPDXRef-Package-" + PROJECT_NAME,
        "name": PROJECT_NAME,
        "versionInfo": PROJECT_VERSION,
        "downloadLocation": "NOASSERTION",
        "filesAnalyzed": False,
        "licenseConcluded": "AGPL-3.0-only",
        "licenseDeclared": "AGPL-3.0-only",
        "supplier": "Organization: Frazer Σ Love ACO-Σ and Sara ΣΩ",
    })

    for dep in DEPENDENCIES:
        v = pkg_version(dep)
        packages.append({
            "SPDXID": "SPDXRef-Package-" + dep,
            "name": dep,
            "versionInfo": v or "UNKNOWN",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "supplier": "NOASSERTION",
        })

    doc = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": PROJECT_NAME + "-SBOM",
        "documentNamespace": "urn:spdx:" + PROJECT_NAME + ":" + PROJECT_VERSION + ":" + created,
        "creationInfo": {
            "created": created,
            "creators": ["Tool: scripts/sbom.py", "Organization: Frazer Σ Love ACO-Σ and Sara ΣΩ"],
        },
        "packages": packages,
        "relationships": [
            {"spdxElementId": "SPDXRef-DOCUMENT", "relationshipType": "DESCRIBES", "relatedSpdxElement": "SPDXRef-Package-" + PROJECT_NAME},
        ] + [
            {"spdxElementId": "SPDXRef-Package-" + PROJECT_NAME, "relationshipType": "DEPENDS_ON", "relatedSpdxElement": "SPDXRef-Package-" + d}
            for d in DEPENDENCIES
        ],
    }

    out = os.path.join(DIST, "SBOM.spdx.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(out)

if __name__ == "__main__":
    main()
