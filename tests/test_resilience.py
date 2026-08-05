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
        assert total_delivery(default_network()) == pytest.approx(80.0)

    def test_monotone_under_removal(self):
        net = default_network()
        smaller = net.without_route("highland_aquifer", "border_town")
        assert total_delivery(smaller) < total_delivery(net)

    @pytest.mark.parametrize(
        "network",
        [
            default_network(),
            # A network whose route capacities dwarf the aquifer yields: the old
            # sum-of-per-source-max-flows would report 3 * 50 = 150 here.
            HydrologicalNetwork(
                [Aquifer("w1", 4.0), Aquifer("w2", 3.0), Aquifer("w3", 2.0)],
                [
                    Route("w1", "town", 50.0, 1.0, 0.0),
                    Route("w2", "town", 50.0, 1.0, 0.0),
                    Route("w3", "town", 50.0, 1.0, 0.0),
                ],
            ),
            # Two settlements sharing one over-provisioned aquifer.
            HydrologicalNetwork(
                [Aquifer("spring", 10.0)],
                [Route("spring", "north", 40.0, 1.0, 0.0), Route("spring", "south", 40.0, 1.0, 0.0)],
            ),
            # Route capacity binds instead of yield.
            HydrologicalNetwork(
                [Aquifer("deep", 100.0)],
                [Route("deep", "camp", 7.0, 1.0, 0.0)],
            ),
        ],
        ids=["default", "yield_bound_three_sources", "yield_bound_two_settlements", "capacity_bound"],
    )
    def test_never_exceeds_aquifer_supply(self, network: HydrologicalNetwork):
        """Delivery is physically bounded by what the aquifers actually produce.

        This is the invariant the previous implementation violated: it summed
        each settlement's per-source maximum flow independently, double-counting
        shared yield, and reported 120.0 units against an 80.0-unit supply.
        """
        assert total_delivery(network) <= network.total_supply() + 1e-9

    def test_per_settlement_maxima_are_alternatives_not_addends(self):
        """Summing per-settlement maxima overstates the network — by design.

        The sum is what a naive additive reading would produce; asserting it is
        strictly greater pins the fact that the settlements compete for the same
        yield, so a future change cannot quietly make the sum the headline.
        """
        net = default_network()
        per_settlement = sum(net.delivery_capacity([name]) for name in net.settlements)
        assert per_settlement == pytest.approx(120.0)
        assert per_settlement > total_delivery(net)


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
        assert critical[0].loss == pytest.approx(20.0)
        losses = [entry.loss for entry in critical]
        assert losses == sorted(losses, reverse=True)

    def test_some_routes_are_redundant(self):
        """Redundancy is measured, not assumed to be absent.

        Two routes of the canonical network cost nothing when cut. The
        manuscript reports critical and redundant counts separately precisely
        because this partition is not forced to be all-or-nothing.
        """
        critical = single_route_criticality(default_network())
        redundant = [entry for entry in critical if entry.loss == pytest.approx(0.0)]
        assert len(redundant) == 2
        assert {(entry.source, entry.target) for entry in redundant} == {
            ("deep_well", "border_town"),
            ("oasis_spring", "valley_compact"),
        }

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
        assert seq[0].delivery_before == pytest.approx(80.0)
        assert seq[0].delivery_after == pytest.approx(60.0)
        assert seq[-1].delivery_after == pytest.approx(35.0)
        assert seq[-1].cumulative_loss == pytest.approx(80.0 - 35.0)

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
        # Retained fractions over the six single cuts: 60, 70, 75, 75, 80, 80
        # out of 80 -> mean 440/480.
        assert resilience_index(default_network()) == pytest.approx(440.0 / 480.0)

    def test_is_a_mean_not_a_worst_case(self):
        """The index must exceed the worst single cut, so it cannot be read as a bound.

        With every retained fraction distinct-in-part, the mean sits strictly
        above the minimum. Any prose calling the index a worst-case guarantee is
        contradicted by this test.
        """
        net = default_network()
        baseline = total_delivery(net)
        retained = [entry.delivery_after / baseline for entry in single_route_criticality(net, baseline)]
        assert resilience_index(net) == pytest.approx(sum(retained) / len(retained))
        assert resilience_index(net) > min(retained)
        assert min(retained) == pytest.approx(0.75)

    def test_zero_yield_network_delivers_nothing(self):
        """A zero-yield network genuinely delivers 0.0, so the guard is exercised.

        Two routes, so the ``len(routes) == 1`` sever shortcut in
        ``single_route_criticality`` cannot be what produces the zero: the
        baseline itself is zero because the aquifers yield nothing. (Before
        delivery honoured aquifer yield, ``total_delivery`` on this network was
        the sum of route capacities and the zero came from the wrong branch.)
        """
        net = HydrologicalNetwork(
            [Aquifer("a", 0.0), Aquifer("z", 0.0)],
            [Route("a", "b", 5.0, 1.0, 0.0), Route("z", "b", 7.0, 1.0, 0.0)],
        )
        assert len(net.routes) > 1
        assert total_delivery(net) == pytest.approx(0.0)
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
