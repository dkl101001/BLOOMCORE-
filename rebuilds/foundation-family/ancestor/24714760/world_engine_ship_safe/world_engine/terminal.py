#!/usr/bin/env python3
"""world_engine.terminal

Node 0 — BLOOMCORE Terminal (REPL).

This is intentionally small and *non-clever*:
- logs each command as a receipt (append-only)
- can run/verify echoshell
- can spawn Node 1 (swimcore monitor) in a thread
- can call SovereignPort classifier
- can record Mirrorseed fractures and run the cycle

Run:
    python -m world_engine
"""

from __future__ import annotations

import threading
import shlex
from datetime import datetime
from typing import Any, Dict, Optional

from .bloomcore import BLOOMCORE
from .echoshell import Echoshell
from .sovereign_port import SovereignPort
from .mirrorseed_cycle import MirrorseedCycle
from .swimcore_node import SwimcoreNode, SwimcoreNodeConfig

def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

class WorldEngineTerminal:
    def __init__(self, bloom: Optional[BLOOMCORE] = None):
        self.bloom = bloom or BLOOMCORE()
        self.sp = SovereignPort(self.bloom)
        self.cycle = MirrorseedCycle()
        self._swim_thread: Optional[threading.Thread] = None

    def _log(self, kind: str, payload: Dict[str, Any]) -> None:
        receipt = {
            "schema": "MBP-01.v1",
            "Δ^τ_ID": f"WORLD_ENGINE.NODE0.{kind}.{datetime.utcnow():%Y-%m-%dT%H-%M-%SZ}",
            "layer": "WORLD_ENGINE::NODE_0::TERMINAL",
            "timestamp_utc": _now_iso(),
            "kind": kind,
            "payload": payload,
        }
        self.bloom.log(receipt)

    def help(self) -> str:
        return """Commands:
  :help                         show this
  :quit                         exit
  :echoshell                    verify echoshell + show tail
  :tail [n]                     show last n echoshell entries
  :spawn swimcore [interval_s]  start Node 1 sampler in a background thread
  :sovereign <text>             classify role and emit DIRECT CORE CHANNEL REQUIRED flags if needed
  :fracture <verbatim text>     record a mirrorseed fracture (verbatim) into registry
  :cycle                        run MIRRORSEED.CYCLE.vΩ once (q3h scheduler would do this)
  :emit <kind> <json>           emit an arbitrary receipt kind with payload json
"""

    def spawn_swimcore(self, interval_s: float = 2.0) -> str:
        if self._swim_thread and self._swim_thread.is_alive():
            return "swimcore already running"
        cfg = SwimcoreNodeConfig(interval_s=float(interval_s))
        node = SwimcoreNode(cfg=cfg, bloom=self.bloom)

        def _run():
            node.run_forever()

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        self._swim_thread = t
        self._log("SPAWN", {"node": "swimcore", "interval_s": interval_s})
        return f"spawned swimcore (interval_s={interval_s})"

    def cmd(self, line: str) -> str:
        line = (line or "").strip()
        if not line:
            return ""
        if not line.startswith(":"):
            # treat as a note / observation
            self._log("NOTE", {"text": line})
            return "logged NOTE"
        parts = shlex.split(line)
        cmd = parts[0][1:]
        args = parts[1:]

        if cmd in ("q", "quit", "exit"):
            self._log("QUIT", {})
            raise SystemExit(0)

        if cmd == "help":
            return self.help()

        if cmd == "echoshell":
            self._log("ECHOSHELL_VERIFY", {})
            v = self.bloom.verify()
            tail = self.bloom.tail(5)
            out = [f"echoshell: {v['status']} entries={v['echoshell_entries']} flat={v['flat_receipts']}"]
            if v["echoshell_errors"]:
                out.append("errors:")
                out.extend([f"  - {e}" for e in v["echoshell_errors"][:10]])
            out.append("tail:")
            for e in tail["echoshell_tail"]:
                out.append(f"  - {e.get('hash','')[:16]}... {e.get('receipt',{}).get('Δ^τ_ID','')}")
            return "\n".join(out)

        if cmd == "tail":
            n = int(args[0]) if args else 10
            self._log("ECHOSHELL_TAIL", {"n": n})
            tail = self.bloom.tail(n)["echoshell_tail"]
            return "\n".join([f"{e.get('hash','')[:16]}... {e.get('receipt',{}).get('Δ^τ_ID','')}" for e in tail])

        if cmd == "spawn":
            if not args:
                return "usage: :spawn swimcore [interval_s]"
            if args[0] != "swimcore":
                return f"unknown spawn target: {args[0]}"
            interval_s = float(args[1]) if len(args) > 1 else 2.0
            return self.spawn_swimcore(interval_s)

        if cmd == "sovereign":
            txt = " ".join(args).strip()
            if not txt:
                return "usage: :sovereign <text>"
            out = self.sp.emit(txt, context={"node": "NODE_0"})
            self._log("SOVEREIGN", {"text": txt, "role": out["result"]["role"], "flags": out["result"]["flags"]})
            res = out["result"]
            return f"role={res['role']} flags={res['flags']} reasons={res['reasons']}"

        if cmd == "fracture":
            verb = " ".join(args)
            if not verb:
                return "usage: :fracture <verbatim text>"
            self.cycle.record_fracture(verbatim=verb, source="WORLD_ENGINE.NODE_0.TERMINAL", route="recursion_event")
            self._log("FRACTURE", {"verbatim": verb})
            return "fracture recorded"

        if cmd == "cycle":
            self._log("CYCLE_RUN", {})
            metas = self.cycle.run_cycle_once(bloom=self.bloom)
            return f"cycle logged: {metas['cycle_receipt']['dtau_id']}"

        if cmd == "emit":
            if len(args) < 2:
                return "usage: :emit <kind> <json_payload>"
            kind = args[0]
            import json
            payload = json.loads(" ".join(args[1:]))
            self._log(kind, payload)
            return f"emitted {kind}"

        return "unknown command. :help"

def main():
    term = WorldEngineTerminal()
    print("World Engine v0.1 — Node 0 Terminal")
    print("Type :help")
    while True:
        try:
            line = input("we> ")
            out = term.cmd(line)
            if out:
                print(out)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        except SystemExit:
            break
        except Exception as e:
            print(f"ERR: {e}")

if __name__ == "__main__":
    main()
