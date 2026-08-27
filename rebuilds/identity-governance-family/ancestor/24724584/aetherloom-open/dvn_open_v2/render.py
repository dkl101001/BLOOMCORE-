# ============================================================
# OPEN Markdown Renderer
# Title: ψΔ^τ AetherLoom Regime Read (OPEN v2.4.3)
# ============================================================
from __future__ import annotations
from typing import Dict, Any

def render_response_vector_block(rv: Dict[str, Any]) -> str:
    plain = rv.get("plain_language", "")
    tp = rv.get("technical_parameters", {})
    posture = rv.get("posture_agent", "Modeled Agent")
    gov = rv.get("governor", None)

    lines = [
        "6) Response Vector (Agent)",
        f"Posture (agent): {posture}",
        f"Response Vector: {plain}",
    ]

    if gov:
        lines.append(f"Governor: {gov.get('kind')} (w_mul={gov.get('weight_multiplier')})")

    if tp:
        lines.append("Technical Parameters (simulation):")
        for k in sorted(tp.keys()):
            lines.append(f"  • {k}: {tp[k]}")

    return "\n".join(lines)

def render_integrity_block(report: Dict[str, Any]) -> str:
    integ = report.get("integrity", {})
    posture = integ.get("sentinel_posture", "OK")

    ah = [
        f"{a.get('adapter_id')} {'ok' if a.get('ok') else 'FAIL'}"
        for a in integ.get("adapter_health", [])
    ]
    ah_line = " · ".join(ah) if ah else "(none)"

    receipts = report.get("receipts", {}) or {}
    if isinstance(receipts, dict) and receipts:
        counts = " · ".join(
            [f"{k}:{len(v) if isinstance(v, list) else 1}" for k, v in receipts.items()]
        )
    else:
        counts = "(none)"

    return f"\nIntegrity\nSentinel: {posture} | AdapterHealth: {ah_line}\nReceipts: {counts}"
