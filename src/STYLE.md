# Style — QUANTUM src/

- Deterministic: no RNG, no wall-clock in any module or persisted artifact.
- Pure core: domain modules import stdlib only.
- Ruff (88-col): `uv run ruff format src/` then `uv run ruff check src/`.
- Mypy clean: `uv run mypy src/`.
- Full type hints + docstrings on every public symbol.
- Validation raises `ValueError`/`KeyError` with actionable messages.
