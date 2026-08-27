# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
from importlib.resources import files


REQUIRED_FIELDS = {
    "canonical_identity",
    "mythic_name",
    "mathematical_definition",
    "phase_and_lineage",
    "ancestral_source_reference",
    "ancestral_source_hash",
    "ancestral_entrypoint",
    "ancestral_state_transition",
    "causal_topology",
    "seed_mapping_contract",
    "protected_invariants",
    "jax_entrypoint",
    "state_schema",
    "input_schema",
    "output_schema",
    "dtype_and_precision",
    "device_and_backend_scope",
    "vectorization_strategy",
    "differentiation_scope",
    "parallelism_scope",
    "prng_policy",
    "stochastic_keys_are_explicit",
    "deterministic_subkernels",
    "nondeterministic_or_backend_sensitive_regions",
    "numerical_tolerances",
    "one_step_parity_tests",
    "rollout_parity_tests",
    "zero_extension_recovery_tests",
    "backend_divergence_declarations",
    "source_result_residue_trace",
    "receipt_schema",
    "tests",
    "open_equations",
}


def load_contract():
    path = files("bloomcore_foundation_fire").joinpath("full_fire_jax_object.json")
    return json.loads(path.read_text(encoding="utf-8"))


def test_v110_contract_is_packaged_and_complete():
    contract = load_contract()
    assert contract["schema"] == "BLOOMCORE.PHASE38.V1_10.FULL_FIRE_JAX_OBJECT.v1"
    assert contract["scope_status"] == "BOUNDED_SOURCE_COMPLETE"
    assert contract["phase38_source"]["sha256"] == (
        "ff058db5dd35fee55168494b17a642fa6ef94bea26e24a5988f07ab80c76de29"
    )
    declared = contract["full_fire_jax_object"]
    assert REQUIRED_FIELDS == set(declared)
    assert declared["canonical_identity"].startswith("NONE__")
    assert declared["ancestral_source_reference"] is None
    assert declared["ancestral_source_hash"] is None
    assert declared["ancestral_entrypoint"] is None
    assert declared["stochastic_keys_are_explicit"] is True
    assert declared["causal_topology"]["declared_adjacency_role"] == (
        "INERT_CUSTODY_PAYLOAD"
    )
    assert declared["receipt_schema"]["authority"] == "WITNESS_ONLY"
