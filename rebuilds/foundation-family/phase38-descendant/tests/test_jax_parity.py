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


def assert_shared_state_close(fire, oracle, *, rtol=3e-4, atol=5e-5):
    assert int(np.asarray(fire.tick)) == oracle.tick
    for name in (
        "vector",
        "previous",
        "identity",
        "field",
        "memory",
        "hdot_history",
        "energy_prev",
        "topology",
        "coupling",
    ):
        np.testing.assert_allclose(
            np.asarray(getattr(fire, name)),
            np.asarray(getattr(oracle, name)),
            rtol=rtol,
            atol=atol,
        )


def assert_metrics_close(fire, oracle, *, rtol=3e-4, atol=3e-5):
    np.testing.assert_allclose(
        np.asarray(fire[:-3], dtype=np.float32),
        np.asarray(oracle[:-3], dtype=np.float32),
        rtol=rtol,
        atol=atol,
    )
    np.testing.assert_array_equal(
        np.asarray(fire[-3:], dtype=np.int32),
        np.asarray(oracle[-3:], dtype=np.int32),
    )


def test_one_step_oracle_jax_parity():
    vector, field, topology = fixture()
    config = FireConfig(phi_min=0.0, require_wuwei=True, noise_scale=0.0)
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
    assert_shared_state_close(fire_next, oracle_next, rtol=2e-5, atol=2e-5)
    assert_metrics_close(fire_metrics, oracle_metrics)


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
    assert_shared_state_close(fire, oracle)
    oracle_metric_matrix = np.asarray(oracle_metrics)
    fire_metric_matrix = np.column_stack(
        [np.asarray(value) for value in fire_metrics]
    )
    np.testing.assert_allclose(
        fire_metric_matrix[:, :-3],
        oracle_metric_matrix[:, :-3],
        rtol=3e-4,
        atol=5e-5,
    )
    np.testing.assert_array_equal(
        fire_metric_matrix[:, -3:].astype(np.int32),
        oracle_metric_matrix[:, -3:].astype(np.int32),
    )


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

    deterministic = FireConfig(phi_min=0.0, require_wuwei=True, noise_scale=0.0)
    extended = zero_extend_jax(base, 2)
    base_det = base
    ext_det = extended
    for _ in range(5):
        base_det, base_metrics = jax_step(
            base_det, drive, weight, jnp.asarray(True), deterministic
        )
        ext_det, ext_metrics = jax_step(
            ext_det,
            jnp.zeros(6, dtype=jnp.float32),
            jnp.pad(weight, ((0, 2), (0, 2))),
            jnp.asarray(True),
            deterministic,
        )
        for name in ("vector", "previous", "identity", "memory", "coupling"):
            np.testing.assert_allclose(
                np.asarray(getattr(ext_det, name)[:4]),
                np.asarray(getattr(base_det, name)),
                atol=1e-6,
            )
        for name in ("field", "hdot_history", "energy_prev"):
            np.testing.assert_allclose(
                np.asarray(getattr(ext_det, name)),
                np.asarray(getattr(base_det, name)),
                atol=1e-6,
            )
        assert_metrics_close(ext_metrics, base_metrics, rtol=1e-5, atol=1e-6)
    np.testing.assert_array_equal(np.asarray(ext_det.topology[:4, :4]), topology)


def test_full_fire_backend_is_gpu():
    assert jax.default_backend() == "gpu"
    assert jax.devices()[0].platform == "gpu"
