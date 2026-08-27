# Signed Release Instructions (BLOOMFORCE-CORE)

This project supports **signed releases** in two layers:
1) **Artifact hashing** (SHA256SUMS)
2) **Artifact signing** (GPG) and optionally **Sigstore**

## 1) Generate SBOMs

```bash
make sbom
# or
python scripts/sbom_gen.py
```

Outputs:
- `sbom/sbom.cdx.json` (CycloneDX 1.5)
- `sbom/sbom.spdx.json` (SPDX 2.3)

## 2) Build distribution artifacts

```bash
make build
ls -lah dist/
python -m twine check dist/*
```

## 3) Generate checksum manifests

### Repo manifest
Creates `SHA256SUMS` for the repo content (excluding dist/build caches):

```bash
make checksums
# or
bash scripts/make_checksums.sh
```

### Dist manifest (recommended)
Create a dist-only manifest for the built artifacts:

```bash
(cd dist && sha256sum * > SHA256SUMS.dist)
```

## 4) Sign artifacts (GPG)

### One-time: create or choose a signing key
```bash
gpg --list-secret-keys --keyid-format=long
# If you need a new key:
gpg --full-generate-key
```

### Sign checksum manifests (recommended)
```bash
gpg --armor --detach-sign SHA256SUMS
gpg --armor --detach-sign dist/SHA256SUMS.dist
```

This produces:
- `SHA256SUMS.asc`
- `dist/SHA256SUMS.dist.asc`

### Sign the source distribution zip (optional)
If you distribute a zip/tarball directly, sign it too:
```bash
gpg --armor --detach-sign bloomforce-core-<ver>-fullstack.zip
```

## 5) Verification (what users do)

### Verify signatures
```bash
gpg --verify SHA256SUMS.asc SHA256SUMS
gpg --verify dist/SHA256SUMS.dist.asc dist/SHA256SUMS.dist
```

### Verify hashes
```bash
sha256sum -c SHA256SUMS
(cd dist && sha256sum -c SHA256SUMS.dist)
```

## 6) Optional: Sigstore (keyless signing)

If you want keyless signing with transparency logs, use Sigstore's `cosign`
or `sigstore` tooling.

Example (cosign, for dist artifacts):
```bash
cosign sign-blob --yes dist/bloomforce_core-<ver>-py3-none-any.whl > dist/bloomforce_core-<ver>-py3-none-any.whl.sig
cosign verify-blob --signature dist/bloomforce_core-<ver>-py3-none-any.whl.sig dist/bloomforce_core-<ver>-py3-none-any.whl
```

(Exact commands vary by tooling version; keep these as optional guidance.)

## Turnkey helper

Run this to perform lint/type/test, generate SBOM + checksums, build dist artifacts, and sign manifests (if GPG is available):

```bash
bash scripts/sign_release.sh
# or
make sign-release
```
