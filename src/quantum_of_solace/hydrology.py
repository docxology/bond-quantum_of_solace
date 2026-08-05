"""Deterministic desert hydrology and route-network model (QUANTUM).

Models a directed water network over desert nodes: aquifers with a per-period
yield, settlements that consume water, and routes that carry flow with a
capacity, a distance, and an evaporation loss fraction. The module provides
real, deterministic algorithms rather than stubs:

* per-node **mass balance** accounting for evaporation on transit;
* **shortest route** through the network via Dijkstra, minimising the
  evaporation-adjusted cost per delivered unit;
* **maximum flow** from a source to a sink via the Edmonds–Karp algorithm,
  honouring every route's capacity.

Everything is computed from the supplied data — no random draws, no external
calls. The module imports only the standard library so it stays copy-pasteable
out of the BOND suite without ``bond_api`` or any infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush

__all__ = [
    "Aquifer",
    "FlowSolution",
    "HydrologicalNetwork",
    "MassBalance",
    "Route",
    "ShortestRoute",
]

#: Floating-point tolerance beneath which an augmenting path is ignored.
MAX_FLOW_DELTA = 1e-9


def _require_number(value: object, label: str, *, minimum: float = 0.0) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{label} must be a non-boolean number")
    if value < minimum:
        raise ValueError(f"{label} must be >= {minimum}")


def _require_name(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _require_fraction(value: object, label: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{label} must be a non-boolean number")
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"{label} must be in [0, 1]")


@dataclass(frozen=True)
class Aquifer:
    """A desert water source: a name, a per-period yield, and water quality.

    ``quality`` is the potability of the source on the closed interval
    ``[0, 1]`` (1.0 = potable without treatment).
    """

    name: str
    yield_rate: float
    quality: float = 1.0

    def __post_init__(self) -> None:
        _require_name(self.name, "Aquifer.name")
        _require_number(self.yield_rate, "Aquifer.yield_rate")
        _require_fraction(self.quality, "Aquifer.quality")


@dataclass(frozen=True)
class Route:
    """A directed water route between two named nodes.

    ``evaporation`` is the fraction of any volume sent that is lost to heat
    before reaching ``target``; ``cost_per_unit`` is the economic cost of
    moving one unit of delivered water along the route.
    """

    source: str
    target: str
    capacity: float
    distance_km: float
    evaporation: float
    cost_per_unit: float = 1.0

    def __post_init__(self) -> None:
        _require_name(self.source, "Route.source")
        _require_name(self.target, "Route.target")
        _require_number(self.capacity, "Route.capacity")
        _require_number(self.distance_km, "Route.distance_km")
        _require_fraction(self.evaporation, "Route.evaporation")
        _require_number(self.cost_per_unit, "Route.cost_per_unit")


@dataclass(frozen=True)
class ShortestRoute:
    """Result of a shortest-route search through the network."""

    path: tuple[str, ...]
    total_cost: float
    delivered_fraction: float

    @property
    def evaporation_loss(self) -> float:
        """Fraction of the sent volume that the path loses to evaporation."""
        return 1.0 - self.delivered_fraction

    @property
    def hops(self) -> int:
        """Number of traversed edges (path nodes minus one)."""
        return max(0, len(self.path) - 1)


@dataclass(frozen=True)
class FlowSolution:
    """Result of a maximum-flow computation over the network.

    ``reachable`` is the set of nodes still reachable from the source in the
    residual graph after the flow is maximal — the source side of the minimum
    cut (by the max-flow/min-cut theorem).
    """

    total_flow: float
    edge_flows: tuple[tuple[str, str, float], ...]
    augmentations: int
    reachable: tuple[str, ...] = ()

    def flow_on(self, source: str, target: str) -> float:
        """Return the flow sent over a specific edge (0.0 if unused)."""
        for edge_source, edge_target, volume in self.edge_flows:
            if edge_source == source and edge_target == target:
                return volume
        return 0.0


@dataclass(frozen=True)
class MassBalance:
    """Per-node water accounting: what arrived minus what departed."""

    node: str
    delivered_in: float
    sent_out: float
    lost_evaporation: float

    @property
    def net_surplus(self) -> float:
        """Net water accumulating at the node (negative = net consumer)."""
        return self.delivered_in - self.sent_out


class _Edge:
    """Mutable residual-graph edge used by the Edmonds–Karp search."""

    __slots__ = ("to", "rev_index", "capacity")

    def __init__(self, to: str, rev_index: int, capacity: float) -> None:
        self.to = to
        self.rev_index = rev_index
        self.capacity = capacity


class HydrologicalNetwork:
    """A directed desert water network with deterministic flow algorithms.

    Args:
        aquifers: The source nodes, each with a per-period yield.
        routes: The directed routes between nodes.
    """

    def __init__(self, aquifers: list[Aquifer], routes: list[Route]) -> None:
        if not aquifers:
            raise ValueError("a water network needs at least one aquifer")
        self._aquifers: dict[str, Aquifer] = {}
        for aquifer in aquifers:
            self._aquifers[aquifer.name] = aquifer
        self._routes: list[Route] = list(routes)
        if not self._routes:
            raise ValueError("a water network needs at least one route")

        self._out: dict[str, list[Route]] = {}
        for route in self._routes:
            self._out.setdefault(route.source, []).append(route)

        self._nodes: tuple[str, ...] = tuple(sorted(set(self._aquifers) | {r.target for r in self._routes}))

    # -- queries -----------------------------------------------------------

    @property
    def node_names(self) -> tuple[str, ...]:
        """Every node (aquifers and route targets), sorted."""
        return self._nodes

    @property
    def aquifers(self) -> tuple[str, ...]:
        """The source-node names, in declaration order."""
        return tuple(self._aquifers)

    @property
    def routes(self) -> tuple[Route, ...]:
        """The routes, in declaration order."""
        return tuple(self._routes)

    def is_source(self, name: str) -> bool:
        """True when ``name`` names a declared aquifer (water source)."""
        return name in self._aquifers

    def supply(self, name: str) -> float:
        """The per-period yield of aquifer ``name`` (0.0 for non-sources)."""
        aquifer = self._aquifers.get(name)
        return aquifer.yield_rate if aquifer is not None else 0.0

    def total_supply(self) -> float:
        """Sum of every aquifer's per-period yield."""
        return sum(aquifer.yield_rate for aquifer in self._aquifers.values())

    def evaporation_loss(self, volume: float, route: Route) -> float:
        """Volume lost when sending ``volume`` along ``route``."""
        _require_number(volume, "volume")
        return volume * route.evaporation

    def delivered_volume(self, volume: float, route: Route) -> float:
        """Volume that actually arrives when sending ``volume`` along ``route``."""
        _require_number(volume, "volume")
        return volume * (1.0 - route.evaporation)

    def out_routes(self, node: str) -> tuple[Route, ...]:
        """Routes departing from ``node`` (empty if it is a dead-end sink)."""
        return tuple(self._out.get(node, ()))

    def effective_unit_cost(self, route: Route) -> float:
        """Cost to deliver one unit of water along ``route``, net of evaporation.

        A more evaporative route needs more sent volume to deliver a unit, so
        its effective cost is ``cost_per_unit / (1 - evaporation)``.
        """
        return route.cost_per_unit / (1.0 - route.evaporation)

    # -- mass balance ------------------------------------------------------

    def mass_balance(
        self,
        flows: dict[tuple[str, str], float],
    ) -> list[MassBalance]:
        """Account water at every node given a mapping of edge → sent volume.

        For each node the balance is: delivered-in (net of evaporation on each
        inbound edge) minus sent-out. Returns a row per node, sorted by name.
        """
        delivered: dict[str, float] = {}
        sent: dict[str, float] = {}
        lost: dict[str, float] = {}
        for (source, target), volume in flows.items():
            route = self._find_route(source, target)
            _require_number(volume, "edge flow")
            delivered[target] = delivered.get(target, 0.0) + self.delivered_volume(volume, route)
            sent[source] = sent.get(source, 0.0) + volume
            lost[target] = lost.get(target, 0.0) + self.evaporation_loss(volume, route)
        rows: list[MassBalance] = []
        for node in self._nodes:
            rows.append(
                MassBalance(
                    node=node,
                    delivered_in=delivered.get(node, 0.0),
                    sent_out=sent.get(node, 0.0),
                    lost_evaporation=lost.get(node, 0.0),
                )
            )
        return rows

    def _find_route(self, source: str, target: str) -> Route:
        for route in self._routes:
            if route.source == source and route.target == target:
                return route
        raise ValueError(f"no route from {source!r} to {target!r}")

    # -- routing -----------------------------------------------------------

    def shortest_route(self, source: str, target: str) -> ShortestRoute:
        """Shortest ``source`` → ``target`` path by effective delivered cost.

        Uses Dijkstra over the evaporation-adjusted unit cost of each edge.
        Raises ``ValueError`` when no path exists.
        """
        if source == target:
            return ShortestRoute(path=(source,), total_cost=0.0, delivered_fraction=1.0)
        best: dict[str, tuple[float, tuple[str, ...], float]] = {}
        frontier: list[tuple[float, str, tuple[str, ...], float]] = [(0.0, source, (source,), 1.0)]
        while frontier:
            cost, node, path, delivered_fraction = heappop(frontier)
            if node in best and best[node][0] <= cost:
                continue
            best[node] = (cost, path, delivered_fraction)
            if node == target:
                return ShortestRoute(path=path, total_cost=cost, delivered_fraction=delivered_fraction)
            for route in self._out.get(node, ()):
                edge_cost = self.effective_unit_cost(route)
                heappush(
                    frontier,
                    (
                        cost + edge_cost,
                        route.target,
                        path + (route.target,),
                        delivered_fraction * (1.0 - route.evaporation),
                    ),
                )
        raise ValueError(f"no route from {source!r} to {target!r}")

    # -- maximum flow ------------------------------------------------------

    def max_flow(self, source: str, target: str) -> FlowSolution:
        """Maximum flow from ``source`` to ``target`` (Edmonds–Karp).

        Builds a residual graph with reverse edges so already-assigned flow can
        be re-routed, then repeatedly augments along the shortest (BFS)
        augmenting path. Returns the total flow, the per-edge flow tuple, and
        the number of augmentations. All quantities are explicit and
        deterministic.
        """
        if source not in self._aquifers:
            raise ValueError(f"{source!r} is not an aquifer (water sources produce the flow)")

        adjacency: dict[str, list[_Edge]] = {node: [] for node in self._nodes}
        forward_index: dict[tuple[str, str], _Edge] = {}

        for route in self._routes:
            forward = _Edge(route.target, len(adjacency[route.target]), route.capacity)
            reverse = _Edge(route.source, len(adjacency[route.source]), 0.0)
            adjacency[route.source].append(forward)
            adjacency[route.target].append(reverse)
            forward_index[(route.source, route.target)] = forward

        total = 0.0
        augmentations = 0
        while True:
            parent: dict[str, tuple[str, _Edge]] = {}
            seen = {source}
            queue: list[str] = [source]
            reached = False
            while queue and not reached:
                node = queue.pop(0)
                for edge in adjacency.get(node, []):
                    if edge.capacity > MAX_FLOW_DELTA and edge.to not in seen:
                        parent[edge.to] = (node, edge)
                        seen.add(edge.to)
                        if edge.to == target:
                            reached = True
                            break
                        queue.append(edge.to)
            if not reached:
                break

            bottleneck = float("inf")
            node = target
            while node != source:
                previous, edge = parent[node]
                bottleneck = min(bottleneck, edge.capacity)
                node = previous
            if bottleneck <= MAX_FLOW_DELTA:
                break

            node = target
            while node != source:
                previous, edge = parent[node]
                edge.capacity -= bottleneck
                adjacency[node][edge.rev_index].capacity += bottleneck
                node = previous
            total += bottleneck
            augmentations += 1

        edge_flows = tuple(
            (route.source, route.target, route.capacity - forward_index[(route.source, route.target)].capacity)
            for route in self._routes
        )
        edge_flows = tuple(
            (src_name, tgt_name, volume) for src_name, tgt_name, volume in edge_flows if volume > MAX_FLOW_DELTA
        )
        return FlowSolution(
            total_flow=total,
            edge_flows=edge_flows,
            augmentations=augmentations,
            reachable=tuple(sorted(seen)),
        )

    # -- network surgery ---------------------------------------------------

    def without_route(self, source: str, target: str) -> HydrologicalNetwork:
        """Return a copy of the network with the ``source`` → ``target`` route removed."""
        return self.without_routes({(source, target)})

    def without_routes(self, excluded: set[tuple[str, str]]) -> HydrologicalNetwork:
        """Return a copy of the network with every excluded route removed.

        Raises ``ValueError`` when the removal would leave no routes.
        """
        remaining = [route for route in self._routes if (route.source, route.target) not in excluded]
        if not remaining:
            raise ValueError("cannot remove every route from the network")
        return HydrologicalNetwork(list(self._aquifers.values()), remaining)


