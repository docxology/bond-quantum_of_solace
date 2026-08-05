# QUANTUM — Quantum of Solace (2008)

Agent-facing documentation hub for this PROJECT BOND film package: deterministic
models of water-rights cartels, desert hydrology, commodity concentration,
scarcity pricing, aqueduct interdiction and cooperative power.

## Reading order

1. `agent_instructions.md` — the operational contract: scope, gates, the
   pure-core boundary, the frozen `bond_api` surface, computed metrics.
2. `architecture.md` — what each module in `src/quantum_of_solace/` computes,
   how `analysis.py` composes them, and how `mission.py` implements the frozen
   `MissionProvider`.
3. `testing_philosophy.md` — the zero-mock doctrine, what the coverage gate
   actually measures, and why an assertion must be able to fail.
4. `style_guide.md` — determinism, layer discipline, type hints, error messages.
5. `output_conventions.md` — the regenerable `output/` layout.

## File inventory

| File | Purpose |
|---|---|
| `README.md` | Index of this directory and pointers to the package-root docs |
| `agent_instructions.md` | Hard rules for agents working here |
| `architecture.md` | Module-by-module architecture and the frozen protocol surface |
| `testing_philosophy.md` | Real-data testing, coverage semantics, non-vacuous assertions |
| `style_guide.md` | Determinism, type hints, error-message conventions |
| `output_conventions.md` | What `output/` holds and how to regenerate it |

## The three things most likely to trip you

* **The frozen surface.** `mission.py`'s `MissionProvider` and `GADGET_REGISTRY`
  are consumed by other packages. Add, never rename or remove.
* **Dimensional consistency in `water_cartel.py`.** Inflow, max release and
  downstream demand are per-period rates; leverage compares horizon volumes.
  A ratio above 1 means someone divided a horizon volume by a rate again.
* **Numbers in prose.** Every metric arrives as a manuscript token. Two tests
  fail if one is typed by hand.
