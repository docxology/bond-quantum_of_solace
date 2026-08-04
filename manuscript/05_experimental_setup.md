# Experimental Setup

This package is a BOND-suite film repository with a `src/` layout, a local-only
git working tree, and ≥90% branch coverage enforced on `src/`.

## Software environment

* Python {{PYTHON_VERSION}} (the project pins `requires-python >= 3.10`)
* `numpy`, `matplotlib`, `pyyaml` as runtime dependencies
* `bond-api` (the frozen protocol) as a path dependency
* `pytest`, `pytest-cov`, `mypy`, `ruff` as dev dependencies

## Problem instances

All models run on fixed, deterministic instances documented in each module's
`default_*` factory:

* `default_network()` — three aquifers ({{HYDRO_TOTAL_SUPPLY}} units/period
  total) routing to two settlements over six evaporative routes.
* `default_dams()` — three reservoirs with matching downstream demands; the
  cartel controls two of them at a 50% restriction over twelve periods.
* `default_cartel()` — three actors controlling {{CARTEL_COMMODITIES}} with
  known shares; the shadow cartel leads water and lithium.

## Reproducibility

Result tokens (delivery, leverage, HHI) are computed by `run_quantum_assessment()`
and injected into the manuscript. The generation timestamp is {{GENERATION_TIMESTAMP}}
(from the config date) so hydration is deterministic. Migration between Python
versions is possible without changing any numeric result.
