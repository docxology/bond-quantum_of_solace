# QUANTUM — Agent Working Agreement

Build/test/verify guide for agents working inside this BOND-suite film package.
Read [`docs/agent_instructions.md`](docs/agent_instructions.md) before modifying
any file, and [`docs/architecture.md`](docs/architecture.md) before adding one.

## Scope and isolation

Work ONLY inside this directory. It is its own git repository, tracking
`origin/main` at `github.com/docxology/bond-quantum_of_solace`. Commits are
path-scoped (`git add -A` inside this repo only). Do not touch a sibling package, the bond root, or the template repo.

## Build

```bash
uv sync --extra dev
```

Runtime deps: `numpy`, `matplotlib`, `pyyaml`, and `bond-api` as a path
dependency on the recorded copy at `vendor/bond-api` (`[tool.uv.sources]` in
`pyproject.toml`; see `VENDOR.md`). Dev extras add `pytest`,
`pytest-cov`, `mypy`, `ruff` and `types-PyYAML`.

## Run

```bash
uv run python scripts/generate_analysis.py                # assessment JSON + six figures
uv run python scripts/z_generate_manuscript_variables.py  # the manuscript token map
uv run python scripts/run_mission.py full                 # the five-stage mission flow
uv run python scripts/run_mission.py recon "your goal"    # a single phase
```

`run_mission.py` exits 2 on an unknown phase, 1 on an unsuccessful outcome,
0 otherwise.

## Test

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90        # the gate
uv run pytest tests/test_hydrology.py -v                  # one module
uv run pytest tests/ -k leverage -v                       # one concern
```

The gate is line **and** branch coverage on `src/` with a 90% floor. Read the
`Missing` column, not just the exit code — a passing total can still hide an
unexercised error path. This file quotes no coverage percentage or test count
on purpose: run the command for the live figure.

## Verify

Run all of it before calling work done, and read the real output:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
grep -rn "unittest.mock\|MagicMock\|mocker.patch\|@patch\|create_autospec" tests/ || echo "no mocks"
grep -rn "template_[c]ode_project" . --exclude-dir=.venv --exclude-dir=.git || echo "no exemplar leftovers"
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/generate_analysis.py && uv run python scripts/z_generate_manuscript_variables.py
git status --short   # clean after a path-scoped commit
```

`uv` cannot write its cache under a restrictive sandbox. `Failed to initialize
cache` is an environment restriction, not a package failure — re-run with the
sandbox disabled.

## Layer contract

| Surface | Rule |
|---|---|
| `src/quantum_of_solace/hydrology.py`, `water_cartel.py`, `cartel_graph.py`, `pricing.py`, `resilience.py`, `shapley.py` | Pure, deterministic domain core — **stdlib only** (plus one sibling domain import for `resilience` and `shapley`), no `bond_api`, no infrastructure, no RNG, no wall clock |
| `src/quantum_of_solace/analysis.py` | The single assessment; imports the domain core only, and owns the fixed parameter constants |
| `src/quantum_of_solace/mission.py` | The only `bond_api` importer; a thin adapter with no mathematics of its own |
| `src/quantum_of_solace/manuscript_variables.py`, `figures.py` | Token hydration and figure generation, both reading `analysis.py` |
| `scripts/` | Thin orchestrators (`sys.path` bootstrap, argument dispatch, printing) — no business logic |

Machine-readable form: [`manuscript/layer_contract.yaml`](manuscript/layer_contract.yaml).

## Hard guardrails

- **Do not change the frozen surface.** `mission.py`'s `MissionProvider`
  (`brief`/`recon`/`plan`/`execute`/`debrief`) and `GADGET_REGISTRY` are
  consumed across packages. Add entries; never rename or remove.
- **No mocks** anywhere in `tests/` — no `MagicMock`, `unittest.mock`,
  `mocker.patch`, `@patch` or `create_autospec`.
- **Deterministic**: no untracked RNG, no wall clock in `src/` or in any
  persisted artifact. `MISSION_SEED` is recorded for provenance; nothing draws
  from it.
- **Ruff + mypy clean** on `src/`, `scripts/` and `tests/`.
- **No exemplar-lineage strings** (the name of the scaffold this package was
  forked from). The Verify command above checks it; its pattern is written as a
  bracket class so the check is not satisfied by its own text.
- **Never hand-author a metric** — not in the manuscript, not in these docs.
  Metrics are injected from `manuscript/config.yaml` plus
  `src/quantum_of_solace/manuscript_variables.py`, and two live tests fail if
  one is typed by hand.
- **Keep leverage dimensionally consistent.** Inflow, max release and
  downstream demand are per-period rates; every leverage ratio divides a
  horizon volume by a horizon volume. A leverage above 1 is a bug.
