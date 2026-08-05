# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

from typing import Any, Dict

from executor_lite.backends.noop import NoopBackend
from executor_lite.backends.process import ProcessBackend
from executor_lite.backends.file_patch import FilePatchBackend
from executor_lite.backends.base import Backend

def load_backend(active_backend: str, backends_cfg: Dict[str, Dict[str, Any]]) -> Backend:
    name = str(active_backend)
    cfg = dict(backends_cfg.get(name) or {})

    if name == "noop":
        return NoopBackend(cfg=cfg)
    if name == "process":
        return ProcessBackend(
            allow_pids=list(cfg.get("allow_pids") or []),
            allow_cmd_regex=list(cfg.get("allow_cmd_regex") or []),
            signal_map=dict(cfg.get("signal_map") or {}),
        )
    if name == "file_patch":
        return FilePatchBackend(
            artifacts_dir=str(cfg.get("artifacts_dir", "~/.sentinel/artifacts")),
            install_dir=str(cfg.get("install_dir", "~/.sentinel/installed_artifacts")),
        )
    raise ValueError(f"unknown backend: {name}")
