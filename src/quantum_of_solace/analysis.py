"""Canonical QUANTUM assessment: deterministic metrics over the domain modules.

:func:`run_quantum_assessment` computes the film's headline quantitative
picture from the three pure domain modules on their fixed default instances.
It is the single source of truth shared by the mission adapter, the figure
generators, the manuscript variables, and the analysis CLI — so every surface
reports the same measured numbers.

All results are computed (never hand-authored) and fully deterministic.
"""

from __future__ import annotations

from typing import cast

from quantum_of_solace.cartel_graph import (
    HHI_HIGHLY_CONCENTRATED,
    HHI_MODERATELY_CONCENTRATED,
    CommodityCartelGraph,
    concentration_band,
    default_cartel,
)
from quantum_of_solace.hydrology import HydrologicalNetwork, default_network
from quantum_of_solace.pricing import default_demand, market_outcome, monopoly_quantity, revenue, scarcity_impact
from quantum_of_solace.resilience import (
    interdiction_sequence,
    resilience_index,
    single_route_criticality,
    total_delivery,
)
from quantum_of_solace.shapley import (
    banzhaf_power,
    coalition_value,
    default_weights as shapley_default_weights,
    dominance_gap,
    power_ranking,
    shapley_value,
)
from quantum_of_solace.water_cartel import Dam, cartel_leverage, default_dams, run_reservoir

__all__ = [
    "CONTROLLED_DAMS",
    "INTERDICTION_STEPS",
    "RESTRICTION_FRAC",
    "SIMULATION_PERIODS",
    "assess_cartel_graph",
    "assess_hydrology",
    "assess_pricing",
    "assess_resilience",
    "assess_shapley",
    "assess_water_cartel",
    "run_quantum_assessment",
]

#: The dams the QUANTUM cartel controls in the canonical assessment.
CONTROLLED_DAMS = frozenset({"highland_reservoir", "desert_holding"})
#: Fraction of normal releases the cartel withholds (a 50% squeeze).
RESTRICTION_FRAC = 0.5
#: Number of simulation periods in the reservoir model.
SIMULATION_PERIODS = 12
#: Cuts in the canonical greedy worst-case aqueduct interdiction sequence.
INTERDICTION_STEPS = 3


def assess_hydrology(network: HydrologicalNetwork | None = None) -> dict[str, object]:
    """Headline hydrology metrics: supply, delivery capacity, routing cost.

    ``network_delivery`` is the whole-network routable volume per period,
    bounded by aquifer yield as well as route capacity, so it never exceeds
    ``total_supply``. ``settlement_delivery`` gives each settlement's maximum
    when the network is directed at it *alone*; those per-settlement figures are
    mutually exclusive alternatives and must never be summed — the settlements
    compete for the same aquifer yield. ``shortest_route_cost`` is the least
    evaporation-adjusted cost to reach a settlement from its cheapest source.

    Both delivery figures are routed volume, not volume net of evaporation; see
    the :mod:`quantum_of_solace.hydrology` module docstring.
    """
    net = network if network is not None else default_network()
    settlements = list(net.settlements)
    delivery: dict[str, float] = {}
    route_cost: dict[str, float] = {}
    for settlement in settlements:
        delivery[settlement] = net.delivery_capacity([settlement])
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
        "aquifer_count": len(net.aquifers),
        "settlement_count": len(settlements),
        "settlements": settlements,
        "network_delivery": net.delivery_capacity(),
        "settlement_delivery": delivery,
        "shortest_route_cost": route_cost,
    }


