import os, tempfile
from bloomforce_core import Engine, ObsBundle, save_ledger_jsonl, load_ledger_jsonl

def test_jsonl_save_load_strict():
    eng = Engine()
    for i in range(5):
        eng.step(obs=ObsBundle(psi_rho=0.5, grad_rho=0.1, delta_tau_mass=0.05), seed=2000+i)

    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "ledger.jsonl")
        save_ledger_jsonl(eng.ledger, p)
        led2 = load_ledger_jsonl(p, strict=True)
        assert len(led2.receipts) == len(eng.ledger.receipts)
        assert led2.verify_chain() is True
