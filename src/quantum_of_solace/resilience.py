"""Aqueduct interdiction and water-network resilience model (QUANTUM).

A cartel that cannot stop the water outright can still *cut the routes* — an
aqueduct here, a pipeline there. This module quantifies how fragile the desert
delivery network is to exactly that kind of attack, using deterministic
network-science algorithms on top of :mod:`quantum_of_solace.hydrology`:

* :func:`total_delivery` — the network's headline delivered volume (sum of
  per-source maximum flows to every settlement);
* :func:`single_route_criticality` — for each route, the delivery lost if that
  route is interdicted, ranked most-critical first;
* :func:`interdiction_sequence` — a greedy worst-case attack that repeatedly
  removes the most critical remaining route;
* :func:`resilience_index` — mean fraction of delivery retained after any
  single-route interdiction (1.0 = fully redundant);
* :func:`minimum_cut` — the smallest-capacity set of routes separating the
  supply from a settlement (via the residual graph of the max-flow solution),
  whose value equals the maximum flow by the max-flow/min-cut theorem.

The module imports only the standard library plus the hydrology core.
"""

from __future__ import annotations

from dataclasses import dataclass

from quantum_of_solace.hydrology import HydrologicalNetwork

__all__ = [
    "CutResult",
    "InterdictionStep",
    "RouteCriticality",
    "interdiction_sequence",
    "minimum_cut",
    "resilience_index",
    "single_route_criticality",
    "total_delivery",
]


def total_delivery(network: HydrologicalNetwork) -> float:
    """The network's total delivered volume: per-source max flow to every settlement.

    Sums, over every non-source node, the maximum flow each aquifer can push
    to it. Deterministic and monotone: removing routes never increases it.
    """
    settlements = sorted(set(network.node_names) - set(network.aquifers))
    return sum(
        network.max_flow(source, settlement).total_flow for settlement in settlements for source in network.aquifers
    )


@dataclass(frozen=True)
class RouteCriticality:
    """The delivery impact of interdicting one route."""

    source: str
    target: str
    delivery_after: float
    loss: float

    @property
    def loss_fraction(self) -> float:
        """Loss relative to baseline (0.0 when the route is redundant)."""
        return self.loss / (self.delivery_after + self.loss) if self.delivery_after + self.loss > 0.0 else 0.0


def single_route_criticality(
    network: HydrologicalNetwork,
    baseline: float | None = None,
) -> list[RouteCriticality]:
    """Rank every route by the delivery lost if it alone is interdicted.

    Returns entries sorted by loss descending (most critical first). When the
    network has a single route, interdicting it leaves zero delivery.
    """
    if baseline is None:
        baseline = total_delivery(network)
    entries: list[RouteCriticality] = []
    for route in network.routes:
        if len(network.routes) == 1:
            delivery_after = 0.0
        else:
            delivery_after = total_delivery(network.without_route(route.source, route.target))
        entries.append(
            RouteCriticality(
                source=route.source,
                target=route.target,
                delivery_after=delivery_after,
                loss=max(0.0, baseline - delivery_after),
            )
        )
    return sorted(entries, key=lambda entry: entry.loss, reverse=True)


@dataclass(frozen=True)
class InterdictionStep:
    """One step of the greedy worst-case interdiction sequence."""

    step: int
    source: str
    target: str
    delivery_before: float
    delivery_after: float
    step_loss: float
    cumulative_loss: float


def interdiction_sequence(network: HydrologicalNetwork, steps: int = 3) -> list[InterdictionStep]:
    """Greedy worst-case interdiction: repeatedly cut the most critical route.

    At each step the remaining network's most critical route (by
    :func:`single_route_criticality`) is removed and the delivery drop is
    recorded. ``steps`` is clamped to the number of routes; the sequence stops
    early when nothing is left to deliver.

    Raises:
        ValueError: if ``steps`` is not a positive integer.
    """
    if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
        raise ValueError("steps must be a positive integer")
    current = network
    sequence: list[InterdictionStep] = []
    cumulative = 0.0
    for step_index in range(min(steps, len(network.routes))):
        baseline = total_delivery(current)
        if baseline <= 0.0:
            break
        most_critical = single_route_criticality(current, baseline)[0]
        if len(current.routes) == 1:
            delivery_after = 0.0  # the last route severs the network entirely
        else:
            current = current.without_route(most_critical.source, most_critical.target)
            delivery_after = total_delivery(current)
        step_loss = max(0.0, baseline - delivery_after)
        cumulative += step_loss
        sequence.append(
            InterdictionStep(
                step=step_index + 1,
                source=most_critical.source,
                target=most_critical.target,
                delivery_before=baseline,
                delivery_after=delivery_after,
                step_loss=step_loss,
                cumulative_loss=cumulative,
            )
        )
        if delivery_after <= 0.0:
            break
    return sequence


def resilience_index(network: HydrologicalNetwork) -> float:
    """Mean fraction of delivery retained after any single-route interdiction.

    1.0 means every route is redundant (no single cut costs anything); 0.0
    means even the least critical route completely severs supply.
    """
    baseline = total_delivery(network)
    if baseline <= 0.0 or not network.routes:
        return 0.0
    retained = [entry.delivery_after / baseline for entry in single_route_criticality(network, baseline)]
    return sum(retained) / len(retained)


@dataclass(frozen=True)
class CutResult:
    """A minimum cut: its value and the route set that realises it."""

    value: float
    cut_edges: tuple[tuple[str, str], ...]


def minimum_cut(network: HydrologicalNetwork, source: str, target: str) -> CutResult:
    """Minimum-capacity route cut separating ``source`` from ``target``.

    Computed from the residual reachability of the Edmonds–Karp solution: the
    cut routes are exactly those leaving the reachable source side. By the
    max-flow/min-cut theorem the cut value equals the maximum flow.
    """
    solution = network.max_flow(source, target)
    reachable = set(solution.reachable)
    cut_edges: list[tuple[str, str]] = []
    cut_value = 0.0
    for route in network.routes:
        if route.source in reachable and route.target not in reachable:
            cut_edges.append((route.source, route.target))
            cut_value += route.capacity
    return CutResult(value=cut_value, cut_edges=tuple(cut_edges))
