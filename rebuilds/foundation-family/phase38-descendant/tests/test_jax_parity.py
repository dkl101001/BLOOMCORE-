# SPDX-License-Identifier: AGPL-3.0-only
import numpy as np
import pytest

jax = pytest.importorskip("jax")
jnp = pytest.importorskip("jax.numpy")

from bloomcore_foundation_fire.jax_backend import (
    initial_jax_state,
    jax_rollout,
    jax_step,
    zero_extend_jax,
)
from bloomcore_foundation_fire.model import FireConfig, initial_oracle_state
from bloomcore_foundation_fire.numpy_oracle import oracle_rollout, oracle_step


def fixture():
    vector = np.asarray([0.2, -0.1, 0.35, 0.05], dtype=np.float32)
    field = np.linspace(-0.3, 0.3, 64, dtype=np.float32).reshape(8, 8)
    topology = np.asarray(
        [[1, 1, 0, 0], [1, 1, 1, 0], [0, 1, 1, 1], [0, 0, 1, 1]],
        dtype=np.float32,
    )
    return vector, field, topology


def test_one_step_oracle_jax_parity():
    vector, field, topology = fixture()
    config = FireConfig(phi_min=0.0, require_wuwei=False, noise_scale=0.0)
    oracle = initial_oracle_state(vector=vector, field=field, topology=topology)
    fire = initial_jax_state(vector=vector, field=field, topology=topology)
    drive = np.asarray([0.0, 0.01, -0.02, 0.0], dtype=np.float32)
    weight = np.eye(4, dtype=np.float32)
    oracle_next, oracle_metrics = oracle_step(
        oracle, drive=drive, weight=weight, truth_flag=True, config=config
    )
    fire_next, fire_metrics = jax_step(
        fire, jnp.asarray(drive), jnp.asarray(weight), jnp.asarray(True), config
    )
    np.testing.assert_allclose(np.asarray(fire_next.vector), oracle_next.vector, rtol=2e-5, atol=2e-5)
    np.testing.assert_allclose(np.asarray(fire_next.field), oracle_next.field, rtol=2e-5, atol=2e-5)
    np.testing.assert_allclose(
        np.asarray(fire_metrics[:-3], dtype=np.float32),
        np.asarray(oracle_metrics[:-3], dtype=np.float32),
        rtol=3e-4,
        atol=3e-5,
    )
    np.testing.assert_array_equal(np.asarray(fire_next.topology), topology)


def test_five_step_rollout_parity():
    vector, field, topology = fixture()
    config = FireConfig(phi_min=0.0, require_wuwei=False, noise_scale=0.0)
    drives = np.asarray(
        [[0.0, 0.01 * i, -0.005 * i, 0.0] for i in range(5)], dtype=np.float32
    )
    truths = np.ones(5, dtype=bool)
    weight = np.eye(4, dtype=np.float32)
    oracle, oracle_metrics = oracle_rollout(
        initial_oracle_state(vector=vector, field=field, topology=topology),
        drives=drives,
        weight=weight,
        truth_flags=truths,
        config=config,
    )
    fire, fire_metrics = jax_rollout(
        initial_jax_state(vector=vector, field=field, topology=topology),
        jnp.asarray(drives),
        jnp.asarray(weight),
        jnp.asarray(truths),
        config,
    )
    np.testing.assert_allclose(np.asarray(fire.vector), oracle.vector, rtol=3e-4, atol=5e-5)
    np.testing.assert_allclose(np.asarray(fire.field), oracle.field, rtol=3e-4, atol=5e-5)
    assert np.asarray(fire_metrics.verdict).shape == (5,)
    assert len(oracle_metrics) == 5


def test_jax_zero_extension_and_explicit_key_replay():
    vector, field, topology = fixture()
    config = FireConfig(phi_min=0.0, require_wuwei=False, noise_scale=0.01)
    base = initial_jax_state(vector=vector, field=field, topology=topology, seed=38)
    replay = initial_jax_state(vector=vector, field=field, topology=topology, seed=38)
    different = initial_jax_state(vector=vector, field=field, topology=topology, seed=39)
    drive = jnp.zeros(4, dtype=jnp.float32)
    weight = jnp.eye(4, dtype=jnp.float32)
    base_next, _ = jax_step(base, drive, weight, jnp.asarray(True), config)
    replay_next, _ = jax_step(replay, drive, weight, jnp.asarray(True), config)
    different_next, _ = jax_step(different, drive, weight, jnp.asarray(True), config)
    np.testing.assert_array_equal(np.asarray(base_next.field), np.asarray(replay_next.field))
    assert not np.array_equal(np.asarray(base_next.field), np.asarray(different_next.field))

    deterministic = FireConfig(phi_min=0.0, require_wuwei=False, noise_scale=0.0)
    extended = zero_extend_jax(base, 2)
    base_det, _ = jax_step(base, drive, weight, jnp.asarray(True), deterministic)
    ext_det, _ = jax_step(
        extended,
        jnp.zeros(6, dtype=jnp.float32),
        jnp.pad(weight, ((0, 2), (0, 2))),
        jnp.asarray(True),
        deterministic,
    )
    np.testing.assert_allclose(np.asarray(ext_det.vector[:4]), np.asarray(base_det.vector), atol=1e-6)
    np.testing.assert_array_equal(np.asarray(ext_det.topology[:4, :4]), topology)


def test_full_fire_backend_is_gpu():
    assert jax.default_backend() == "gpu"
    assert jax.devices()[0].platform == "gpu"
