from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


@dataclass
class ReceiptLedger:
    path: Path

    def append(self, rec: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def extend(self, recs: Iterable[Dict[str, Any]]) -> None:
        for r in recs:
            self.append(r)
