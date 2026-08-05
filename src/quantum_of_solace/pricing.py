"""Water scarcity pricing and monopoly-economics model (QUANTUM).

A cartel's leverage over water is only worth something because water is priced
at its scarcity. This module models the market side of the QUANTUM threat with
classical microeconomic tools on a linear inverse demand curve
``p(q) = a - b·q``:

* :func:`market_clearing_price` — the scarcity price at which a fixed supply
  is fully absorbed (0 when supply exceeds the choke quantity);
* :func:`point_elasticity` — the point price elasticity of demand, which is
  characteristically low (inelastic) for water;
* :func:`scarcity_impact` — how a cartel-cut supply raises the price, and the
  scarcity rent the cartel collects on the reduced volume;
* :func:`monopoly_price` / :func:`monopoly_quantity` / :func:`deadweight_loss`
  — the standard linear-demand monopoly solution (MR = MC) and the social cost
  of concentrated control.

Everything is deterministic and computed from supplied parameters; the module
imports only the standard library.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "DEFAULT_DEMAND_A",
    "DEFAULT_DEMAND_B",
    "DEFAULT_MARGINAL_COST",
    "MarketOutcome",
    "consumer_surplus",
    "deadweight_loss",
    "default_demand",
    "inverse_demand",
    "market_clearing_price",
    "market_outcome",
    "monopoly_price",
    "monopoly_quantity",
    "point_elasticity",
    "revenue",
    "scarcity_impact",
]

#: Canonical demand-curve intercept (choke price) for the QUANTUM assessment.
DEFAULT_DEMAND_A = 100.0
#: Canonical demand-curve slope (price drop per unit of quantity).
DEFAULT_DEMAND_B = 0.25
#: Canonical constant marginal cost of delivering a water unit.
DEFAULT_MARGINAL_COST = 10.0


def _require_demand_params(a: object, b: object) -> tuple[float, float]:
    if not isinstance(a, (int, float)) or isinstance(a, bool) or a <= 0:
        raise ValueError("demand intercept a must be a positive number")
    if not isinstance(b, (int, float)) or isinstance(b, bool) or b <= 0:
        raise ValueError("demand slope b must be a positive number")
    return float(a), float(b)


def _require_non_negative(value: object, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{label} must be a non-negative number")
    return float(value)


def default_demand() -> tuple[float, float, float]:
    """The canonical (intercept, slope, marginal cost) demand parameters."""
    return DEFAULT_DEMAND_A, DEFAULT_DEMAND_B, DEFAULT_MARGINAL_COST


def inverse_demand(quantity: float, a: float, b: float) -> float:
    """Price at which exactly ``quantity`` units are demanded, clamped at 0."""
    intercept, slope = _require_demand_params(a, b)
    _require_non_negative(quantity, "quantity")
    return max(0.0, intercept - slope * quantity)


def market_clearing_price(supply: float, a: float, b: float) -> float:
    """The scarcity price that clears a fixed supply of water.

    Zero when the supply exceeds the quantity demanded even at price 0.
    """
    return inverse_demand(supply, a, b)


def point_elasticity(price: float, quantity: float, b: float) -> float:
    """Point price elasticity of demand ``b·p/q`` at (price, quantity).

    Raises ``ValueError`` for a zero quantity (elasticity is undefined there).
    """
    if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
        raise ValueError("price must be a non-negative number")
    if not isinstance(quantity, (int, float)) or isinstance(quantity, bool) or quantity <= 0:
        raise ValueError("quantity must be a positive number")
    if not isinstance(b, (int, float)) or isinstance(b, bool) or b <= 0:
        raise ValueError("demand slope b must be a positive number")
    return float(b) * float(price) / float(quantity)


def revenue(price: float, quantity: float) -> float:
    """Total revenue ``p·q`` at the given price and quantity."""
    p = _require_non_negative(price, "price")
    q = _require_non_negative(quantity, "quantity")
    return p * q


def consumer_surplus(price: float, quantity: float, a: float, b: float) -> float:
    """Consumer surplus under a linear demand curve: ``(a - p)·q / 2``.

    The slope is validated but does not enter the triangle's area, which is
    fixed by the intercept, the price and the traded quantity.
    """
    intercept, _slope = _require_demand_params(a, b)
    p = _require_non_negative(price, "price")
    q = _require_non_negative(quantity, "quantity")
    if p > intercept:
        raise ValueError("price cannot exceed the demand intercept")
    return (intercept - p) * q / 2.0


def monopoly_quantity(a: float, b: float, marginal_cost: float) -> float:
    """Profit-maximising quantity for a monopolist: ``(a - mc) / (2b)``."""
    intercept, slope = _require_demand_params(a, b)
    mc = _require_marginal_cost(marginal_cost, intercept)
    return (intercept - mc) / (2.0 * slope)


def monopoly_price(a: float, b: float, marginal_cost: float) -> float:
    """Profit-maximising price for a monopolist: ``(a + mc) / 2``.

    The slope ``b`` does not enter the price (it cancels between the marginal
    revenue and marginal cost conditions) but is still validated, so an
    ill-formed demand curve is rejected here as it is everywhere else.
    """
    intercept, _slope = _require_demand_params(a, b)
    mc = _require_marginal_cost(marginal_cost, intercept)
    return (intercept + mc) / 2.0


def deadweight_loss(a: float, b: float, marginal_cost: float) -> float:
    """Deadweight loss from monopoly pricing on a linear demand curve.

    With a flat marginal cost the competitive quantity is ``(a - mc)/b`` and
    the monopoly quantity half of it, so the welfare triangle is
    ``b·(q_comp - q_mono)² / 2``.
    """
    intercept, slope = _require_demand_params(a, b)
    mc = _require_marginal_cost(marginal_cost, intercept)
    competitive_q = (intercept - mc) / slope
    monopoly_q = (intercept - mc) / (2.0 * slope)
    return float(slope * (competitive_q - monopoly_q) ** 2 / 2.0)


def _require_marginal_cost(marginal_cost: object, intercept: float) -> float:
    mc = _require_non_negative(marginal_cost, "marginal_cost")
    if mc > intercept:
        raise ValueError("marginal_cost cannot exceed the demand intercept a")
    return mc


def scarcity_impact(
    supply_baseline: float,
    supply_restricted: float,
    a: float,
    b: float,
) -> dict[str, float]:
    """Price and rent consequences of a cartel cutting the water supply.

    Args:
        supply_baseline: Per-period volume the network would otherwise deliver.
        supply_restricted: The reduced volume after the cartel withholds water.
        a, b: Linear demand curve parameters.

    Returns:
        A deterministic dict: baseline/restricted clearing prices, the price
        rise fraction, the cartel's scarcity rent on the reduced volume, and
        the point elasticity at the baseline price.
    """
    baseline = _require_non_negative(supply_baseline, "supply_baseline")
    restricted = _require_non_negative(supply_restricted, "supply_restricted")
    if restricted > baseline:
        raise ValueError("supply_restricted cannot exceed supply_baseline")
    base_price = market_clearing_price(baseline, a, b)
    restricted_price = market_clearing_price(restricted, a, b)
    if base_price > 0.0:
        price_rise_frac = (restricted_price - base_price) / base_price
        elasticity = point_elasticity(base_price, baseline, b)
    else:
        price_rise_frac = 0.0
        elasticity = 0.0
    scarcity_rent = (restricted_price - base_price) * restricted
    return {
        "baseline_price": base_price,
        "restricted_price": restricted_price,
        "price_rise_frac": price_rise_frac,
        "scarcity_rent": scarcity_rent,
        "elasticity": elasticity,
    }


@dataclass(frozen=True)
class MarketOutcome:
    """The full monopoly-vs-competitive comparison for one demand market."""

    a: float
    b: float
    marginal_cost: float
    competitive_price: float
    competitive_quantity: float
    monopoly_price: float
    monopoly_quantity: float
    monopoly_revenue: float
    consumer_surplus_competitive: float
    consumer_surplus_monopoly: float
    deadweight_loss: float


def market_outcome(a: float, b: float, marginal_cost: float) -> MarketOutcome:
    """Compute the complete competitive vs monopoly market comparison."""
    intercept, slope = _require_demand_params(a, b)
    mc = _require_marginal_cost(marginal_cost, intercept)
    competitive_price = mc
    competitive_quantity = (intercept - mc) / slope
    mono_price = monopoly_price(intercept, slope, mc)
    mono_quantity = monopoly_quantity(intercept, slope, mc)
    return MarketOutcome(
        a=intercept,
        b=slope,
        marginal_cost=mc,
        competitive_price=competitive_price,
        competitive_quantity=competitive_quantity,
        monopoly_price=mono_price,
        monopoly_quantity=mono_quantity,
        monopoly_revenue=mono_price * mono_quantity,
        consumer_surplus_competitive=consumer_surplus(competitive_price, competitive_quantity, intercept, slope),
        consumer_surplus_monopoly=consumer_surplus(mono_price, mono_quantity, intercept, slope),
        deadweight_loss=deadweight_loss(intercept, slope, mc),
    )
