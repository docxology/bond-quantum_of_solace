# QUANTUM — Quantum of Solace · Todo / Build Log

Phase 2 conversion of this film package from the template scaffold. Priority
top-to-bottom.

## Done

- **Pure domain core** (stdlib-only, deterministic, no `bond_api`):
  - `hydrology.py` — desert water network: mass balance, Dijkstra
    shortest-effort routing, Edmonds–Karp maximum flow, route removal and
    min-cut residual reachability.
  - `water_cartel.py` — reservoir simulation, withheld-volume and per-dam
    leverage, aggregate cartel leverage.
  - `cartel_graph.py` — Herfindahl–Hirschman concentration, top-k ratios,
    dominance, diversification.
  - `pricing.py` — linear-demand water pricing: clearing scarcity price,
    elasticity, monopoly price/quantity, deadweight loss, scarcity rent.
  - `resilience.py` — aqueduct interdiction: per-route criticality, greedy
    worst-case interdiction, resilience index, minimum cut.
  - `shapley.py` — exact Shapley value, normalised Banzhaf–Coleman index,
    power ranking, dominance gap (cooperative game theory).
- **Assessment + mission**: `analysis.py` (single deterministic source of
  truth; now six subsystems), `mission.py` (`bond_api.MissionProvider`,
  gadgets registered, full provenance).
- **Manuscript + figures**: token-hydrated sections (42 `{{TOKEN}}`s), six
  canonical figures (delivery, leverage, HHI, pricing curve, interdiction,
  Shapley power).
- **Scripts**: `run_mission.py` (brief/recon/plan/execute/debrief/full),
  `generate_analysis.py`, `z_generate_manuscript_variables.py`.
- **Tests**: 169 passing, ≥90% line+branch (measured 98.37%), zero mocks.
- **Gates**: pytest `--cov-fail-under=90`, ruff check+format, mypy — all green.

## Integration points / declared next steps

- **Provenance delegation (optional)**: `mission.py` computes its own canonical
  SHA-256 input hash. When `bond-utilities` is bound as a dependency, delegate
  to `bond_utilities.mission_io.record_provenance_outcome` for a suite-wide
  provenance record. Acceptance: outcome provenance block byte-identical to the
  record written by that helper.
- **Fleet discovery**: verify the orchestrator discovers `quantum_of_solace`
  via `bond_api.discovery` in a full-suite run (this package already satisfies
  the `<slug>.mission.MissionProvider` convention; not yet exercised against a
  live orchestrator).
- **Stub-free typed bond-api**: `bond-api` ships without `py.typed`; mypy uses
  an `ignore_missing_imports` override. If bond-api later publishes stubs,
  drop the override.

## Verification reminders

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
git status --short   # clean after commit
```
