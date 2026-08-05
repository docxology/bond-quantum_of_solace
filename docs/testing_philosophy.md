# Testing Philosophy — QUANTUM

## Zero mocks, real computation

Every test exercises the **real** domain algorithms on real, fixed problem
data. There is no `MagicMock`, `unittest.mock`, `mocker.patch`, `@patch` or
`create_autospec` anywhere in `tests/`, and no stand-in objects substituted for
the modules under test. A test passes because the code computed the right
answer, not because a call signature was intercepted.

Nothing here needs a mock, and that is by design rather than by discipline: the
domain core is pure, so it takes fixed inputs and returns values. There is no
network, no database, no clock, and no filesystem in `src/` — the only I/O in
the package is figure and JSON writing, which the tests exercise against real
files under pytest's `tmp_path`, and the CLI scripts, which the tests run as
real subprocesses and read the real stdout of.

## What the coverage gate measures

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

The gate is **line and branch** coverage on `src/` (`branch = true` in
`[tool.coverage.run]`), floored at 90%. Branch coverage matters more than the
line number here: the domain modules are dense with validation guards and
early returns, and line coverage alone would let a `raise` path or a
zero-denominator guard go unexercised while still reporting green.

The measured figure sits well above the floor, but no document in this package
quotes it — a hardcoded percentage in prose goes stale the moment a module is
added. Run the command to see the current number.

Two rules follow from taking the gate seriously:

* **A defensive branch is either reachable or it is deleted.** During the
  Phase-5 review two guards that could never fire — a zero-bottleneck check in
  Edmonds–Karp and an empty-commodity check in the HHI aggregate — were removed
  rather than decorated with `pragma: no cover`, and the reasoning that makes
  them unreachable was written into a comment at the site.
* **Coverage never comes from deleting a test.** If a number moves, fix the
  code or update the expectation to the newly correct value; do not drop the
  assertion.

## Test suite map

| File | Binds |
|---|---|
| `tests/test_hydrology.py` | Dataclass validation, mass balance, Dijkstra routing (including stale-frontier pruning and unreachable targets), Edmonds–Karp max flow, residual reachability, network surgery |
| `tests/test_water_cartel.py` | Reservoir simulation, capacity clamping, evaporation, withheld volume, and the horizon-consistency of every leverage ratio |
| `tests/test_cartel_graph.py` | HHI per commodity and portfolio-mean, concentration ratios, dominance, diversification, the Merger-Guidelines band classifier, share validation |
| `tests/test_pricing.py` | Inverse demand, clearing price, elasticity, surplus, monopoly solution, deadweight loss, scarcity impact |
| `tests/test_resilience.py` | Route criticality ranking, greedy interdiction sequences, resilience index, minimum cut, and the zero-baseline degenerate network |
| `tests/test_shapley.py` | Coalition values, exact Shapley efficiency, normalised Banzhaf, ranking, dominance gap, and the worthless-game degenerate case |
| `tests/test_analysis.py` | The canonical assessment, its parameter metadata, and partially connected networks where some source→settlement pairs have no path |
| `tests/test_figures.py` | Every figure generator writing a real PNG under `tmp_path` |
| `tests/test_mission.py` | `bond_api` protocol conformance and the gadget registry |
| `tests/test_manuscript_variables.py` | The token map, config loading, and that each computed token equals its source metric |
| `tests/test_scripts_smoke.py` | Thin CLI subprocess runs plus the live manuscript cross-reference |
| `tests/test_claim_ledger.py` | Re-derives every entry in `data/claim_ledger.yaml` from the running code, and checks each algorithm attribution against a real bib key and a resolvable symbol |

## Assertions must be able to fail

A test that cannot fail is worse than no test, because it reports safety it
does not provide. Three habits enforce that here.

**Compare numbers as numbers.** The token map is a `dict[str, str]`, so
`variables["PRICE_RESTRICTED"] > variables["PRICE_BASELINE"]` is a
*lexicographic* comparison that happens to agree with the arithmetic one — until
the digits change. Token comparisons go through `float()`.

**Assert the scan set is non-empty.** The manuscript cross-reference test walks
`manuscript/[0-9]*.md` for tokens. If the glob matched nothing, the set
difference would be empty and the test would pass vacuously, so a companion
test asserts the section count and the token count are both above a floor.

**Bind to the generator, not to an artifact.** The cross-reference test calls
`generate_variables()` live rather than reading
`output/data/manuscript_variables.json`, which is git-ignored and may be stale
or absent. A companion test additionally scans the results section for bare
decimals once tokens are masked out, so a hand-authored metric that escapes the
injection pipeline fails the suite.

The same reasoning drives `tests/test_claim_ledger.py`. `data/claim_ledger.yaml`
records the package's headline claims; a file like that decays silently unless
something re-derives it, so the test recomputes every entry from the live
assessment, checks each claim names a token that is actually produced, and
checks each algorithm attribution against a real key in `references.bib` and a
symbol that actually resolves. Perturbing any recorded value fails the suite —
which is what makes the ledger evidence rather than assertion.

## Positive controls for invariants

Where a claim is an invariant rather than a value, the test states the
counterfactual. `test_dam_leverage_does_not_scale_with_period_count` asserts
that doubling the simulated horizon leaves the leverage share unchanged, and
its docstring records that the previous, dimensionally inconsistent formulation
would have doubled it. That is what makes it a control rather than a
restatement of whatever the code currently does.

## Determinism in tests

Fixed inputs and analytical expectations: known HHI values, known max-flow
totals, exactly enumerated Shapley values. No RNG is seeded because none is
used. `tests/conftest.py` forces `MPLBACKEND=Agg` so figure tests are headless,
and puts `src/` and the project root on `sys.path`.

## Protocol conformance

`test_mission.py` asserts the provider satisfies the frozen `bond_api`
`MissionProvider` protocol via a runtime `isinstance` check, that
`bond_api.run_mission` drives all five stages to a successful outcome with a
non-empty provenance hash, and that the gadget registry exposes every subsystem
under the package slug. Those assertions are the package's half of the
cross-package contract: if they break, discovery breaks fleet-wide.
