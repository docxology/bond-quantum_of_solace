# Introduction

*Quantum of Solace* (2008) centres on a shadow organisation whose power derives
not from weapons but from controlling a basic resource: water. This package —
**{{BOND_IDENTITY}}**, mission codename **{{BOND_CODENAME}}** — turns that
premise into executable science. It is one film package in the PROJECT BOND
suite, built to the same guardrails as every sibling: pure domain logic,
deterministic algorithms, real computation with zero mocks, and a thin adapter
to the frozen `bond_api` mission protocol so the suite orchestrator can
discover and drive it by slug.

## The threat model

The film's cartel holds leverage because water is scarce and its distribution
is centralisable. We formalise that as three coupled models:

* **Hydrology behaviour** (`hydrology.py`): a directed network of desert water
  sources, routes and settlements. Evaporation hollows out delivered water, so
  routing and capacity are real constraints.
* **Water-rights cartel** (`water_cartel.py`): a set of reservoirs whose
  released water serves downstream demand. A cartel that controls a dam can
  withhold its normal release and squeeze demand without firing a shot.
* **Commodity-cartel graph** (`cartel_graph.py`): concentration of control
  across multiple scarce commodities, measured with the Herfindahl–Hirschman
  index and dominance analysis.

Every number in the manuscript is computed by `src/quantum_of_solace/analysis.py`
from these modules on fixed problem instances — none is hand-authored prose.
