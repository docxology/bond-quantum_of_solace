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

## The mission adapter

`quantum_of_solace/mission.py` adapts the three models to the frozen `bond_api`
protocol: `brief`, `recon`, `plan`, `execute` and `debrief`, with provenance
carrying a canonical input hash and a fixed seed. The domain modules import
nothing from `bond_api`, so they remain standalone.
