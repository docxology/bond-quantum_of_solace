# QUANTUM — Agent Working Agreement

Module/dir guide for agents working inside this BOND-suite film package. Read
[`docs/agent_instructions.md`](docs/agent_instructions.md) before modifying any
file.

## Scope and isolation

Work ONLY inside this directory. It is its own git repository with **no
remote** — never push. Commits are path-scoped (`git add -A` inside this repo
only).

## Layer contract

| Surface | Rule |
|---|---|
| `src/quantum_of_solace/hydrology.py`, `water_cartel.py`, `cartel_graph.py` | Pure, deterministic domain core — **stdlib only**, no `bond_api`, no infrastructure, no RNG, no wall-clock |
| `src/quantum_of_solace/analysis.py` | Assessment orchestrator; imports the domain core and the mission metadata only |
| `src/quantum_of_solace/mission.py` | Thin `bond_api` adapter; registers gadgets with the `GadgetRegistry` |
| `src/quantum_of_solace/manuscript_variables.py`, `figures.py` | Hydration / figure generators |
| `scripts/` | Thin orchestrators (sys.path bootstrap + argv forwarding) |

## Hard guardrails

- **No mocks** anywhere in `tests/` (no `MagicMock`/`@patch`/`create_autospec`).
- **≥90% line+branch coverage** on `src/`:
  `uv run pytest tests/ --cov=src --cov-fail-under=90`
- **Deterministic**: fixed seeds, no untracked RNG, no wall-clock in artifacts.
- **Ruff + mypy clean**: `uv run ruff check src/ scripts/ tests/`,
  `uv run ruff format src/ scripts/ tests/`, `uv run mypy src/ scripts/`.
- **No `template[_]code_project` lineage strings** (aim zero).
- Manuscript metrics are injected from `manuscript/config.yaml` +
  `src/quantum_of_solace/manuscript_variables.py`; never hand-author a metric
  in prose.

## Verification checklist

Run before calling work done:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
grep -r "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/ || echo Clean
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
git status --short   # clean after path-scoped commit
```
