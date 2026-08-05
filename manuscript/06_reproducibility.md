# Reproducibility

## Provenance

Every `MissionOutcome` from `quantum_of_solace/mission.py` carries a
`Provenance` record: package version, the fixed seed {{MISSION_SEED}} (the film
uses no randomness), and a canonical SHA-256 input hash of the full assessment,
taken over a key-sorted JSON serialisation so the digest does not depend on
dictionary ordering. The same input always reproduces the same hash and the
same results.

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
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

The suite is real-computation only: no mock framework appears anywhere in
`tests/`, so a passing assertion means the algorithm produced the right number
rather than that a call signature was intercepted.

## Manuscript–code binding

Two live tests keep this document honest. One re-derives the token map by
calling `generate_variables()` and fails if any token used in a numbered
section is not produced, binding prose to the generator rather than to a
possibly stale artifact under `output/`; it also asserts the scanned section
set is non-empty, so an empty scan fails instead of passing vacuously. The
other scans the results section for bare decimal numerals after the tokens are
masked out, so a hand-authored metric that escapes the injection pipeline is
caught at test time.

## Configuration hash

The manuscript identity (title, subtitle, version, date) is authored once in
`manuscript/config.yaml` ({{BOND_VERSION}}, dated {{CONFIG_DATE}}) and injected
via `quantum_of_solace/manuscript_variables.py`, never duplicated in prose.
Keywords: {{CONFIG_KEYWORDS}}. Actors modelled: {{CARTEL_ACTORS}}.
