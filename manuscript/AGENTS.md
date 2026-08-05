# QUANTUM — Quantum of Solace (2008) special-agent mission software

Manuscript identity and result tokens are injected from `manuscript/config.yaml`
and `src/quantum_of_solace/manuscript_variables.py`; never hand-author a metric
in prose. Figures are referenced via Pandoc-crossref `[@fig:label]` and live
under `output/figures/`.

## Sections

The canonical set, all present: `00_abstract`, `01_introduction`,
`02_methodology`, `03_results`, `04_conclusion`, `05_experimental_setup`,
`06_reproducibility`, `07_scope_and_related_work`, `99_references`, plus
`preamble.md`, `config.yaml`, `references.bib`, this file, `README.md`,
`SYNTAX.md` and `layer_contract.yaml`.

## Token protocol

Numbered sections (`[0-9]*.md`) may use `{{VARIABLE}}` placeholders that
`scripts/z_generate_manuscript_variables.py` resolves via
`quantum_of_solace.manuscript_variables.generate_variables()`.

Two live tests in `tests/test_scripts_smoke.py` enforce the protocol:

* `test_every_prose_token_is_generated` calls `generate_variables()` and fails
  if any token used in a numbered section is not produced. It binds to the
  generator, not to `output/data/manuscript_variables.json`, which is
  git-ignored and may be stale or absent.
* `test_scan_set_is_not_empty` fails if the section glob or the token scan
  comes back near-empty, so a vacuous scan cannot report clean.
* `test_results_prose_carries_no_bare_decimal_metrics` masks the tokens out of
  `03_results.md` and fails on any bare decimal left behind — a hand-authored
  metric that escaped the pipeline.

### Token families

The list below is the shape, not an inventory; enumerate the live set with

```bash
uv run python scripts/z_generate_manuscript_variables.py
python3 -c "import json,pathlib;print('\n'.join(sorted(json.loads(pathlib.Path('output/data/manuscript_variables.json').read_text()))))"
```

| Prefix | Source | Carries |
|---|---|---|
| `BOND_*`, `CONFIG_*`, `PYTHON_VERSION`, `GENERATION_TIMESTAMP` | `manuscript/config.yaml` | Identity, version, keywords, the deterministic date stamp |
| `MISSION_SEED` | `mission.py` | The provenance seed |
| `HYDRO_*` | `assess_hydrology` | Supply, whole-network routable delivery, node/route/aquifer/settlement counts, settlement names |
| `RESULT_BORDER_*`, `RESULT_VALLEY_*` | `assess_hydrology` | Per-settlement routing maxima — alternatives competing for the same yield, never to be summed in prose |
| `CARTEL_*`, `RESULT_AGG_LEVERAGE*` | `assess_water_cartel` | Restriction, periods, dam counts, ownership share, leverage-to-ownership ratio, horizon demand, withheld volume, leverage share |
| `RESULT_*_HHI*`, `HHI_*_THRESHOLD` | `assess_cartel_graph` | Per-commodity and portfolio HHI, the concentration band and its published thresholds |
| `PRICE_*` | `assess_pricing` | Demand parameters, baseline/restricted supply and price, rise, rent, elasticity, monopoly point, deadweight loss |
| `RESIL_*` | `assess_resilience` | Baseline delivery, route/critical/redundant counts, critical route and loss, mean retention (`RESIL_INDEX`) and worst-case retention (`RESIL_WORST_RETENTION`), interdiction-sequence steps and cumulative loss |
| `SHAPLEY_*` | `assess_shapley` | Weights, per-actor Shapley values, Banzhaf power, ranking, dominance gap, grand-coalition value |

Adding a token: put the value in `analysis.py` first, expose it in
`manuscript_variables.py`, add a test that the token matches its source, then
reference it in prose.

## Figures

| Label | PNG | Generator |
|---|---|---|
| `{#fig:delivery}` | `hydrology_settlement_delivery.png` | `figures.figure_hydrology_delivery` |
| `{#fig:leverage}` | `water_cartel_leverage.png` | `figures.figure_cartel_leverage` |
| `{#fig:hhi}` | `cartel_hhi_concentration.png` | `figures.figure_hhi_concentration` |
| `{#fig:pricing}` | `water_pricing_curve.png` | `figures.figure_pricing_curve` |
| `{#fig:interdict}` | `resilience_route_criticality.png` | `figures.figure_resilience_interdiction` |
| `{#fig:shapley}` | `cartel_shapley_power.png` | `figures.figure_shapley_power` |

Regenerate with `uv run python scripts/generate_analysis.py`.

## References

`references.bib` carries only real, checkable sources for models this package
actually implements. Do not add a citation for a method that is not in `src/`,
and do not add one you cannot verify — an unverifiable entry is removed, not
shipped.
