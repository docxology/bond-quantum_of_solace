"""Tests for the desert hydrology network model."""

import pytest

from quantum_of_solace.hydrology import (
    Aquifer,
    FlowSolution,
    HydrologicalNetwork,
    MassBalance,
    Route,
    ShortestRoute,
    default_network,
)


class TestAquifer:
    def test_valid(self):
        aquifer = Aquifer(name="source", yield_rate=10.0, quality=0.8)
        assert aquifer.name == "source"
        assert aquifer.yield_rate == 10.0
        assert aquifer.quality == 0.8

    def test_default_quality(self):
        assert Aquifer("a", 1.0).quality == 1.0

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"name": "", "yield_rate": 1.0},
            {"name": "a", "yield_rate": -1.0},
            {"name": "a", "yield_rate": True},
            {"name": "a", "yield_rate": 1.0, "quality": 1.5},
            {"name": "a", "yield_rate": 1.0, "quality": -0.1},
            {"name": "a", "yield_rate": 1.0, "quality": True},
        ],
    )
    def test_invalid(self, kwargs):
        with pytest.raises(ValueError):
            Aquifer(**kwargs)


class TestRoute:
    def test_valid(self):
        route = Route("a", "b", 10.0, 5.0, 0.1, 2.0)
        assert route.cost_per_unit == 2.0

    def test_simple(self):
        assert Route("a", "b", 10.0, 5.0, 0.1).cost_per_unit == 1.0

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"source": "", "target": "b", "capacity": 1.0, "distance_km": 1.0, "evaporation": 0.0},
            {"source": "a", "target": "", "capacity": 1.0, "distance_km": 1.0, "evaporation": 0.0},
            {"source": "a", "target": "b", "capacity": -1.0, "distance_km": 1.0, "evaporation": 0.0},
            {"source": "a", "target": "b", "capacity": 1.0, "distance_km": -1.0, "evaporation": 0.0},
            {"source": "a", "target": "b", "capacity": 1.0, "distance_km": 1.0, "evaporation": 1.5},
            {
                "source": "a",
                "target": "b",
                "capacity": 1.0,
                "distance_km": 1.0,
                "evaporation": 0.0,
                "cost_per_unit": -1,
            },
        ],
    )
    def test_invalid(self, kwargs):
        with pytest.raises(ValueError):
            Route(**kwargs)


class TestShortestRoute:
    def test_properties(self):
        route = ShortestRoute(path=("a", "b", "c"), total_cost=2.5, delivered_fraction=0.81)
        assert route.evaporation_loss == pytest.approx(0.19)
        assert route.hops == 2
        assert ShortestRoute(("a",), 0.0, 1.0).hops == 0


class TestFlowSolution:
    def test_flow_on(self):
        solution = FlowSolution(total_flow=5.0, edge_flows=(("a", "b", 3.0),), augmentations=1)
        assert solution.flow_on("a", "b") == 3.0
        assert solution.flow_on("x", "y") == 0.0


class TestMassBalance:
    def test_net_surplus(self):
        assert MassBalance("n", 10.0, 4.0, 2.0).net_surplus == 6.0


class TestHydrologicalNetworkInit:
    def test_empty_aquifers(self):
        with pytest.raises(ValueError):
            HydrologicalNetwork([], [Route("a", "b", 1.0, 1.0, 0.0)])

    def test_empty_routes(self):
        with pytest.raises(ValueError):
            HydrologicalNetwork([Aquifer("a", 1.0)], [])


@pytest.fixture
def network():
    aquifers = [
        Aquifer("highland", 40.0, 0.9),
        Aquifer("deep_well", 25.0, 0.6),
        Aquifer("oasis", 15.0, 0.8),
    ]
    routes = [
        Route("highland", "border_town", 30.0, 120.0, 0.15, 1.0),
        Route("highland", "valley", 20.0, 90.0, 0.10, 0.8),
        Route("deep_well", "border_town", 20.0, 70.0, 0.20, 0.6),
        Route("deep_well", "valley", 25.0, 110.0, 0.18, 0.6),
        Route("oasis", "border_town", 15.0, 40.0, 0.05, 0.4),
        Route("oasis", "valley", 10.0, 60.0, 0.08, 0.4),
    ]
    return HydrologicalNetwork(aquifers, routes)


