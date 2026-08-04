# Output Conventions — QUANTUM

`output/` holds regenerable analysis artifacts and is **git-ignored**. Never
edit a file under `output/` directly — change its generator and re-run.

## Layout

```
output/data/quantum_assessment.json       from scripts/generate_analysis.py
output/data/manuscript_variables.json     from scripts/z_generate_manuscript_variables.py
output/figures/hydrology_settlement_delivery.png
output/figures/water_cartel_leverage.png
output/figures/cartel_hhi_concentration.png
```

The assessment JSON is written by `run_quantum_assessment()` with
`sort_keys=True, indent=2`; regenerating reproduces identical bytes (a live
determinism proof).

## Regeneration

```bash
uv run python scripts/generate_analysis.py
uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/run_mission.py full
```

After exploratory runs, re-run the canonical scripts and confirm `git status`
is clean (only ignored `output/` changes).
