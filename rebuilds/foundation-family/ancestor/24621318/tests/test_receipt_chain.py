from bloomforce_core import Engine, ObsBundle

def test_receipt_chain_verifies():
    eng = Engine()
    for i in range(10):
        eng.step(obs=ObsBundle(psi_rho=0.5, grad_rho=0.1 + 0.01*i, delta_tau_mass=0.05), seed=1000+i)
    assert eng.ledger.verify_chain() is True
