# Testing Philosophy — QUANTUM

## Zero-mock policy

All tests exercise the **real** domain algorithms on real, fixed problem data.
No `MagicMock`, `@patch`, `mocker`, or `create_autospec` anywhere in `tests/`.
A test must pass because the code computes the right answer, not because it
intercepts a call signature.

## Coverage gate

`uv run pytest tests/ --cov=src --cov-fail-under=90` enforces ≥90% line
**and** branch coverage on `src/` (both are required — but both exceed 90%).

## Test categories

| File | Covers |
|---|---|
| `tests/test_hydrology.py` | mass balance, routing, max flow (incl. intermediate-node multi-path) |
| `tests/test_water_cartel.py` | reservoir simulation, withholding, leverage |
| `tests/test_cartel_graph.py` | HHI, concentration ratios, dominance, diversification |
| `tests/test_analysis.py` | the canonical assessment orchestrator |
| `tests/test_figures.py` | figure generators under `tmp_path` |
| `tests/test_mission.py` | `bond_api` protocol conformance + gadget registry |
| `tests/test_manuscript_variables.py` | `{{TOKEN}}` map + config loading |
| `tests/test_scripts_smoke.py` | thin CLI subprocess runs + live token cross-reference |

## Determinism in tests

Fixed inputs and analytical expectations (e.g. known HHI values, known max-flow
totals). No reliance on RNG streams except where a property (timing) is the
point — and QUANTUM has no timing tests.

## Protocol conformance

`test_mission.py` asserts the provider satisfies the frozen `bond_api`
`MissionProvider` protocol (`isinstance` runtime check) and that
`bond_api.run_mission` drives all five stages successfully.
