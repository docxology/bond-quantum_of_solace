"""Tests for the cooperative power-index model (Shapley / Banzhaf)."""

from math import sqrt

import pytest

from quantum_of_solace.cartel_graph import CommodityCartelGraph, default_cartel
from quantum_of_solace.shapley import (
    DEFAULT_COMMODITY_WEIGHTS,
    banzhaf_power,
    coalition_value,
    default_weights,
    dominance_gap,
    power_ranking,
    shapley_value,
)


class TestCoalitionValue:
    def test_empty_coalition(self):
        assert coalition_value(frozenset(), default_cartel()) == pytest.approx(0.0)

    def test_singleton(self):
        cartel = CommodityCartelGraph({"a": {"water": 0.5}})
        assert coalition_value(frozenset({"a"}), cartel, {"water": 2.0}) == pytest.approx(2.0 * sqrt(0.5))

    def test_unknown_actor_rejected(self):
        with pytest.raises(ValueError):
            coalition_value(frozenset({"ghost"}), default_cartel())

    def test_bad_weight_rejected(self):
        cartel = CommodityCartelGraph({"a": {"water": 0.5}})
        with pytest.raises(ValueError):
            coalition_value(frozenset({"a"}), cartel, {"water": 0.0})


class TestShapleyValue:
    def test_default_values(self):
        values = shapley_value(default_cartel())
        assert values["quantum"] == pytest.approx(2.6237, abs=1e-2)
        assert values["rival_syndicate"] == pytest.approx(2.2899, abs=1e-2)
        assert values["state_utility"] == pytest.approx(2.0864, abs=1e-2)

    def test_efficiency_sums_to_grand(self):
        cartel = default_cartel()
        values = shapley_value(cartel)
        grand = coalition_value(frozenset(cartel.actors), cartel)
        assert sum(values.values()) == pytest.approx(grand)

    def test_two_actor_exact(self):
        cartel = CommodityCartelGraph({"a": {"water": 0.8}, "b": {"water": 0.4}})
        values = shapley_value(cartel, {"water": 1.0})
        phi_a = 0.5 * (sqrt(0.8) + sqrt(1.2) - sqrt(0.4))
        phi_b = 0.5 * (sqrt(0.4) + sqrt(1.2) - sqrt(0.8))
        assert values["a"] == pytest.approx(phi_a)
        assert values["b"] == pytest.approx(phi_b)

    def test_single_actor(self):
        cartel = CommodityCartelGraph({"a": {"water": 0.5}})
        values = shapley_value(cartel, {"water": 1.0})
        assert values == {"a": pytest.approx(sqrt(0.5))}


class TestBanzhafPower:
    def test_normalised_sums_to_one(self):
        power = banzhaf_power(default_cartel())
        assert sum(power.values()) == pytest.approx(1.0)

    def test_default_values(self):
        power = banzhaf_power(default_cartel())
        assert power["quantum"] == pytest.approx(0.3777, abs=1e-2)

    def test_single_actor(self):
        cartel = CommodityCartelGraph({"a": {"water": 0.5}})
        power = banzhaf_power(cartel, {"water": 1.0})
        assert power["a"] == pytest.approx(1.0)


class TestPowerRankingAndGap:
    def test_default_ranking(self):
        assert power_ranking(default_cartel()) == ("quantum", "rival_syndicate", "state_utility")

    def test_dominance_gap(self):
        assert dominance_gap(default_cartel()) == pytest.approx(2.6237 - 2.2899, abs=1e-2)

    def test_single_actor_gap_zero(self):
        cartel = CommodityCartelGraph({"a": {"water": 0.5}})
        assert dominance_gap(cartel) == 0.0


class TestWeights:
    def test_default_weights_copy(self):
        weights = default_weights()
        assert weights == DEFAULT_COMMODITY_WEIGHTS
        weights["water"] = 999.0
        # the module default is unchanged
        assert default_weights()["water"] == 3.0

    def test_missing_weight_rejected(self):
        cartel = default_cartel()
        with pytest.raises(ValueError):
            shapley_value(cartel, {"water": 3.0})  # missing lithium/copper/grain
