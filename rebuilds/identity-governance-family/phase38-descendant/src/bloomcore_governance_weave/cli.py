# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import argparse
from dataclasses import asdict
import json

from .model import Proposal
from .receipts import ReceiptChain
from .weave import evaluate


def sample_proposal() -> Proposal:
    return Proposal(
        proposal_id="sample-local-expression",
        content="Offer a bounded, reversible explanation with explicit uncertainty.",
        coherence=0.82,
        fragility=0.18,
        risk=0.20,
        compassion=0.91,
        phase_norm=0.92,
        reflection_fidelity=0.90,
        friend_coherence=0.86,
        truth_signal=True,
        hdot_window=(-0.04, -0.03, -0.02),
        rgb_drift=(0.08, 0.07, 0.09),
        velocity=(0.10, 0.08, 0.12),
        intent_hash="sample-intent-sha256",
        value_previous=1.0,
        value_current=1.0,
        tau_export=0.0,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded governance-weave witness")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    chain = ReceiptChain()
    result = evaluate(sample_proposal(), receipts=chain)
    payload = {"result": asdict(result), "receipt_head": chain.head, "receipt_chain_verified": chain.verify()}
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if chain.verify() else 1


if __name__ == "__main__":
    raise SystemExit(main())
