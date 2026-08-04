#!/usr/bin/env python3
"""Hydrate the QUANTUM manuscript ``{{TOKEN}}`` map.

Thin orchestrator: writes ``output/data/manuscript_variables.json`` by
computing ``generate_variables()``. Result-derived tokens always come from the
real assessment; config tokens come from ``manuscript/config.yaml``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))  # noqa: E402

from quantum_of_solace.manuscript_variables import generate_variables  # noqa: E402

OUT_DATA = PROJECT_ROOT / "output" / "data"


def main() -> int:
    variables = generate_variables()
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DATA / "manuscript_variables.json"
    out_path.write_text(json.dumps(variables, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"Manuscript variables written: {out_path} ({len(variables)} tokens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
