#!/usr/bin/env python3
"""Generate the canonical QUANTUM analysis artifact set.

Thin orchestrator: computes the full assessment from the real domain models
and writes ``output/data/quantum_assessment.json`` plus every canonical figure
under ``output/figures/``. All deterministic — regenerating reproduces the
same bytes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))  # noqa: E402

from quantum_of_solace.analysis import run_quantum_assessment  # noqa: E402
from quantum_of_solace.figures import render_all_figures  # noqa: E402

OUT_DATA = PROJECT_ROOT / "output" / "data"
OUT_FIGURES = PROJECT_ROOT / "output" / "figures"


def main() -> int:
    assessment = run_quantum_assessment()
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    assessment_path = OUT_DATA / "quantum_assessment.json"
    assessment_path.write_text(json.dumps(assessment, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    figures = render_all_figures(OUT_FIGURES)
    print(f"Assessment written: {assessment_path}")
    print("Figures rendered:")
    for name, path in figures.items():
        print(f"  {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
