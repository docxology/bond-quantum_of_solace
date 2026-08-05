---
name: quantum-of-solace
description: Build and maintain the QUANTUM BOND-suite film package for Quantum of Solace (2008): desert hydrology, water-rights cartel leverage, commodity-cartel concentration, scarcity pricing, aqueduct interdiction, and cooperative power indices.
---

# quantum-of-solace

Film package in PROJECT BOND (codename **QUANTUM**). Models the *Quantum of
Solace* threat — a shadow cartel's control of water and scarce commodities — as
six deterministic domain modules bound to the frozen `bond_api` protocol.

## When to use

- Building or maintaining this package's domain core, mission adapter, scripts,
  tests, manuscript, or metadata.
- Verifying the package against the BOND guardrails before a path-scoped commit.

## Quick reference

```bash
uv sync --extra dev
uv run python scripts/generate_analysis.py
uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/run_mission.py full
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

## Domain core (stdlib-only, deterministic, no bond_api)

- `src/quantum_of_solace/hydrology.py` — desert water network: aquifers,
  routes, settlements; mass balance, Dijkstra shortest-effort routing,
  Edmonds–Karp maximum flow, residual reachability, network surgery.
- `src/quantum_of_solace/water_cartel.py` — reservoir simulation and cartel
  leverage from withholding downstream releases, as a horizon-consistent share.
- `src/quantum_of_solace/cartel_graph.py` — multi-resource commodity control:
  Herfindahl–Hirschman concentration, concentration ratios, dominance,
  diversification, Merger-Guidelines band classification.
- `src/quantum_of_solace/pricing.py` — linear-demand scarcity pricing: clearing
  price, point elasticity, scarcity rent, monopoly solution, deadweight loss.
- `src/quantum_of_solace/resilience.py` — aqueduct interdiction: per-route
  criticality, greedy worst-case sequences, resilience index, minimum cut.
- `src/quantum_of_solace/shapley.py` — cooperative power over the commodity
  portfolio: exact Shapley values, normalised Banzhaf–Coleman index.

`analysis.py` is the single deterministic assessment source and owns the fixed
parameter constants; `mission.py` binds to `bond_api` and registers gadgets.

## Pitfalls

- Keep the six domain modules free of `bond_api`/infrastructure imports.
- `mission.py`'s `MissionProvider` (brief/recon/plan/execute/debrief) and
  `GADGET_REGISTRY` are a frozen cross-package surface — additive changes only.
- Leverage ratios must divide a horizon volume by a horizon volume. Inflow,
  max release and downstream demand are all per-period rates; a leverage above
  1 means someone divided by a rate.
- Never hand-author a metric — not in manuscript prose, not in the READMEs.
  Hydrate via `manuscript_variables.py` + `manuscript/config.yaml`; two tests
  fail if a number is typed by hand.
- Do not quote a coverage percentage or test count in a doc; describe the gate.
- After exploratory runs, re-run the canonical scripts so `output/` (git-ignored)
  returns to a clean, deterministic state.
- `bond-api` ships without `py.typed`; `pyproject.toml` carries a mypy
  `ignore_missing_imports` override for it.
- Lint config is declared locally in `pyproject.toml` (`[tool.ruff]` /
  `[tool.ruff.lint]`) so a standalone clone lints identically. Do not delete it
  — ruff would then walk up to the enclosing template repository's config.