def assess_water_cartel(
    dams: list[Dam] | None = None,
) -> dict[str, object]:
    """Headline water-cartel metrics: leverage report and controlled dams.

    ``aggregate_leverage`` is a horizon-consistent share in ``[0, 1]``: total
    withheld volume over ``periods`` divided by the demand served over the same
    ``periods`` (``horizon_demand``).

    ``ownership_share`` is the cartel's share of the dam fleet by count, and
    ``leverage_to_ownership`` divides the leverage share by it. That ratio is
    the honest measure of how the holding converts: above 1 the cartel punches
    above its ownership, below 1 it punches below. Nothing forces either sign,
    so the manuscript must read the measured value rather than assume one.
    """
    fleet = dams if dams is not None else default_dams()
    report = cartel_leverage(fleet, set(CONTROLLED_DAMS), RESTRICTION_FRAC, SIMULATION_PERIODS)
    aggregate = float(cast("float", report["aggregate"]))
    controlled_in_fleet = sum(1 for dam in fleet if dam.name in CONTROLLED_DAMS)
    ownership_share = controlled_in_fleet / len(fleet) if fleet else 0.0
    return {
        "aggregate_leverage": report["aggregate"],
        "restriction_frac": RESTRICTION_FRAC,
        "periods": SIMULATION_PERIODS,
        "dam_count": len(fleet),
        "controlled_dam_count": len(CONTROLLED_DAMS),
        "controlled_dams": sorted(CONTROLLED_DAMS),
        "ownership_share": ownership_share,
        "leverage_to_ownership": aggregate / ownership_share if ownership_share > 0.0 else 0.0,
        "horizon_demand": report["horizon_demand"],
        "withheld_volume": report["withheld_volume"],
        "per_dam": report["per_dam"],
    }


def assess_cartel_graph(cartel: CommodityCartelGraph | None = None) -> dict[str, object]:
    """Headline cartel-graph metrics: per-commodity and aggregate HHI, dominance."""
    cg = cartel if cartel is not None else default_cartel()
    hhi_by_commodity = {commodity: cg.hhi(commodity) for commodity in cg.commodities}
    aggregate_hhi = cg.hhi()
    return {
        "commodities": list(cg.commodities),
        "actors": list(cg.actors),
        "actor_count": len(cg.actors),
        "hhi_by_commodity": hhi_by_commodity,
        "aggregate_hhi": aggregate_hhi,
        "band_by_commodity": {commodity: concentration_band(value) for commodity, value in hhi_by_commodity.items()},
        "aggregate_band": concentration_band(aggregate_hhi),
        "hhi_moderate_threshold": HHI_MODERATELY_CONCENTRATED,
        "hhi_high_threshold": HHI_HIGHLY_CONCENTRATED,
        "dominance_map": cg.dominance_map(),
        "quantum_high_value_controls": {
            commodity: cg.share_of("quantum", commodity) for commodity in ("water", "lithium")
        },
    }


def assess_pricing() -> dict[str, object]:
    """Headline water-scarcity pricing metrics.

    Baseline vs restricted per-period supply is computed from the real dam
    fleet (unrestricted vs cartel-restricted reservoir release), so the
    scarcity price and rent are measured from the water-cartel model, not
    hand-authored.
    """
    fleet = default_dams()
    baseline = sum(run_reservoir(dam, SIMULATION_PERIODS, 0.0).total_release() for dam in fleet) / SIMULATION_PERIODS
    restricted = (
        sum(
            run_reservoir(
                dam, SIMULATION_PERIODS, RESTRICTION_FRAC if dam.name in CONTROLLED_DAMS else 0.0
            ).total_release()
            for dam in fleet
        )
        / SIMULATION_PERIODS
    )
    a, b, mc = default_demand()
    impact = scarcity_impact(baseline, restricted, a, b)
    outcome = market_outcome(a, b, mc)
    # Revenue is maximised where marginal revenue is zero, i.e. the monopoly
    # quantity of a zero-marginal-cost seller: a/(2b). Reported so the
    # manuscript can say whether a given cut lands short of, at, or beyond it
    # instead of assuming that withholding always raises takings.
    revenue_max_quantity = monopoly_quantity(a, b, 0.0)
    return {
        "a": a,
        "b": b,
        "marginal_cost": mc,
        "supply_baseline": baseline,
        "supply_restricted": restricted,
        "revenue_baseline": revenue(impact["baseline_price"], baseline),
        "revenue_restricted": revenue(impact["restricted_price"], restricted),
        "revenue_max_quantity": revenue_max_quantity,
        "baseline_price": impact["baseline_price"],
        "restricted_price": impact["restricted_price"],
        "price_rise_frac": impact["price_rise_frac"],
        "scarcity_rent": impact["scarcity_rent"],
        "elasticity": impact["elasticity"],
        "monopoly_price": outcome.monopoly_price,
        "monopoly_quantity": outcome.monopoly_quantity,
        "deadweight_loss": outcome.deadweight_loss,
        "consumer_surplus_competitive": outcome.consumer_surplus_competitive,
        "consumer_surplus_monopoly": outcome.consumer_surplus_monopoly,
    }


