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
    pricing = cast("dict[str, Any]", metrics["pricing"])
    resilience = cast("dict[str, Any]", metrics["resilience"])
    shapley = cast("dict[str, Any]", metrics["shapley"])
    delivery = cast("dict[str, float]", hydrology["settlement_delivery"])
    hhi = cast("dict[str, float]", cartel["hhi_by_commodity"])
    shapley_values = cast("dict[str, float]", shapley["shapley"])
    banzhaf_values = cast("dict[str, float]", shapley["banzhaf"])

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
        "PRICE_SUPPLY_BASELINE": _fmt(cast("float", pricing["supply_baseline"]), 1),
        "PRICE_SUPPLY_RESTRICTED": _fmt(cast("float", pricing["supply_restricted"]), 1),
        "PRICE_BASELINE": _fmt(cast("float", pricing["baseline_price"]), 1),
        "PRICE_RESTRICTED": _fmt(cast("float", pricing["restricted_price"]), 1),
        "PRICE_RISE": _fmt(cast("float", pricing["price_rise_frac"]) * 100.0, 1),
        "PRICE_SCARCITY_RENT": _fmt(cast("float", pricing["scarcity_rent"]), 1),
        "PRICE_ELASTICITY": _fmt(cast("float", pricing["elasticity"]), 3),
        "PRICE_MONOPOLY": _fmt(cast("float", pricing["monopoly_price"]), 1),
        "PRICE_MONOPOLY_Q": _fmt(cast("float", pricing["monopoly_quantity"]), 1),
        "PRICE_DWL": _fmt(cast("float", pricing["deadweight_loss"]), 1),
        "RESIL_BASELINE": _fmt(cast("float", resilience["baseline_delivery"]), 1),
        "RESIL_CRITICAL_ROUTE": cast("str", resilience["critical_route"]),
        "RESIL_CRITICAL_LOSS": _fmt(cast("float", resilience["critical_loss"]), 1),
        "RESIL_CRITICAL_FRAC": _fmt(cast("float", resilience["critical_loss_frac"]) * 100.0, 1),
        "RESIL_INDEX": _fmt(cast("float", resilience["resilience_index"]), 3),
        "RESIL_CRITICAL_COUNT": str(resilience["critical_route_count"]),
        "SHAPLEY_TOP_ACTOR": cast("str", shapley["top_actor"]),
        "SHAPLEY_QUANTUM": _fmt(shapley_values["quantum"], 3),
        "SHAPLEY_RIVAL": _fmt(shapley_values["rival_syndicate"], 3),
        "SHAPLEY_STATE": _fmt(shapley_values["state_utility"], 3),
        "SHAPLEY_GAP": _fmt(cast("float", shapley["dominance_gap"]), 3),
        "SHAPLEY_TOTAL": _fmt(cast("float", shapley["grand_coalition_value"]), 1),
        "SHAPLEY_BANZHAF_QUANTUM": _fmt(banzhaf_values["quantum"], 3),
    }


def _python_version() -> str:
    import sys

    return f"{sys.version_info.major}.{sys.version_info.minor}"
