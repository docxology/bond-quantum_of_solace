# QUANTUM — Quantum of Solace · Remaining Work

Open work only. Completed build history lives in the git log, not here — a TODO
that accumulates a "Done" section stops being a to-do list.

Ordered by whether it blocks anything.

## Blocked on other packages

- **Fleet discovery, exercised.** This package satisfies the
  `<slug>.mission.MissionProvider` convention and its own tests assert protocol
  conformance against `bond_api` directly, but the provider has never been
  driven by a live `bond-orchestrator` run. Nothing here can close this alone.
  *Acceptance:* an orchestrator run that discovers `quantum_of_solace`,
  executes it, and reports the same `input_hash` this package's
  `scripts/run_mission.py execute` prints.

- **Suite-wide provenance format.** `mission.py` computes its own canonical
  SHA-256 over a key-sorted JSON dump of the assessment. If `bond-utilities`
  standardises a provenance-record helper, this should delegate to it rather
  than keep a private implementation. *Acceptance:* the outcome's provenance
  block is byte-identical to the record the shared helper writes. *Do not*
  start this before confirming the helper exists and its shape is stable —
  `bond_api`'s protocol is frozen, `bond-utilities` is not.

- **Typed `bond-api`.** `bond-api` ships without a `py.typed` marker, so
  `pyproject.toml` carries an `ignore_missing_imports` override for
  `bond_api.*`. Drop the override the moment upstream publishes stubs; until
  then mypy is structurally blind to the protocol's internals.

## Modelling gaps worth closing

These are honest limits of the current models, not defects. Each would need a
new tested module plus a token and a manuscript paragraph.

- **Exact interdiction, not just greedy.** `resilience.interdiction_sequence`
  is a greedy heuristic. The exact k-arc interdiction optimum (Wood's
  formulation) is a different problem and can beat greedy. Either implement the
  exact solver for small k, or measure the greedy gap against brute force over
  all `C(routes, k)` subsets on the canonical instance — the network is small
  enough that brute force is tractable and would turn a caveat into a number.

- **Multi-period cartel dynamics.** The reservoir simulation applies a constant
  restriction fraction for the whole horizon. A time-varying squeeze — ramping,
  or releasing to break a coalition — is the more interesting strategic object
  and is not modelled.

- **Demand response.** `pricing.py` clears a fixed linear demand curve against
  a supply the reservoir model produces, but nothing feeds price back into
  consumption. There is no dynamic equilibrium, so the scarcity rent is an
  upper bound on a single period rather than a path.

- **Shapley scaling.** Both power indices enumerate all `2ⁿ` coalitions. That
  is exact and fast at the canonical three actors, and it is the right choice
  there — but it will not survive a graph with a dozen actors. If the cartel
  graph ever grows, add a sampled estimator *beside* the exact solver with a
  test that the two agree on the small instance, rather than replacing it.

## Documentation debt

- **No rendered PDF.** The manuscript is complete and token-hydrated but has
  only ever been checked as markdown. It has not been run through the template
  render pipeline, so figure placement, `@fig:` cross-references and the
  bibliography are unverified in output form.

## Verification reminders

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
grep -rn "template_code_project" . --exclude-dir=.venv --exclude-dir=.git || echo "no exemplar leftovers"
git status --short   # clean after commit
```
