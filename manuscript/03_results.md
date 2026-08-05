# Results

All results below are computed by `quantum_of_solace/analysis.py` on the fixed
canonical problem instances and injected from `manuscript/config.yaml` + the
assessment — they are measured, not authored.

## 1. Desert water network resilience

The canonical network holds {{HYDRO_TOTAL_SUPPLY}} units/period of aquifer
yield across {{HYDRO_NODE_COUNT}} nodes and {{HYDRO_ROUTE_COUNT}} routes —
{{HYDRO_AQUIFER_COUNT}} aquifers feeding {{HYDRO_SETTLEMENT_COUNT}} settlements
({{HYDRO_SETTLEMENTS}}). A single whole-network Edmonds–Karp maximum flow,
bounded by the aquifer yields as well as the route capacities, routes
{{HYDRO_NETWORK_DELIVERY}} units/period into the settlements; the yields, not
the pipes, are the binding constraint.

Directed at one settlement alone, the network can push {{RESULT_BORDER_DELIVERY}}
units/period to border_town or {{RESULT_VALLEY_DELIVERY}} to valley_compact.
These two figures are **alternatives, not addends**: the settlements draw on the
same aquifers, so their sum exceeds what the network can route in total and must
never be added. @fig:delivery plots them side by side for that reason, against
the network-wide bound.

Both figures are *routed* volume under capacity and yield constraints, not
volume net of evaporation. Maximising volume after per-edge evaporation is a
generalised (lossy) flow problem whose optimum differs from the capacity
maximum flow, and a maximum-flow assignment is not unique, so the evaporation
implied by "the" solution is not a property of the network. Evaporation is
therefore accounted separately and exactly — in the per-node mass balance and in
the effective unit cost that shortest-effort routing minimises. Routed volume is
an upper bound on delivered volume, and this manuscript does not claim otherwise.

