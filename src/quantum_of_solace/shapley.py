"""Cooperative power indices over commodity control (QUANTUM).

:mod:`quantum_of_solace.cartel_graph` measures *concentration*; this module
measures *power* — how much of a commodity portfolio's value each actor can
claim. It casts multi-resource control as a transferable-utility coalition
game whose value function


``v(S) = Σ_c w_c · √(Σ_{a∈S} share_{a,c})``


exhibits diminishing returns to combined control (the first units of control
are worth more than later ones), then solves it exactly:

* :func:`coalition_value` — the value of any coalition of actors;
* :func:`shapley_value` — the exact Shapley value per actor
  (``φ_a = Σ_S |S|!(n-|S|-1)!/n! · [v(S∪{a}) − v(S)]``), which always sums to
  the grand-coalition value;
* :func:`banzhaf_power` — the normalised continuous Banzhaf–Coleman index,
  the summed marginal contributions renormalised to 1;
* :func:`power_ranking` / :func:`dominance_gap` — who leads and by how much.

Exact enumeration (2ⁿ coalitions) keeps every value deterministic and
reproducible. The module imports only the standard library plus the commodity
graph core.
"""

from __future__ import annotations

from itertools import combinations
from math import factorial, sqrt

from quantum_of_solace.cartel_graph import CommodityCartelGraph

__all__ = [
    "DEFAULT_COMMODITY_WEIGHTS",
    "banzhaf_power",
    "coalition_value",
    "default_weights",
    "dominance_gap",
    "power_ranking",
    "shapley_value",
]

#: Canonical commodity weights: water is the film's core leverage, lithium next.
DEFAULT_COMMODITY_WEIGHTS = {
    "water": 3.0,
    "lithium": 2.0,
    "copper": 1.0,
    "grain": 1.0,
}


def default_weights() -> dict[str, float]:
    """Return a fresh copy of the canonical commodity weights."""
    return dict(DEFAULT_COMMODITY_WEIGHTS)


def _resolve_weights(cartel: CommodityCartelGraph, weights: dict[str, float] | None) -> dict[str, float]:
    resolved = dict(DEFAULT_COMMODITY_WEIGHTS) if weights is None else dict(weights)
    for commodity in cartel.commodities:
        value = resolved.get(commodity)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"weight for commodity {commodity!r} must be a positive number")
    return resolved


def coalition_value(
    coalition: frozenset[str],
    cartel: CommodityCartelGraph,
    weights: dict[str, float] | None = None,
) -> float:
    """The value of a coalition: sum over commodities of the weighted control.

    Control here is ``sqrt(combined share)`` to model diminishing returns to
    concentrated control. Unknown actors are rejected.
    """
    for actor in coalition:
        if actor not in cartel.actors:
            raise ValueError(f"unknown actor {actor!r} in coalition")
    resolved = _resolve_weights(cartel, weights)
    total = 0.0
    for commodity in cartel.commodities:
        combined = sum(cartel.share_of(actor, commodity) for actor in coalition)
        total += resolved[commodity] * sqrt(combined)
    return total


def shapley_value(
    cartel: CommodityCartelGraph,
    weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """Exact Shapley value for each actor by full coalition enumeration.

    By Shapley efficiency the values always sum to the grand-coalition value.
    """
    actors = list(cartel.actors)
    n = len(actors)
    resolved = _resolve_weights(cartel, weights)
    values = {actor: 0.0 for actor in actors}
    for size in range(1, n + 1):
        for coalition in combinations(actors, size):
            coalition_set = frozenset(coalition)
            for actor in coalition_set:
                previous = coalition_value(coalition_set - {actor}, cartel, resolved)
                value = coalition_value(coalition_set, cartel, resolved)
                # Coalition T (this one, containing ``actor``) has |T|=size; the
                # partner set S = T\\{actor} has |S|=size-1, so the Shapley weight
                # is |S|!·(n-|S|-1)!/n! = (size-1)!·(n-size)!/n!.
                weight = factorial(size - 1) * factorial(n - size) / factorial(n)
                values[actor] += weight * (value - previous)
    return values


def banzhaf_power(
    cartel: CommodityCartelGraph,
    weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """Normalised continuous Banzhaf–Coleman power index per actor.

    Each actor's score is the sum of its marginal contributions over all
    coalitions not containing it, renormalised so the scores sum to 1.
    """
    actors = list(cartel.actors)
    resolved = _resolve_weights(cartel, weights)
    raw = {actor: 0.0 for actor in actors}
    for size in range(len(actors)):
        for coalition in combinations(actors, size):
            coalition_set = frozenset(coalition)
            for actor in actors:
                if actor not in coalition_set:
                    with_actor = coalition_value(coalition_set | {actor}, cartel, resolved)
                    without_actor = coalition_value(coalition_set, cartel, resolved)
                    raw[actor] += with_actor - without_actor
    total = sum(raw.values())
    if total <= 0.0:
        return {actor: 0.0 for actor in actors}
    return {actor: raw[actor] / total for actor in actors}


def power_ranking(
    cartel: CommodityCartelGraph,
    weights: dict[str, float] | None = None,
) -> tuple[str, ...]:
    """Actors sorted by Shapley value descending (ties broken by name)."""
    values = shapley_value(cartel, weights)
    return tuple(sorted(values, key=lambda actor: (-values[actor], actor)))


def dominance_gap(
    cartel: CommodityCartelGraph,
    weights: dict[str, float] | None = None,
) -> float:
    """The gap between the most powerful actor and the second-most powerful."""
    values = shapley_value(cartel, weights)
    ranking = power_ranking(cartel, weights)
    if len(ranking) < 2:
        return 0.0
    return values[ranking[0]] - values[ranking[1]]