def default_network() -> HydrologicalNetwork:
    """The canonical QUANTUM desert water network.

    A deterministic, fixed instance emblematic of the film's setting: scattered
    highland aquifers and deep desert wells feeding two border settlements
    across evaporative routes.
    """
    aquifers = [
        Aquifer(name="highland_aquifer", yield_rate=40.0, quality=0.9),
        Aquifer(name="deep_well", yield_rate=25.0, quality=0.6),
        Aquifer(name="oasis_spring", yield_rate=15.0, quality=0.8),
    ]
    routes = [
        Route("highland_aquifer", "border_town", capacity=30.0, distance_km=120.0, evaporation=0.15, cost_per_unit=1.0),
        Route(
            "highland_aquifer", "valley_compact", capacity=20.0, distance_km=90.0, evaporation=0.10, cost_per_unit=0.8
        ),
        Route("deep_well", "border_town", capacity=20.0, distance_km=70.0, evaporation=0.20, cost_per_unit=0.6),
        Route("deep_well", "valley_compact", capacity=25.0, distance_km=110.0, evaporation=0.18, cost_per_unit=0.6),
        Route("oasis_spring", "border_town", capacity=15.0, distance_km=40.0, evaporation=0.05, cost_per_unit=0.4),
        Route("oasis_spring", "valley_compact", capacity=10.0, distance_km=60.0, evaporation=0.08, cost_per_unit=0.4),
    ]
    return HydrologicalNetwork(aquifers=aquifers, routes=routes)
