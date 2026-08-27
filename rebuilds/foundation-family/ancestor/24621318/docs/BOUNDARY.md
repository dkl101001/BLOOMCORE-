# Boundary Guarantees

BLOOMFORCE-CORE guarantees:

1) **No proprietary gate logic is encoded**
   - Gate is a `GateProvider` contract returning a scalar in [0,1].
   - Default gate is 1.0 (fully open).

2) **No proprietary observation reconstruction is encoded**
   - Observations can be provided directly as an `ObsBundle`.
   - `ObsProvider` is an interface for upstream derivation.

3) **Receipts are append-only and verifiable**
   - Receipt chain hashes include `{ts, kind, payload, prev_hash}`.
   - Verification recomputes hashes and checks prev links.

4) **Audit without control**
   - Receipts are produced for introspection and replay support.
   - The core engine does not enforce governance policies.
