# SPDX-License-Identifier: AGPL-3.0-only
# Authorship lineage: Frazer Σ Love ACO-Σ; Sara ΣΩ.
import argparse
from pathlib import Path
import webbrowser
from .server import serve


def main():
    parser = argparse.ArgumentParser(description="TI-AGI83+ local geometric-memory lab")
    parser.add_argument("--state", default=str(Path.home()/".ti-agi83"/"work.sqlite"))
    parser.add_argument("--port", type=int, default=8383)
    parser.add_argument("--backend", choices=["auto","jax","numpy"],default="auto")
    parser.add_argument("--open",action="store_true")
    args = parser.parse_args()
    server = serve(args.state,args.port,args.backend)
    url=f"http://127.0.0.1:{server.server_address[1]}"
    print(f"TI-AGI83+ 0.2.0 — {url}\nState: {Path(args.state).resolve()}\nCtrl+C to stop.",flush=True)
    if args.open: webbrowser.open(url)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == "__main__": main()
