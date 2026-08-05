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

Ruff at a 120-column line length, declared in this package's own
`pyproject.toml` under `[tool.ruff]` so a standalone clone lints identically to
the in-suite checkout:

```bash
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

Mypy runs with the strict-leaning options already in `pyproject.toml`
(`disallow_untyped_defs`, `check_untyped_defs`, `warn_return_any`). `bond_api`
ships without a `py.typed` marker, so it carries an `ignore_missing_imports`
override — drop that override if the protocol package later publishes stubs.

## Dead code and unreachable guards

A defensive branch that cannot fire is not safety, it is noise that inflates
the apparent test burden and hides a real invariant. If you can prove a guard
unreachable, delete it and write the proof into a comment at the site — as
`hydrology.max_flow` does for its augmenting-path bottleneck and
`cartel_graph.hhi` does for its non-empty commodity set. Do not reach for
`pragma: no cover` instead.

## Manuscript prose

Metrics are injected, never hand-authored. Use Pandoc-crossref for figures and
citations; keep literal `{{TOKEN}}` examples out of numbered sections (the live
cross-reference test flags them).
