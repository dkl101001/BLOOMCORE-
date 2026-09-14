# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import statistics

import numpy as np
import pytest

jax = pytest.importorskip("jax")
jnp = pytest.importorskip("jax.numpy")

from bloomcore_governance_weave.cli import sample_proposal
from bloomcore_governance_weave.jax_backend import jitted_jax_audit
from bloomcore_governance_weave.numpy_backend import numpy_audit
from bloomcore_governance_weave.weave import evaluate


def test_shared_audit_formulas_match_jax():
    proposal = sample_proposal()
    result = evaluate(proposal)
    values = jnp.asarray(
        [
            proposal.coherence,
            proposal.fragility,
            proposal.risk,
            proposal.compassion,
            proposal.phase_norm,
            proposal.reflection_fidelity,
            proposal.friend_coherence,
            statistics.median(proposal.hdot_window),
            *proposal.rgb_drift,
            *proposal.velocity,
            proposal.value_previous,
            proposal.value_current,
            proposal.tau_export,
        ],
        dtype=jnp.float32,
    )
    numpy_actual = numpy_audit(np.asarray(values))
    jax_actual = np.asarray(jitted_jax_audit(values))
    expected = np.asarray(
        [
            result.veil_pressure,
            result.wisdom_score,
            float(result.wisdom_gate),
            float(result.anti_closure_violation),
            float(result.critic_veto),
        ],
        dtype=np.float32,
    )
    np.testing.assert_allclose(numpy_actual, expected, rtol=2e-6, atol=2e-6)
    np.testing.assert_allclose(jax_actual, numpy_actual, rtol=2e-6, atol=2e-6)


def test_preserved_nlse_anti_closure_predicate_is_reachable(family_root):
    import sys

    root = family_root / "ancestor" / "25075639" / "src"
    sys.path.insert(0, str(root))
    try:
        from bloomcore_nlse_antigovernor.audit.antigovernor import anti_governor_violation

        delta, violation = anti_governor_violation(jnp.asarray(1.0), jnp.asarray(0.5), jnp.asarray(0.0))
        assert float(delta) == pytest.approx(-0.5)
        assert bool(violation)
    finally:
        sys.path.remove(str(root))
