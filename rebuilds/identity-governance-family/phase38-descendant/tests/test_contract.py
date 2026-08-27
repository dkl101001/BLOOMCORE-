# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import importlib.resources
import json


def test_packaged_execution_object_has_explicit_authority_boundaries():
    path = importlib.resources.files("bloomcore_governance_weave").joinpath("phase38_execution_object.json")
    contract = json.loads(path.read_text("utf-8"))
    assert contract["canonical_identity"] == "NONE__PROPOSED_BOUNDED_DESCENDANT"
    assert contract["operational_authority"] == "NONE"
    assert contract["native_state_mutation"] is False
    assert contract["external_side_effects"] is False
    assert contract["market_execution"] is False
    assert contract["numpy_entrypoint"] == "bloomcore_governance_weave.numpy_backend:numpy_audit"
    assert contract["identity_resolution"]["Da_Vinci"] == "UNRESOLVED"
    assert contract["receipt_role"] == "POST_EXECUTION_WITNESS_ONLY"
    assert contract["phase38_source_sha256"] == "ff058db5dd35fee55168494b17a642fa6ef94bea26e24a5988f07ab80c76de29"
