"""Tests for the commodity-cartel graph model."""

import pytest

from quantum_of_solace.cartel_graph import (
    HHI_HIGHLY_CONCENTRATED,
    HHI_MODERATELY_CONCENTRATED,
    CommodityCartelGraph,
    concentration_band,
    default_cartel,
)


class TestCommodityCartelGraphInit:
    def test_empty_shares(self):
        with pytest.raises(ValueError):
            CommodityCartelGraph({})

    def test_empty_portfolio(self):
        with pytest.raises(ValueError):
            CommodityCartelGraph({"a": {}})

    def test_bad_share(self):
        with pytest.raises(ValueError):
            CommodityCartelGraph({"a": {"w": 1.5}})

    def test_bad_actor_name(self):
        with pytest.raises(ValueError):
            CommodityCartelGraph({"": {"w": 0.5}})


@pytest.fixture
def graph():
    return CommodityCartelGraph(
        {
            "quantum": {"water": 0.45, "lithium": 0.55, "copper": 0.20, "grain": 0.10},
            "rival": {"water": 0.25, "lithium": 0.30, "copper": 0.50, "grain": 0.40},
            "state": {"water": 0.30, "lithium": 0.15, "copper": 0.30, "grain": 0.50},
        }
    )


class TestQueries:
    def test_layout(self, graph):
        assert graph.actors == ("quantum", "rival", "state")
        assert graph.commodities == ("copper", "grain", "lithium", "water")

    def test_portfolio(self, graph):
        assert graph.portfolio("quantum")["water"] == 0.45

    def test_portfolio_missing(self, graph):
        with pytest.raises(KeyError):
            graph.portfolio("nobody")

    def test_controls_and_share(self, graph):
        assert graph.controls("quantum", "water")
        assert not graph.controls("quantum", "oil")
        assert graph.share_of("quantum", "water") == 0.45
        assert graph.share_of("quantum", "oil") == 0.0

    def test_holders(self, graph):
        assert set(graph.holders("water")) == {"quantum", "rival", "state"}
        assert graph.holders("oil") == ()


class TestConcentration:
    def test_hhi_per_commodity(self, graph):
        # water: 0.45^2 + 0.25^2 + 0.30^2 = 0.2025+0.0625+0.09 = 0.355 -> 3550
        assert graph.hhi("water") == pytest.approx(3550.0)
        assert 0 < graph.hhi("lithium") < 10000.0

    def test_hhi_aggregate(self, graph):
        aggregate = graph.hhi()
        assert aggregate == pytest.approx(
            (graph.hhi("water") + graph.hhi("lithium") + graph.hhi("copper") + graph.hhi("grain")) / 4.0
        )

    def test_concentration_ratio(self, graph):
        # water top-2: 0.45+0.30 = 0.75
        assert graph.concentration_ratio("water", top=2) == pytest.approx(0.75)

    def test_concentration_ratio_validation(self, graph):
        with pytest.raises(ValueError):
            graph.concentration_ratio("water", top=0)

    def test_report(self, graph):
        report = graph.report("water")
        assert report.dominant_actor == "quantum"
        assert report.dominant_share == 0.45
        assert report.num_actors == 3
        assert report.hhi == pytest.approx(3550.0)

    def test_report_unknown_commodity(self, graph):
        with pytest.raises(ValueError):
            graph.report("oil")


class TestActorMetrics:
    def test_mean_control(self, graph):
        # quantum mean = (0.45+0.55+0.20+0.10)/4 = 0.325
        assert graph.mean_control("quantum") == pytest.approx(0.325)

    def test_mean_control_unknown(self, graph):
        assert graph.mean_control("nobody") == 0.0

    def test_diversification(self, graph):
        # quantum portfolio HHI points: 45^2+55^2+20^2+10^2 = 2025+3025+400+100=5550
        assert graph.diversification("quantum") == pytest.approx(1.0 - 5550.0 / 10000.0)

    def test_diversification_single(self, graph):
        single = CommodityCartelGraph({"a": {"w": 0.5}})
        assert single.diversification("a") == 0.0

    def test_dominance_count_and_map(self, graph):
        assert graph.dominance_count("quantum") == 2  # water + lithium
        dominance = graph.dominance_map()
        assert dominance["water"] == "quantum"
        assert dominance["lithium"] == "quantum"


class TestDefaultCartel:
    def test_default(self):
        cartel = default_cartel()
        assert "quantum" in cartel.actors
        assert "lithium" in cartel.commodities
        assert cartel.dominance_map()["water"] == "quantum"


class TestConcentrationBand:
    """The Merger-Guidelines concentration bands the manuscript cites."""

    def test_unconcentrated(self):
        assert concentration_band(0.0) == "unconcentrated"
        assert concentration_band(HHI_MODERATELY_CONCENTRATED - 0.1) == "unconcentrated"

    def test_moderately_concentrated_is_the_closed_middle_band(self):
        assert concentration_band(HHI_MODERATELY_CONCENTRATED) == "moderately concentrated"
        assert concentration_band(2000.0) == "moderately concentrated"
        assert concentration_band(HHI_HIGHLY_CONCENTRATED) == "moderately concentrated"

    def test_highly_concentrated_above_the_upper_threshold(self):
        assert concentration_band(HHI_HIGHLY_CONCENTRATED + 0.1) == "highly concentrated"
        assert concentration_band(10000.0) == "highly concentrated"

    def test_thresholds_are_ordered(self):
        assert HHI_MODERATELY_CONCENTRATED < HHI_HIGHLY_CONCENTRATED

    def test_rejects_bad_input(self):
        with pytest.raises(ValueError, match="non-negative"):
            concentration_band(-1.0)
        with pytest.raises(ValueError, match="non-negative"):
            concentration_band(True)
        with pytest.raises(ValueError, match="non-negative"):
            concentration_band("2500")  # type: ignore[arg-type]

    def test_default_cartel_is_highly_concentrated_on_every_commodity(self):
        cartel = default_cartel()
        for commodity in cartel.commodities:
            assert concentration_band(cartel.hhi(commodity)) == "highly concentrated"


class TestShareValidation:
    def test_non_numeric_share_rejected(self):
        with pytest.raises(ValueError, match="non-boolean number"):
            CommodityCartelGraph({"a": {"water": "0.5"}})  # type: ignore[dict-item]

    def test_boolean_share_rejected(self):
        with pytest.raises(ValueError, match="non-boolean number"):
            CommodityCartelGraph({"a": {"water": True}})
