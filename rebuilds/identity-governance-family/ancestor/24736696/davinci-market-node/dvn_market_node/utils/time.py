from __future__ import annotations

from datetime import datetime


def ny_iso_now() -> str:
    # caller supplies NY-local timestamps if desired; this is a simple fallback
    return datetime.now().astimezone().isoformat()
