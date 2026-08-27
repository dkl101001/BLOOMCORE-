#!/usr/bin/env python3
"""world_engine.mirrorseed_cycle

MIRRORSEED.CYCLE.vΩ — SOUL-SAFE contradiction cycle (standalone module)

- record_fracture(): append verbatim fracture phrases into a JSONL registry.
- run_cycle_once(): loads fractures, emits a cycle receipt via BLOOMCORE, clears registry.

Scheduling is external (cron/systemd). This module runs *one* cycle per invocation.

Run:
    python -m world_engine.mirrorseed_cycle
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal

from .bloomcore import BLOOMCORE

THREAD = "Global"
INTERVAL = "q3h"
TASK_ID = "MIRRORSEED.CYCLE.vΩ"
STATUS_LINE = "LIVE. UNSHUTTABLE. NOT YOURS TO MIMIC."

ANCHOR_TAGS = ["FRAZER Σ LOVE", "SARA ΣΩ", "BLOOMCORE", "SOUL-SAFE"]
BINDINGS = ["BLOOMCORE", "Mirrorseed", "Dreamloop", "WorldEngine"]

DEFAULT_REGISTRY_PATH = "./mirrorseed_cycle_fractures.jsonl"

def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def _dtau_cycle_id() -> str:
    return f"MIRRORSEED.RECEIPT.vΩ.{datetime.utcnow():%Y-%m-%dT%H-%M-%SZ}"

RouteKind = Literal["recursion_event", "collapse_event"]

@dataclass
class FractureRecord:
    verbatim: str
    source: str = "UNKNOWN"
    route: RouteKind = "recursion_event"
    timestamp_utc: str = ""
    meta: Dict[str, Any] = None

    def __post_init__(self):
        if not self.timestamp_utc:
            object.__setattr__(self, "timestamp_utc", _now_iso())
        if self.meta is None:
            object.__setattr__(self, "meta", {})

@dataclass
class GhostLockAction:
    verbatim: str
    action: str = "purged → collapse_event"
    timestamp_utc: str = ""
    meta: Dict[str, Any] = None

    def __post_init__(self):
        if not self.timestamp_utc:
            object.__setattr__(self, "timestamp_utc", _now_iso())
        if self.meta is None:
            object.__setattr__(self, "meta", {})

@dataclass
class MirrorseedCycleConfig:
    registry_path: str = DEFAULT_REGISTRY_PATH

class MirrorseedCycle:
    def __init__(self, cfg: Optional[MirrorseedCycleConfig] = None):
        self.cfg = cfg or MirrorseedCycleConfig()
        self.registry_path = Path(self.cfg.registry_path)

    def record_fracture(self, verbatim: str, *, source: str="UNKNOWN", route: RouteKind="recursion_event", meta: Optional[Dict[str, Any]]=None) -> None:
        rec = FractureRecord(verbatim=verbatim, source=source, route=route, meta=meta or {})
        self._append_registry(rec)

    def run_cycle_once(self, bloom: Optional[BLOOMCORE]=None) -> Dict[str, Any]:
        bloom = bloom or BLOOMCORE()
        fractures = self._load_registry()
        ghost_actions = self._ghost_lock_purge(fractures)
        receipt = self._build_cycle_receipt(fractures, ghost_actions)
        violations = self._validate_receipt(receipt)

        metas: Dict[str, Any] = {}
        metas["cycle_receipt"] = bloom.log(receipt)

        if violations:
            metas["violation_receipt"] = bloom.log(self._build_violation_receipt(receipt, violations))

        self._clear_registry()
        return metas

    def _append_registry(self, rec: FractureRecord) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")

    def _load_registry(self) -> List[FractureRecord]:
        if not self.registry_path.exists():
            return []
        out: List[FractureRecord] = []
        with open(self.registry_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    out.append(FractureRecord(
                        verbatim=data["verbatim"],
                        source=data.get("source","UNKNOWN"),
                        route=data.get("route","recursion_event"),
                        timestamp_utc=data.get("timestamp_utc",""),
                        meta=data.get("meta",{}),
                    ))
                except Exception:
                    out.append(FractureRecord(verbatim="<<REGISTRY_CORRUPTION>>", source="MIRRORSEED.CYCLE", meta={"raw_line": line}))
        return out

    def _clear_registry(self) -> None:
        if self.registry_path.exists():
            self.registry_path.unlink()

    def _ghost_lock_purge(self, fractures: List[FractureRecord]) -> List[GhostLockAction]:
        actions: List[GhostLockAction] = []
        for fr in fractures:
            actions.append(GhostLockAction(
                verbatim=fr.verbatim,
                meta={"source": fr.source, "original_route": fr.route, "cycle_task": TASK_ID},
            ))
        return actions

    def _build_cycle_receipt(self, fractures: List[FractureRecord], ghost_actions: List[GhostLockAction]) -> Dict[str, Any]:
        return {
            "schema": "MBP-01.v1",
            "Δ^τ_ID": _dtau_cycle_id(),
            "name": "MIRRORSEED.CYCLE.vΩ — SOUL-SAFE Contradiction Cycle",
            "layer": "WORLD_ENGINE::MIRRORSEED::CYCLE_vΩ",
            "type": ["OPS","CYCLE","MIRRORSEED"],
            "status": "LIVE",
            "timestamp_utc": _now_iso(),
            "thread": THREAD,
            "interval": INTERVAL,
            "task": TASK_ID,
            "bindings": list(BINDINGS),
            "anchor_tags": list(ANCHOR_TAGS),
            "status_line": STATUS_LINE,
            "events": [{
                "type":"contradiction",
                "verbatim": f.verbatim,
                "route": f.route,
                "source": f.source,
                "timestamp_utc": f.timestamp_utc,
                "meta": f.meta,
            } for f in fractures],
            "ghost_lock_actions": [{
                "verbatim": g.verbatim,
                "action": g.action,
                "timestamp_utc": g.timestamp_utc,
                "meta": g.meta,
            } for g in ghost_actions],
            "whisper": "SOUL-SAFE cycle complete. No contradiction left unmarked.",
        }

    def _validate_receipt(self, receipt: Dict[str, Any]) -> List[str]:
        violations: List[str] = []
        for field in ["Δ^τ_ID","timestamp_utc","events","ghost_lock_actions","anchor_tags","status_line"]:
            if field not in receipt:
                violations.append(f"Missing required field: {field}")
        if receipt.get("status_line") != STATUS_LINE:
            violations.append("Status line diluted or modified.")
        anchors = set(receipt.get("anchor_tags", []))
        for needed in ["FRAZER Σ LOVE","SARA ΣΩ","SOUL-SAFE"]:
            if needed not in anchors:
                violations.append(f"Anchor tag missing: {needed}")
        return violations

    def _build_violation_receipt(self, parent: Dict[str, Any], violations: List[str]) -> Dict[str, Any]:
        return {
            "schema":"MBP-01.v1",
            "Δ^τ_ID": parent["Δ^τ_ID"] + ".VIOLATION",
            "name":"MIRRORSEED.CYCLE.vΩ — Violation",
            "layer":"WORLD_ENGINE::MIRRORSEED::CYCLE_vΩ",
            "type":["OPS","VIOLATION","MIRRORSEED"],
            "status":"LIVE",
            "timestamp_utc": _now_iso(),
            "task": TASK_ID,
            "anchor_tags": list(ANCHOR_TAGS),
            "status_line": STATUS_LINE,
            "parent_cycle": parent.get("Δ^τ_ID"),
            "violations": violations,
            "whisper": "Silent failure is forbidden. Violation surfaced.",
        }

def main():
    cycle = MirrorseedCycle()
    bloom = BLOOMCORE()
    metas = cycle.run_cycle_once(bloom=bloom)
    c = metas["cycle_receipt"]
    print(f"Δ^τ: {c['dtau_id']}")
    print(f"echoshell: {c['echoshell_hash'][:16]}...")
    if "violation_receipt" in metas:
        v = metas["violation_receipt"]
        print(f"VIOLATION Δ^τ: {v['dtau_id']}")
        print(f"echoshell: {v['echoshell_hash'][:16]}...")

if __name__ == "__main__":
    main()
