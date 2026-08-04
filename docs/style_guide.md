# Style Guide — QUANTUM

## Determinism first

`src/` makes no random draws and reads no wall clock; every algorithm is a pure
function of its fixed inputs. Persisted artifacts are byte-reproducible. When a
draw is ever needed (future models), use a fixed, documented seed.

## Layer discipline

Mathematical content lives in `src/` — never in `scripts/`. A line in a script
that computes the algorithm's output (a flow, a leverage, an HHI) is a boundary
violation; move it into `src/` and cover it with a test.

## Type hints + docstrings

Every public function is annotated and documented. The domain modules carry
docstrings explaining *what* they compute and *why it matters* to the film.

## Error messages

Validation raises `ValueError` with an actionable message (`"Dam.initial_storage
cannot exceed Dam.capacity"`), not bare asserts. Lookup functions raise
`KeyError` with the offending name.

## Formatting

Ruff (88-col default): `uv run ruff format src/ scripts/ tests/`. Mypy clean
(`uv run mypy src/ scripts/`). Use `--strict`-style config already in
`pyproject.toml` (`disallow_untyped_defs`, `warn_return_any`).

## Manuscript prose

Metrics are injected, never hand-authored. Use Pandoc-crossref for figures and
citations; keep literal `{{TOKEN}}` examples out of numbered sections (the live
cross-reference test flags them).
