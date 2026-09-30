# SPDX-License-Identifier: AGPL-3.0-only
# Authorship lineage: Frazer Σ Love ACO-Σ; Sara ΣΩ.
"""Loopback-only, serialized desktop service. No model or external connection."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import json
import secrets
from .store import Store
from . import __version__
from .audit import export_csv

WEB = Path(__file__).with_name("web")
MAX_BODY = 8*1024*1024


def serve(state, port=8383, backend="auto"):
    store = Store(state,backend)
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_): pass

        def valid_host(self):
            host = self.headers.get("Host","")
            return host in (f"127.0.0.1:{self.server.server_address[1]}", f"localhost:{self.server.server_address[1]}")

        def send(self, payload, status=200, mime="application/json; charset=utf-8"):
            body = payload if isinstance(payload,bytes) else json.dumps(payload,ensure_ascii=False,allow_nan=False).encode()
            self.send_response(status); self.send_header("Content-Type",mime); self.send_header("Content-Length",str(len(body)))
            self.send_header("Cache-Control","no-store"); self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers(); self.wfile.write(body)

        def do_GET(self):
            if not self.valid_host(): self.send({"error":"Local host required"},403); return
            url = urlsplit(self.path); q = parse_qs(url.query)
            try:
                if url.path == "/api/bootstrap":
                    self.send({"token":token,"sheets":store.list(),"backend":store.backend,"version":__version__}); return
                if url.path == "/api/memory": self.send(store.memory(q.get("scope",["invoice"])[0])); return
                if url.path == "/api/games": self.send(store.game_scores()); return
                if url.path == "/api/history": self.send(store.history()); return
                if url.path == "/api/export": self.send(store.export()); return
                if url.path == "/api/csv":
                    s=store.sheet(int(q.get("id",["0"])[0]));self.send(export_csv(s["schema"],s["rows"]).encode(),mime="text/csv; charset=utf-8");return
                name = {"/":"index.html","/app.js":"app.js","/arcade-engine.js":"arcade-engine.js","/arcade-ui.js":"arcade-ui.js"}.get(url.path)
                if name:
                    self.send((WEB/name).read_bytes(),mime="text/html; charset=utf-8" if name.endswith("html") else "text/javascript; charset=utf-8");return
                self.send({"error":"Not found"},404)
            except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:
                self.send({"error":str(e)},400)

        def do_POST(self):
            if not self.valid_host() or not secrets.compare_digest(self.headers.get("X-TI-Token",""),token):
                self.send({"error":"Local session required"},403);return
            origin=self.headers.get("Origin")
            allowed={f"http://127.0.0.1:{self.server.server_address[1]}",f"http://localhost:{self.server.server_address[1]}"}
            if origin and origin not in allowed: self.send({"error":"Local origin required"},403);return
            try:
                length=int(self.headers.get("Content-Length","0"))
                if not 0 < length <= MAX_BODY: raise ValueError("Request exceeds the 8 MiB limit")
                data=json.loads(self.rfile.read(length)); path=urlsplit(self.path).path
                if not isinstance(data,dict): raise ValueError("JSON object required")
                if path=="/api/save": result=store.save(int(data["id"]),data["rows"],data["signature"])
                elif path=="/api/audit": result=store.run_audit(int(data["id"]))
                elif path=="/api/repair": result=store.repair(int(data["id"]),int(data["audit_id"]),data["signature"])
                elif path=="/api/undo": result=store.undo(int(data["id"]),data["signature"])
                elif path=="/api/game-score": result=store.record_game_score(data["game"],data["score"],data["play_id"])
                elif path=="/api/import": result=store.import_sheet(data["schema"],data["csv"],data["name"])
                else: self.send({"error":"Not found"},404);return
                self.send(result)
            except (ValueError,KeyError,TypeError,json.JSONDecodeError,UnicodeError) as e:
                self.send({"error":str(e)},400)
            except Exception:
                self.send({"error":"Operation failed; the transaction was rolled back. Check the local database and retry."},500)

    server=HTTPServer(("127.0.0.1",port),Handler)
    server.store=store
    original_close=server.server_close
    def close(): original_close();store.close()
    server.server_close=close
    return server
