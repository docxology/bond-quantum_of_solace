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
