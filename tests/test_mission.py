"""Tests for the QUANTUM mission adapter against the frozen bond_api protocol."""

import pytest
from bond_api.protocol import MissionProvider as Protocol, ReconRequest, run_mission
from bond_api.registry import GadgetRegistry

from quantum_of_solace.mission import (
    GADGET_REGISTRY,
    QUANTUM_CODENAME,
    MissionProvider,
)


@pytest.fixture
def provider():
    return MissionProvider()


class TestMissionProvider:
    def test_satisfies_protocol(self, provider):
        assert isinstance(provider, Protocol)
        assert provider.film == "quantum_of_solace"

    def test_brief(self, provider):
        brief = provider.brief()
        assert brief.film == "quantum_of_solace"
        assert brief.codename == QUANTUM_CODENAME
        assert len(brief.objectives) == 6
        assert len(brief.assets) == 6
        assert any(c.kind == "determinism" for c in brief.constraints)

    def test_recon(self, provider):
        report = provider.recon(ReconRequest(goal="map desert water supply"))
        labels = {finding.label for finding in report.findings}
        assert {
            "goal",
            "network_supply",
            "settlement_delivery",
            "cartel_leverage",
            "aggregate_hhi",
            "scarcity_price",
            "critical_route",
            "top_power",
        } <= labels

    def test_plan(self, provider):
        plan = provider.plan(provider.brief())
        assert len(plan.steps) == 8
        assert plan.steps[0].name == "hydrology"
        assert {step.name for step in plan.steps} >= {"pricing", "resilience", "shapley"}

    def test_execute(self, provider):
        outcome = provider.execute(provider.plan(provider.brief()))
        assert outcome.success is True
        assert outcome.results["film"] == "quantum_of_solace"
        assert outcome.provenance.seed == 0
        assert outcome.provenance.input_hash
        assert outcome.results["assessment"]["hydrology"]["total_supply"] == 80.0
        assert "pricing" in outcome.results["assessment"]
        assert "resilience" in outcome.results["assessment"]
        assert "shapley" in outcome.results["assessment"]

    def test_debrief(self, provider):
        outcome = provider.execute(provider.plan(provider.brief()))
        debrief = provider.debrief(outcome)
        assert len(debrief.lessons) == 6
        assert debrief.outcome is outcome

    def test_run_mission_flow(self, provider):
        debrief = run_mission(provider, ReconRequest(goal="assess the QUANTUM cartel"))
        assert debrief.outcome.success is True
        assert debrief.outcome.provenance.input_hash


class TestGadgetRegistry:
    def test_registration(self):
        assert isinstance(GADGET_REGISTRY, GadgetRegistry)
        assert GADGET_REGISTRY.contains("quantum_of_solace", "hydrology")
        assert GADGET_REGISTRY.contains("quantum_of_solace", "full_assessment")
        for gadget in ("pricing", "resilience", "shapley"):
            assert GADGET_REGISTRY.contains("quantum_of_solace", gadget)
        assert GADGET_REGISTRY.lookup("quantum_of_solace", "cartel_graph") is not None

    def test_registry_not_frozen_after_import(self):
        # a fresh registry can still be mutated; the module-level one is stable
        assert GADGET_REGISTRY.films() == ("quantum_of_solace",)
