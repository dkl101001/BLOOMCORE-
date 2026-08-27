# Provisional Appendix — Method of Operation (BLOOMFORCE-CORE)

This appendix describes the public engine cut and its operation as a recursive
state-update mechanism producing an append-only, hash-chained receipt ledger.

## Inputs
- `ObsBundle = {psi_rho, grad_rho, delta_tau_mass}`
- gate scalar `G in [0,1]` supplied by a GateProvider (default 1.0)
- stochastic source (seeded or stateful); optional snapshots for reconstructive replay

## State
- `BloomforceState = {tick, x, last_force, rng_state}`

## Step
1) gate: `G = clamp01(GateProvider(S_t, O_t, rng))`
2) forcing: `F_bloom = a*grad_rho + b*delta_tau_mass` (clamped)
3) effective: `F_eff = G * F_bloom`
4) update: `x_{t+1} = x_t + F_eff`
5) receipt: append hash-chained record of obs/gate/forces/state
6) optional: snapshot RNG state to support reconstructive replay

## Boundary
The gate logic and observation reconstruction are couplers and are excluded from the public engine.
