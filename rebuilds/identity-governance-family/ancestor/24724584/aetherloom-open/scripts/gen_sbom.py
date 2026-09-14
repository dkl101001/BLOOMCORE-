#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

try:
    from importlib.metadata import metadata, requires
except Exception:
    print("importlib.metadata unavailable", file=sys.stderr)
    raise

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="aetherloom-open", help="Project name (distribution)")
    ap.add_argument("--out", default="SBOM.aetherloom-open.spdxish.json", help="Output JSON path")
    args = ap.parse_args()

    dist = args.project

    md = metadata(dist)
    reqs = requires(dist) or []

    doc = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"SBOM for {dist}",
        "documentNamespace": f"urn:uuid:{dist}-{datetime.now(timezone.utc).isoformat()}",
        "creationInfo": {
            "created": datetime.now(timezone.utc).isoformat(),
            "creators": [
                "Person: Frazer Σ Love ACO-Σ",
                "Person: Sara ΣΩ",
                "Tool: scripts/gen_sbom.py",
            ],
        },
        "packages": [
            {
                "name": md.get("Name", dist),
                "SPDXID": "SPDXRef-Package-AETHERLOOM",
                "versionInfo": md.get("Version", "unknown"),
                "downloadLocation": "NOASSERTION",
                "licenseDeclared": md.get("License", "AGPL-3.0-only") or "AGPL-3.0-only",
                "supplier": "NOASSERTION",
                "originator": "NOASSERTION",
                "summary": md.get("Summary", ""),
                "homepage": md.get("Home-page", ""),
            }
        ],
        "relationships": [],
        "externalRefs": [],
        "annotations": [],
        "dependencies": sorted([r.strip() for r in reqs if r.strip()]),
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote SBOM -> {args.out} (deps={len(doc['dependencies'])})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
