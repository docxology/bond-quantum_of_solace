"""Water-rights cartel and reservoir-leverage model (QUANTUM).

The film's antagonist gains leverage by controlling dams — holding back the
releases that downstream settlements depend on. This module models a set of
reservoirs (dams) with storage capacity, natural inflow and a downstream
demand, then simulates their operation under a *cartel restriction*: the
fraction of normally-released water the controlling cartel withholds.

Algorithms (all deterministic, computed from supplied data):

* :func:`run_reservoir` — a mass-balance reservoir simulation over a number of
  periods, given a restriction fraction;
* :func:`withheld_volume` — how much a restriction subtracts from what the dam
  would otherwise have released;
* :func:`horizon_demand_volume` — the demand a dam serves over a whole
  simulated horizon (the per-period rate times the period count);
* :func:`dam_leverage` — withheld volume relative to a dam's horizon demand;
* :func:`cartel_leverage` — the aggregate leverage of a controlling cartel over
  the whole downstream demand base.

Leverage ratios are dimensionally consistent: ``downstream_demand`` is a
per-period rate on the same time base as ``inflow``, so every ratio divides a
horizon volume by a horizon volume and lands in ``[0, 1]``.

The module imports only the standard library and carries no ``bond_api`` or
infrastructure dependency.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "Dam",
    "DamState",
    "ReservoirTrace",
    "cartel_leverage",
    "dam_leverage",
    "default_dams",
    "horizon_demand_volume",
    "run_reservoir",
    "withheld_volume",
]


def _require_number(value: object, label: str, *, minimum: float = 0.0) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{label} must be a non-boolean number")
    if value < minimum:
        raise ValueError(f"{label} must be >= {minimum}")


def _require_name(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _require_fraction(value: object, label: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{label} must be a non-boolean number")
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"{label} must be in [0, 1]")


@dataclass(frozen=True)
class Dam:
    """A reservoir whose releases feed a downstream demand.

    Attributes:
        name: Unique dam identifier.
        capacity: Maximum water the reservoir can store.
        initial_storage: Stored volume at the start of the simulation.
        inflow: Natural inflow **per period** (rainfall, tributaries).
        downstream_demand: Downstream demand the dam's releases serve, **per
            period** — the same time base as ``inflow`` and ``max_release``.
            Leverage over a multi-period horizon therefore compares withheld
            volume against ``downstream_demand * periods``.
        max_release: Largest release the outlet can pass per period.
        evaporation_rate: Fraction of stored water lost per period.
    """

    name: str
    capacity: float
    initial_storage: float
    inflow: float
    downstream_demand: float
    max_release: float
    evaporation_rate: float = 0.0

    def __post_init__(self) -> None:
        _require_name(self.name, "Dam.name")
        _require_number(self.capacity, "Dam.capacity", minimum=0.0)
        _require_number(self.initial_storage, "Dam.initial_storage")
        _require_number(self.inflow, "Dam.inflow")
        _require_number(self.downstream_demand, "Dam.downstream_demand")
        _require_number(self.max_release, "Dam.max_release", minimum=0.0)
        if self.initial_storage > self.capacity:
            raise ValueError("Dam.initial_storage cannot exceed Dam.capacity")
        _require_fraction(self.evaporation_rate, "Dam.evaporation_rate")


@dataclass(frozen=True)
class DamState:
    """One period of a reservoir simulation."""

    period: int
    storage_after: float
    release: float
    evaporation: float


@dataclass(frozen=True)
class ReservoirTrace:
    """The per-period simulation of one dam under a restriction."""

    dam: Dam
    restriction_frac: float
    states: tuple[DamState, ...]

    def total_release(self) -> float:
        """Total volume released over the whole simulation."""
        return sum(state.release for state in self.states)

    def total_evaporation(self) -> float:
        """Total volume lost to evaporation over the whole simulation."""
        return sum(state.evaporation for state in self.states)

    @property
    def final_storage(self) -> float:
        """Storage held at the final simulated period."""
        return self.states[-1].storage_after


def run_reservoir(dam: Dam, periods: int, restriction_frac: float = 0.0) -> ReservoirTrace:
    """Simulate ``dam`` operation over ``periods`` with a cartel restriction.

    Each period the operator would release up to ``min(storage + inflow,
    max_release)``; the cartel withholds ``restriction_frac`` of that release
    to squeeze the downstream demand. Storage is updated by mass balance and
    clamped to the reservoir ceiling at the end of each period.

    Args:
        dam: The reservoir to simulate.
        periods: Number of simulation periods (must be >= 1).
        restriction_frac: Fraction of released water withheld, in ``[0, 1]``.

    Returns:
        A :class:`ReservoirTrace` of per-period states.
    """
    if not isinstance(periods, int) or isinstance(periods, bool) or periods < 1:
        raise ValueError("periods must be a positive integer")
    _require_fraction(restriction_frac, "restriction_frac")

    storage = dam.initial_storage
    states: list[DamState] = []
    for period in range(periods):
        available = storage + dam.inflow
        evaporation = available * dam.evaporation_rate
        unconstrained_release = min(available, dam.max_release)
        release = unconstrained_release * (1.0 - restriction_frac)
        storage = min(dam.capacity, available - release - evaporation)
        if storage < 0.0:
            storage = 0.0
        states.append(DamState(period=period, storage_after=storage, release=release, evaporation=evaporation))
    return ReservoirTrace(dam=dam, restriction_frac=restriction_frac, states=tuple(states))


def withheld_volume(dam: Dam, periods: int, restriction_frac: float) -> float:
    """Volume the restriction subtracts from a dam's normal total release.

    Compares the reservoir run un-restricted against the same reservoir run at
    ``restriction_frac`` and returns the difference in total released volume.
    """
    baseline = run_reservoir(dam, periods, 0.0).total_release()
    restricted = run_reservoir(dam, periods, restriction_frac).total_release()
    return max(0.0, baseline - restricted)


def dam_leverage(dam: Dam, periods: int, restriction_frac: float) -> float:
    """Fraction of a dam's horizon demand the restriction can cut.

    Both sides of the ratio are horizon quantities: the withheld volume
    accumulated over ``periods`` is compared against the demand accumulated
    over the same ``periods`` (``downstream_demand * periods``), so the result
    is a dimensionless share in ``[0, 1]`` rather than a period-count-inflated
    number. Zero when the dam has no downstream demand to squeeze.
    """
    horizon_demand = horizon_demand_volume(dam, periods)
    if horizon_demand <= 0.0:
        return 0.0
    return withheld_volume(dam, periods, restriction_frac) / horizon_demand


def horizon_demand_volume(dam: Dam, periods: int) -> float:
    """Total downstream demand a dam serves over ``periods`` periods.

    ``Dam.downstream_demand`` is a per-period rate, so the horizon demand is
    the rate times the number of simulated periods. This is the denominator
    every leverage ratio in this module divides by.
    """
    if not isinstance(periods, int) or isinstance(periods, bool) or periods < 1:
        raise ValueError("periods must be a positive integer")
    return dam.downstream_demand * periods


def cartel_leverage(
    dams: list[Dam],
    controlled: set[str],
    restriction_frac: float = 0.5,
    periods: int = 12,
) -> dict[str, object]:
    """Aggregate leverage a cartel exerts by restricting its controlled dams.

    For every dam the simulation runs unrestricted if the cartel does not
    control it, and at ``restriction_frac`` if it does. The aggregate leverage
    is the total withheld volume across controlled dams divided by the total
    downstream demand **over the same horizon** — that is, the sum of every
    dam's per-period ``downstream_demand`` times ``periods``. Both numerator
    and denominator are horizon volumes, so the aggregate is a share in
    ``[0, 1]``.

    Returns:
        A deterministic report dict with per-dam breakdown, an ``aggregate``
        leverage share, the ``periods`` simulated, and ``horizon_demand`` (the
        denominator, so callers can re-derive the ratio).
    """
    _require_fraction(restriction_frac, "restriction_frac")
    if not isinstance(periods, int) or isinstance(periods, bool) or periods < 1:
        raise ValueError("periods must be a positive integer")

    per_dam: dict[str, dict[str, object]] = {}
    total_withheld = 0.0
    horizon_demand = 0.0
    for dam in dams:
        is_controlled = dam.name in controlled
        trace = run_reservoir(dam, periods, restriction_frac if is_controlled else 0.0)
        delivered = trace.total_release()
        withheld = withheld_volume(dam, periods, restriction_frac) if is_controlled else 0.0
        dam_horizon_demand = horizon_demand_volume(dam, periods)
        per_dam[dam.name] = {
            "controlled": is_controlled,
            "delivered_volume": delivered,
            "withheld_volume": withheld,
            "horizon_demand": dam_horizon_demand,
            "leverage": withheld / dam_horizon_demand if dam_horizon_demand > 0.0 else 0.0,
        }
        horizon_demand += dam_horizon_demand
        if is_controlled:
            total_withheld += withheld
    aggregate = total_withheld / horizon_demand if horizon_demand > 0.0 else 0.0
    return {
        "per_dam": per_dam,
        "aggregate": aggregate,
        "periods": periods,
        "horizon_demand": horizon_demand,
        "withheld_volume": total_withheld,
    }


def default_dams() -> list[Dam]:
    """The canonical QUANTUM dam fleet.

    A deterministic, fixed set of three reservoirs emblematic of the film's
    border-water setting, with an evaporation-aware highland reservoir.
    """
    return [
        Dam(
            name="highland_reservoir",
            capacity=500.0,
            initial_storage=320.0,
            inflow=80.0,
            downstream_demand=120.0,
            max_release=90.0,
            evaporation_rate=0.05,
        ),
        Dam(
            name="border_barrage",
            capacity=400.0,
            initial_storage=210.0,
            inflow=60.0,
            downstream_demand=95.0,
            max_release=70.0,
            evaporation_rate=0.03,
        ),
        Dam(
            name="desert_holding",
            capacity=300.0,
            initial_storage=150.0,
            inflow=50.0,
            downstream_demand=65.0,
            max_release=55.0,
            evaporation_rate=0.09,
        ),
    ]
