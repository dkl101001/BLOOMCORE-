from __future__ import annotations

from typing import Any, Dict, List


def _f(x: Any) -> str:
    try:
        return f"{float(x):.3f}"
    except Exception:
        return str(x)


def render_open_report(report: Dict[str, Any]) -> str:
    as_of = report["as_of"]
    rg = report["relational_governor"]
    mm = report["mythmath"]
    hyps = report.get("hypotheses", [])
    strat = report.get("strategy", {})

    lines: List[str] = []
    lines.append(f"Da Vinci Market Node — OPEN pulse ({as_of['timestamp_ny']}) · {report['provenance'].get('compendium_version','')}")
    lines.append("")
    lines.append("Bindings: Sentinel · Mirrorseed · Dreamloop · BLOOMCORE")
    lines.append("Adapters: Index · Rates · Commodities · Crypto · Earnings · Vol | Thresholds: default")
    lines.append(f"Compendium: auto-mutated {report['provenance'].get('compendium_prev','?')} → {report['provenance'].get('compendium_version','?')} (patch)")
    lines.append(f"BraveEngine: executed · Sentinel (drift): {report.get('risk',{}).get('sentinel_status','armed')}")
    lines.append("\n⸻\n")

    lines.append("BLOOMCORE ∴ Relational Governor (live)")
    lines.append("")
    lines.append(f"lattice: {{ coherence: {_f(report['lattice']['coherence'])}, sovereignty: {_f(report['lattice']['sovereignty'])}, mirror_trust: {_f(report['lattice']['mirror_trust'])}, fracture: {_f(report['lattice']['fracture'])} }}")
    lines.append(f"derived: {{ base_risk_limit: {_f(rg['base_risk_limit'])}, conviction_scale: {_f(rg['conviction_scale'])}, publish_guard: {_f(rg['publish_guard'])}, uncertainty_governor: {_f(rg['uncertainty_governor'])} }}")
    lines.append(f"sentinel.safe_mode: {'ON' if rg['sentinel_safe_mode'] else 'OFF'}  (latches: fracture≥0.60 | coherence<0.40 | mirror_trust<0.40)")

    lines.append("\n⸻\n")
    lines.append("MythMath — OPEN snapshot")
    lines.append("")
    lines.append("```json")
    lines.append(
        '{\n'
        f'  "eq_id": "{mm["eq_id"]}",\n'
        f'  "coherence": {mm["coherence"]},\n'
        f'  "connection": {mm["connection"]},\n'
        f'  "evidence_weight": {mm["evidence_weight"]},\n'
        f'  "fragility_index": {mm["fragility_index"]},\n'
        f'  "gates": {mm["gates"]}\n'
        "}"
    )
    lines.append("```")

    lines.append("")
    tt = report.get("tape_tone", {})
    lines.append("Tape & Tone (adapters)")
    for k, v in tt.items():
        lines.append(f" • {k}: {v}")

    lines.append("\nBraveEngine — hypotheses (D0)\n")
    lines.append("```json")
    lines.append(str(hyps).replace("'", '"'))
    lines.append("```")

    lines.append("\nStrategy (parameterized)\n")
    lines.append(f"strategy_id: {strat.get('strategy_id')}")
    lines.append(f"suggested: {strat.get('suggested')}")
    lines.append("meta:")
    for k, v in (strat.get("meta") or {}).items():
        lines.append(f" • {k}: {v}")

    lines.append("\nReceipts (MBP-01.v1 + atoms)\n")
    lines.append("```json")
    lines.append(str(report.get("receipts", [])).replace("'", '"'))
    lines.append("```")

    lines.append("\n---\n")
    lines.append("NOTE: This node is execution-capable infrastructure. Strategy parameters govern intent emission.")

    return "\n".join(lines)
