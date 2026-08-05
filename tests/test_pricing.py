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
        # |eps| = p / (b*q) = 50 / (2*100) = 0.25.
        assert point_elasticity(50.0, 100.0, 2.0) == pytest.approx(0.25)

    @pytest.mark.parametrize(
        ("a", "b", "quantity"),
        [
            (100.0, 2.0, 10.0),
            (100.0, 2.0, 40.0),
            (100.0, 0.25, 214.0),
            (80.0, 4.0, 5.0),
            (250.0, 0.5, 300.0),
        ],
    )
    def test_matches_a_numerical_derivative_of_the_demand_curve(self, a: float, b: float, quantity: float):
        """Independent ground truth: differentiate the demand curve numerically.

        ``point_elasticity`` must equal |dq/dp * p/q| where dq/dp is measured by
        central difference on the *inverse* demand curve rather than restated
        from the same closed form, so an algebraically wrong formula (the
        historical ``b*p/q``, off by a factor of b^2) cannot pass. The two agree
        only when b == 1, which is why no case below uses b == 1.
        """
        price = inverse_demand(quantity, a, b)
        step = 1e-4

        def quantity_at(p: float) -> float:
            # Invert p = a - b*q exactly through the same parameters.
            return (a - p) / b

        dq_dp = (quantity_at(price + step) - quantity_at(price - step)) / (2.0 * step)
        expected = abs(dq_dp * price / quantity)
        assert point_elasticity(price, quantity, b) == pytest.approx(expected, rel=1e-6)

    def test_inelastic_below_one_elastic_above(self):
        """The unit-elastic point is the demand curve's midpoint quantity a/(2b)."""
        a, b = 100.0, 0.25
        midpoint = a / (2.0 * b)
        assert point_elasticity(inverse_demand(midpoint, a, b), midpoint, b) == pytest.approx(1.0)
        low_q = midpoint * 0.5
        high_q = midpoint * 1.5
        assert point_elasticity(inverse_demand(low_q, a, b), low_q, b) > 1.0
        assert point_elasticity(inverse_demand(high_q, a, b), high_q, b) < 1.0

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
        # b = 0.5, deliberately not 1.0: at b == 1 the correct elasticity
        # p/(b*q) and the historical wrong form b*p/q coincide, so a b == 1
        # fixture cannot detect the defect.
        impact = scarcity_impact(40.0, 30.0, 100.0, 0.5)
        assert impact["baseline_price"] == pytest.approx(80.0)
        assert impact["restricted_price"] == pytest.approx(85.0)
        assert impact["price_rise_frac"] == pytest.approx(85.0 / 80.0 - 1.0)
        assert impact["scarcity_rent"] == pytest.approx(5.0 * 30.0)
        assert impact["elasticity"] == pytest.approx(80.0 / (0.5 * 40.0))

    def test_price_rise_is_the_volume_cut_over_the_elasticity(self):
        """On a linear curve the proportional moves relate exactly by 1/|eps|.

        dp = b*dq, so (dp/p) / (dq/q) = b*q/p = 1/elasticity — exactly, not
        approximately. This binds the elasticity the assessment reports to the
        price and volume it reports beside it, so the three cannot drift apart.
        """
        baseline, restricted, a, b = 214.0, 142.5, 100.0, 0.25
        impact = scarcity_impact(baseline, restricted, a, b)
        volume_cut_frac = (baseline - restricted) / baseline
        ratio = impact["price_rise_frac"] / volume_cut_frac
        assert ratio == pytest.approx(1.0 / impact["elasticity"], rel=1e-12)

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
