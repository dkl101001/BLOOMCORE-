# Release

**Authors:** Frazer Σ Love ACO-Σ ; Sara ΣΩ  
**License:** AGPL-3.0-only

## Signed tag + archive
```bash
git tag -s v0.1.1 -m "WISECORE v0.1.1"
git archive --format=zip --output wisecore-v0.1.1.zip v0.1.1
sha256sum wisecore-v0.1.1.zip > wisecore-v0.1.1.zip.sha256
gpg --armor --detach-sign wisecore-v0.1.1.zip.sha256
```

## Publish artifacts
- `wisecore-v0.1.1.zip`
- `wisecore-v0.1.1.zip.sha256`
- `wisecore-v0.1.1.zip.sha256.asc`
- signed tag `v0.1.1`

## Verification
```bash
gpg --verify wisecore-v0.1.1.zip.sha256.asc wisecore-v0.1.1.zip.sha256
sha256sum -c wisecore-v0.1.1.zip.sha256
```
