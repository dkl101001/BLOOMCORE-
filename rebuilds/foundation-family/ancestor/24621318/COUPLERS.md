# Couplers Boundary (BLOOMFORCE-CORE)

This repo ships **BLOOMFORCE-CORE** only:
- engine core
- receipt ledger + verification
- provider interfaces (plug points)
- CLI + IO + tests

It intentionally does **NOT** ship proprietary modules.

## What is a coupler?

A coupler is anything that:
- derives observations from a proprietary substrate (e.g., holographic boundary reconstruction)
- computes gate values from proprietary criteria (e.g., ECA gate thresholds/mappings)
- injects governance constraints or domain lockouts

Couplers plug into the engine through provider interfaces.
