# Rival Orchestration Kernel (ROK)
# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rok.kernel import run as run_kernel
from rok.validate import validate_paths
from rok.replay import resolve_inputs, replay_paths, stream_run_summaries, format_summary, summary_to_json_dict

def _cmd_run(args: argparse.Namespace) -> int:
    out = Path(args.out)
    run_kernel(args.task, out, max_revisions=args.max_revisions, force_override=args.override)
    print(str(out))
    return 0

def _cmd_validate(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.paths]
    rep = validate_paths(paths, strict=args.strict, schema_version=args.schema_version)
    if rep.ok:
        print("validate: OK")
        return 0
    for issue in rep.issues:
        print(f"{issue.severity} {issue.file}:{issue.line} {issue.event} :: {issue.message}")
    return 2

def _cmd_replay(args: argparse.Namespace) -> int:
    paths = resolve_inputs(args.inputs)
    if args.jsonl:
        for obj in stream_run_summaries(paths, schema_version=args.schema_version):
            print(json.dumps(obj, ensure_ascii=False))
        return 0

    summary = replay_paths(paths, schema_version=args.schema_version)
    if args.json:
        print(json.dumps(summary_to_json_dict(summary), ensure_ascii=False, indent=2))
    else:
        print(format_summary(summary))
    return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="rok", description="Rival Orchestration Kernel (ROK)")
    sub = p.add_subparsers(dest="cmd", required=True)

    runp = sub.add_parser("run", help="Run protocol and emit JSONL traces.")
    runp.add_argument("--task", required=True)
    runp.add_argument("--out", required=True)
    runp.add_argument("--max-revisions", type=int, default=1)
    runp.add_argument("--override", action="store_true")
    runp.set_defaults(fn=_cmd_run)

    val = sub.add_parser("validate", help="Validate JSONL trace schema.")
    val.add_argument("paths", nargs="+")
    val.add_argument("--strict", action="store_true")
    val.add_argument("--schema-version", default=None, help="Require exact schema_version on every event line (e.g., v1).")
    val.set_defaults(fn=_cmd_validate)

    rep = sub.add_parser("replay", help="Replay JSONL traces and summarize outcomes.")
    rep.add_argument("inputs", nargs="+")
    rep.add_argument("--schema-version", default=None, help="Require exact schema_version in replayed logs (e.g., v1).")
    rep.add_argument("--json", action="store_true", help="Emit JSON output suitable for dashboards.")
    rep.add_argument("--jsonl", action="store_true", help="Emit one JSON object per run (streaming).")
    rep.set_defaults(fn=_cmd_replay)

    return p

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.fn(args))
