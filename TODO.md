# TODO — quantum_of_solace (QUANTUM)

QUANTUM is the PROJECT BOND package for *Quantum of Solace* (2008): six
deterministic domain models (desert hydrology, water-rights cartel,
commodity-cartel graph, scarcity pricing, aqueduct interdiction, cooperative
power), a composed assessment in `analysis.py`, and a thin frozen-`bond_api`
`MissionProvider` adapter. Measured on 2026-08-05 with
`uv run pytest tests/ --cov=src --cov-fail-under=90` (Python 3.14.6,
pytest 9.1.1): **248 tests, all passing, 100.00% line-and-branch coverage** on
the ten `src/quantum_of_solace/*.py` modules. `ruff check`, `ruff format
--check` and `mypy src/ scripts/` (16 files) are all clean. Every one of the
eight findings in `output/verify/quantum_of_solace.json` was re-checked against
today's tree and every one is closed; what remains below is the four items the
remediation pass explicitly could not resolve, plus work found while reading.

Ordered within each group by how much it blocks.

## Open work

### Correctness

**C1 — `controlled_dam_count` is read off a module constant, not off the fleet.**
`src/quantum_of_solace/analysis.py:130` reports
`"controlled_dam_count": len(CONTROLLED_DAMS)` — the size of the frozenset
literal at `analysis.py:56` — while `analysis.py:123-124` correctly counts only
dams *present in the supplied fleet* (`controlled_in_fleet`) when computing
`ownership_share`. `assess_water_cartel` accepts a caller-supplied `dams`
argument, so for any fleet omitting `highland_reservoir` or `desert_holding` the
two fields disagree: `controlled_dam_count` would still say 2 while
`ownership_share` correctly reports 1/n or 0. The canonical fleet hides this
because both happen to equal 2, and the manuscript token
`CARTEL_CONTROLLED_DAMS` carries the constant-derived field. Carried over
unresolved from the audit.
*Done when:* `controlled_dam_count` is derived from `controlled_in_fleet`, and a
test passes a fleet missing one controlled dam and asserts
`controlled_dam_count == 1` alongside `ownership_share == 1/len(fleet)` — a test
that fails against today's code.
*Command:* `uv run pytest tests/test_analysis.py -k controlled -v`

**C2 — closed 2026-11-03: the `bond-api` path dependency is the sibling-relative form.**
`pyproject.toml` pins `bond-api = { path = "../bond-api" }`, the form that resolves identically
in-suite and survives relocation, and `uv.lock` was regenerated from that declaration — the
"standalone clone lints and runs identically" intent in `pyproject.toml:39-42` is no longer
defeated by a path that resolves on exactly one machine.
The suite-wide question is settled in the other direction: the fleet is being repointed to the
relative form, so this package matches its siblings instead of diverging from them.
*Closure measured 2026-11-03:* a relocated copy with `../bond-api` beside it syncs (`rc=0`) and the
suite is **248 passed**.
*Command:* `cd "$(git rev-parse --show-toplevel)" && uv sync --extra dev && uv run pytest -q`

**Superseded 2026-11-04 by the vendoring wave** (the measurement above stands as the 2026-11-03
record): the fleet settled on the opposite form and this package now resolves `bond-api` from the
recorded copy at `vendor/bond-api`, so a clone resolves with no sibling anywhere. `uv lock --check`
went rc=1 → rc=0 on that declaration; see the wave section at the end of this file.

### Verification

