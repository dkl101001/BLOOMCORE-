# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from .policy import AllowlistPolicy

@dataclass
class KernelConfig:
    policy: AllowlistPolicy

def load_kernel_config(path: str) -> KernelConfig:
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return KernelConfig(
        policy=AllowlistPolicy(
            policy_id=str(obj.get("policy_id", "ALLOWLIST.v1")),
            allow_scopes=list(obj.get("allow_scopes", ["local"])),
            allow_actions=list(obj.get("allow_actions", ["write_file"])),
            deny_actions=list(obj.get("deny_actions", [])),
            require_evidence_for_actions=list(obj.get("require_evidence_for_actions", [])),
            max_params_bytes=int(obj.get("max_params_bytes", 65536)),
        )
    )
