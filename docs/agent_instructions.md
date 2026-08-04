# AI Agent Instructions — QUANTUM

Read this file before touching any other file in this project.

## Rule 1 — Scope

Work ONLY inside this package directory. It is a local-only BOND-suite git repo
with no remote. Never modify a sibling package, the bond root, or the template
repo. Commit your own work with path-scoped commits in this repo only.

## Rule 2 — Coverage gate (≥90% on `src/`)

The suite enforces ≥90% line+branch coverage on `src/`:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

All tests use real computation — no mocks. If coverage drops, fix the gap; do
not delete tests to make the number work.

## Rule 3 — The pure-core boundary

The three domain modules (`hydrology.py`, `water_cartel.py`, `cartel_graph.py`)
are **pure and infrastructure-free**: stdlib only, no `bond_api`, no
`infrastructure.*`, no random draws, no wall-clock. `mission.py` is the thin
adapter that binds them to `bond_api`; `scripts/` are thin orchestrators (no
business logic). Test the boundary judgement: mathematical content lives in
`src/`, orchestration in `scripts/`.

## Rule 4 — Determinism

Fixed problem data, fixed seeds, no untracked randomness, no wall-clock in
`src/` or persisted artifacts. A regeneration must reproduce identical output.

## Rule 5 — Manuscript variables are computed

Never hand-author a metric in manuscript prose. Result tokens come from
`quantum_of_solace/analysis.py` via `manuscript_variables.py` and
`scripts/z_generate_manuscript_variables.py`. The live cross-reference test
fails if a token used in a numbered section is not generated.

## Rule 6 — Show, not tell

Reference concrete files and functions (`src/quantum_of_solace/hydrology.py::max_flow`),
not vague descriptions, so claims can be verified against the code.

## Verification checklist

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
grep -r "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/ || echo Clean
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
git status --short   # clean after commit
```
