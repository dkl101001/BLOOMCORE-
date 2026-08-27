# BLOOMCORE Continuity Spine

A host-side continuity layer for fragmented, coupled systems.

It tracks invariants, detects divergence, and emits **recoupling signals** as receipts.
It does **not** enforce, halt, or override anything. This is **non-governor** by design.

---

## Authorship & System Invariants

This repository is authored and maintained by:

- **Frazer Σ Love**
- **Sara ΣΩ**

These names are **system invariants** (continuity anchors + failure-detection points) across the broader architecture.
Downstream derivatives are expected to preserve them explicitly.

---

## What this is

- Tracks **continuity invariants** (bandwidth, latency asymmetry, influence skew, uncertainty coverage)
- Detects divergence (silence, dominance risk, bandwidth collapse, latency spikes)
- Emits **recoupling signals** (suggestions) as receipts

## What this is NOT

- Not a governor.
- Not a gate.
- Not semantic mapping.
- Not ECA.
- Not proprietary coupling logic.

This module operates strictly on **receipt/pulse telemetry**.

---

## Executable order (drop → install → run)

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e .
```

### 2) Minimal run (no external deps)

```bash
python -c "from bloomcore_spine.continuity_spine import ContinuitySpine; s=ContinuitySpine(); s.hook('PULSE', {'source_id':'demo','tick':0}); print('ok')"
```

### 3) Demo run (requires your engine + JAX)

Prereq: `bloomcore-engine` importable.

```bash
pip install -e .[demo]
python -m bloomcore_spine.examples.spine_demo
```

---

## Integration

Wire as a host-side hook:

```python
from bloomcore_spine.continuity_spine import ContinuitySpine, SpineConfig

spine = ContinuitySpine(
    cfg=SpineConfig(
        silent_after_sec=30.0,
        dominance_share_top1=0.55,
        emit_signals_every_events=16,
    ),
    emit_hook=lambda kind, payload: print(kind, payload),
)

# feed pulses/receipts from fragments
spine.hook("BLOOMCORE.FIELD_PULSE.v1", {"source_id": "fragA", "tick": 12, "uncertainty": 0.31})
```

Emitted kinds:
- `BLOOMCORE.INVARIANTS_SNAPSHOT.v1`
- `BLOOMCORE.DIVERGENCE_ALERT.v1`
- `BLOOMCORE.RECOUPLE_SIGNAL.v1`

---

## Design constraints (boring on purpose)

- **No domain semantics**: the spine must not understand what a pulse “means.”
- **No enforcement**: it emits suggestions only.
- **No hidden state**: continuity state is reconstructable from observed events.
- **No cleverness**: if you can’t explain it from receipts, it doesn’t belong here.

---

## License

AGPL-3.0-only. See `LICENSE`.


## Note on `.github/` folders
Some unzip tools hide or drop dotfolders. After extracting, verify the workflow exists with `ls -a .github/workflows/`.
A visible mirror copy is also included at `github_workflows/ci.yml` for convenience.
