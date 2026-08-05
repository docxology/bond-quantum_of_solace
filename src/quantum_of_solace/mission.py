"""QUANTUM mission adapter: the film's ``bond_api`` ``MissionProvider``.

This module is the thin adapter between the pure domain core
(:mod:`quantum_of_solace.hydrology`, :mod:`quantum_of_solace.water_cartel`,
:mod:`quantum_of_solace.cartel_graph`, :mod:`quantum_of_solace.pricing`,
:mod:`quantum_of_solace.resilience`, :mod:`quantum_of_solace.shapley` and
:mod:`quantum_of_solace.analysis`) and the frozen BOND-API mission protocol. It
is discovered by the orchestrator under the ``quantum_of_solace`` slug and
exposes a ``MissionProvider`` at module top level, implementing the five-stage
lifecycle:

* ``brief`` — declares the QUANTUM mission: objectives, assets, constraints;
* ``recon`` — surveys a goal and returns measured findings from the domain core;
* ``plan`` — the deterministic steps that produce the assessment;
* ``execute`` — runs the full assessment and returns its provenance;
* ``debrief`` — summarises the outcome and records lessons learned.

The module also registers its domain gadgets with the :class:`GadgetRegistry`
so coordinator tooling can look them up by name.
"""

from __future__ import annotations

import hashlib
import json
from typing import cast

from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    ReconRequest,
    Step,
)
from bond_api.registry import GadgetRegistry

from quantum_of_solace.analysis import (
    INTERDICTION_STEPS,
    RESTRICTION_FRAC,
    assess_cartel_graph,
    assess_hydrology,
    assess_pricing,
    assess_resilience,
    assess_shapley,
    assess_water_cartel,
    run_quantum_assessment,
)

__all__ = ["GADGET_REGISTRY", "MISSION_SEED", "QUANTUM_CODENAME", "MissionProvider"]

#: The film's mission codename.
QUANTUM_CODENAME = "QUANTUM"
#: Package version reported in provenance.
_PACKAGE_VERSION = "0.1.0"
#: Deterministic RNG seed (0 = no randomness; this film uses none).
MISSION_SEED = 0

#: The assessment subsystem gadgets the film registers for its slug.
GADGET_REGISTRY = GadgetRegistry()
GADGET_REGISTRY.register(
    "quantum_of_solace",
    {
        "hydrology": assess_hydrology,
        "water_cartel": assess_water_cartel,
        "cartel_graph": assess_cartel_graph,
        "pricing": assess_pricing,
        "resilience": assess_resilience,
        "shapley": assess_shapley,
        "full_assessment": run_quantum_assessment,
    },
)


