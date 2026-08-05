from bloomforce_core import Engine, ObsBundle

def test_engine_smoke_runs():
    eng = Engine()
    s, r = eng.step(obs=ObsBundle(psi_rho=0.5, grad_rho=0.1, delta_tau_mass=0.05), seed=1234)
    assert r.kind == "BLOOMFORCE_STEP"
    assert isinstance(s.x, float)
