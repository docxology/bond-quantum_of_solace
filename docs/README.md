# docs/ — QUANTUM (Quantum of Solace, 2008)

The agent-facing documentation hub for this BOND-suite film package. Everything
here describes *this* package — the desert-hydrology, water-cartel, commodity
concentration, scarcity-pricing, aqueduct-interdiction and cooperative-power
models in `src/quantum_of_solace/` — not the exemplar it was forked from.

## What lives here

| File | Read it when you need |
|---|---|
| [`agent_instructions.md`](agent_instructions.md) | The hard rules: scope, the coverage gate, the pure-core boundary, determinism, computed manuscript metrics. **Read first, before editing anything.** |
| [`architecture.md`](architecture.md) | Module-by-module map of `src/`, how the six domain models compose through `analysis.py`, and how `mission.py` implements the frozen `bond_api` `MissionProvider`. |
| [`testing_philosophy.md`](testing_philosophy.md) | Why there are no mocks, what the coverage gate really measures, and which tests bind claims to computed values. |
| [`style_guide.md`](style_guide.md) | Determinism, layer discipline, type hints, error-message conventions, formatting. |
| [`output_conventions.md`](output_conventions.md) | What `output/` holds, which generator writes each artifact, and how to regenerate everything. |
| [`AGENTS.md`](AGENTS.md) | The short file inventory and reading order for this directory. |

## Where the rest of the truth lives

* [`../README.md`](../README.md) — what the package is and how to run it.
* [`../AGENTS.md`](../AGENTS.md) — the working agreement and verification checklist.
* [`../TODO.md`](../TODO.md) — what is actually left to do.
* [`../manuscript/AGENTS.md`](../manuscript/AGENTS.md) — the manuscript token
  protocol and the figure/label table.
* [`../manuscript/layer_contract.yaml`](../manuscript/layer_contract.yaml) —
  the machine-readable form of the layer rules stated in `architecture.md`.

## The one rule that governs all of these

No number in this package is written by hand. Results come from
`quantum_of_solace/analysis.py`, reach the manuscript as tokens through
`manuscript_variables.py`, and are checked by a live test that re-derives the
token map and fails on any token used in prose but not produced — plus a second
test that fails on any bare decimal left in the results narrative.
