# Scope and Related Work

## Scope

This package models the specific threat of *Quantum of Solace*: leverage over
scarce water and commodities exerted by a controlling cartel. It deliberately
does **not** attempt a general integrated assessment model (GAM) or a
hydrologic-hydraulic engineering simulator; the models are intentionally small,
deterministic, and auditable so every claim can be traced to a computed number.

## Related work

The algorithms used are classical and well-established:

* **Network flow** — Edmonds–Karp maximum flow is described in Edmonds &
  Karp (1972); shortest-path routing follows Dijkstra (1959).
* **Market concentration** — the Herfindahl–Hirschman index is a standard
  industrial-organisation concentration measure; the pairwise Version was
  introduced by Sheth (1968).
* **Reservoir operation** — period mass-balance reservoir simulation is the
  standard textbook formulation of deterministic reservoir rule curves.

The novelty is not the mathematics but its application: encoding a film's
strategic threat as executable, reproducible mission software bound to a frozen
protocol, and coupling three otherwise-independent models into one measured
assessment.
