# tests/ — QUANTUM test suite

Real data + computation, zero mocks. The live coverage number is reported by
the gate (`uv run pytest tests/ --cov=src --cov-fail-under=90`); both line and
branch exceed 90%.

| File | Covers |
|---|---|
| `test_hydrology.py` | mass balance, routing, Edmonds–Karp max flow |
| `test_water_cartel.py` | reservoir simulation, withholding, leverage |
| `test_cartel_graph.py` | HHI, concentration, dominance |
| `test_analysis.py` | the assessment orchestrator |
| `test_figures.py` | figure generators |
| `test_mission.py` | `bond_api` protocol conformance + gadgets |
| `test_manuscript_variables.py` | `{{TOKEN}}` hydration |
| `test_scripts_smoke.py` | CLI subprocess smoke + live token cross-reference |

## Zero-mock

No mocking-framework usage anywhere — enforced both by convention and by the
root suite audit. A test passes only when the real algorithm computes the right
answer.
