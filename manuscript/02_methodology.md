# Methodology

We implement three deterministic models. All are pure functions of fixed
problem data; there is no random number generation and no dependence on the
wall clock, so a regeneration reproduces identical output.

## Desert hydrology (`quantum_of_solace/hydrology.py`)

An aquifer contributes a per-period yield and a potability quality; a route
carries flow with a capacity, a distance and an evaporation loss fraction.
Three algorithms operate on the resulting network:

* **Mass balance** — for each node, inflow is delivered net of evaporation and
  outflow is subtracted, giving a per-node surplus.
* **Shortest-effort routing** — Dijkstra over the *effective* delivered unit
  cost ``cost_per_unit / (1 - evaporation)``, so evaporative routes are
  penalised, plus the compound delivered fraction.
* **Maximum flow** — Edmonds–Karp with a residual graph and reverse edges, so
  already-assigned flow can be re-routed. This yields the most water a
  settlement can receive per period under the route capacities.

## Water-rights cartel (`quantum_of_solace/water_cartel.py`)

A dam has storage capacity, initial storage, natural inflow, a downstream
demand, a maximum release and an evaporation rate. `run_reservoir` simulates
mass balance period by period; a *restriction fraction* withholds that share of
each period's otherwise-released water. Leverage for a dam is the withheld
volume relative to its downstream demand, and aggregate cartel leverage is
total withheld volume across the controlled dams divided by total demand.

## Commodity-cartel graph (`quantum_of_solace/cartel_graph.py`)

A bipartite control graph maps actors to the share each holds of each
commodity. Concentration is the Herfindahl–Hirschman index in percentage
points, ``sum((share * 100)²)``, reported per commodity and aggregated as the
portfolio mean. Dominance, concentration ratios for the top-k holders, and an
actor's portfolio diversification complete the picture.

## Water scarcity pricing (`quantum_of_solace/pricing.py`)

On a linear inverse demand curve ``p(q) = a − b·q``, :func:`market_clearing_price`
is the scarcity price at which a fixed supply is absorbed, and
:func:`scarcity_impact` prices the cartel's supply cut: the restricted price,
the price-rise fraction, and the scarcity rent collected on the reduced volume.
The standard monopoly solution (MR = MC), with :func:`monopoly_price`,
:func:`monopoly_quantity` and :func:`deadweight_loss`, quantifies the social
cost of concentrated control. The baseline and restricted supplies in the
assessment are computed from the *real* dam fleet (unrestricted vs
cartel-restricted reservoir release), so pricing is measured from the same
model, not assumed.

## Aqueduct interdiction (`quantum_of_solace/resilience.py`)

Over the hydrology network, :func:`single_route_criticality` ranks every route
by the delivery lost if it alone is cut (recomputing maximum flow after each
removal); :func:`interdiction_sequence` drives a greedy worst-case attack that
repeatedly removes the most critical remaining route; and
:func:`resilience_index` reports the mean fraction of delivery retained after a
single cut. :func:`minimum_cut` finds the least-capacity set of routes
separating supply from a settlement via the residual reachability of the
Edmonds–Karp solution, whose value equals the maximum flow by the
max-flow/min-cut theorem.

## Cooperative power (`quantum_of_solace/shapley.py`)

Multi-resource control is cast as a transferable-utility coalition game with a
diminishing-returns value function ``v(S) = Σ_c w_c·√(Σ_{a∈S} share)`` and
solved **exactly** by full enumeration: :func:`shapley_value` (efficiency always
holds: the values sum to the grand-coalition value), :func:`banzhaf_power`
(normalised continuous Banzhaf–Coleman index), :func:`power_ranking`, and
:func:`dominance_gap` between the top two actors.

## The mission adapter

`quantum_of_solace/mission.py` adapts the six models to the frozen `bond_api`
protocol: `brief`, `recon`, `plan`, `execute` and `debrief`, with provenance
carrying a canonical input hash and a fixed seed. The domain modules import
nothing from `bond_api`, so they remain standalone.
