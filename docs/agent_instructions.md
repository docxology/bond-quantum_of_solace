# AI Agent Instructions — QUANTUM

Read this file before touching any other file in this project. It is the
operational contract; `architecture.md` explains what the code does and
`testing_philosophy.md` explains how it is proved.

## Rule 1 — Scope

Work ONLY inside this package directory. It is a local-only BOND-suite git repo
with **no remote** — never push, and never modify a sibling package, the bond
root, or the template repo. Commit with path-scoped commits in this repo only.

## Rule 2 — The coverage gate

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Line **and** branch coverage on `src/`, floored at 90%. If coverage drops, fix
the gap — do not delete a test to make the number work, and do not sprinkle
`pragma: no cover` over a branch you could have exercised. If a branch is
genuinely unreachable, delete it and write the reasoning into a comment at the
site.

## Rule 3 — The pure-core boundary

The six domain modules — `hydrology.py`, `water_cartel.py`, `cartel_graph.py`,
`pricing.py`, `resilience.py`, `shapley.py` — are **pure and
infrastructure-free**: standard library only (plus, for `resilience` and
`shapley`, one sibling domain module), no `bond_api`, no `infrastructure.*`, no
random draws, no wall clock.

`analysis.py` composes them and imports no `bond_api`. `mission.py` is the only
module that imports `bond_api`, and it adds no mathematics. `scripts/` are thin
orchestrators: `sys.path` bootstrap, argument dispatch, printing. A line in a
script that computes a flow, a leverage or an index is a boundary violation —
move it into `src/` and cover it with a test.

## Rule 4 — Do not change the frozen surface

`bond-cli`, the coordinator reconcile and the orchestrator consume this package
across the fleet through two module-level names in `mission.py`:

* `MissionProvider` with `brief`, `recon`, `plan`, `execute`, `debrief`;
* `GADGET_REGISTRY`, registering the subsystems under the slug.

Deepen *inside* the package — new domain modules, richer internals, additional
registry entries. Do not rename these, change their signatures, or drop an
existing gadget key. Changing what a `Finding` *says* is fine; changing the set
of labels a consumer may rely on is not.

## Rule 5 — Determinism

Fixed problem data, no untracked randomness, no wall clock in `src/` or in any
persisted artifact. `MISSION_SEED` is 0 and nothing draws from it — the seed is
recorded for provenance, not used as a control. A regeneration must reproduce
identical bytes; the manuscript timestamp comes from the config date, never
from `datetime.now()`.

## Rule 6 — Every metric is computed

Never hand-author a number in prose — not in the manuscript, not in the READMEs.
Result tokens come from `analysis.py` via `manuscript_variables.py` and
`scripts/z_generate_manuscript_variables.py`. Two live tests enforce this: one
re-derives the token map and fails if a token used in a numbered section is not
produced, the other fails on any bare decimal left in the results narrative.

The same discipline applies to documentation. Do not paste a coverage
percentage or a test count into a doc — describe the gate and let the reader
run it. A quoted figure is stale the next time a module lands.

If you state a new quantitative result, the order is: add the value to the
assessment in `analysis.py` → add a token in `manuscript_variables.py` → add a
test that the token matches its source → reference the token in prose.

## Rule 7 — Show, not tell

Reference concrete files and functions
(`src/quantum_of_solace/hydrology.py::max_flow`), not vague descriptions, so
every claim can be checked against the code.

## Verification checklist

Run all of it before calling work done, and read the real output rather than
just the exit codes:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
grep -rn "unittest.mock\|MagicMock\|mocker.patch\|@patch\|create_autospec" tests/ || echo "no mocks"
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
grep -rn "template_code_project" . --exclude-dir=.venv --exclude-dir=.git || echo "no exemplar leftovers"
uv run python scripts/generate_analysis.py
uv run python scripts/z_generate_manuscript_variables.py
git status --short   # clean after a path-scoped commit
```

`uv` cannot write its cache under a restrictive sandbox. A
`Failed to initialize cache` error is an environment restriction, not a package
failure — re-run with the sandbox disabled.
