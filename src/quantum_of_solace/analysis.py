"""Canonical QUANTUM assessment: deterministic metrics over the domain modules.

:func:`run_quantum_assessment` computes the film's headline quantitative
picture from the three pure domain modules on their fixed default instances.
It is the single source of truth shared by the mission adapter, the figure
generators, the manuscript variables, and the analysis CLI — so every surface
reports the same measured numbers.

All results are computed (never hand-authored) and fully deterministic.
"""

from __future__ import annotations

from quantum_of_solace.cartel_graph import CommodityCartelGraph, default_cartel
from quantum_of_solace.hydrology import HydrologicalNetwork, default_network
from quantum_of_solace.water_cartel import Dam, cartel_leverage, default_dams

__all__ = [
    "CONTROLLED_DAMS",
    "RESTRICTION_FRAC",
    "SIMULATION_PERIODS",
    "assess_cartel_graph",
    "assess_hydrology",
    "assess_water_cartel",
    "run_quantum_assessment",
]

#: The dams the QUANTUM cartel controls in the canonical assessment.
CONTROLLED_DAMS = frozenset({"highland_reservoir", "desert_holding"})
#: Fraction of normal releases the cartel withholds (a 50% squeeze).
RESTRICTION_FRAC = 0.5
#: Number of simulation periods in the reservoir model.
SIMULATION_PERIODS = 12


def assess_hydrology(network: HydrologicalNetwork | None = None) -> dict[str, object]:
    """Headline hydrology metrics: supply, settlement delivery, routing cost.

    ``settlement_delivery`` sums each settlement's maximum flow over all
    sources; ``shortest_route_cost`` is the least evaporation-adjusted cost to
    reach a settlement from its cheapest source.
    """
    net = network if network is not None else default_network()
    settlements = sorted(set(net.node_names) - set(net.aquifers))
    delivery: dict[str, float] = {}
    route_cost: dict[str, float] = {}
    for settlement in settlements:
        delivery[settlement] = sum(net.max_flow(source, settlement).total_flow for source in net.aquifers)
        costs: list[float] = []
        for source in net.aquifers:
            try:
                costs.append(net.shortest_route(source, settlement).total_cost)
            except ValueError:
                continue
        route_cost[settlement] = min(costs) if costs else 0.0
    return {
        "total_supply": net.total_supply(),
        "node_count": len(net.node_names),
        "route_count": len(net.routes),
        "settlement_delivery": delivery,
        "shortest_route_cost": route_cost,
    }


def assess_water_cartel(
    dams: list[Dam] | None = None,
) -> dict[str, object]:
    """Headline water-cartel metrics: leverage report and controlled dams."""
    fleet = dams if dams is not None else default_dams()
    report = cartel_leverage(fleet, set(CONTROLLED_DAMS), RESTRICTION_FRAC, SIMULATION_PERIODS)
    return {
        "aggregate_leverage": report["aggregate"],
        "restriction_frac": RESTRICTION_FRAC,
        "periods": SIMULATION_PERIODS,
        "controlled_dams": sorted(CONTROLLED_DAMS),
        "per_dam": report["per_dam"],
    }


def assess_cartel_graph(cartel: CommodityCartelGraph | None = None) -> dict[str, object]:
    """Headline cartel-graph metrics: per-commodity and aggregate HHI, dominance."""
    cg = cartel if cartel is not None else default_cartel()
    hhi_by_commodity = {commodity: cg.hhi(commodity) for commodity in cg.commodities}
    return {
        "commodities": list(cg.commodities),
        "actors": list(cg.actors),
        "hhi_by_commodity": hhi_by_commodity,
        "aggregate_hhi": cg.hhi(),
        "dominance_map": cg.dominance_map(),
        "quantum_high_value_controls": {
            commodity: cg.share_of("quantum", commodity) for commodity in ("water", "lithium")
        },
    }


def run_quantum_assessment() -> dict[str, object]:
    """Run the full canonical QUANTUM assessment over all three subsystems."""
    return {
        "hydrology": assess_hydrology(),
        "water_cartel": assess_water_cartel(),
        "cartel_graph": assess_cartel_graph(),
    }
