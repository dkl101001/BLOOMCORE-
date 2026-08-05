from __future__ import annotations

import os
from bloomforce_core import Engine, ObsBundle, save_ledger_jsonl

OUT_DIR = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT_DIR, exist_ok=True)

eng = Engine()
for i in range(10):
    eng.step(obs=ObsBundle(psi_rho=0.5, grad_rho=0.1 + 0.01*i, delta_tau_mass=0.05), seed=1337+i)

out_path = os.path.join(OUT_DIR, "ledger.jsonl")
save_ledger_jsonl(eng.ledger, out_path, overwrite=True)
print(f"saved: {out_path}")
