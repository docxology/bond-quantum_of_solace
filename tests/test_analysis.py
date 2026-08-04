"""Tests for the canonical QUANTUM assessment orchestrator."""

import pytest

from quantum_of_solace.analysis import (
    assess_cartel_graph,
    assess_hydrology,
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


class TestRunQuantumAssessment:
    def test_full(self):
        assessment = run_quantum_assessment()
        assert set(assessment) == {"hydrology", "water_cartel", "cartel_graph"}
        assert assessment["hydrology"]["total_supply"] == 80.0

    def test_deterministic(self):
        assert run_quantum_assessment() == run_quantum_assessment()
