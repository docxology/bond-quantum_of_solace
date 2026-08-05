# data/ — QUANTUM

Agent guide for the `data/` directory.

`claim_ledger.yaml` is a declaration of sourced, computed claims. Each entry
carries an `id`, the human-readable `claim`, the numeric `value`, an optional
`tolerance`, the manuscript `token` that renders it, the `evidence` chain of
modules that produce it, and a `determinism` flag.

## Rules

- **Do not hand-adjust a value to silence a test.** `tests/test_claim_ledger.py`
  re-derives every entry from the running code; a mismatch means the model
  changed, so verify the new number before recording it.
- **Every claim needs a token.** If you add a claim, add the corresponding
  manuscript variable in `src/quantum_of_solace/manuscript_variables.py` first.
- **Every attribution needs a real citation.** The `reference` field is a bibtex
  key that must exist in `manuscript/references.bib`, and `module` must resolve
  to a callable inside `quantum_of_solace`.
- Nothing in `src/` reads this file; it is validation input only.

See [`README.md`](README.md) for the overview.
