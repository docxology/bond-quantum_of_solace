"""Tests for the aqueduct-interdiction and resilience model."""

import pytest

from quantum_of_solace.hydrology import Aquifer, HydrologicalNetwork, Route
from quantum_of_solace.resilience import (
    CutResult,
    InterdictionStep,
    RouteCriticality,
    interdiction_sequence,
    minimum_cut,
    resilience_index,
    single_route_criticality,
    total_delivery,
)
from quantum_of_solace.hydrology import default_network


class TestTotalDelivery:
    def test_default(self):
        assert total_delivery(default_network()) == pytest.approx(120.0)

    def test_monotone_under_removal(self):
        net = default_network()
        smaller = net.without_route("highland_aquifer", "border_town")
        assert total_delivery(smaller) < total_delivery(net)


class TestRouteCriticality:
    def test_loss_fraction(self):
        entry = RouteCriticality(source="a", target="b", delivery_after=9.0, loss=1.0)
        assert entry.loss_fraction == pytest.approx(0.1)

    def test_zero_baseline_fraction(self):
        entry = RouteCriticality(source="a", target="b", delivery_after=0.0, loss=0.0)
        assert entry.loss_fraction == 0.0

    def test_ranked_most_critical_first(self):
        critical = single_route_criticality(default_network())
        assert critical[0].source == "highland_aquifer"
        assert critical[0].target == "border_town"
        assert critical[0].loss == pytest.approx(30.0)
        losses = [entry.loss for entry in critical]
        assert losses == sorted(losses, reverse=True)

    def test_single_route_network_severs(self):
        net = HydrologicalNetwork([Aquifer("a", 5.0)], [Route("a", "b", 5.0, 1.0, 0.0)])
        critical = single_route_criticality(net)
        assert critical[0].delivery_after == pytest.approx(0.0)
        assert critical[0].loss == pytest.approx(5.0)


class TestInterdictionSequence:
    def test_default_sequence(self):
        seq = interdiction_sequence(default_network(), steps=3)
        assert len(seq) == 3
        assert all(isinstance(step, InterdictionStep) for step in seq)
        assert seq[0].delivery_before == pytest.approx(120.0)
        assert seq[0].delivery_after == pytest.approx(90.0)
        assert seq[-1].delivery_after == pytest.approx(45.0)
        assert seq[-1].cumulative_loss == pytest.approx(120.0 - 45.0)

    def test_steps_validation(self):
        with pytest.raises(ValueError):
            interdiction_sequence(default_network(), steps=0)
        with pytest.raises(ValueError):
            interdiction_sequence(default_network(), steps=True)

    def test_single_route_stops_after_sever(self):
        net = HydrologicalNetwork([Aquifer("a", 5.0)], [Route("a", "b", 5.0, 1.0, 0.0)])
        seq = interdiction_sequence(net, steps=3)
        assert len(seq) == 1
        assert seq[0].delivery_after == pytest.approx(0.0)


class TestResilienceIndex:
    def test_default(self):
        assert resilience_index(default_network()) == pytest.approx(5.0 / 6.0)

    def test_no_routes_yields_zero(self):
        # unreachable: build a zero-yield network so baseline delivery is 0
        net = HydrologicalNetwork([Aquifer("a", 0.0)], [Route("a", "b", 5.0, 1.0, 0.0)])
        assert resilience_index(net) == pytest.approx(0.0)


class TestMinimumCut:
    def test_theorem_default(self):
        net = default_network()
        cut = minimum_cut(net, "highland_aquifer", "border_town")
        solution = net.max_flow("highland_aquifer", "border_town")
        assert isinstance(cut, CutResult)
        assert cut.value == pytest.approx(solution.total_flow)
        assert cut.cut_edges == (("highland_aquifer", "border_town"),)

    def test_theorem_small_network(self):
        net = HydrologicalNetwork(
            [Aquifer("S", 100.0)],
            [
                Route("S", "A", 10.0, 1.0, 0.0),
                Route("S", "B", 10.0, 1.0, 0.0),
                Route("A", "T", 5.0, 1.0, 0.0),
                Route("B", "T", 5.0, 1.0, 0.0),
            ],
        )
        cut = minimum_cut(net, "S", "T")
        assert cut.value == pytest.approx(net.max_flow("S", "T").total_flow)
        assert cut.value == pytest.approx(10.0)


def _source_only_network() -> HydrologicalNetwork:
    """A network whose only route runs source→source, so nothing is delivered.

    ``total_delivery`` sums flows into non-source nodes; with no settlement at
    all the baseline is exactly zero. This is the degenerate case the
    zero-baseline guards exist for.
    """
    return HydrologicalNetwork(
        aquifers=[Aquifer(name="upper", yield_rate=10.0), Aquifer(name="lower", yield_rate=5.0)],
        routes=[Route("upper", "lower", capacity=8.0, distance_km=10.0, evaporation=0.1)],
    )


class TestZeroBaselineNetwork:
    def test_total_delivery_is_zero(self):
        assert total_delivery(_source_only_network()) == 0.0

    def test_resilience_index_is_zero_not_one(self):
        """No delivery to retain means zero resilience, not vacuous perfection."""
        assert resilience_index(_source_only_network()) == 0.0

    def test_interdiction_sequence_stops_immediately(self):
        assert interdiction_sequence(_source_only_network(), steps=3) == []
