# Experimental Setup

This package is a BOND-suite film repository with a `src/` layout, its own git
repository, and a line-and-branch coverage floor enforced on `src/` by the
package's own pytest gate.

## Software environment

* Python {{PYTHON_VERSION}} (the project pins `requires-python >= 3.10`)
* `numpy`, `matplotlib`, `pyyaml` as runtime dependencies
* `bond-api` (the frozen protocol) as a path dependency
* `pytest`, `pytest-cov`, `mypy`, `ruff` as dev dependencies

Lint and format settings are declared in this package's own `pyproject.toml`,
so a standalone clone lints identically to the in-suite checkout.

## Problem instances

All models run on fixed, deterministic instances built by each module's
`default_*` factory. Every parameter quoted below is a manuscript token read
back out of the running assessment, not a number transcribed into prose:

* `default_network()` — {{HYDRO_AQUIFER_COUNT}} aquifers
  ({{HYDRO_TOTAL_SUPPLY}} units/period total) routing to
  {{HYDRO_SETTLEMENT_COUNT}} settlements ({{HYDRO_SETTLEMENTS}}) over
  {{HYDRO_ROUTE_COUNT}} evaporative routes, {{HYDRO_NODE_COUNT}} nodes in all.
* `default_dams()` — {{CARTEL_DAM_COUNT}} reservoirs with per-period downstream
  demands; the cartel controls {{CARTEL_CONTROLLED_DAMS}} of them at a
  {{CARTEL_RESTRICTION_PCT}}% restriction over {{CARTEL_PERIODS}} periods,
  giving a horizon demand base of {{CARTEL_HORIZON_DEMAND}} units.
* `default_cartel()` — {{CARTEL_ACTOR_COUNT}} actors ({{CARTEL_ACTORS}})
  controlling {{CARTEL_COMMODITIES}} with known shares; the shadow cartel leads
  water and lithium.
* `default_demand()` — a linear inverse demand curve with intercept
  `a = {{PRICE_DEMAND_A}}` and slope `b = {{PRICE_DEMAND_B}}`, at a constant
  marginal delivery cost of {{PRICE_MARGINAL_COST}}. Baseline and restricted
  supply are *measured* from the dam-fleet simulation
  ({{PRICE_SUPPLY_BASELINE}} → {{PRICE_SUPPLY_RESTRICTED}} units/period), not
  assumed.
* `default_weights()` — canonical Shapley commodity weights
  ({{SHAPLEY_WEIGHTS}}) over the diminishing-returns control value function.
* `INTERDICTION_STEPS` — {{RESIL_SEQ_STEPS}} cuts in the canonical greedy
  worst-case interdiction sequence.

## Determinism

Result tokens are computed by `run_quantum_assessment()` and injected into the
manuscript. The mission seed is {{MISSION_SEED}} and no model draws a random
number, so seeding is a formality rather than a control. The generation
timestamp is {{GENERATION_TIMESTAMP}}, taken from the config date rather than
the wall clock, so hydration is reproducible. The exact-enumeration Shapley and
Banzhaf solvers evaluate all `2^n` coalitions rather than sampling, so power
indices carry no estimation error. Migration between Python versions leaves
every numeric result unchanged.
