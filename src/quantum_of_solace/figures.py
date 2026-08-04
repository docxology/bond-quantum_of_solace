"""Deterministic figure generators for the QUANTUM assessment.

Each generator computes its data from the actual domain algorithms (via
:mod:`quantum_of_solace.analysis`) and writes a PNG under a given output
directory. No random draws, no wall-clock dependence — a figure is a pure
function of the fixed problem data, so regeneration is byte-stable.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from typing import cast

from quantum_of_solace.analysis import assess_cartel_graph, assess_hydrology, assess_water_cartel

__all__ = [
    "ALL_FIGURES",
    "figure_cartel_leverage",
    "figure_hhi_concentration",
    "figure_hydrology_delivery",
    "render_all_figures",
]

#: The figure generators in canonical render order.
ALL_FIGURES = ("figure_hydrology_delivery", "figure_cartel_leverage", "figure_hhi_concentration")


def figure_hydrology_delivery(out_dir: Path) -> Path:
    """Bar chart of each settlement's maximum delivered water per period."""
    metrics = assess_hydrology()
    delivery = cast("dict[str, float]", metrics["settlement_delivery"])
    settlements = sorted(delivery)
    values = [delivery[name] for name in settlements]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(settlements, values, color="#1e3a8a")
    ax.set_ylabel("Max delivered water (units / period)")
    ax.set_title("Desert network settlement delivery")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    for i, value in enumerate(values):
        ax.text(i, value + 0.5, f"{value:.0f}", ha="center", va="bottom")
    out_path = out_dir / "hydrology_settlement_delivery.png"
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def figure_cartel_leverage(out_dir: Path) -> Path:
    """Bar chart of per-dam cartel leverage (withheld share of demand)."""
    metrics = assess_water_cartel()
    per_dam = cast("dict[str, dict[str, object]]", metrics["per_dam"])
    names = sorted(per_dam)
    leverage = [cast("float", per_dam[name]["leverage"]) for name in names]
    controlled = [bool(per_dam[name]["controlled"]) for name in names]

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["#b91c1c" if flag else "#475569" for flag in controlled]
    ax.bar(names, leverage, color=colors)
    ax.set_ylabel("Leverage (withheld / downstream demand)")
    ax.set_title("Cartel leverage by dam (red = cartel-controlled)")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    for i, value in enumerate(leverage):
        ax.text(i, value + 0.01, f"{value:.2f}", ha="center", va="bottom")
    out_path = out_dir / "water_cartel_leverage.png"
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def figure_hhi_concentration(out_dir: Path) -> Path:
    """Bar chart of Herfindahl–Hirschman concentration per commodity."""
    metrics = assess_cartel_graph()
    hhi_by_commodity = cast("dict[str, float]", metrics["hhi_by_commodity"])
    commodities = sorted(hhi_by_commodity)
    values = [hhi_by_commodity[name] for name in commodities]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(commodities, values, color="#0f766e")
    ax.set_ylabel("Herfindahl–Hirschman Index (points)")
    ax.set_title("Multi-resource market concentration by commodity")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    for i, value in enumerate(values):
        ax.text(i, value + 20.0, f"{value:.0f}", ha="center", va="bottom")
    out_path = out_dir / "cartel_hhi_concentration.png"
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def render_all_figures(out_dir: Path) -> dict[str, Path]:
    """Render every canonical figure into ``out_dir`` (created if needed)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    renderer = {
        "figure_hydrology_delivery": figure_hydrology_delivery,
        "figure_cartel_leverage": figure_cartel_leverage,
        "figure_hhi_concentration": figure_hhi_concentration,
    }
    return {name: renderer[name](out_dir) for name in ALL_FIGURES}
