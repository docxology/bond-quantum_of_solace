"""Tests for the canonical QUANTUM assessment orchestrator."""

import pytest

from quantum_of_solace.analysis import (
    INTERDICTION_STEPS,
    SIMULATION_PERIODS,
    assess_cartel_graph,
    assess_hydrology,
    assess_pricing,
    assess_resilience,
    assess_shapley,
    assess_water_cartel,
    run_quantum_assessment,
)
from quantum_of_solace.cartel_graph import CommodityCartelGraph
from quantum_of_solace.hydrology import Aquifer, HydrologicalNetwork, Route
from quantum_of_solace.water_cartel import Dam


class TestAssessHydrology:
    def test_default(self):
        metrics = assess_hydrology()
        assert metrics["total_supply"] == 80.0
        assert metrics["node_count"] == 5
        assert metrics["route_count"] == 6
        delivery = metrics["settlement_delivery"]
        assert delivery["border_town"] == 65.0
        assert delivery["valley_compact"] == 55.0
        assert metrics["shortest_route_cost"]["border_town"] > 0.0

    def test_provided_network(self):
        net = HydrologicalNetwork([Aquifer("a", 5.0)], [Route("a", "b", 5.0, 1.0, 0.0)])
        metrics = assess_hydrology(net)
        assert metrics["settlement_delivery"]["b"] == 5.0
        assert metrics["shortest_route_cost"]["b"] == 1.0

    def test_unreachable_settlement(self):
        # no route reaches "c" -> route_cost stays 0.0 and delivery 0.0
        net = HydrologicalNetwork(
            [Aquifer("a", 5.0), Aquifer("z", 5.0)],
            [Route("a", "b", 5.0, 1.0, 0.0), Route("z", "b", 5.0, 1.0, 0.0)],
        )
        metrics = assess_hydrology(net)
        assert metrics["settlement_delivery"]["b"] == 10.0
        assert "c" not in metrics["settlement_delivery"]


class TestAssessWaterCartel:
    def test_default(self):
        metrics = assess_water_cartel()
        assert metrics["aggregate_leverage"] > 0.0
        assert metrics["restriction_frac"] == 0.5
        assert metrics["periods"] == 12
        assert sorted(metrics["controlled_dams"]) == ["desert_holding", "highland_reservoir"]
        assert isinstance(metrics["per_dam"], dict)

    def test_provided_fleet(self):
        fleet = [Dam("only", 100.0, 50.0, 10.0, 20.0, 15.0)]
        metrics = assess_water_cartel(fleet)
        assert metrics["per_dam"]["only"]["controlled"] is False


class TestAssessCartelGraph:
    def test_default(self):
        metrics = assess_cartel_graph()
        assert "water" in metrics["hhi_by_commodity"]
        assert metrics["aggregate_hhi"] > 0.0
        assert metrics["dominance_map"]["water"] == "quantum"
        assert metrics["quantum_high_value_controls"]["water"] == 0.45

    def test_provided(self):
        graph = CommodityCartelGraph({"a": {"w": 1.0}})
        metrics = assess_cartel_graph(graph)
        assert metrics["hhi_by_commodity"]["w"] == pytest.approx(10000.0)


class TestAssessPricing:
    def test_default(self):
        metrics = assess_pricing()
        assert metrics["supply_restricted"] < metrics["supply_baseline"]
        assert metrics["restricted_price"] > metrics["baseline_price"]
        assert metrics["price_rise_frac"] > 0.0
        assert metrics["scarcity_rent"] > 0.0
        assert metrics["monopoly_price"] == pytest.approx(55.0)
        assert metrics["deadweight_loss"] == pytest.approx(4050.0)


class TestAssessResilience:
    def test_default(self):
        metrics = assess_resilience()
        assert metrics["baseline_delivery"] == pytest.approx(120.0)
        assert metrics["critical_route"] == "highland_aquifer->border_town"
        assert metrics["critical_loss"] == pytest.approx(30.0)
        assert metrics["critical_route_count"] == 6
        assert 0.0 < metrics["resilience_index"] < 1.0
        assert len(metrics["interdiction_sequence"]) == 3

    def test_provided_network(self):
        net = HydrologicalNetwork([Aquifer("a", 5.0)], [Route("a", "b", 5.0, 1.0, 0.0)])
        metrics = assess_resilience(net)
        assert metrics["baseline_delivery"] == pytest.approx(5.0)


