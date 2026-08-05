# Results

All results below are computed by `quantum_of_solace/analysis.py` on the fixed
canonical problem instances and injected from `manuscript/config.yaml` + the
assessment — they are measured, not authored.

## 1. Desert water network resilience

The canonical network holds {{HYDRO_TOTAL_SUPPLY}} units/period of aquifer
yield across {{HYDRO_NODE_COUNT}} nodes and {{HYDRO_ROUTE_COUNT}} routes. Under
Edmonds–Karp maximum flow the two border settlements draw up to
{{RESULT_BORDER_DELIVERY}} (border_town) and {{RESULT_VALLEY_DELIVERY}}
(valley_compact) delivered units/period. Evaporation is the dominant loss;
shortest-effort routing counteracts it. @fig:delivery shows each settlement's
maximum delivered water.

![Settlement delivery under maximum flow](../output/figures/hydrology_settlement_delivery.png){#fig:delivery}

## 2. Cartel leverage over water rights

With a 50% restriction on its two controlled dams, the cartel achieves an
aggregate leverage of **{{RESULT_AGG_LEVERAGE}}** — that is, a withheld volume
equal to more than the entire downstream demand base over the simulated
horizon, revealing how a minority ownership of dams converts into outsized
squeeze. @fig:leverage reports leverage per dam; controlled dams are red.

![Cartel leverage by dam](../output/figures/water_cartel_leverage.png){#fig:leverage}

## 3. Multi-resource commodity control

Across {{CARTEL_COMMODITIES}}, control is concentrated: water HHI
{{RESULT_WATER_HHI}} and lithium HHI {{RESULT_LITHIUM_HHI}} both sit well above
the 2500 "moderately concentrated" threshold, and the portfolio-mean HHI is
**{{RESULT_AGG_HHI}}** points. @fig:hhi plots concentration per commodity, and
the dominance map shows the shadow cartel holding the largest share of water
and lithium while a rival syndicate and a state utility split copper and grain.

![Herfindahl–Hirschman concentration by commodity](../output/figures/cartel_hhi_concentration.png){#fig:hhi}

## 4. Water scarcity pricing

The cartel's leveraged control converts directly into money. Cutting the
network's delivered supply from {{PRICE_SUPPLY_BASELINE}} to
{{PRICE_SUPPLY_RESTRICTED}} units/period drives the water price from
**{{PRICE_BASELINE}}** to **{{PRICE_RESTRICTED}}** — a {{PRICE_RISE}}% rise — and
since water is sharply inelastic (point elasticity {{PRICE_ELASTICITY}}), the
price moves far more than the volume. The cartel collects a scarcity rent of
**{{PRICE_SCARCITY_RENT}}** on the reduced volume. Even without withholding, the
underlying market is already monopolistic: the monopoly price would be
{{PRICE_MONOPOLY}} on {{PRICE_MONOPOLY_Q}} units, imposing a deadweight loss of
**{{PRICE_DWL}}** versus the competitive outcome. @fig:pricing shows the demand
curve with the baseline, restricted and monopoly prices.

![Water scarcity pricing under cartel restriction](../output/figures/water_pricing_curve.png){#fig:pricing}

## 5. Aqueduct interdiction and resilience

The desert supply is fragile: all {{RESIL_CRITICAL_COUNT}} routes are critical —
no single aqueduct is redundant — and a single cut retains only
**{{RESIL_INDEX}}** of baseline delivery. The most critical single route,
{{RESIL_CRITICAL_ROUTE}}, costs {{RESIL_CRITICAL_LOSS}} units ({{RESIL_CRITICAL_FRAC}}%)
of the {{RESIL_BASELINE}}-unit baseline if lost. @fig:interdict shows the greedy
worst-case interdiction sequence, in which three well-chosen cuts collapse
delivery almost entirely.

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
