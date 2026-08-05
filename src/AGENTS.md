# src/ — QUANTUM package source

## Layout

```
quantum_of_solace/
  hydrology.py          PURE desert water network (stdlib-only, deterministic)
  water_cartel.py       PURE reservoir / cartel-leverage model (stdlib-only)
  cartel_graph.py       PURE commodity-control graph (stdlib-only)
  pricing.py            PURE water scarcity & monopoly economics (stdlib-only)
  resilience.py         PURE aqueduct interdiction & min-cut (stdlib-only)
  shapley.py            PURE exact Shapley/Banzhaf power indices (stdlib-only)
  analysis.py           deterministic assessment (imports domain core only)
  mission.py            thin bond_api MissionProvider adapter + gadgets
  manuscript_variables.py  {{TOKEN}} hydration (config.yaml + assessment)
  figures.py            deterministic matplotlib figure generators
```

## Boundary

The six domain modules (`hydrology`, `water_cartel`, `cartel_graph`, `pricing`,
`resilience`, `shapley`) are the mathematical core: **stdlib-only, no
`bond_api`, no infrastructure, no random draws, no wall-clock** —
copy-pasteable outside the suite. `analysis.py` and `mission.py`
orchestrate/bind and may import `bond_api` (mission only).
