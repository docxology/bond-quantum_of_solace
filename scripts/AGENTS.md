# scripts/ — QUANTUM thin orchestrators

Each script bootstraps `src/` onto `sys.path` and forwards to the package. No
business logic lives here.

| Script | Purpose |
|---|---|
| `run_mission.py` | Drive the `bond_api` mission phases (brief/recon/plan/execute/debrief/full) |
| `generate_analysis.py` | Write `output/data/quantum_assessment.json` + figures |
| `z_generate_manuscript_variables.py` | Hydrate the `{{TOKEN}}` map to `output/data/manuscript_variables.json` |
