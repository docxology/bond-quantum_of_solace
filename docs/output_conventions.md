# Output Conventions — QUANTUM

`output/` holds regenerable analysis artifacts and is **git-ignored**. Never
edit a file under `output/` directly — change its generator and re-run.

## Layout

```
output/data/quantum_assessment.json       from scripts/generate_analysis.py
output/data/manuscript_variables.json     from scripts/z_generate_manuscript_variables.py
output/figures/hydrology_settlement_delivery.png   figures.figure_hydrology_delivery
output/figures/water_cartel_leverage.png           figures.figure_cartel_leverage
output/figures/cartel_hhi_concentration.png        figures.figure_hhi_concentration
output/figures/water_pricing_curve.png             figures.figure_pricing_curve
output/figures/resilience_route_criticality.png    figures.figure_resilience_interdiction
output/figures/cartel_shapley_power.png            figures.figure_shapley_power
```

Six figures, one per domain model, all rendered by `render_all_figures()` in
the canonical order given by `figures.ALL_FIGURES`.

The assessment JSON is written by `run_quantum_assessment()` with
`sort_keys=True, indent=2`; regenerating reproduces identical bytes (a live
determinism proof). The token map is written by `generate_variables()` the same
way — but note that the manuscript cross-reference test deliberately calls the
generator rather than reading this file, so a stale or missing artifact can
never make that test pass.

## Regeneration

```bash
uv run python scripts/generate_analysis.py
uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/run_mission.py full
```

After exploratory runs, re-run the canonical scripts and confirm `git status`
is clean (only ignored `output/` changes).
