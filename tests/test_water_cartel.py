"""Tests for the water-rights cartel / reservoir-leverage model."""

import pytest

from quantum_of_solace.water_cartel import (
    Dam,
    DamState,
    cartel_leverage,
    dam_leverage,
    default_dams,
    horizon_demand_volume,
    run_reservoir,
    withheld_volume,
)


def _dam(**overrides):
    base = {
        "name": "d",
        "capacity": 100.0,
        "initial_storage": 50.0,
        "inflow": 10.0,
        "downstream_demand": 20.0,
        "max_release": 15.0,
        "evaporation_rate": 0.0,
    }
    base.update(overrides)
    return Dam(**base)


class TestDam:
    def test_defaults(self):
        dam = _dam()
        assert dam.evaporation_rate == 0.0
        assert dam.max_release == 15.0

    def test_invalid_storage_over_capacity(self):
        with pytest.raises(ValueError):
            _dam(initial_storage=150.0, capacity=100.0)

    def test_invalid_evaporation(self):
        with pytest.raises(ValueError):
            _dam(evaporation_rate=1.5)

    def test_invalid_name(self):
        with pytest.raises(ValueError):
            _dam(name="")

    def test_invalid_negative(self):
        with pytest.raises(ValueError):
            _dam(capacity=-1.0)
        with pytest.raises(ValueError):
            _dam(inflow=True)


class TestRunReservoir:
    def test_periods_validation(self):
        with pytest.raises(ValueError):
            run_reservoir(_dam(), 0)
        with pytest.raises(ValueError):
            run_reservoir(_dam(), True)

    def test_restriction_validation(self):
        with pytest.raises(ValueError):
            run_reservoir(_dam(), 3, restriction_frac=1.2)

    def test_trace_shape(self):
        trace = run_reservoir(_dam(), 4, restriction_frac=0.5)
        assert len(trace.states) == 4
        assert trace.dam.name == "d"
        assert trace.restriction_frac == 0.5
        assert isinstance(trace.states[0], DamState)

    def test_restriction_reduces_release(self):
        baseline = run_reservoir(_dam(), 3, 0.0).total_release()
        restricted = run_reservoir(_dam(), 3, 0.5).total_release()
        assert baseline > restricted

    def test_capacity_clamp_and_evaporation(self):
        with_capacity = _dam(capacity=50.0, initial_storage=50.0, inflow=30.0, max_release=0.0)
        clamped = run_reservoir(with_capacity, 1).states[0]
        assert clamped.storage_after <= 50.0
        evaporating = run_reservoir(_dam(evaporation_rate=0.1), 2)
        assert evaporating.total_evaporation() > 0.0
        assert evaporating.final_storage > 0.0

    def test_reservoir_trace_totals(self):
        trace = run_reservoir(_dam(inflow=5.0), 3, 0.1)
        assert trace.total_release() > 0
        assert trace.total_evaporation() == 0.0


