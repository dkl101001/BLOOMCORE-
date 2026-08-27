# Contributing

1) Install dev deps:
```bash
python -m pip install -e ".[dev]"
```

2) Run checks:
```bash
make lint type test
```

3) Pre-commit:
```bash
pre-commit install
pre-commit run -a
```
