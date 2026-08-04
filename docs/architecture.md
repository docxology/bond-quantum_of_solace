# Architecture — QUANTUM

## Layers

```
bond_api (frozen protocol, external path dependency)
      │  discovers <slug>.mission & provides MissionProvider protocol
      ▼
src/quantum_of_solace/mission.py          (thin adapter: MissionProvider + gadgets)
      │
      ▼
src/quantum_of_solace/analysis.py         (single deterministic assessment)
      │  imports domain core only
      ▼
hydrology.py · water_cartel.py · cartel_graph.py   (PURE, stdlib-only, deterministic)
```

Additional consumers of `analysis.py`:

* `figures.py` — canonical plot generators (matplotlib, `Agg`).
* `manuscript_variables.py` — `{{TOKEN}}` hydration from `manuscript/config.yaml`.

`scripts/*.py` are thin orchestrators: they bootstrap `src/` on `sys.path` and
forward to the package. No business logic lives in `scripts/`.

## Dependency direction

* Domain core → stdlib only (copy-pasteable without the suite).
* `analysis.py` → domain core (no `bond_api`).
* `mission.py` → `bond_api` + `analysis`.
* `scripts/` → package (+ `bond_api` for the mission CLI).
* `tests/` → package + `bond_api` (protocol conformance).

## Adding a capability

1. Add the pure function/module to the domain core with a matching test.
2. Surface it in `analysis.py` if it should feed the manuscript/figures/mission.
3. Optionally expose it as a gadget in `mission.py`'s `GADGET_REGISTRY`.
4. Optionally add a figure and/or a manuscript `{{TOKEN}}` (then a test).
