# Architecture — QUANTUM

## The shape of the package

```
bond_api (frozen protocol, external path dependency)
      │  discovers <slug>.mission and defines the MissionProvider protocol
      ▼
src/quantum_of_solace/mission.py       thin adapter: MissionProvider + GadgetRegistry
      │
      ▼
src/quantum_of_solace/analysis.py      the single deterministic assessment
      │  imports the domain core only — never bond_api
      ▼
hydrology.py  water_cartel.py  cartel_graph.py  pricing.py  resilience.py  shapley.py
                     (PURE domain core: stdlib only, deterministic)
```

`figures.py` and `manuscript_variables.py` sit beside `mission.py` as further
consumers of `analysis.py`; `scripts/*.py` are thin orchestrators that bootstrap
`src/` onto `sys.path` and forward to the package. No business logic lives in
`scripts/`.

## The domain core, module by module

Six pure modules. Each imports only the standard library (`resilience` and
`shapley` additionally import a sibling domain module), makes no random draws,
reads no clock, and is importable without `bond_api` or any infrastructure.

### `hydrology.py` — the desert water network

The physical substrate. `Aquifer` (per-period yield, potability) and `Route`
(capacity, distance, evaporation fraction, unit cost) are frozen, validating
dataclasses; `HydrologicalNetwork` holds them and answers:

* `mass_balance(flows)` → per-node `MassBalance` rows: delivered-in net of
  evaporation, sent-out, and evaporative loss.
* `shortest_route(source, target)` → Dijkstra over the *effective* delivered
  unit cost `cost_per_unit / (1 - evaporation)`, so evaporative routes are
  penalised; returns the path, its cost, and the compound delivered fraction.
* `max_flow(source, target)` → Edmonds–Karp with a residual graph and reverse
  edges, returning total flow, per-edge flows, the augmentation count, and the
  residual-reachable node set (the source side of the minimum cut).
* `without_route` / `without_routes` → structural surgery returning a new
  network, which is how the interdiction model works.
* `default_network()` → the canonical fixed instance.

### `water_cartel.py` — reservoirs and withholding

`Dam` (capacity, initial storage, per-period inflow, per-period downstream
demand, max release, evaporation rate) and the simulation over it:

* `run_reservoir(dam, periods, restriction_frac)` → a `ReservoirTrace` of
  per-period `DamState` rows under mass balance, where the cartel withholds
  `restriction_frac` of each period's otherwise-released volume.
* `withheld_volume` → unrestricted total release minus restricted total.
* `horizon_demand_volume(dam, periods)` → `downstream_demand * periods`.
* `dam_leverage` and `cartel_leverage` → withheld volume over horizon demand.

**Dimensional invariant.** `inflow`, `max_release` and `downstream_demand` are
all per-period rates. Every leverage ratio therefore divides a horizon volume
by a horizon volume and lands in `[0, 1]`; it does not grow with the length of
the simulation. A test (`test_dam_leverage_does_not_scale_with_period_count`)
pins that invariant, because the earlier formulation divided a horizon volume
by a single-period demand and produced ratios far above 1.

### `cartel_graph.py` — multi-resource concentration

`CommodityCartelGraph` is a bipartite actor → commodity share map. It computes
per-commodity and portfolio-mean `hhi()` in percentage points, top-k
`concentration_ratio()`, a full per-commodity `report()`, plus actor-level
`mean_control`, `diversification` and `dominance_count` / `dominance_map`.
`concentration_band()` classifies an index value against the published
Horizontal Merger Guidelines bands, with the thresholds exported as
`HHI_MODERATELY_CONCENTRATED` and `HHI_HIGHLY_CONCENTRATED` — so no document
ever has to assert which side of a threshold a measurement fell on.

### `pricing.py` — scarcity, elasticity, monopoly

Classical microeconomics on a linear inverse demand curve `p(q) = a - b·q`:
`inverse_demand`, `market_clearing_price`, `point_elasticity`, `revenue`,
`consumer_surplus`, `monopoly_price`, `monopoly_quantity`, `deadweight_loss`,
`scarcity_impact` (the price rise and rent a supply cut produces) and
`market_outcome` (the whole competitive-vs-monopoly comparison as a frozen
`MarketOutcome`).

`point_elasticity` returns the *magnitude* of the point price elasticity,
`p/(b·q)`: on `p = a − b·q` the demand function is `q(p) = (a − p)/b`, so
`dq/dp = −1/b`. It previously returned `b·p/q`, wrong by a factor of `b²`, and
is now cross-checked against a numerical derivative of the demand curve in
`test_matches_a_numerical_derivative_of_the_demand_curve`. Note the two forms
coincide at `b = 1`, so no fixture in that test uses `b = 1`.

