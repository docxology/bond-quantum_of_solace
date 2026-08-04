#!/usr/bin/env python3
"""Drive the QUANTUM mission through a chosen ``bond_api`` lifecycle phase.

Thin orchestrator over :class:`quantum_of_solace.mission.MissionProvider`.
Phases: ``brief``, ``recon``, ``plan``, ``execute``, ``debrief``, or ``full``
(run the whole five-stage flow). Exits 0 on success.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))  # noqa: E402

from bond_api.protocol import ReconRequest, run_mission  # noqa: E402
from quantum_of_solace.mission import MissionProvider  # noqa: E402

_DEFAULT_GOAL = "quantify the cartel's leverage over desert water rights"


def _phase_brief(provider: MissionProvider, goal: str) -> int:
    brief = provider.brief()
    print(f"Film: {brief.film} | Codename: {brief.codename}")
    print("Objectives:")
    for objective in brief.objectives:
        print(f"  - {objective}")
    print(f"Assets: {', '.join(asset.name for asset in brief.assets)}")
    print(f"Constraints: {', '.join(constraint.kind for constraint in brief.constraints)}")
    return 0


def _phase_recon(provider: MissionProvider, goal: str) -> int:
    report = provider.recon(ReconRequest(goal=goal))
    for finding in report.findings:
        print(f"{finding.label}: {finding.detail}")
    return 0


def _phase_plan(provider: MissionProvider, goal: str) -> int:
    plan = provider.plan(provider.brief())
    for index, step in enumerate(plan.steps, start=1):
        print(f"{index}. {step.name} -> {step.action}")
    return 0


def _phase_execute(provider: MissionProvider, goal: str) -> int:
    outcome = provider.execute(provider.plan(provider.brief()))
    print(f"Success: {outcome.success}")
    print(f"Steps completed: {outcome.results['steps_completed']}")
    print(f"Input hash: {outcome.provenance.input_hash}")
    print(f"Seed: {outcome.provenance.seed}")
    return 0 if outcome.success else 1


def _phase_debrief(provider: MissionProvider, goal: str) -> int:
    debrief = provider.debrief(provider.execute(provider.plan(provider.brief())))
    print("Lessons learned:")
    for lesson in debrief.lessons:
        print(f"  - {lesson}")
    return 0


def _phase_full(provider: MissionProvider, goal: str) -> int:
    debrief = run_mission(provider, ReconRequest(goal=goal))
    outcome = debrief.outcome
    print(f"Film {outcome.results['film']} / {outcome.results['codename']}")
    print(f"Success: {outcome.success} | hash {outcome.provenance.input_hash[:12]}…")
    for lesson in debrief.lessons:
        print(f"  lesson: {lesson}")
    return 0 if outcome.success else 1


_PHASES: dict[str, Callable[[MissionProvider, str], int]] = {
    "brief": _phase_brief,
    "recon": _phase_recon,
    "plan": _phase_plan,
    "execute": _phase_execute,
    "debrief": _phase_debrief,
    "full": _phase_full,
}


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    phase = args[0] if args else "full"
    if phase not in _PHASES:
        print(f"unknown phase {phase!r}; expected one of {', '.join(sorted(_PHASES))}", file=sys.stderr)
        return 2
    goal = args[1] if len(args) > 1 else _DEFAULT_GOAL
    return _PHASES[phase](MissionProvider(), goal)


if __name__ == "__main__":
    raise SystemExit(main())
