"""Manuscript token hydration for the QUANTUM manuscript.

:func:`generate_variables` computes the ``{{TOKEN}}`` map that manuscript
sections reference. Configuration values (identity, keywords, date) come from
``manuscript/config.yaml``; result-derived tokens come from the real
:func:`quantum_of_solace.analysis.run_quantum_assessment` — never hand-authored
prose numbers. The default ``now`` is taken from the config date so hydration
is deterministic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

from quantum_of_solace.analysis import run_quantum_assessment
from quantum_of_solace.mission import QUANTUM_CODENAME

__all__ = ["load_mission_config", "generate_variables"]

#: Default location of the manuscript config, relative to the package root.
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "manuscript" / "config.yaml"


def load_mission_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load ``manuscript/config.yaml`` as a plain mapping."""
    path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
    with open(path, encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict):
        raise ValueError(f"manuscript config at {path} must be a YAML mapping")
    return raw


def _fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def generate_variables(
    config_path: Path | None = None,
    assessment: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, str]:
    """Compute the full ``{{TOKEN}}`` → value map for the QUANTUM manuscript.

    Args:
        config_path: Override for the manuscript config location.
        assessment: Override for the computed assessment (defaults to a fresh
            :func:`run_quantum_assessment`).
        now: Override for the generation timestamp (defaults to the config's
            ``paper.date`` for determinism).

    Returns:
        A mapping of token name to its string value.
    """
    config = load_mission_config(config_path)
    paper = cast("dict[str, Any]", config.get("paper", {}))
    keywords = cast("list[Any]", config.get("keywords", []))
    date_stamp = now if now is not None else cast("str", paper.get("date", "2026"))

    metrics = assessment if assessment is not None else run_quantum_assessment()
    hydrology = cast("dict[str, Any]", metrics["hydrology"])
    water = cast("dict[str, Any]", metrics["water_cartel"])
    cartel = cast("dict[str, Any]", metrics["cartel_graph"])
    delivery = cast("dict[str, float]", hydrology["settlement_delivery"])
    hhi = cast("dict[str, float]", cartel["hhi_by_commodity"])

    return {
        "BOND_IDENTITY": cast("str", paper.get("title", "Quantum of Solace")),
        "BOND_CODENAME": QUANTUM_CODENAME,
        "BOND_VERSION": cast("str", paper.get("version", "0.1.0")),
        "BOND_SUBTITLE": cast("str", paper.get("subtitle", "")),
        "CONFIG_KEYWORDS": ", ".join(str(k) for k in keywords),
        "CONFIG_DATE": date_stamp,
        "PYTHON_VERSION": _python_version(),
        "GENERATION_TIMESTAMP": date_stamp,
        "HYDRO_TOTAL_SUPPLY": _fmt(cast("float", hydrology["total_supply"]), 1),
        "HYDRO_NODE_COUNT": str(hydrology["node_count"]),
        "HYDRO_ROUTE_COUNT": str(hydrology["route_count"]),
        "RESULT_BORDER_DELIVERY": _fmt(delivery["border_town"], 1),
        "RESULT_VALLEY_DELIVERY": _fmt(delivery["valley_compact"], 1),
        "RESULT_AGG_LEVERAGE": _fmt(cast("float", water["aggregate_leverage"]), 3),
        "RESULT_AGG_HHI": _fmt(cast("float", cartel["aggregate_hhi"]), 1),
        "RESULT_WATER_HHI": _fmt(hhi["water"], 1),
        "RESULT_LITHIUM_HHI": _fmt(hhi["lithium"], 1),
        "CARTEL_COMMODITIES": ", ".join(cast("list[str]", cartel["commodities"])),
        "CARTEL_ACTORS": ", ".join(cast("list[str]", cartel["actors"])),
    }


def _python_version() -> str:
    import sys

    return f"{sys.version_info.major}.{sys.version_info.minor}"
