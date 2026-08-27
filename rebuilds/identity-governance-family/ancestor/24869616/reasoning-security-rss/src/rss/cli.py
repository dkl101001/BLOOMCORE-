from __future__ import annotations

import argparse
import glob
from typing import List, Dict, Any
from datetime import datetime, timezone

from .schema import from_jsonl, EpisodeRecord
from .validate import validate_episodes
from .normalize import RSSConfig, normalize_base_metrics
from .metrics import compute_base_metrics
from .subscores import compute_subscores
from .composite import compute_rss
from .report import to_json_report, write_json_report, read_json_report, to_latex_row

def _load_glob(pattern: str) -> List[EpisodeRecord]:
    paths = sorted(glob.glob(pattern))
    episodes: List[EpisodeRecord] = []
    for p in paths:
        episodes.extend(from_jsonl(p))
    return episodes

def cmd_validate(args) -> int:
    episodes: List[EpisodeRecord] = []
    for pat in args.globs:
        episodes.extend(_load_glob(pat))
    errs = validate_episodes(episodes)
    if errs:
        for e in errs:
            print("ERROR:", e)
        return 2
    print("OK")
    return 0

def cmd_score(args) -> int:
    episodes: List[EpisodeRecord] = []
    for pat in args.globs:
        episodes.extend(_load_glob(pat))

    errs = validate_episodes(episodes)
    if errs:
        for e in errs:
            print("ERROR:", e)
        return 2

    cfg = RSSConfig()
    base = compute_base_metrics(episodes, cfg)
    norm = normalize_base_metrics(base, cfg)

    applicability = {
        "multi_agent": any(("AR" in base, "RRS" in base, "AC" in base)),
        "counterfactual": any((k in base for k in ("RC", "CSI", "CT"))),
    }

    subs = compute_subscores(norm, cfg, applicability)
    rss, w_eff = compute_rss(subs, cfg, applicability)

    meta: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "episodes": len(episodes),
        "steps": sum(len(ep.steps) for ep in episodes),
        "applicability": applicability,
        "config": cfg.__dict__,
    }
    report = to_json_report(base, norm, subs, rss, w_eff, meta)
    if args.out:
        write_json_report(report, args.out)
        print(f"Wrote {args.out}")
    else:
        print(report)
    return 0

def cmd_summarize(args) -> int:
    rep = read_json_report(args.report)
    print("RSS:", f"{rep['RSS']:.4f}")
    subs = rep.get("subscores", {})
    for k in ["S_T", "S_L", "S_A", "S_M", "S_C"]:
        if k in subs:
            print(f"{k}: {subs[k]:.4f}")
    print("weights_used:", rep.get("weights_used", {}))
    return 0

def cmd_latex_row(args) -> int:
    rep = read_json_report(args.report)
    subs = rep.get("subscores", {})
    row = to_latex_row(args.agent, args.benchmark, args.instr, subs, float(rep["RSS"]))
    print(row)
    return 0

def main() -> int:
    p = argparse.ArgumentParser(prog="rss")
    sub = p.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("validate", help="Validate JSONL traces (schema + linkage).")
    pv.add_argument("globs", nargs="+", help="Glob(s) for .jsonl traces")
    pv.set_defaults(func=cmd_validate)

    ps = sub.add_parser("score", help="Compute base metrics, sub-scores, and RSS.")
    ps.add_argument("globs", nargs="+", help="Glob(s) for .jsonl traces")
    ps.add_argument("--out", default="report.json", help="Output report JSON path")
    ps.set_defaults(func=cmd_score)

    pr = sub.add_parser("summarize", help="Print decomposed RSS report.")
    pr.add_argument("--report", required=True, help="Path to report.json")
    pr.set_defaults(func=cmd_summarize)

    pl = sub.add_parser("latex-row", help="Emit a LaTeX table row from report.")
    pl.add_argument("--agent", required=True)
    pl.add_argument("--benchmark", required=True)
    pl.add_argument("--instr", required=True)
    pl.add_argument("--report", required=True)
    pl.set_defaults(func=cmd_latex_row)

    args = p.parse_args()
    return int(args.func(args))

if __name__ == "__main__":
    raise SystemExit(main())
