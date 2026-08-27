PY ?= python

.PHONY: install-dev lint format type test smoke audit build verify clean distclean

install-dev:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e ".[dev]"

lint:
	$(PY) -m ruff check .

format:
	$(PY) -m ruff check . --fix
	$(PY) -m ruff format .

type:
	$(PY) -m pyright

test:
	$(PY) -m pytest -q

smoke:
	$(PY) -m bloomforce_core run --steps 3 --summary
	$(PY) -m bloomforce_core run --steps 5 --save /tmp/bloomforce_ledger.jsonl
	$(PY) -m bloomforce_core verify --load /tmp/bloomforce_ledger.jsonl

audit:
	$(PY) -m pip_audit -r <($(PY) -m pip freeze) || true

build:
	$(PY) -m build

verify:
	bash scripts/ship_smoke.sh

clean:
	@find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf
	@rm -rf .pytest_cache .ruff_cache

distclean: clean
	@rm -rf dist build *.egg-info

.PHONY: sbom checksums

sbom:
	python scripts/sbom_gen.py

checksums:
	bash scripts/make_checksums.sh


.PHONY: sign-release
sign-release:
	bash scripts/sign_release.sh