### `resilience.py` — aqueduct interdiction

Built on `hydrology`. `total_delivery` delegates to
`HydrologicalNetwork.delivery_capacity` — one whole-network maximum flow with a
super-source capped at each aquifer's yield — so it can never exceed
`total_supply`. `single_route_criticality` recomputes it with each route removed
and ranks the losses; `interdiction_sequence` runs the greedy worst-case attack
that repeatedly cuts the most critical remaining route; `resilience_index` is
the **mean** fraction of delivery retained after a single cut (the assessment
reports `worst_case_retention` separately, because a mean is not a bound);
`minimum_cut` reads the least-capacity separating route set off the residual
graph, its value equal to the maximum flow.

**Supply invariant.** `total_delivery <= total_supply`, pinned by
`test_never_exceeds_aquifer_supply`. The earlier formulation summed each
settlement's per-source maximum flow independently, double-counting shared
aquifer yield, and reported 120.0 delivered units against an 80.0-unit supply.
Per-settlement capacities remain available but are **alternatives, not
addends** — settlements compete for the same water.

### `shapley.py` — cooperative power

Casts control as a transferable-utility coalition game with the
diminishing-returns value `v(S) = Σ_c w_c·√(Σ_{a∈S} share)` and solves it
**exactly** by enumerating all `2ⁿ` coalitions: `coalition_value`,
`shapley_value` (efficiency holds — the values sum to the grand-coalition
value), `banzhaf_power` (normalised continuous index), `power_ranking` and
`dominance_gap`.

## How the pieces compose

`analysis.py` is the single source of truth every other surface reads. Its six
`assess_*` functions run the models on their canonical `default_*` instances,
and `run_quantum_assessment()` returns all six as one dict. The composition is
genuine, not parallel: `assess_pricing` takes its baseline and restricted
supplies from the *reservoir simulation* rather than assuming them, and
`assess_resilience` attacks the same hydrology network whose delivery
`assess_hydrology` reports. Fixed parameters live here as named constants —
`CONTROLLED_DAMS`, `RESTRICTION_FRAC`, `SIMULATION_PERIODS`,
`INTERDICTION_STEPS` — so the mission plan, the figures and the manuscript all
quote the same values.

## How `mission.py` implements the frozen `MissionProvider`

`mission.py` is the only module that imports `bond_api`, and it adds no
mathematics of its own — every number it reports comes from calling
`analysis.py`. Its public shape is consumed by `bond-cli`, the coordinator
reconcile and the orchestrator across packages, so **it must not change**:

| Surface | Contract |
|---|---|
| `MissionProvider` (module-level class) | Discovered as `<slug>.mission.MissionProvider`; carries `film = "quantum_of_solace"` |
| `brief() -> MissionBrief` | Codename, six objectives, six model `Asset`s, determinism and provenance `Constraint`s |
| `recon(ReconRequest) -> ReconReport` | Eight `Finding`s, each detail a number measured by the domain core |
| `plan(MissionBrief) -> MissionPlan` | Eight `Step`s, one per subsystem plus assembly and provenance |
| `execute(MissionPlan) -> MissionOutcome` | Runs the full assessment; `Provenance` = package version, `MISSION_SEED`, canonical SHA-256 input hash |
| `debrief(MissionOutcome) -> Debrief` | Six standing lessons |
| `GADGET_REGISTRY` (module-level) | A `GadgetRegistry` with the six `assess_*` callables plus `full_assessment` registered under the slug |

The input hash is taken over a key-sorted, separator-normalised JSON dump, so
the same assessment always yields the same digest regardless of dict ordering.

## Dependency direction

* Domain core → stdlib only (copy-pasteable out of the suite).
* `analysis.py` → domain core, never `bond_api`.
* `mission.py` → `bond_api` + `analysis.py`.
* `figures.py`, `manuscript_variables.py` → `analysis.py` (+ `mission.py` for
  the codename and seed constants).
* `scripts/` → the package (+ `bond_api` for the mission CLI).
* `tests/` → the package + `bond_api` (protocol conformance).

The machine-readable form of these rules is
[`../manuscript/layer_contract.yaml`](../manuscript/layer_contract.yaml).

## Adding a capability

1. Add the pure function or module to the domain core, with a matching test
   that asserts a computed value — not just a shape.
2. Surface it in `analysis.py` if it should feed the manuscript, figures or
   mission, adding any fixed parameter as a named constant there.
3. Optionally register it as a gadget in `mission.py`'s `GADGET_REGISTRY`
   (adding to the registry is safe; changing the existing entries is not).
4. Optionally add a figure in `figures.py` and a manuscript token in
   `manuscript_variables.py`, then reference the token in prose — never the
   number.
