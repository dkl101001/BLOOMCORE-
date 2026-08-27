#!/bin/sh
set -eu

MANIFEST="${1:-HASHES.sha256}"

if ! command -v openssl >/dev/null 2>&1; then
  echo "openssl not found; cannot sign" >&2
  exit 2
fi

if [ ! -f "release_private.pem" ] || [ ! -f "release_public.pem" ]; then
  openssl genpkey -algorithm RSA -out release_private.pem -pkeyopt rsa_keygen_bits:3072
  openssl rsa -pubout -in release_private.pem -out release_public.pem
fi

openssl dgst -sha256 -sign release_private.pem -out "${MANIFEST}.sig" "${MANIFEST}"

echo "Signed ${MANIFEST} -> ${MANIFEST}.sig"
echo "Public key: release_public.pem"
