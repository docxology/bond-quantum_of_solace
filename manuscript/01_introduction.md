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

The film's cartel holds leverage because water is scarce, its distribution is
centralisable, and the same organisation spreads its grip across neighbouring
commodities. We formalise that as six coupled models, each a separate module in
the pure domain core.

**The physical layer — where the water is and how it moves.**

* **Desert hydrology** (`hydrology.py`): a directed network of desert water
  sources, routes and settlements. Evaporation hollows out delivered water, so
  routing and capacity are real constraints, and what a settlement can receive
  is bounded by a maximum flow rather than by nominal aquifer yield.
* **Water-rights cartel** (`water_cartel.py`): a set of reservoirs whose
  released water serves downstream demand. A cartel that controls a dam can
  withhold its normal release and squeeze demand without firing a shot.

**The economic layer — what that control is worth.**

* **Commodity-cartel graph** (`cartel_graph.py`): concentration of control
  across multiple scarce commodities, measured with the Herfindahl–Hirschman
  index, top-k concentration ratios and dominance analysis.
* **Scarcity pricing** (`pricing.py`): the market that converts a withheld
  volume into money — a linear demand curve, the clearing price of a restricted
  supply, the point elasticity that governs how much of a volume cut converts
  into price, and
  the monopoly solution with its deadweight loss.

**The coercive layer — what the cartel can do beyond owning the taps.**

* **Aqueduct interdiction** (`resilience.py`): the fragility of the delivery
  network to cut routes — per-route criticality, a greedy worst-case attack
  sequence, a single-cut resilience index, and minimum cuts.
* **Cooperative power** (`shapley.py`): who can actually capture the value of
  the commodity portfolio, resolved exactly as a transferable-utility coalition
  game via the Shapley value and the Banzhaf–Coleman index.

The layers compose rather than sit side by side: the hydrology network sets the
delivered volumes the interdiction model attacks, and the reservoir simulation
supplies the baseline and restricted supplies the pricing model clears.

Every number in the manuscript is computed by `src/quantum_of_solace/analysis.py`
from these modules on fixed problem instances and injected as a manuscript
token — none is hand-authored prose.
