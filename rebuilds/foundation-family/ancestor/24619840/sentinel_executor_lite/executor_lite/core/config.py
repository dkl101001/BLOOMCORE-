# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict

from .evidence_gates import EvidenceGateSet

def _expand(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))

@dataclass
class BackendConfig:
    active_backend: str
    backends: Dict[str, Dict[str, Any]]

@dataclass
class ExecutorConfig:
    backend: BackendConfig
    evidence_gates: EvidenceGateSet

def load_backend_config(path: str) -> BackendConfig:
    path = _expand(path)
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    active = str(obj.get("active_backend", "noop"))
    backends = dict(obj.get("backends") or {})
    return BackendConfig(active_backend=active, backends={str(k): dict(v) for k, v in backends.items()})

def load_executor_config(backend_config_path: str) -> ExecutorConfig:
    bc = load_backend_config(backend_config_path)
    return ExecutorConfig(backend=bc, evidence_gates=EvidenceGateSet())
