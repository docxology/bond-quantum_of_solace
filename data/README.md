# data/ — vocabularies and claim ledgers for the QUANTUM film package

`claim_ledger.yaml` registers this package's headline numeric claims — all
computed by the domain core on fixed instances — together with the module that
produces each one, the manuscript token that carries it into the paper, and the
bibliography key for each algorithm attribution.

**The ledger is checked, not trusted.** `tests/test_claim_ledger.py` re-derives
every entry from the live assessment via `generate_variables()` and fails if a
value has drifted, if a claim names a token that is not generated, if an
attribution cites a bib key absent from `manuscript/references.bib`, or if it
names a symbol that does not resolve. A stale claim is therefore a test
failure, not a quiet lie — which is the only way a file like this stays worth
reading.

Treat it as validation input, not executable configuration: nothing in `src/`
reads it.

## Editing it

Never adjust a value here to make a test pass. If a number moved, the model
moved: confirm the new value is correct, then update the ledger entry, the
manuscript token if a new one is needed, and the prose that discusses it.
