# Quantum of Solace — QUANTUM

Special-agent mission software for the 2008 film *Quantum of Solace*, built as
one package of the **PROJECT BOND** suite (codename **QUANTUM**). It is bound
to the suite's frozen `bond_api` mission protocol, so the fleet orchestrator
can discover and drive it by slug.

## The film, as a specification

*Quantum of Solace* is the Bond film in which the villain never points a
weapon at a city. Dominic Greene's organisation buys a stretch of Bolivian
desert, quietly corners the aquifer beneath it, and then sells the country's
own water back to it. The threat is entirely structural: control a scarce
resource's distribution and you have coercive power without firing a shot.

That premise decomposes into six questions, and each one is a module in this
package:

| Question the film raises | Module | What it computes |
|---|---|---|
| How much water actually reaches the settlements? | `quantum_of_solace/hydrology.py` | A directed desert network of aquifers, evaporative routes and settlements: per-node mass balance, Dijkstra routing over evaporation-adjusted delivered cost, Edmonds–Karp maximum flow, residual reachability, and network surgery |
| What does holding the dams get you? | `quantum_of_solace/water_cartel.py` | Period-by-period reservoir simulation under a withholding restriction; withheld volume, horizon demand, per-dam and aggregate cartel leverage as a share in `[0, 1]` |
| Is the grip systemic or just local? | `quantum_of_solace/cartel_graph.py` | A bipartite actor→commodity control graph: Herfindahl–Hirschman index per commodity and portfolio-wide, top-k concentration ratios, dominance maps, diversification, and Merger-Guidelines band classification |
| What is the withheld water worth? | `quantum_of_solace/pricing.py` | Linear inverse demand: market-clearing scarcity price, point elasticity, scarcity rent on a restricted supply, the monopoly solution (MR = MC), consumer surplus and deadweight loss |
| What if they cut the aqueducts instead? | `quantum_of_solace/resilience.py` | Per-route interdiction criticality, greedy worst-case attack sequences, a single-cut resilience index, and minimum cuts via the max-flow/min-cut theorem |
| Who can actually capture the value? | `quantum_of_solace/shapley.py` | Multi-resource control as a transferable-utility coalition game, solved exactly: Shapley values, normalised Banzhaf–Coleman index, power ranking, dominance gap |

Three further modules bind those six together:

| Module | Role |
|---|---|
| `quantum_of_solace/analysis.py` | The single deterministic assessment. Six `assess_*` functions plus `run_quantum_assessment()`, run on fixed `default_*` instances. Genuinely composed: pricing takes its supplies from the reservoir simulation, interdiction attacks the same hydrology network the delivery figures come from |
| `quantum_of_solace/mission.py` | The thin `bond_api` adapter (see below). Adds no mathematics |
| `quantum_of_solace/figures.py` | Six deterministic matplotlib generators, one per model |
| `quantum_of_solace/manuscript_variables.py` | Hydrates the manuscript token map from `manuscript/config.yaml` plus the live assessment |

Every reported number is computed from these modules on fixed instances —
never hand-authored.

## The MissionProvider surface

`quantum_of_solace/mission.py` exposes the frozen protocol that `bond-cli`, the
coordinator and the orchestrator consume across packages. **Its public shape
does not change**; deepening happens inside the package.

```python
from quantum_of_solace.mission import MissionProvider, GADGET_REGISTRY

provider = MissionProvider()          # provider.film == "quantum_of_solace"
brief    = provider.brief()           # codename, objectives, model assets, constraints
report   = provider.recon(request)    # eight findings, each a measured number
plan     = provider.plan(brief)       # eight deterministic steps
outcome  = provider.execute(plan)     # full assessment + Provenance(version, seed, sha256)
debrief  = provider.debrief(outcome)  # six standing lessons
```

`GADGET_REGISTRY` is a module-level `GadgetRegistry` holding the six
subsystem entry points — `hydrology`, `water_cartel`, `cartel_graph`,
`pricing`, `resilience`, `shapley` — plus `full_assessment`, all registered
under the `quantum_of_solace` slug.

## Layout

```
src/quantum_of_solace/   pure domain core + mission adapter + manuscript hydration
scripts/                 thin CLIs (run_mission, generate_analysis, manuscript vars)
tests/                   real-data tests, zero mocks
manuscript/              token-hydrated sections + config + references
docs/                    agent-facing documentation hub
output/                  regenerable analysis artifacts (git-ignored)
```

## Quick start

```bash
uv sync --extra dev

uv run python scripts/generate_analysis.py                # assessment JSON + six figures
uv run python scripts/z_generate_manuscript_variables.py  # the manuscript token map
uv run python scripts/run_mission.py full                 # the five-stage mission flow
```

`run_mission.py` also accepts a single phase — `brief`, `recon`, `plan`,
`execute` or `debrief` — and an optional goal string:

```bash
uv run python scripts/run_mission.py recon "map the Bolivian aquifer network"
```

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

The suite is real-computation only — no mock framework anywhere in `tests/` —
and the coverage gate measures line **and** branch coverage on `src/` with a
90% floor. This README deliberately quotes no coverage percentage or test
count: run the command for the current figure rather than trusting a number
that goes stale.

## Project BOND

Local-only working tree; never push. One of 27 film packages plus the shared
infrastructure (`bond-api`, `bond-utilities`, `bond-coordinator`,
`bond-orchestrator`, `bond-cli`, `bond-ops`). This package binds to _only_
`bond-api` (the frozen protocol); the domain core stays importable without it.
See [`docs/agent_instructions.md`](docs/agent_instructions.md) for the
guardrails and [`docs/architecture.md`](docs/architecture.md) for the
module-by-module map.
