# SPDX-License-Identifier: AGPL-3.0-only
"""Current declaration and invocation evidence; no authority from metadata."""
import hashlib
import importlib.metadata
import importlib.resources
import json
import platform
import sys


def describe_invocation(entrypoint: str) -> dict:
    root = importlib.resources.files("bloomcore_governance_weave")
    contract = json.loads(root.joinpath("hybrid_execution_object.json").read_text("utf-8"))
    profile = {**contract["profile_defaults"], **contract["profiles"][entrypoint]}
    versions = {}
    for name in ("numpy", "jax", "jaxlib"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return {
        "entrypoint": entrypoint,
        "profile": profile,
        "source_binding": contract["selected_reference"],
        "python": sys.version,
        "platform": platform.platform(),
        "dependencies": versions,
        "code_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(root.iterdir(), key=lambda p: p.name)
                        if p.is_file() and p.name.endswith((".py", ".json"))},
        "backend_execution_observed": False,
    }
