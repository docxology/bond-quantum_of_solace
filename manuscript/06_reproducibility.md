# Reproducibility

## Provenance

Every `MissionOutcome` from `quantum_of_solace/mission.py` carries a
`Provenance` record: package version, a fixed seed (0 — the film uses no
randomness), and a canonical SHA-256 input hash of the full assessment. The
same input always reproduces the same hash and the same results.

## Regeneration pipeline

The canonical artifacts are disposable and regenerated deterministically:

```bash
uv run python scripts/generate_analysis.py            # assessment JSON + figures
uv run python scripts/z_generate_manuscript_variables.py  # hydrate tokens
uv run python scripts/run_mission.py full             # end-to-end mission
```

`output/` is git-ignored; a clean regeneration leaves the tracked tree stable.
The verification gate is:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## Configuration hash

The manuscript identity (title, subtitle, version, date) is authored once in
`manuscript/config.yaml` ({{BOND_VERSION}}, dated {{CONFIG_DATE}}) and injected
via `quantum_of_solace/manuscript_variables.py`, never duplicated in prose.
Keywords: {{CONFIG_KEYWORDS}}. Actors modelled: {{CARTEL_ACTORS}}.