**V1 — `experiment_plan.yaml` declares an ablation programme that nothing runs
and no test binds.** `experiment_plan.yaml:48-52` states a `baseline`
("unrestricted reservoir operation (restriction_frac=0)") and three ablations
("toggle controlled dams to measure marginal leverage", "remove the most
critical aqueduct and recompute scarcity price", "drop commodity weights to test
Shapley ranking stability"). `grep -rn "ablation" src/ tests/ scripts/` returns
nothing: none is implemented, none is reported, and no test reads this file at
all. The `expected_figures` block (`experiment_plan.yaml:35-42`) lists six PNG
paths never compared against `figures.ALL_FIGURES`, so a renamed figure would
leave the plan silently stale. A declarative plan nobody executes is a claim
with no gate behind it.
*Done when:* a test parses `experiment_plan.yaml`, asserts `expected_figures`
matches `figures.ALL_FIGURES` and that each `secondary_metrics` `source`
resolves to a real callable, with the unimplemented ablations either implemented
or removed from the plan.
*Command:* `uv run pytest tests/ -k experiment_plan -v` — collects zero tests
today; that is the finding.

**V2 — `domain_profile.yaml` review gates are unbound to the gates they
describe.** `domain_profile.yaml:6-12` asserts `coverage_min_percent: 90`,
`zero_mocks: true`, `ruff: true`, `mypy: true`. The real floor lives at
`pyproject.toml:78` (`fail_under = 90`). Nothing checks the two agree, so
changing one leaves the other advertising a number that is no longer enforced.
`artifact_expectations` (`domain_profile.yaml:19-29`) is likewise an unchecked
list of paths.
*Done when:* a test reads `domain_profile.yaml` and asserts
`review_gates.coverage_min_percent` equals the `[tool.coverage.report]
fail_under` value parsed from `pyproject.toml`, and that every
`artifact_expectations` path exists on disk.
*Command:* `uv run pytest tests/ -k domain_profile -v`

**V3 — the 100% figure excludes two real surfaces.** `pyproject.toml:69-75` sets
`source = ["src"]` and omits `*/__init__.py`. So the 50 lines of re-exports in
`src/quantum_of_solace/__init__.py` are never measured, and `scripts/` is
outside the source set entirely — `generate_analysis.py`, `run_mission.py` and
`z_generate_manuscript_variables.py` are exercised only as subprocesses by
`tests/test_scripts_smoke.py`, so their branches (notably `run_mission.py`'s
exit-2-on-unknown-phase and exit-1-on-unsuccessful-outcome paths documented in
`AGENTS.md`) contribute nothing to the reported total. The number is honest for
what it measures; it is narrower than "the package".
*Done when:* either `--cov=src --cov=scripts` becomes the gate quoted in
`AGENTS.md`, `README.md` and `docs/`, with the floor still met; or the current
scope is stated in one sentence beside the gate so no reader infers script
coverage from it.
*Command:* `uv run pytest tests/ --cov=src --cov=scripts --cov-report=term-missing`

**V4 — the provider has never been driven by a live orchestrator.**
`src/quantum_of_solace/mission.py` satisfies the `<slug>.mission.MissionProvider`
convention and `tests/test_mission.py` asserts protocol conformance against
`bond_api` directly, but no `bond-orchestrator` run has ever discovered and
executed this package. Blocked — nothing inside this directory can close it.
*Done when:* an orchestrator run discovers `quantum_of_solace`, executes it, and
reports the same `input_hash` that `scripts/run_mission.py execute` prints
locally.
*Command (local half):* `uv run python scripts/run_mission.py execute` — record
the `input_hash` and compare against the orchestrator's.

### Documentation

**D1 — two docs describe the metric gate as narrower than it is.**
`docs/agent_instructions.md:66` and `docs/README.md:35` both say the second gate
"fails on any bare decimal left in the results narrative". Since the audit
remediation that gate scans **every** numbered manuscript section, not just
`03_results.md`, and a second gate
(`test_prose_carries_no_untokenised_quantity_claims`,
`tests/test_scripts_smoke.py:175-191`) catches word-numeral quantity claims that
carry no token. The sentences are understated rather than false, which is why
they survived — but a reader following Rule 6 will under-scope their own checks.
Carried over unresolved from the audit.
*Done when:* both sentences name all numbered sections and mention the
quantity-phrase gate, and the grep below finds nothing.
*Command:* `grep -rn "results narrative" docs/ || echo "gate description updated"`

**D2 — the manuscript has never been rendered.** All nine sections
(`manuscript/00_abstract.md` … `99_references.md`) are complete and
token-hydrated, and `output/figures/` holds all six PNGs, but the manuscript has
only ever been checked as markdown. It has not been through the template render
pipeline, so figure placement, the `@fig:` cross-references and the
`references.bib` bibliography are unverified in output form. A first render
routinely leaves `??` cross-references.
*Done when:* a PDF exists and a visual read of the rendered pages confirms zero
`??` references, all six figures placed, and a populated bibliography.
*Command:* render via the template pipeline, then
`pdftotext <out>.pdf - | grep -c '??'` expecting `0`

### Extension

Genuine future work. None of these is a defect; each needs a new tested function,
a token, and a manuscript paragraph.

**E1 — measure the greedy interdiction gap instead of caveating it.**
`resilience.interdiction_sequence`
(`src/quantum_of_solace/resilience.py:112-152`) is a greedy heuristic; the exact
k-arc interdiction optimum (Wood's formulation) is a different problem and can
beat it. The canonical network has 6 routes, so brute force over all `C(6,k)`
subsets is trivially tractable and would turn a prose caveat into a number.
*Done when:* an exact small-k solver or a `greedy_optimality_gap` lives in
`resilience.py`, tested against exhaustive enumeration on the canonical network
and reported as a token.
*Command:* `uv run pytest tests/test_resilience.py -k gap -v`

**E2 — measure delivered volume net of evaporation.** See the first Known
limitation below for why this is currently unmeasured and honestly labelled.
Closing it means implementing a generalised lossy-flow maximisation (not the
capacity max-flow) with a stated tie-break that makes the assignment unique.
*Done when:* a `delivered_volume_net_of_evaporation` exists with a test pinning
it strictly below `HYDRO_NETWORK_DELIVERY` on the canonical network, and the
manuscript reports both.
*Command:* `uv run pytest tests/test_hydrology.py -k net_of_evaporation -v`

**E3 — adopt the shared provenance helper (its precondition is now met).**
`mission.py:80-83` computes its own canonical SHA-256 over a key-sorted JSON
dump. `bond-utilities` now ships `bond_utilities/mission_io.py` with
`hash_payload()` (line 45) and `record_provenance_outcome()` (line 153) on the
same canonical-JSON scheme, so the "confirm the helper exists" condition the
previous TODO waited on is satisfied. The remaining question is not technical:
this package's stated contract (`README.md` "binds to _only_ `bond-api`";
`AGENTS.md` layer contract) forbids a second suite dependency, so adopting the
helper means amending that contract.
*Done when:* either the provenance block is byte-identical to what the shared
helper writes and the layer contract is amended to permit the dependency; or a
test asserts `_canonical_hash` agrees byte-for-byte with `hash_payload`'s scheme
without importing it, and this closes as "compatible by test, not by dependency".
*Command:* `uv run pytest tests/test_mission.py -k provenance -v`

**E4 — multi-period cartel dynamics.** The reservoir simulation applies one
constant restriction fraction across the whole 12-period horizon
(`analysis.py:121`, `RESTRICTION_FRAC`). A time-varying squeeze — ramping, or
releasing to fracture a coalition — is the more interesting strategic object and
is not modelled.
*Done when:* `run_reservoir` accepts a per-period restriction schedule, with a
test that a constant schedule reproduces today's `aggregate_leverage` exactly.
*Command:* `uv run pytest tests/test_water_cartel.py -k schedule -v`

**E5 — demand response.** `pricing.py` clears a fixed linear demand curve
against a supply the reservoir model produces, but nothing feeds price back into
consumption. There is no dynamic equilibrium, so `PRICE_SCARCITY_RENT` is an
upper bound on a single period rather than a path.
*Done when:* a multi-period clearing loop exists with a convergence test, and the
manuscript distinguishes the single-period bound from the path.
*Command:* `uv run pytest tests/test_pricing.py -k equilibrium -v`

**E6 — a sampled Shapley estimator, if and only if the graph grows.** Both power
indices in `shapley.py` enumerate all `2ⁿ` coalitions. That is exact and fast at
the canonical three actors and is the right choice there. Trigger: a cartel
graph beyond roughly ten actors.
*Done when (if triggered):* a sampled estimator sits **beside** the exact solver
— never replacing it — with a test that the two agree within tolerance on the
canonical three-actor instance.
*Command:* `uv run pytest tests/test_shapley.py -k sampled -v`

## Known limitations (not bugs)

- **Reported flow is *routed* volume, not volume net of evaporation — and the
  claim was softened to say so.** The audit found delivery figures exceeding the
  network's own supply; the fix bounded max-flow by aquifer yield but did **not**
  make max-flow evaporation-aware. Maximising volume net of per-edge evaporation
  is a generalised lossy-flow problem whose optimum is not the capacity
  max-flow, and a max-flow assignment is not unique, so "the" evaporation implied
  by a solution is not a well-defined property of the network. The honest scope
  now stated at `src/quantum_of_solace/hydrology.py:20-32`, in
  `manuscript/03_results.md` §1 and in `manuscript/02_methodology.md` is: routed
  volume is an *upper bound* on delivered volume; evaporation is modelled exactly
  and separately in the per-node mass balance and in the evaporation-adjusted
  routing cost; the manuscript claims nothing more. The property itself remains
  unmeasured — that is E2, not a defect in the current claim.
- **The quantity-phrase gate is lexical and cannot see a wrong number.**
  `tests/test_scripts_smoke.py:100-121` matches a fixed list of phrase forms
  (`minority`, `several times`, `orders of magnitude`, …) plus bare decimals. It
  catches prose asserting a magnitude without a token; it cannot detect a wrong
  value inside a correctly-plumbed token. That defence is
  `data/claim_ledger.yaml` re-derived by `tests/test_claim_ledger.py`, plus the
  per-metric derivation tests. Both gates carry negative controls
  (`test_the_decimal_gate_rejects_a_hand_authored_metric`,
  `test_the_quantity_gate_rejects_the_claims_it_was_written_for` at
  `tests/test_scripts_smoke.py:193`) that replay the exact false sentences which
  once shipped, so a gate that stopped matching fails rather than passing
  silently. Do not re-litigate this as "make the gate semantic".
- **mypy is structurally blind to `bond_api` internals.** `bond-api` ships no
  `py.typed` marker (verified: none under `bond-api/src/bond_api/`), so
  `pyproject.toml:100-102` carries `ignore_missing_imports` for `bond_api.*`.
  Nothing in this package can fix that. Reopen the moment upstream publishes the
  marker — the fix is deleting that override block and re-running mypy.
- **Per-settlement delivery maxima are alternatives, never addends.**
  `RESULT_BORDER_DELIVERY` (65.0) and `RESULT_VALLEY_DELIVERY` (55.0) sum to
  120.0 against an 80.0-unit network. This is correct and deliberate: the
  settlements compete for the same aquifers.
  `tests/test_resilience.py:64-75` pins the strict inequality so a future change
  cannot quietly make the sum a headline. A modelling fact with a test, not a
  bug.

## Verification

The gates for this package, with expected outcomes. Run all of them and read the
output, not just the exit codes.

```bash
# The gate. Expect: all tests pass, coverage >= 90% on src/.
uv run pytest tests/ --cov=src --cov-fail-under=90

# Style and types. Expect: "All checks passed!", "N files already formatted",
# "Success: no issues found in 17 source files" (16 until the vendoring pass
# added scripts/vendor.py).
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/

# No mocks anywhere. Expect: "no mocks".
grep -rn "unittest.mock\|MagicMock\|mocker.patch\|@patch\|create_autospec" tests/ || echo "no mocks"

# No exemplar lineage. Expect: "no exemplar leftovers". The pattern is written
# as a bracket class so this command and the other copies of it are not
# themselves its only hits (measured before the fix: rc=0 with four hits, every
# one of them a copy of this command or the rule it enforces — no real leftover).
grep -rn "template_[c]ode_project" . --exclude-dir=.venv --exclude-dir=.git || echo "no exemplar leftovers"

# Artifacts regenerate deterministically. Expect: exit 0, six PNGs, token JSON.
uv run python scripts/generate_analysis.py
uv run python scripts/z_generate_manuscript_variables.py

# The mission flow. Expect: exit 0 (exit 2 on an unknown phase).
uv run python scripts/run_mission.py full

# Expect: clean after a path-scoped commit.
git status --short
```

`uv` cannot write its cache under a restrictive sandbox. `Failed to initialize
cache at ~/.cache/uv` is an environment restriction, not a package failure —
re-run with the sandbox disabled.

## Vendoring wave (2026-11-04)

The fleet's second vendoring pass removes the sibling checkout that C2 had just
settled on: `bond-api` now ships as the recorded copy at `vendor/bond-api`
(`VENDOR.md`, `PROVENANCE.json`, upstream `c0362ff0c9d7` — payload `aggregate_sha256`
`2e8fa087be…`), `[tool.uv.sources]` points there, and `uv.lock` was regenerated
from that declaration (`uv lock --check` rc=1 → rc=0; the regenerated lock is
byte-identical across two runs). The git-clean blob set was verified 16/16
against the patch's `copied_paths`, and `scripts/vendor.py --check` reports
`ok` with 0 findings.

This repository's `[tool.ruff]` already declared `line-length = 120`, and the
generated patch therefore arrived with the checker bytes that conform to that
width (`checker_sha256 0372e5d8…`): no re-conform and no re-seal were needed —
the wave's first such row. Effective width measured 120, against 88 under
`--isolated`.

| # | Observation | Evidence |
|---|---|---|
| W1 | The generated `extend-exclude = ["vendor"]` is load-bearing for `ruff format`, not for this rule set's lint. | Two-arm control, table kept in `pyproject.toml` and only its body varied. As committed: whole-tree `ruff check` rc=0 "All checks passed!" with 0 findings under `vendor/`; whole-tree `ruff format --check` rc=1 with one target (`README.md`). Exclusion line removed: `ruff check` still rc=0 (the vendored sources produce no `select = ["E","F"]` findings); `ruff format --check` rc=1 with two targets (adds `vendor/bond-api/README.md`). |
| W2 | The lineage audit's documented expectation was unreachable in this repository and is corrected in place. | At the pre-change head the command exited 0 with four hits — three copies of the command itself and one rule line stating what it forbids; no real leftover. The pattern is now a bracket class in all four sites, and the audit re-measured rc=1 with 0 hits, printing `no exemplar leftovers` (the documented expectation). |
| W3 | The live expectations in the verification block are re-dated and re-measured; the dated figures earlier in this file keep their dates and gains a supersession pointer. | mypy 16 → **17** source files (the vendoring pass adds `scripts/vendor.py`); scoped format 39 → **41** files; suite 248 → **249** passed at 100.00% (954/212, 0 partial). The "Measured on 2026-08-05" intro figures and C2's "Closure measured 2026-11-03" figures are left as dated measurements. |
| W4 | Recorded, not swept: the whole-tree formatter red on `README.md`. | `ruff format --check .` rc=1 on one file, `README.md` (a fenced block), at both ends, outside the documented scoped gate; present before the change and identical after it. |

End-to-end evidence at the branch tip: gate 1 rc=0, 249 passed, 100.00%; mocks
rc=1 with 0 hits; lineage rc=1 with 0 hits; `ruff check` rc=0 and `ruff format
--check` 41 files; whole-tree check rc=0 with 0 findings under `vendor/`; mypy
17 files in both spellings; the analysis + manuscript-variable regeneration
byte-identical across two runs (digest `ae008845051d9ea8`), 8 output files;
`run_mission.py full` rc=0.
