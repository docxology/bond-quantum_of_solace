"""Commodity-cartel graph: multi-resource control and market concentration (QUANTUM).

The film's cartel controls more than water — it spreads control across several
scarce commodities to make its grip systemic. This module models a bipartite
control graph from actors (cartels, states, syndicates) to commodities
(water, lithium, copper, grain), where each actor holds a share of each
commodity's total controlled stock.

Algorithms (all deterministic, from the supplied share data):

* **HHI concentration** — the Herfindahl–Hirschman Index per commodity, and an
  aggregate across the commodity portfolio;
* **concentration ratio** — the combined share of the top-k controlling actors
  for a commodity;
* **dominance** — which actor holds the largest share of each commodity, and
  how many commodities each actor dominates;
* **diversification / multi-resource grip** — how evenly an actor spreads its
  control across the commodity portfolio.

The module imports only the standard library and carries no ``bond_api`` or
infrastructure dependency.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "HHI_HIGHLY_CONCENTRATED",
    "HHI_MODERATELY_CONCENTRATED",
    "CommodityCartelGraph",
    "ConcentrationReport",
    "concentration_band",
    "default_cartel",
]

#: Lower HHI bound (points) of the "moderately concentrated" band used by the
#: U.S. DOJ/FTC Horizontal Merger Guidelines (2010, §5.3).
HHI_MODERATELY_CONCENTRATED = 1500.0
#: HHI (points) above which the same guidelines call a market "highly
#: concentrated" — the threshold the QUANTUM commodity portfolio clears.
HHI_HIGHLY_CONCENTRATED = 2500.0


def concentration_band(hhi_points: float) -> str:
    """Classify an HHI value into the Merger-Guidelines concentration band.

    Returns ``"unconcentrated"`` below
    :data:`HHI_MODERATELY_CONCENTRATED`, ``"moderately concentrated"`` up to
    and including :data:`HHI_HIGHLY_CONCENTRATED`, and ``"highly
    concentrated"`` above it.
    """
    if not isinstance(hhi_points, (int, float)) or isinstance(hhi_points, bool) or hhi_points < 0:
        raise ValueError("hhi_points must be a non-negative number")
    if hhi_points < HHI_MODERATELY_CONCENTRATED:
        return "unconcentrated"
    if hhi_points <= HHI_HIGHLY_CONCENTRATED:
        return "moderately concentrated"
    return "highly concentrated"


def _require_share(value: object, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{label} must be a non-boolean number")
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"{label} must be a share in [0, 1]")
    return float(value)


def _hhi_points(shares: list[float]) -> float:
    """Herfindahl–Hirschman Index in percentage points (range 0..10000)."""
    return sum((share * 100.0) ** 2 for share in shares)


@dataclass(frozen=True)
class ConcentrationReport:
    """Concentration metrics for one commodity across its controlling actors."""

    commodity: str
    hhi: float
    concentration_ratio: float
    dominant_actor: str
    dominant_share: float
    num_actors: int


class CommodityCartelGraph:
    """A multi-resource control graph from actors to commodities.

    Args:
        shares: Mapping ``actor -> {commodity: share}``. A share is the fraction
            of a commodity's total controlled stock held by that actor; every
            commodity's shares need not sum to 1.0 (the remainder may be held
            by unmodelled actors).
    """

    def __init__(self, shares: dict[str, dict[str, float]]) -> None:
        if not shares:
            raise ValueError("a cartel graph needs at least one actor")
        normalized: dict[str, dict[str, float]] = {}
        for actor, portfolio in shares.items():
            if not isinstance(actor, str) or not actor.strip():
                raise ValueError("actor names must be non-empty strings")
            if not portfolio:
                raise ValueError(f"actor {actor!r} must control at least one commodity")
            normalized[actor] = {
                commodity: _require_share(share, f"share of {actor!r} in {commodity!r}")
                for commodity, share in portfolio.items()
            }
        self._shares = normalized
        self._commodities: tuple[str, ...] = tuple(
            sorted({commodity for portfolio in normalized.values() for commodity in portfolio})
        )

    # -- queries -----------------------------------------------------------

    @property
    def actors(self) -> tuple[str, ...]:
        """Actor names, in declaration order."""
        return tuple(self._shares)

    @property
    def commodities(self) -> tuple[str, ...]:
        """Commodity names, sorted."""
        return self._commodities

    def portfolio(self, actor: str) -> dict[str, float]:
        """The actor's ``{commodity: share}`` control map."""
        try:
            return self._shares[actor]
        except KeyError:
            raise KeyError(f"no actor {actor!r} in the cartel graph") from None

    def controls(self, actor: str, commodity: str) -> bool:
        """True when ``actor`` holds any share of ``commodity``."""
        return commodity in self._shares.get(actor, {})

    def share_of(self, actor: str, commodity: str) -> float:
        """The share ``actor`` holds of ``commodity`` (0.0 if none)."""
        return self._shares.get(actor, {}).get(commodity, 0.0)

    def holders(self, commodity: str) -> tuple[str, ...]:
        """Actors that hold a share of ``commodity``, in declaration order."""
        return tuple(actor for actor in self._shares if commodity in self._shares[actor])

    # -- concentration -----------------------------------------------------

    def hhi(self, commodity: str | None = None) -> float:
        """Herfindahl–Hirschman Index in percentage points.

        With ``commodity`` given, the HHI of that commodity alone; otherwise
        the arithmetic mean HHI across the whole commodity portfolio.
        """
        if commodity is not None:
            shares = [self.share_of(actor, commodity) for actor in self._shares if self.controls(actor, commodity)]
            return _hhi_points(shares)
        # ``_commodities`` is never empty: the constructor rejects any actor
        # with an empty portfolio, so at least one commodity always exists.
        return sum(self.hhi(commodity) for commodity in self._commodities) / len(self._commodities)

    def concentration_ratio(self, commodity: str, top: int = 3) -> float:
        """Combined share of the top-``top`` controlling actors of a commodity."""
        if not isinstance(top, int) or isinstance(top, bool) or top < 1:
            raise ValueError("top must be a positive integer")
        shares = sorted(
            (self.share_of(actor, commodity) for actor in self._shares if self.controls(actor, commodity)),
            reverse=True,
        )
        return sum(shares[:top])

    def report(self, commodity: str) -> ConcentrationReport:
        """Full concentration report for one commodity."""
        holders = [actor for actor in self._shares if self.controls(actor, commodity)]
        if not holders:
            raise ValueError(f"no actor controls commodity {commodity!r}")
        shares = [self.share_of(actor, commodity) for actor in holders]
        dominant_index = max(range(len(holders)), key=lambda i: shares[i])
        return ConcentrationReport(
            commodity=commodity,
            hhi=_hhi_points(shares),
            concentration_ratio=self.concentration_ratio(commodity, top=3) if len(holders) > 1 else shares[0],
            dominant_actor=holders[dominant_index],
            dominant_share=shares[dominant_index],
            num_actors=len(holders),
        )

    # -- actor-level metrics -----------------------------------------------

    def mean_control(self, actor: str) -> float:
        """The actor's average share across the commodities it controls."""
        portfolio = self._shares.get(actor)
        if not portfolio:
            return 0.0
        return sum(portfolio.values()) / len(portfolio)

    def diversification(self, actor: str) -> float:
        """How evenly an actor spreads its grip: 1 - HHI of its own portfolio.

        Ranges from 0.0 (all control in one commodity) toward 1.0 as control
        is spread across many commodities.
        """
        portfolio = self._shares.get(actor)
        if not portfolio or len(portfolio) == 1:
            return 0.0
        return 1.0 - _hhi_points(list(portfolio.values())) / 10000.0

    def dominance_count(self, actor: str) -> int:
        """How many commodities the actor controls the largest share of."""
        return sum(1 for commodity in self._commodities if self.report(commodity).dominant_actor == actor)

    def dominance_map(self) -> dict[str, str]:
        """Commodity → the actor holding its dominant share."""
        return {commodity: self.report(commodity).dominant_actor for commodity in self._commodities}


def default_cartel() -> CommodityCartelGraph:
    """The canonical QUANTUM multi-resource cartel.

    A deterministic, fixed control instance: the shadow organisation
    (``quantum``) dominates water and lithium while a rival syndicate and a
    state utility split copper and grain — modelling systemic, multi-resource
    leverage.
    """
    return CommodityCartelGraph(
        {
            "quantum": {"water": 0.45, "lithium": 0.55, "copper": 0.20, "grain": 0.10},
            "rival_syndicate": {"water": 0.25, "lithium": 0.30, "copper": 0.50, "grain": 0.40},
            "state_utility": {"water": 0.30, "lithium": 0.15, "copper": 0.30, "grain": 0.50},
        }
    )
