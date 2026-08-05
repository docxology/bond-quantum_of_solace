# Quantum of Solace — QUANTUM

Special-agent mission software for the 2008 film *Quantum of Solace*, built as
one package of the **PROJECT BOND** suite (codename **QUANTUM**). The film's
central threat — a shadow cartel whose leverage rests on controlling water and
the logistics around scarce commodities — is modelled with three deterministic,
real-data mathematical modules, all bound to the suite's frozen `bond_api`
mission protocol.

## What it models

| Module | Concept | Algorithms |
|---|---|---|
| `quantum_of_solace/hydrology.py` | Desert water network (sources, routes, settlements, evaporation) | Mass balance, Dijkstra shortest-effort routing, Edmonds–Karp maximum flow, route removal / min-cut support |
| `quantum_of_solace/water_cartel.py` | Water-rights cartel: reservoirs serving downstream demand | Period reservoir simulation, withheld-volume leverage, aggregate cartel leverage |
| `quantum_of_solace/cartel_graph.py` | Multi-resource commodity control | Herfindahl–Hirschman concentration, top-k concentration ratios, dominance, diversification |
| `quantum_of_solace/pricing.py` | Water scarcity & monopoly economics | Linear inverse demand, market-clearing scarcity price, elasticity, monopoly price/DWL, scarcity rent |
| `quantum_of_solace/resilience.py` | Aqueduct interdiction & network fragility | Per-route criticality, greedy worst-case interdiction, resilience index, min-cut (max-flow/min-cut theorem) |
| `quantum_of_solace/shapley.py` | Cooperative power over the commodity portfolio | Exact Shapley value, normalised Banzhaf–Coleman index, power ranking, dominance gap |

Every reported number is computed from the domain modules on fixed instances —
never hand-authored. `quantum_of_solace/analysis.py` is the single assessment
source of truth consumed by the mission, figures, and manuscript variables.

## Layout

```
src/quantum_of_solace/   pure domain core + mission adapter + manuscript hydration
scripts/                 thin CLIs (run_mission, generate_analysis, manuscript vars)
tests/                   real-data tests, zero mocks
manuscript/              token-hydrated sections + config
docs/                    agent-facing documentation hub
output/                  regenerable analysis artifacts (git-ignored)
```

## Quick start

```bash
uv sync --extra dev
uv run python scripts/generate_analysis.py              # assessment JSON + figures
uv run python scripts/z_generate_manuscript_variables.py  # {{TOKEN}} map
uv run python scripts/run_mission.py full               # five-stage mission flow
uv run pytest tests/ --cov=src --cov-fail-under=90      # the coverage gate
```

## Project BOND

Local-only working tree; never push. One of 27 film packages plus the shared
infrastructure (`bond-api`, `bond-utilities`, `bond-orchestrator`, …). This
package binds to _only_ `bond-api` (the frozen protocol); the domain core stays
importable without it. See `docs/agent_instructions.md` for the guardrails.
