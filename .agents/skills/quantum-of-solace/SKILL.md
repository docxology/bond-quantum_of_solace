---
name: quantum-of-solace
description: Build and maintain the QUANTUM BOND-suite film package for Quantum of Solace (2008): water-rights cartel, desert hydrology, commodity-cartel graph.
---

# quantum-of-solace

Film package in PROJECT BOND (codename **QUANTUM**). Models the *Quantum of
Solace* threat — a shadow cartel's control of water and scarce commodities — as
three deterministic domain modules bound to the frozen `bond_api` protocol.

## When to use

- Building or maintaining this package's domain core, mission adapter, scripts,
  tests, manuscript, or metadata.
- Verifying the package against the BOND guardrails before a path-scoped commit.

## Quick reference

```bash
uv sync --extra dev
uv run python scripts/generate_analysis.py
uv run python scripts/run_mission.py full
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format src/ scripts/ tests/
uv run mypy src/ scripts/
```

## Domain core (stdlib-only, deterministic, no bond_api)

- `src/quantum_of_solace/hydrology.py` — desert water network: aquifers,
  routes, settlements; mass balance, Dijkstra shortest-effort routing,
  Edmonds–Karp maximum flow.
- `src/quantum_of_solace/water_cartel.py` — reservoir simulation and
  cartel leverage from withholding downstream releases.
- `src/quantum_of_solace/cartel_graph.py` — multi-resource commodity control:
  Herfindahl–Hirschman concentration, dominance, diversification.

`analysis.py` is the single deterministic assessment source; `mission.py` binds
to `bond_api` and registers gadgets.

## Pitfalls

- Keep the three domain modules free of `bond_api`/infrastructure imports.
- Never hand-author a metric in manuscript prose — hydrate via
  `manuscript_variables.py` + `manuscript/config.yaml`.
- After exploratory runs, re-run the canonical scripts so `output/` (git-ignored)
  returns to a clean, deterministic state.
- `bond-api` ships without `py.typed`; `pyproject.toml` carries a mypy
  `ignore_missing_imports` override for it.
