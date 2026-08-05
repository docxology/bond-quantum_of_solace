# Scope and Related Work

## Scope

This package models the specific threat of *Quantum of Solace*: leverage over
scarce water and commodities exerted by a controlling cartel. The models are
intentionally small, deterministic, and auditable so every claim can be traced
to a computed number.

It deliberately does **not** attempt any of the following, and no result here
should be read as if it did:

* a general integrated assessment model, or a hydrologic–hydraulic engineering
  simulator — routes carry a capacity and a loss fraction, not a hydraulic
  head, a channel geometry, or a groundwater response;
* stochastic hydrology — inflows are fixed rates, so nothing here estimates a
  drought return period or a reservoir reliability;
* an econometric demand study — the demand curve is a stylised linear
  instrument for reasoning about scarcity rent, not a fitted model of any real
  water market, though the sharply inelastic behaviour it produces matches the
  direction reported in the empirical meta-analysis literature
  [@espey1997price];
* strategic interaction between the actors — the power indices allocate the
  value of a cooperative game and do not model entry, deterrence, or
  retaliation.

## Related work

The algorithms are classical and well-established; the citations below point at
the specific source for each.

* **Network flow** — Edmonds–Karp maximum flow [@edmonds1972theoretical],
  building on Ford & Fulkerson [@ford1956maximal]; shortest-path routing
  follows Dijkstra [@dijkstra1959note]. The minimum cut is read off the
  residual graph via the max-flow/min-cut theorem [@ford1956maximal].
* **Network interdiction** — ranking arcs by the flow lost when they are
  removed, and attacking greedily in that order, is the deterministic
  network-interdiction problem in Wood's formulation [@wood1993deterministic].
  This package solves the greedy heuristic, not the exact interdiction optimum.
* **Market concentration** — the Herfindahl–Hirschman index derives from
  Hirschman [@hirschman1945national] and Herfindahl
  [@herfindahl1950concentration]; the concentration bands used to classify a
  measured index come from the U.S. Horizontal Merger Guidelines
  [@doj2010merger].
* **Prices** — linear-demand monopoly pricing (MR = MC) and deadweight-loss
  analysis are textbook microeconomics; the empirical inelasticity of
  residential water demand that makes withholding profitable is documented by
  Espey, Espey & Shaw [@espey1997price].
* **Cooperative power** — the Shapley value [@shapley1953value] and the Banzhaf
  index [@banzhaf1965weighted], whose continuous and normalised forms are
  characterised by Dubey & Shapley [@dubey1979mathematical]. Both are computed
  here by exact enumeration rather than by sampling.
* **Reservoir operation** — period mass-balance reservoir simulation under a
  release rule is the standard formulation in water-resource systems analysis
  [@loucks2017water].

The novelty is not the mathematics but its application: encoding a film's
strategic threat as executable, reproducible mission software bound to a frozen
protocol, and coupling six otherwise-independent models into one measured
assessment in which the hydrology network's delivered flows feed the
interdiction analysis and the reservoir simulation feeds the price model.