class TestAssessShapley:
    def test_default(self):
        metrics = assess_shapley()
        assert metrics["top_actor"] == "quantum"
        assert metrics["ranking"] == ["quantum", "rival_syndicate", "state_utility"]
        assert metrics["dominance_gap"] > 0.0
        assert metrics["grand_coalition_value"] == pytest.approx(7.0)


class TestRunQuantumAssessment:
    def test_full(self):
        assessment = run_quantum_assessment()
        assert set(assessment) == {
            "hydrology",
            "water_cartel",
            "cartel_graph",
            "pricing",
            "resilience",
            "shapley",
        }
        assert assessment["hydrology"]["total_supply"] == 80.0

    def test_deterministic(self):
        assert run_quantum_assessment() == run_quantum_assessment()


class TestPartiallyConnectedNetwork:
    """A source that cannot reach a settlement is skipped, not fatal."""

    def _split_network(self) -> HydrologicalNetwork:
        # Each aquifer feeds exactly one settlement, so half of the
        # (source, settlement) pairs have no path at all.
        return HydrologicalNetwork(
            aquifers=[Aquifer(name="north_well", yield_rate=20.0), Aquifer(name="south_well", yield_rate=30.0)],
            routes=[
                Route("north_well", "north_town", capacity=10.0, distance_km=5.0, evaporation=0.1),
                Route("south_well", "south_town", capacity=12.0, distance_km=5.0, evaporation=0.1),
            ],
        )

    def test_unreachable_pairs_are_skipped_and_costs_still_reported(self):
        metrics = assess_hydrology(self._split_network())
        route_cost = metrics["shortest_route_cost"]
        assert set(route_cost) == {"north_town", "south_town"}
        # Each settlement still gets the cost of its own reachable source.
        assert route_cost["north_town"] > 0.0
        assert route_cost["south_town"] > 0.0
        assert metrics["aquifer_count"] == 2
        assert metrics["settlement_count"] == 2
        assert metrics["settlements"] == ["north_town", "south_town"]

    def test_delivery_counts_only_reachable_flow(self):
        metrics = assess_hydrology(self._split_network())
        delivery = metrics["settlement_delivery"]
        assert delivery["north_town"] == 10.0
        assert delivery["south_town"] == 12.0


class TestAssessmentParameterMetadata:
    """The parameters the manuscript cites are emitted by the assessment."""

    def test_water_cartel_horizon_fields(self):
        metrics = assess_water_cartel()
        assert metrics["dam_count"] == 3
        assert metrics["controlled_dam_count"] == 2
        assert metrics["horizon_demand"] == pytest.approx((120.0 + 95.0 + 65.0) * SIMULATION_PERIODS)
        assert metrics["aggregate_leverage"] == pytest.approx(metrics["withheld_volume"] / metrics["horizon_demand"])
        assert 0.0 < metrics["aggregate_leverage"] < 1.0

    def test_cartel_graph_band_fields(self):
        metrics = assess_cartel_graph()
        assert metrics["actor_count"] == 3
        assert metrics["hhi_high_threshold"] == 2500.0
        assert metrics["hhi_moderate_threshold"] == 1500.0
        assert metrics["aggregate_band"] == "highly concentrated"
        assert set(metrics["band_by_commodity"]) == set(metrics["commodities"])

    def test_resilience_sequence_fields(self):
        metrics = assess_resilience()
        assert metrics["interdiction_steps"] == INTERDICTION_STEPS
        assert metrics["sequence_cumulative_loss"] > 0.0
        assert metrics["sequence_delivery_after"] == pytest.approx(
            metrics["baseline_delivery"] - metrics["sequence_cumulative_loss"]
        )
        assert 0.0 < metrics["sequence_loss_frac"] < 1.0
