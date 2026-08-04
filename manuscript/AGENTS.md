# QUANTUM — Quantum of Solace (2008) special-agent mission software.

Manuscript identity and result tokens are injected from `manuscript/config.yaml`
and `src/quantum_of_solace/manuscript_variables.py`; never hand-author a metric
in prose. Figures are referenced via Pandoc-crossref `[@fig:label]` and live
under `output/figures/`.

## {{TOKEN}} protocol

Numbered sections (`[0-9]*.md`) may use `{{VARIABLE}}` placeholders that
`scripts/z_generate_manuscript_variables.py` resolves via
`quantum_of_solace/manuscript_variables.generate_variables()`. The live
cross-reference test (`tests/test_scripts_smoke.py`) fails if any token used in
a numbered section is not produced.

Tokens come from two sources:

* Config identity: `BOND_IDENTITY`, `BOND_CODENAME`, `BOND_VERSION`,
  `BOND_SUBTITLE`, `CONFIG_KEYWORDS`, `CONFIG_DATE`, `GENERATION_TIMESTAMP`,
  `PYTHON_VERSION`.
* Computed assessment: `HYDRO_TOTAL_SUPPLY`, `HYDRO_NODE_COUNT`,
  `HYDRO_ROUTE_COUNT`, `RESULT_BORDER_DELIVERY`, `RESULT_VALLEY_DELIVERY`,
  `RESULT_AGG_LEVERAGE`, `RESULT_AGG_HHI`, `RESULT_WATER_HHI`,
  `RESULT_LITHIUM_HHI`, `CARTEL_COMMODITIES`, `CARTEL_ACTORS`.

## Figures

| Label | PNG | Generator |
|---|---|---|
| `{#fig:delivery}` | `hydrology_settlement_delivery.png` | `figures.figure_hydrology_delivery` |
| `{#fig:leverage}` | `water_cartel_leverage.png` | `figures.figure_cartel_leverage` |
| `{#fig:hhi}` | `cartel_hhi_concentration.png` | `figures.figure_hhi_concentration` |

Regenerate with `uv run python scripts/generate_analysis.py`.