class TestLeverage:
    def test_withheld_volume(self):
        dam = _dam(inflow=10.0, max_release=15.0, capacity=100.0)
        assert withheld_volume(dam, 3, 0.0) == 0.0
        assert withheld_volume(dam, 3, 0.5) > 0.0

    def test_dam_leverage_zero_demand(self):
        dam = _dam(downstream_demand=0.0)
        assert dam_leverage(dam, 3, 0.5) == 0.0

    def test_dam_leverage_is_withheld_over_horizon_demand(self):
        """Leverage divides a horizon volume by a horizon volume, not a rate."""
        dam = _dam(downstream_demand=20.0, inflow=10.0, max_release=15.0)
        periods = 3
        expected = withheld_volume(dam, periods, 0.5) / (dam.downstream_demand * periods)
        assert dam_leverage(dam, periods, 0.5) == pytest.approx(expected)
        assert 0.0 < dam_leverage(dam, periods, 0.5) < 1.0

    def test_dam_leverage_does_not_scale_with_period_count(self):
        """Doubling the horizon must not double the leverage share.

        This is the positive control for the dimensional fix: with a steady
        release the withheld volume and the horizon demand grow at the same
        rate, so the ratio is horizon-invariant. Dividing by a per-period
        demand (the previous behaviour) would double this number.
        """
        # Storage large enough that the release is max_release-bound every period.
        dam = _dam(capacity=1000.0, initial_storage=500.0, inflow=15.0, max_release=15.0, downstream_demand=20.0)
        short = dam_leverage(dam, 4, 0.5)
        long = dam_leverage(dam, 8, 0.5)
        assert short == pytest.approx(long, abs=1e-9)
        assert short == pytest.approx(0.375, abs=1e-9)  # (15*0.5) / 20

    def test_horizon_demand_volume(self):
        dam = _dam(downstream_demand=20.0)
        assert horizon_demand_volume(dam, 6) == 120.0

    def test_horizon_demand_volume_rejects_bad_periods(self):
        dam = _dam()
        with pytest.raises(ValueError, match="positive integer"):
            horizon_demand_volume(dam, 0)
        with pytest.raises(ValueError, match="positive integer"):
            horizon_demand_volume(dam, True)


class TestCartelLeverage:
    def test_validation(self):
        with pytest.raises(ValueError):
            cartel_leverage(default_dams(), set(), restriction_frac=2.0)
        with pytest.raises(ValueError):
            cartel_leverage(default_dams(), set(), periods=0)

    def test_default_fleet_report(self):
        controlled = {"highland_reservoir", "desert_holding"}
        report = cartel_leverage(default_dams(), controlled, 0.5, 12)
        assert report["periods"] == 12
        per_dam = report["per_dam"]
        assert per_dam["highland_reservoir"]["controlled"] is True
        assert per_dam["border_barrage"]["controlled"] is False
        assert report["aggregate"] > 0.0

    def test_aggregate_is_a_share_and_re_derivable(self):
        """The aggregate is withheld / horizon demand and stays inside [0, 1]."""
        controlled = {"highland_reservoir", "desert_holding"}
        fleet = default_dams()
        report = cartel_leverage(fleet, controlled, 0.5, 12)
        expected_demand = sum(dam.downstream_demand for dam in fleet) * 12
        assert report["horizon_demand"] == pytest.approx(expected_demand)
        assert report["aggregate"] == pytest.approx(report["withheld_volume"] / report["horizon_demand"])
        assert 0.0 < report["aggregate"] < 1.0
        # An uncontrolled dam contributes demand to the denominator but no withholding.
        assert report["per_dam"]["border_barrage"]["withheld_volume"] == 0.0
        assert report["per_dam"]["border_barrage"]["horizon_demand"] == pytest.approx(95.0 * 12)

    def test_full_restriction_bounds_the_aggregate(self):
        """A total cut on every dam withholds at most the whole horizon demand."""
        fleet = default_dams()
        report = cartel_leverage(fleet, {dam.name for dam in fleet}, 1.0, 12)
        assert 0.0 < report["aggregate"] <= 1.0

    def test_uncontrolled_cartel_zero(self):
        report = cartel_leverage(default_dams(), set(), 0.5, 4)
        assert report["aggregate"] == 0.0
        assert all(not entry["controlled"] for entry in report["per_dam"].values())

    def test_zero_total_demand(self):
        dam = _dam(downstream_demand=0.0)
        report = cartel_leverage([dam], {"d"}, 0.5, 2)
        assert report["aggregate"] == 0.0


class TestFractionValidation:
    def test_non_numeric_restriction_rejected(self):
        with pytest.raises(ValueError, match="non-boolean number"):
            run_reservoir(_dam(), 3, restriction_frac="half")  # type: ignore[arg-type]

    def test_boolean_restriction_rejected(self):
        with pytest.raises(ValueError, match="non-boolean number"):
            cartel_leverage(default_dams(), set(), restriction_frac=True)
