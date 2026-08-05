# Methodology

We implement six deterministic models, one per module of the pure domain core.
All are pure functions of fixed problem data; there is no random number
generation and no dependence on the wall clock, so a regeneration reproduces
identical output. The sections below follow the dependency order in which
`quantum_of_solace/analysis.py` composes them: hydrology and reservoir
operation first, then the concentration, pricing, interdiction and power models
that read from them.

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
each period's otherwise-released water.

Leverage is defined so that it is dimensionally consistent. Inflow, maximum
release and downstream demand are all **per-period rates**, so a leverage ratio
must divide a horizon volume by a horizon volume:
:func:`horizon_demand_volume` returns `downstream_demand * periods`,
:func:`dam_leverage` divides a dam's withheld volume by it, and
:func:`cartel_leverage` divides the total withheld volume across the controlled
dams by the horizon demand of the whole fleet. Every leverage figure in this
manuscript is therefore a share in the unit interval, and it does not change if
the simulated horizon is lengthened at a steady release.

## Commodity-cartel graph (`quantum_of_solace/cartel_graph.py`)

A bipartite control graph maps actors to the share each holds of each
commodity. Concentration is the Herfindahl–Hirschman index in percentage
points, ``sum((share * 100)²)``, reported per commodity and aggregated as the
portfolio mean. Dominance, concentration ratios for the top-k holders, and an
actor's portfolio diversification complete the picture.

:func:`concentration_band` classifies an index value against the bands of the
U.S. Horizontal Merger Guidelines [@doj2010merger]: *unconcentrated* below
{{HHI_MODERATE_THRESHOLD}} points, *moderately concentrated* up to
{{HHI_HIGH_THRESHOLD}} points, and *highly concentrated* above it. The
classification lives in code so the manuscript never has to assert which side
of a threshold a measurement falls on.

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
carrying a canonical SHA-256 input hash and the fixed seed {{MISSION_SEED}}
(the film's models make no random draws at all). The adapter also registers the
six assessment entry points, plus the composed full assessment, in a
module-level `GadgetRegistry` under the package slug, which is how the
coordinator and CLI reach them across packages. The domain modules import
nothing from `bond_api`, so they remain standalone.