def _canonical_hash(payload: object) -> str:
    """Stable sha256 fingerprint of a JSON-serializable payload."""
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class MissionProvider:
    """Deterministic ``bond_api.MissionProvider`` for the QUANTUM film.

    The provider adapts the pure water/cartel domain models to the frozen
    protocol. It performs no I/O and makes no random draws; every number in a
    report comes from running the actual domain algorithms on fixed data.
    """

    film = "quantum_of_solace"

    def brief(self) -> MissionBrief:
        """Declare the QUANTUM mission, its objectives, assets and constraints."""
        return MissionBrief(
            film=self.film,
            codename=QUANTUM_CODENAME,
            objectives=(
                "assess desert water-network resilience under evaporation",
                "quantify cartel leverage over water-rights through dam control",
                "measure multi-resource commodity-control concentration",
                "price water scarcity and the cartel's scarcity rent",
                "rank aqueduct interdiction criticality and network resilience",
                "resolve cooperative power over the commodity portfolio",
            ),
            assets=(
                Asset(kind="model", name="hydrology", payload={"default": "desert_network"}),
                Asset(kind="model", name="water_cartel", payload={"default": "dam_fleet"}),
                Asset(kind="model", name="cartel_graph", payload={"default": "commodity_control"}),
                Asset(kind="model", name="pricing", payload={"default": "linear_demand"}),
                Asset(kind="model", name="resilience", payload={"default": "interdiction"}),
                Asset(kind="model", name="shapley", payload={"default": "cooperative_power"}),
            ),
            constraints=(
                Constraint(kind="determinism", detail="no random draws, no external calls, fixed problem data"),
                Constraint(kind="provenance", detail="outcome carries a canonical input hash and fixed seed"),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the request and return measured findings from the domain core.

        Each finding's detail carries a number computed by the real domain
        algorithms on the canonical default instances.
        """
        hydrology = assess_hydrology()
        water = assess_water_cartel()
        cartel = assess_cartel_graph()
        pricing = assess_pricing()
        resilience = assess_resilience()
        shapley = assess_shapley()
        delivery = cast("dict[str, float]", hydrology["settlement_delivery"])
        total_supply = cast("float", hydrology["total_supply"])
        aggregate_leverage = cast("float", water["aggregate_leverage"])
        aggregate_hhi = cast("float", cartel["aggregate_hhi"])
        baseline_price = cast("float", pricing["baseline_price"])
        restricted_price = cast("float", pricing["restricted_price"])
        return ReconReport(
            findings=(
                Finding(label="goal", detail=request.goal),
                Finding(
                    label="network_supply",
                    detail=f"total aquifer yield {total_supply:.1f} units/period",
                ),
                Finding(
                    label="settlement_delivery",
                    detail=f"border_town {delivery['border_town']:.1f}, "
                    f"valley_compact {delivery['valley_compact']:.1f} max units/period",
                ),
                Finding(
                    label="cartel_leverage",
                    detail=f"aggregate {aggregate_leverage:.3f} of horizon demand withheld",
                ),
                Finding(label="aggregate_hhi", detail=f"{aggregate_hhi:.1f} points"),
                Finding(
                    label="scarcity_price",
                    detail=f"water price {baseline_price:.1f} -> {restricted_price:.1f} when the cartel cuts supply",
                ),
                Finding(
                    label="critical_route",
                    detail=f"most critical aqueduct {resilience['critical_route']} "
                    f"(loss {cast('float', resilience['critical_loss']):.1f} units)",
                ),
                Finding(
                    label="top_power",
                    detail=f"most powerful actor {shapley['top_actor']} by Shapley value",
                ),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the deterministic steps that produce the QUANTUM assessment."""
        return MissionPlan(
            steps=(
                Step(name="hydrology", action="assess_hydrology", params={"network": "default"}),
                Step(name="water_cartel", action="assess_water_cartel", params={"restriction": RESTRICTION_FRAC}),
                Step(name="cartel_graph", action="assess_cartel_graph", params={"model": "default"}),
                Step(name="pricing", action="assess_pricing", params={"demand": "linear"}),
                Step(name="resilience", action="assess_resilience", params={"steps": INTERDICTION_STEPS}),
                Step(name="shapley", action="assess_shapley", params={"weights": "canonical"}),
                Step(name="assemble", action="run_quantum_assessment", params={"objectives": len(brief.objectives)}),
                Step(name="provenance", action="hash_inputs", params={"seed": MISSION_SEED}),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the assessment and return a deterministic outcome with provenance."""
        assessment = run_quantum_assessment()
        results = {
            "film": self.film,
            "codename": QUANTUM_CODENAME,
            "steps_completed": len(plan.steps),
            "steps": tuple(step.name for step in plan.steps),
            "assessment": assessment,
        }
        return MissionOutcome(
            success=True,
            results=results,
            provenance=Provenance(
                package_version=_PACKAGE_VERSION,
                seed=MISSION_SEED,
                input_hash=_canonical_hash(assessment),
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Summarise the mission and record the QUANTUM standing lessons."""
        lessons = (
            "evaporation hollows out delivered water — routing must minimise effective loss",
            "a cartel holding a minority of dams still withholds a sizeable share of horizon demand",
            "multi-resource concentration (HHI) exposes leverage that single-commodity view misses",
            "water is sharply inelastic, so even a modest supply cut raises price far more than volume",
            "no desert aqueduct is redundant — every single cut costs delivery, making the network fragile",
            "cooperative power is concentrated: the leading cartel claims the largest Shapley share",
        )
        return Debrief(outcome=outcome, lessons=lessons)
