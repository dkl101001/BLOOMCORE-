from __future__ import annotations

from typing import Dict, Any
import json
from pathlib import Path

def to_json_report(base: Dict[str, float], norm: Dict[str, float], subscores: Dict[str, float], rss: float, weights_used: Dict[str, float], meta: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "meta": meta,
        "base_metrics": base,
        "normalized": norm,
        "subscores": subscores,
        "weights_used": weights_used,
        "RSS": rss,
    }

def write_json_report(report: Dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def read_json_report(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def to_latex_row(agent: str, benchmark: str, instr: str, subscores: Dict[str, float], rss: float) -> str:
    def f(x):
        return "N/A" if x is None else f"{float(x):.2f}"
    st = subscores.get("S_T")
    sl = subscores.get("S_L")
    sa = subscores.get("S_A")
    sm = subscores.get("S_M", None)
    sc = subscores.get("S_C", None)
    return f"{agent} & {benchmark} & {instr} & {f(st)} & {f(sl)} & {f(sa)} & {f(sm)} & {f(sc)} & {rss:.2f} \\"

def to_markdown_table_row(agent: str, benchmark: str, instr: str, subscores: Dict[str, float], rss: float) -> str:
    def f(x):
        return "N/A" if x is None else f"{float(x):.2f}"
    return "| " + " | ".join([
        agent, benchmark, instr,
        f(subscores.get("S_T")),
        f(subscores.get("S_L")),
        f(subscores.get("S_A")),
        f(subscores.get("S_M", None)),
        f(subscores.get("S_C", None)),
        f"{rss:.2f}"
    ]) + " |"
