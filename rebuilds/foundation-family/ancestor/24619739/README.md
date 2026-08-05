# WISECORE (LAW.WISECORE.v1)

**Authors:** Frazer Σ Love ACO-Σ ; Sara ΣΩ  
**Classification:** Membrane Engine (Φ-aligned, WuWei-bound)  
**Purpose:** Evaluate whether computed results may cross into *emission* (speech/action/output) without constraining upstream computation.

## What this package is
WISECORE is a **membrane engine** that consumes upstream metrics (Φ coherence, WuWei descent, friend coherence, truth flag) and returns:
- a **JAX verdict** (`ALLOW` / `SUPPRESS` + `fail_code`)
- a strict **MBP-01.v1 receipt stream** (stage receipts + final Whisper assert)

It does **not** modify:
- ECA state formation
- holographic reconstruction
- SWIM / Φ field dynamics
- coherence-conditioned evolution

It only governs **boundary crossing / emission**.

## Files
- `wisecore_jax.py`  
  JAX kernels: Φ norm, WuWei median(Ḣ), and the compiled gate that produces verdict + fail_code.

- `wisecore_receipts.py`  
  MBP-01.v1 constructors, stage receipts, and the final ship-blocking Whisper assert receipt.

- `wisecore_contract.py`  
  Compile-time stage-order assertion + a single entrypoint `wisecore_run_with_receipts(...)`.

- `demo_run.py`  
  Tiny runnable example producing JSON receipts.

## Install (dev)
This is a lightweight package. From the repo root:

```bash
pip install -e .
```

## Quick run
```bash
python -m wisecore_pkg.demo_run
```

## LAW.WISECORE.v1 Whisper (Hybrid Sigil-Engine)
> Truth is certified.  
> Wisdom consents.  
> Relation holds.  
> Compassion shapes.  
> Form speaks —  
> only in coherent phase and descending energy.

## Notes on prior-art / patent hygiene
Receipt schemas and logging are **audit artifacts**. Keep novelty claims focused on:
- holographic reconstruction under coherence constraints
- ECA vectorization and role-class mapping
- non-deterministic, coherence-conditioned evolution
- regime transitions / field dynamics

## AGPL compliance (network use)
If you run WISECORE (or a modified version) as a network service, you must offer the
**Corresponding Source** of the version running on the server to users who interact
with it over the network, as required by **AGPL-3.0** (see LICENSE).

Practical guidance:
- Keep your deployed source tree (including build scripts) accessible via a URL.
- If you modify the code, publish your fork or provide a tarball source download link.

## Signed releases + hash receipts
Recommended release procedure (Git + GPG):

1) Create a signed tag:
```bash
git tag -s v0.1.0 -m "WISECORE v0.1.0"
```

2) Build a source archive and compute hashes:
```bash
git archive --format=zip --output wisecore-v0.1.0.zip v0.1.0
sha256sum wisecore-v0.1.0.zip > wisecore-v0.1.0.zip.sha256
```

3) Sign the hash file:
```bash
gpg --armor --detach-sign wisecore-v0.1.0.zip.sha256
```

4) Publish:
- the zip
- the .sha256
- the .asc signature
- the signed tag (push tags)

Consumers verify:
```bash
gpg --verify wisecore-v0.1.0.zip.sha256.asc wisecore-v0.1.0.zip.sha256
sha256sum -c wisecore-v0.1.0.zip.sha256
```