class TestHydrologicalNetworkQueries:
    def test_names_and_layout(self, network):
        assert network.node_names == ("border_town", "deep_well", "highland", "oasis", "valley")
        assert network.aquifers == ("highland", "deep_well", "oasis")
        assert len(network.routes) == 6

    def test_source_queries(self, network):
        assert network.is_source("highland")
        assert not network.is_source("border_town")
        assert network.supply("highland") == 40.0
        assert network.supply("border_town") == 0.0
        assert network.total_supply() == 80.0

    def test_loss_helpers(self, network):
        route = network.routes[0]
        assert network.evaporation_loss(10.0, route) == pytest.approx(1.5)
        assert network.delivered_volume(10.0, route) == pytest.approx(8.5)
        assert network.effective_unit_cost(route) == pytest.approx(1.0 / 0.85)

    def test_out_routes(self, network):
        assert len(network.out_routes("highland")) == 2
        assert network.out_routes("border_town") == ()


class TestMassBalanceComputation:
    def test_mass_balance(self, network):
        flows = {("highland", "border_town"): 10.0, ("oasis", "valley"): 8.0}
        rows = {row.node: row for row in network.mass_balance(flows)}
        assert rows["border_town"].delivered_in == pytest.approx(8.5)
        assert rows["highland"].sent_out == 10.0
        assert rows["border_town"].lost_evaporation == pytest.approx(1.5)
        assert rows["valley"].delivered_in == pytest.approx(8.0 * 0.92)

    def test_mass_balance_unknown_edge(self, network):
        with pytest.raises(ValueError):
            network.mass_balance({("highland", "oasis"): 1.0})


class TestShortestRouteSearch:
    def test_same_node(self, network):
        result = network.shortest_route("highland", "highland")
        assert result.path == ("highland",)
        assert result.total_cost == 0.0

    def test_reaches_settlement(self, network):
        result = network.shortest_route("highland", "border_town")
        assert result.path[0] == "highland"
        assert result.path[-1] == "border_town"
        assert result.delivered_fraction <= 1.0

    def test_no_path_raises(self):
        net = HydrologicalNetwork([Aquifer("a", 5.0)], [Route("a", "b", 5.0, 1.0, 0.0)])
        with pytest.raises(ValueError):
            net.shortest_route("a", "missing")


class TestMinCutMetadata:
    def test_reachable_equals_source_side(self):
        net = default_network()
        solution = net.max_flow("highland_aquifer", "border_town")
        # the source side of the cut is exactly the highland aquifer
        assert set(solution.reachable) == {"highland_aquifer", "valley_compact"}


class TestNetworkSurgery:
    def test_without_route(self):
        net = default_network()
        assert len(net.without_route("deep_well", "border_town").routes) == 5

    def test_without_routes(self):
        net = default_network()
        pruned = net.without_routes({("deep_well", "border_town"), ("oasis_spring", "valley_compact")})
        assert len(pruned.routes) == 4

    def test_remove_every_route_raises(self):
        net = HydrologicalNetwork([Aquifer("a", 5.0)], [Route("a", "b", 5.0, 1.0, 0.0)])
        with pytest.raises(ValueError):
            net.without_routes({("a", "b")})


class TestMaxFlow:
    def test_default_delivery(self):
        net = default_network()
        border = net.max_flow("highland_aquifer", "border_town")
        assert border.total_flow == pytest.approx(30.0)
        assert border.augmentations >= 1

    def test_source_must_be_aquifer(self, network):
        with pytest.raises(ValueError):
            network.max_flow("border_town", "valley")

    def test_disconnected_is_zero(self):
        net = HydrologicalNetwork([Aquifer("a", 5.0)], [Route("a", "b", 5.0, 1.0, 0.0)])
        solution = net.max_flow("a", "b")
        assert solution.total_flow == pytest.approx(5.0)
        # an unreachable target yields zero flow and no augmentations
        empty = net.max_flow("a", "missing")
        assert empty.total_flow == 0.0
        assert empty.augmentations == 0

    def test_diamond_routing_uses_intermediate_nodes(self):
        # A multi-branch network through intermediate nodes A, B, C.
        aquifers = [Aquifer("S", 100.0)]
        routes = [
            Route("S", "A", 10.0, 1.0, 0.0),
            Route("S", "B", 10.0, 1.0, 0.0),
            Route("A", "T", 5.0, 1.0, 0.0),
            Route("A", "C", 7.0, 1.0, 0.0),
            Route("B", "C", 8.0, 1.0, 0.0),
            Route("C", "T", 10.0, 1.0, 0.0),
        ]
        net = HydrologicalNetwork(aquifers, routes)
        solution = net.max_flow("S", "T")
        # A->T (5) plus C->T (10) = 15; C collects 5 (via A) + 8 (via B) capped at 10.
        assert solution.total_flow == pytest.approx(15.0)
        assert solution.augmentations >= 2