def assess_resilience(network: HydrologicalNetwork | None = None) -> dict[str, object]:
    """Headline aqueduct-interdiction and resilience metrics.

    Ranks the most critical single route, reports the greedy worst-case
    interdiction sequence, and the single-cut resilience index — all computed
    from the real hydrology network.

    ``resilience_index`` is the **mean** retained fraction across every single
    cut; ``worst_case_retention`` is the minimum of the same set, i.e. the
    fraction retained after the single worst cut. Only the latter is a
    worst-case guarantee, and prose must not quote the mean as one.
    ``critical_route_count`` and ``redundant_route_count`` partition
    ``route_count``; nothing forces the critical count to equal the route count.
    """
    net = network if network is not None else default_network()
    baseline = total_delivery(net)
    critical = single_route_criticality(net, baseline)
    most_critical = critical[0]
    sequence = interdiction_sequence(net, steps=INTERDICTION_STEPS)
    sequence_loss = sequence[-1].cumulative_loss if sequence else 0.0
    critical_count = sum(1 for entry in critical if entry.delivery_after < baseline - 1e-9)
    retained = [entry.delivery_after / baseline for entry in critical] if baseline > 0.0 else [0.0]
    return {
        "baseline_delivery": baseline,
        "route_count": len(net.routes),
        "worst_case_retention": min(retained),
        "redundant_route_count": len(net.routes) - critical_count,
        "interdiction_steps": len(sequence),
        "sequence_cumulative_loss": sequence_loss,
        "sequence_loss_frac": sequence_loss / baseline if baseline > 0.0 else 0.0,
        "sequence_delivery_after": sequence[-1].delivery_after if sequence else baseline,
        "critical_route": f"{most_critical.source}->{most_critical.target}",
        "critical_loss": most_critical.loss,
        "critical_loss_frac": most_critical.loss_fraction,
        "critical_route_count": critical_count,
        "resilience_index": resilience_index(net),
        "interdiction_sequence": [
            {
                "step": entry.step,
                "route": f"{entry.source}->{entry.target}",
                "delivery_after": entry.delivery_after,
                "step_loss": entry.step_loss,
                "cumulative_loss": entry.cumulative_loss,
            }
            for entry in sequence
        ],
    }


def assess_shapley(cartel: CommodityCartelGraph | None = None) -> dict[str, object]:
    """Headline cooperative power metrics over commodity control.

    Exact Shapley and normalised Banzhaf values over the cartel's multi-resource
    control graph with the canonical commodity weights.
    """
    cg = cartel if cartel is not None else default_cartel()
    weights = shapley_default_weights()
    values = shapley_value(cg, weights)
    ranking = power_ranking(cg, weights)
    return {
        "weights": weights,
        "shapley": values,
        "banzhaf": banzhaf_power(cg, weights),
        "ranking": list(ranking),
        "top_actor": ranking[0],
        "dominance_gap": dominance_gap(cg, weights),
        "grand_coalition_value": coalition_value(frozenset(cg.actors), cg, weights),
    }


def run_quantum_assessment() -> dict[str, object]:
    """Run the full canonical QUANTUM assessment over all six subsystems."""
    return {
        "hydrology": assess_hydrology(),
        "water_cartel": assess_water_cartel(),
        "cartel_graph": assess_cartel_graph(),
        "pricing": assess_pricing(),
        "resilience": assess_resilience(),
        "shapley": assess_shapley(),
    }