![Settlement delivery under maximum flow](../output/figures/hydrology_settlement_delivery.png){#fig:delivery}

## 2. Cartel leverage over water rights

With a {{CARTEL_RESTRICTION_PCT}}% restriction on the
{{CARTEL_CONTROLLED_DAMS}} dams it controls out of a fleet of
{{CARTEL_DAM_COUNT}}, the cartel achieves an aggregate leverage of
**{{RESULT_AGG_LEVERAGE}}** over the {{CARTEL_PERIODS}}-period horizon: it
withholds {{CARTEL_WITHHELD_VOLUME}} units against a horizon demand of
{{CARTEL_HORIZON_DEMAND}}, or {{RESULT_AGG_LEVERAGE_PCT}}% of everything the
fleet was there to serve. Both sides of that ratio are horizon volumes, so the
figure is a genuine share and does not inflate with the length of the
simulation.

That leverage is *smaller* than the holding that produces it, and the
measurement says so plainly: the cartel holds {{CARTEL_OWNERSHIP_PCT}}% of the
fleet by dam count and converts it into {{RESULT_AGG_LEVERAGE_PCT}}% of horizon
demand withheld, a leverage-to-ownership ratio of
{{CARTEL_LEVERAGE_OWNERSHIP_RATIO}}. Two mechanics account for the shortfall:
the cartel withholds only {{CARTEL_RESTRICTION_PCT}}% of each controlled dam's
release rather than all of it, and the uncontrolled dam keeps releasing at full
rate into the same horizon demand. The interesting quantity here is the ratio
itself, not a direction assumed in advance — the model is free to return a value
above 1, and on this fleet it does not. @fig:leverage reports leverage per dam;
controlled dams are red.

![Cartel leverage by dam](../output/figures/water_cartel_leverage.png){#fig:leverage}

## 3. Multi-resource commodity control

Across {{CARTEL_COMMODITIES}}, control is concentrated: water HHI
{{RESULT_WATER_HHI}} and lithium HHI {{RESULT_LITHIUM_HHI}} both sit well above
the {{HHI_HIGH_THRESHOLD}}-point line above which the U.S. Horizontal Merger
Guidelines [@doj2010merger] call a market *highly concentrated*. The
portfolio-mean HHI is **{{RESULT_AGG_HHI}}** points, which
`concentration_band` classifies as {{RESULT_AGG_HHI_BAND}}. @fig:hhi plots
concentration per commodity, and
the dominance map shows the shadow cartel holding the largest share of water
and lithium while a rival syndicate and a state utility split copper and grain.

![Herfindahl–Hirschman concentration by commodity](../output/figures/cartel_hhi_concentration.png){#fig:hhi}

## 4. Water scarcity pricing

The cartel's leveraged control has a price consequence, and this model measures
it rather than assuming its sign. This section prices
the **dam fleet's** mean per-period release, not the hydrology network's routed
volume — the two models describe different assets and their units are not
interchangeable (§1 reports the network at {{HYDRO_NETWORK_DELIVERY}}
units/period). Cutting that release from {{PRICE_SUPPLY_BASELINE}} to
{{PRICE_SUPPLY_RESTRICTED}} units/period drives the water price from
**{{PRICE_BASELINE}}** to **{{PRICE_RESTRICTED}}** — a {{PRICE_RISE}}% rise.
Demand is inelastic at that baseline (point elasticity {{PRICE_ELASTICITY}},
below the unit-elastic value of 1), so the proportional price rise exceeds the
proportional volume cut — by the reciprocal of the elasticity, not by an
unbounded multiple. The cartel collects a scarcity rent of
**{{PRICE_SCARCITY_RENT}}** on the reduced volume — the price premium times the
volume still sold.

That rent is not a rise in takings, and the assessment measures the difference
rather than gesturing at it. Revenue on this demand curve peaks at
{{PRICE_REVENUE_MAX_Q}} units, and the cut runs from
{{PRICE_SUPPLY_BASELINE}} straight past that peak down to
{{PRICE_SUPPLY_RESTRICTED}}, so gross revenue falls from
{{PRICE_REVENUE_BASELINE}} to {{PRICE_REVENUE_RESTRICTED}}. Inelastic demand
makes a *marginal* withholding lucrative; a cut this deep overshoots. The
coercive value of the squeeze here is the price shock imposed on buyers, not a
larger cheque for the seller. Even without withholding, the
underlying market is already monopolistic: the monopoly price would be
{{PRICE_MONOPOLY}} on {{PRICE_MONOPOLY_Q}} units, imposing a deadweight loss of
**{{PRICE_DWL}}** versus the competitive outcome. @fig:pricing shows the demand
curve with the baseline, restricted and monopoly prices.

![Water scarcity pricing under cartel restriction](../output/figures/water_pricing_curve.png){#fig:pricing}

## 5. Aqueduct interdiction and resilience

Of the {{RESIL_ROUTE_COUNT}} routes, {{RESIL_CRITICAL_COUNT}} are critical —
cutting any one of them lowers routed volume — while {{RESIL_REDUNDANT_COUNT}}
are redundant, their capacity re-routable through the rest of the network. Two
retention figures follow, and they are not interchangeable: the **mean**
fraction retained across all single cuts is **{{RESIL_INDEX}}**, whereas the
worst single cut retains {{RESIL_WORST_RETENTION}}. Only the second is a
worst-case bound; the mean is quoted here as a mean and nowhere else as a
guarantee. The most critical single route, {{RESIL_CRITICAL_ROUTE}}, costs
{{RESIL_CRITICAL_LOSS}} units ({{RESIL_CRITICAL_FRAC}}%) of the
{{RESIL_BASELINE}}-unit baseline if lost. @fig:interdict shows the greedy
worst-case interdiction sequence: {{RESIL_SEQ_STEPS}} well-chosen cuts remove
{{RESIL_SEQ_LOSS}} units, {{RESIL_SEQ_LOSS_FRAC}}% of baseline delivery,
leaving {{RESIL_SEQ_DELIVERY_AFTER}} units still flowing — a heavy loss, but not
a total collapse.

![Greedy worst-case aqueduct interdiction](../output/figures/resilience_route_criticality.png){#fig:interdict}

## 6. Cooperative power over the portfolio

The headline HHI of {{RESULT_AGG_HHI}} points is concentration; the *power* to
capture the commodity portfolio's value is resolved exactly by the Shapley
value. With a grand-coalition portfolio value of {{SHAPLEY_TOTAL}}, the leading
actor **{{SHAPLEY_TOP_ACTOR}}** commands {{SHAPLEY_QUANTUM}}, ahead of the rival
({{SHAPLEY_RIVAL}}) and the state utility ({{SHAPLEY_STATE}}) — a dominance gap
of {{SHAPLEY_GAP}} — and {{SHAPLEY_TOP_ACTOR}}'s normalised Banzhaf power is
{{SHAPLEY_BANZHAF_QUANTUM}}. @fig:shapley plots the per-actor Shapley values,
with the dominant actor highlighted.

![Cooperative power over the commodity portfolio](../output/figures/cartel_shapley_power.png){#fig:shapley}
