# Manuscript — Quantum of Solace (2008)

The QUANTUM paper: deterministic models of water-rights cartels, desert
hydrology, commodity concentration, scarcity pricing, aqueduct interdiction and
cooperative power, with every metric injected rather than typed.

## Sections, in order

| File | Covers |
|---|---|
| `00_abstract.md` | The film's threat and the six models' headline measurements |
| `01_introduction.md` | The premise, and the six models grouped as physical / economic / coercive layers |
| `02_methodology.md` | Each model's algorithms, in the order `analysis.py` composes them, plus the mission adapter |
| `03_results.md` | Six measured results, one per model, each with its figure |
| `04_conclusion.md` | Why the leverage is systemic and convertible |
| `05_experimental_setup.md` | Environment, every fixed problem instance, and the determinism argument |
| `06_reproducibility.md` | Provenance, the regeneration pipeline, and the tests that bind prose to code |
| `07_scope_and_related_work.md` | What is deliberately *not* modelled, and the source for each classical method |
| `99_references.md` | The rendered bibliography |

Supporting files: `config.yaml` (identity, authors, keywords), `preamble.md`
(LaTeX injections), `references.bib`, `layer_contract.yaml`, plus `AGENTS.md`
(token protocol, figure table) and `SYNTAX.md` (citation and cross-reference
syntax).

## Regenerating

```bash
uv run python scripts/generate_analysis.py                # figures + assessment JSON
uv run python scripts/z_generate_manuscript_variables.py  # the token map
```

Token values are hydrated from `config.yaml` plus the live assessment. Never
hand-author a metric here — `tests/test_scripts_smoke.py` re-derives the token
map and fails on an ungenerated token, and separately fails on any bare decimal
left in the results narrative.
