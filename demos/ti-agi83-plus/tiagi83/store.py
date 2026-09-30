# SPDX-License-Identifier: AGPL-3.0-only
# Authorship lineage: Frazer Σ Love ACO-Σ; Sara ΣΩ.
"""Single-transaction work, conductance, incident and evidence persistence."""
import json
import hashlib
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from . import geometry
from .audit import SCHEMAS, SAMPLES, audit, validate_sheet, parse_csv


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()


class Store:
    def __init__(self, path, backend="auto"):
        self.backend = geometry.backend_for(backend)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), timeout=15)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS sheets (id INTEGER PRIMARY KEY, name TEXT NOT NULL, schema TEXT NOT NULL, rows TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 0);
          CREATE TABLE IF NOT EXISTS geometry (scope TEXT PRIMARY KEY, state TEXT NOT NULL, hash TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS audits (id INTEGER PRIMARY KEY, sheet INTEGER NOT NULL REFERENCES sheets(id), signature TEXT NOT NULL, result TEXT NOT NULL, at TEXT NOT NULL, UNIQUE(sheet,signature));
          CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY, audit INTEGER NOT NULL REFERENCES audits(id), scope TEXT NOT NULL, finding TEXT NOT NULL, repaired INTEGER NOT NULL DEFAULT 0, at TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS game_scores (play_id TEXT PRIMARY KEY, game TEXT NOT NULL, score INTEGER NOT NULL, at TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, type TEXT NOT NULL, payload TEXT NOT NULL, prior_hash TEXT NOT NULL, hash TEXT NOT NULL, at TEXT NOT NULL);
        ''')
        version = self.db.execute("SELECT value FROM meta WHERE key='schema'").fetchone()
        if version and version[0] != "1":
            raise ValueError("Unsupported database version; use the matching app version")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO meta VALUES ('schema','1')")
            if not self.db.execute("SELECT 1 FROM sheets").fetchone():
                for schema, rows in SAMPLES.items():
                    self.db.execute("INSERT INTO sheets(name,schema,rows) VALUES (?,?,?)", (schema.title()+" sample", schema, canonical(rows)))
                self.event("initialize", {"schemas": list(SCHEMAS)})
        self.verify()

    def close(self):
        self.db.close()

    def event(self, kind, payload):
        parent = self.db.execute("SELECT hash FROM events ORDER BY id DESC LIMIT 1").fetchone()
        prior = parent[0] if parent else "GENESIS"
        at = datetime.now(timezone.utc).isoformat()
        body = {"type": kind, "payload": payload, "prior_hash": prior, "at": at}
        self.db.execute("INSERT INTO events(type,payload,prior_hash,hash,at) VALUES (?,?,?,?,?)", (kind, canonical(payload), prior, digest(body), at))
        return digest(body)

    def verify(self):
        prior = "GENESIS"
        for e in self.db.execute("SELECT * FROM events ORDER BY id"):
            body = {"type": e["type"], "payload": json.loads(e["payload"]), "prior_hash": e["prior_hash"], "at": e["at"]}
            if e["prior_hash"] != prior or digest(body) != e["hash"]:
                raise ValueError("Receipt chain integrity failure")
            prior = e["hash"]
        for g in self.db.execute("SELECT * FROM geometry"):
            state = json.loads(g["state"]); geometry.validate(state)
            if digest(state) != g["hash"]:
                raise ValueError("Geometric state integrity failure")
        return {"verified_events": self.db.execute("SELECT count(*) FROM events").fetchone()[0], "head": prior, "integrity": "PASS", "scope": "local stored hash-chain consistency; not external authenticity"}

    def sheet(self, id):
        s = self.db.execute("SELECT * FROM sheets WHERE id=?", (id,)).fetchone()
        if not s:
            raise ValueError("Sheet does not exist")
        s = dict(s); s["rows"] = json.loads(s["rows"]); s["cols"] = SCHEMAS[s["schema"]]
        s["signature"] = digest({"id": s["id"], "schema": s["schema"], "revision": s["revision"], "rows": s["rows"]})
        return s

    def list(self):
        return [self.sheet(r[0]) for r in self.db.execute("SELECT id FROM sheets ORDER BY id")]

    def state(self, scope):
        row = self.db.execute("SELECT * FROM geometry WHERE scope=?", (scope,)).fetchone()
        if not row:
            return geometry.initial()
        state = json.loads(row["state"])
        if digest(state) != row["hash"]:
            raise ValueError("Geometric state integrity failure")
        geometry.validate(state)
        return state

    def write_state(self, scope, state):
        geometry.validate(state)
        self.db.execute("INSERT OR REPLACE INTO geometry VALUES (?,?,?)", (scope, canonical(state), digest(state)))

    def import_sheet(self, schema, text, name):
        rows = parse_csv(text, schema)
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 120:
            raise ValueError("Name the sheet in 1–120 characters")
        with self.db:
            cur = self.db.execute("INSERT INTO sheets(name,schema,rows) VALUES (?,?,?)", (name.strip(), schema, canonical(rows)))
            self.event("import", {"sheet": cur.lastrowid, "schema": schema, "rows_digest": digest(rows)})
        return self.sheet(cur.lastrowid)

    def save(self, id, rows, signature):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            sheet = self.sheet(id)
            if signature != sheet["signature"]:
                raise ValueError("Sheet changed in another view; reload before saving")
            rows = validate_sheet(sheet["schema"], rows)
            if rows != sheet["rows"]:
                self.db.execute("UPDATE sheets SET rows=?,revision=revision+1 WHERE id=?", (canonical(rows),id))
                self.event("edit", {"sheet": id, "before": sheet["rows"], "after": rows})
        return self.sheet(id)

    def candidates(self, scope, exclude_audit=None):
        # A fixed disclosed window bounds query work; older incidents remain in custody.
        rs = self.db.execute("SELECT * FROM incidents WHERE scope=? AND audit!=? ORDER BY id DESC LIMIT 200", (scope,exclude_audit or -1)).fetchall()
        return [{"id": r["id"], "finding": json.loads(r["finding"]), "repaired": bool(r["repaired"]), "at": r["at"]} for r in rs]

    def run_audit(self, id):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            s = self.sheet(id)
            result = audit(s["schema"], s["rows"])
            prior = self.db.execute("SELECT * FROM audits WHERE sheet=? AND signature=?", (id,s["signature"])).fetchone()
            if prior:
                aid = prior["id"]
            else:
                at = datetime.now(timezone.utc).isoformat()
                cur = self.db.execute("INSERT INTO audits(sheet,signature,result,at) VALUES (?,?,?,?)", (id,s["signature"],canonical(result),at)); aid = cur.lastrowid
                state = self.state(s["schema"])
                for f in result["findings"]:
                    state = geometry.encounter(state, geometry.pattern(f), self.backend)
                    self.db.execute("INSERT INTO incidents(audit,scope,finding,at) VALUES (?,?,?,?)", (aid,s["schema"],canonical(f),at))
                self.write_state(s["schema"],state)
                self.event("audit", {"sheet": id, "audit": aid, "signature": s["signature"], "findings": result["findings"], "geometry_hash": digest(state)})
        state = self.state(s["schema"]); candidates = geometry.prepared(state,self.candidates(s["schema"], aid),self.backend)
        cache = {}
        for f in result["findings"]:
            key = geometry.pattern(f).tobytes()
            if key not in cache:
                cache[key] = geometry.related(state,f,candidates,self.backend)
            f["memory"] = cache[key]
        return {**result, "audit_id": aid, "signature": s["signature"], "duplicate_observation": bool(prior), "backend": self.backend}

    def repair(self, id, audit_id, signature):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            s = self.sheet(id); a = self.db.execute("SELECT * FROM audits WHERE id=? AND sheet=?", (audit_id,id)).fetchone()
            if not a or signature != s["signature"] or a["signature"] != signature:
                raise ValueError("Fresh audit required: the sheet changed")
            # Recompute the rules; never execute a fix from a historical suggestion.
            result = audit(s["schema"],s["rows"]); fixes = [f for f in result["findings"] if f["fix"] is not None]
            if not fixes:
                raise ValueError("No verified arithmetic repair is available")
            rows = [r[:] for r in s["rows"]]
            for f in fixes:
                rows[f["row"]][f["col"]] = f["fix"]
            after = audit(s["schema"],rows)
            if any(f["fix"] is not None for f in after["findings"]):
                raise ValueError("Repair verification failed")
            self.db.execute("UPDATE sheets SET rows=?,revision=revision+1 WHERE id=?",(canonical(rows),id))
            self.db.execute("UPDATE incidents SET repaired=1 WHERE audit=? AND json_extract(finding,'$.fix') IS NOT NULL", (audit_id,))
            self.event("repair", {"sheet": id, "audit": audit_id, "before": s["rows"], "after": rows, "fixes": len(fixes)})
        return {"sheet": self.sheet(id), "fixes": len(fixes), "remaining": after["findings"]}

    def undo(self, id, signature):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            s = self.sheet(id)
            if signature != s["signature"]:
                raise ValueError("Sheet changed; reload before undo")
            target = None
            for row in self.db.execute("SELECT * FROM events WHERE type IN ('repair','edit','undo') ORDER BY id DESC"):
                p = json.loads(row["payload"])
                if p.get("sheet") == id:
                    target = p; break
            if not target:
                raise ValueError("No edit or repair to undo")
            if target["after"] != s["rows"]:
                raise ValueError("History does not match the current sheet")
            self.db.execute("UPDATE sheets SET rows=?,revision=revision+1 WHERE id=?",(canonical(target["before"]),id))
            self.event("undo", {"sheet": id, "before": s["rows"], "after": target["before"], "preserves_memory": True})
        return self.sheet(id)

    def memory(self, scope):
        if scope not in SCHEMAS:
            raise ValueError("Unknown memory scope")
        state = self.state(scope); c = self.candidates(scope)
        probe = geometry.pattern({"kind":"arithmetic", "col":3, "relative":.1, "delta":1})
        learned = geometry.response(state,probe,self.backend); flat = geometry.response(state,probe,self.backend,flat=True)
        counts = {}
        for x in c:
            k = x["finding"]["kind"]; counts[k] = counts.get(k,0)+1
        return {"state": state, "state_hash": digest(state), "backend": self.backend,
                "probe_delta": float(__import__('numpy').linalg.norm(learned-flat)),
                "probe_learned": learned.tolist(), "probe_flat": flat.tolist(),
                "incidents": c[:25], "counts_in_window": counts, "retrieval_window":200,
                "total_incidents": self.db.execute("SELECT count(*) FROM incidents WHERE scope=?",(scope,)).fetchone()[0],
                "notice":"Conductance influences related-error transport; current arithmetic rules decide repairs."}

    def history(self):
        rows = self.db.execute("SELECT * FROM events ORDER BY id DESC LIMIT 100").fetchall()
        return {"events":[{**dict(r),"payload":json.loads(r["payload"])} for r in rows],"receipt":self.verify(),"window":100}

    def game_scores(self):
        games = {name: {"best": None, "plays": 0} for name in ("snake", "blocks", "pong")}
        for row in self.db.execute("SELECT game, max(score) AS best, count(*) AS plays FROM game_scores GROUP BY game"):
            games[row["game"]] = {"best": row["best"], "plays": row["plays"]}
        return {"games": games}

    def record_game_score(self, game, score, play_id):
        if game not in ("snake", "blocks", "pong"):
            raise ValueError("Unknown game")
        if type(score) is not int or not 0 <= score <= 1_000_000_000:
            raise ValueError("Score must be a bounded nonnegative integer")
        if not isinstance(play_id, str) or len(play_id) != 36 or str(uuid.UUID(play_id)) != play_id:
            raise ValueError("Canonical play UUID required")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            prior = self.db.execute("SELECT * FROM game_scores WHERE play_id=?", (play_id,)).fetchone()
            if prior:
                if prior["game"] != game or prior["score"] != score:
                    raise ValueError("Play ID already records a different score")
            else:
                self.db.execute("INSERT INTO game_scores VALUES (?,?,?,?)", (play_id, game, score, datetime.now(timezone.utc).isoformat()))
                self.event("game_complete", {"play_id": play_id, "game": game, "score": score})
        return self.game_scores()

    def export(self):
        self.verify()
        return {"schema":"TIAGI.EXPORT.v1", "sheets":self.list(),
                "geometry":[dict(r) for r in self.db.execute("SELECT * FROM geometry")],
                "events":[dict(r) for r in self.db.execute("SELECT * FROM events ORDER BY id")],
                "incidents":[dict(r) for r in self.db.execute("SELECT * FROM incidents ORDER BY id")],
                "audits":[dict(r) for r in self.db.execute("SELECT * FROM audits ORDER BY id")],
                "game_scores":[dict(r) for r in self.db.execute("SELECT * FROM game_scores ORDER BY at,play_id")],
                "receipt":self.verify()}
