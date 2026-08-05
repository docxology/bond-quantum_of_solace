"""Tests for the water scarcity pricing and monopoly-economics model."""

import pytest

from quantum_of_solace.pricing import (
    DEFAULT_DEMAND_A,
    DEFAULT_DEMAND_B,
    DEFAULT_MARGINAL_COST,
    consumer_surplus,
    deadweight_loss,
    default_demand,
    inverse_demand,
    market_clearing_price,
    market_outcome,
    monopoly_price,
    monopoly_quantity,
    point_elasticity,
    revenue,
    scarcity_impact,
)


class TestBasicCurves:
    def test_inverse_demand_positive(self):
        assert inverse_demand(10.0, 100.0, 2.0) == pytest.approx(80.0)

    def test_inverse_demand_clamps_at_zero(self):
        assert inverse_demand(60.0, 100.0, 2.0) == pytest.approx(0.0)

    def test_inverse_demand_validation(self):
        with pytest.raises(ValueError):
            inverse_demand(1.0, 0.0, 2.0)
        with pytest.raises(ValueError):
            inverse_demand(1.0, 100.0, 0.0)
        with pytest.raises(ValueError):
            inverse_demand(-1.0, 100.0, 2.0)
        with pytest.raises(ValueError):
            inverse_demand(1.0, 100.0, True)

    def test_market_clearing_price(self):
        assert market_clearing_price(40.0, 100.0, 1.0) == pytest.approx(60.0)
        # supply beyond the choke quantity clears at 0
        assert market_clearing_price(120.0, 100.0, 1.0) == pytest.approx(0.0)

    def test_default_demand(self):
        a, b, mc = default_demand()
        assert (a, b, mc) == (DEFAULT_DEMAND_A, DEFAULT_DEMAND_B, DEFAULT_MARGINAL_COST)


class TestElasticity:
    def test_point_elasticity(self):
        assert point_elasticity(50.0, 100.0, 2.0) == pytest.approx(1.0)

    def test_validation(self):
        with pytest.raises(ValueError):
            point_elasticity(-1.0, 100.0, 2.0)
        with pytest.raises(ValueError):
            point_elasticity(50.0, 0.0, 2.0)
        with pytest.raises(ValueError):
            point_elasticity(50.0, 100.0, 0.0)


class TestRevenueAndSurplus:
    def test_revenue(self):
        assert revenue(10.0, 20.0) == pytest.approx(200.0)
        with pytest.raises(ValueError):
            revenue(-1.0, 5.0)

    def test_consumer_surplus(self):
        assert consumer_surplus(20.0, 40.0, 100.0, 2.0) == pytest.approx(1600.0)
        with pytest.raises(ValueError):
            consumer_surplus(120.0, 40.0, 100.0, 2.0)
        with pytest.raises(ValueError):
            consumer_surplus(20.0, -1.0, 100.0, 2.0)


class TestMonopoly:
    def test_monopoly_quantity(self):
        assert monopoly_quantity(100.0, 2.0, 10.0) == pytest.approx(22.5)

    def test_monopoly_price(self):
        assert monopoly_price(100.0, 2.0, 10.0) == pytest.approx(55.0)

    def test_validation(self):
        with pytest.raises(ValueError):
            monopoly_quantity(100.0, 2.0, 150.0)  # mc > a
        with pytest.raises(ValueError):
            monopoly_price(100.0, 2.0, -1.0)

    def test_deadweight_loss(self):
        assert deadweight_loss(100.0, 2.0, 10.0) == pytest.approx(506.25)

    def test_market_outcome(self):
        outcome = market_outcome(100.0, 2.0, 10.0)
        assert outcome.competitive_price == 10.0
        assert outcome.competitive_quantity == pytest.approx(45.0)
        assert outcome.monopoly_price == pytest.approx(55.0)
        assert outcome.monopoly_quantity == pytest.approx(22.5)
        assert outcome.deadweight_loss == pytest.approx(506.25)
        assert outcome.consumer_surplus_monopoly < outcome.consumer_surplus_competitive


class TestScarcityImpact:
    def test_positive_branch(self):
        impact = scarcity_impact(40.0, 30.0, 100.0, 1.0)
        assert impact["baseline_price"] == pytest.approx(60.0)
        assert impact["restricted_price"] == pytest.approx(70.0)
        assert impact["price_rise_frac"] == pytest.approx(70.0 / 60.0 - 1.0)
        assert impact["scarcity_rent"] == pytest.approx(10.0 * 30.0)
        assert impact["elasticity"] == pytest.approx(1.0 * 60.0 / 40.0)

    def test_baseline_price_zero_branch(self):
        # abundant baseline supply clears at price 0: no rise, no elasticity
        impact = scarcity_impact(120.0, 40.0, 100.0, 1.0)
        assert impact["baseline_price"] == pytest.approx(0.0)
        assert impact["restricted_price"] == pytest.approx(60.0)
        assert impact["price_rise_frac"] == pytest.approx(0.0)
        assert impact["scarcity_rent"] == pytest.approx(60.0 * 40.0)

    def test_restricted_above_baseline_rejected(self):
        with pytest.raises(ValueError):
            scarcity_impact(40.0, 50.0, 100.0, 1.0)

    def test_negative_supply_rejected(self):
        with pytest.raises(ValueError):
            scarcity_impact(-1.0, 10.0, 100.0, 1.0)
