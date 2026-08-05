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

import numpy as np

from quantum_of_solace.analysis import (
    assess_cartel_graph,
    assess_hydrology,
    assess_pricing,
    assess_resilience,
    assess_shapley,
    assess_water_cartel,
)
from quantum_of_solace.pricing import inverse_demand

__all__ = [
    "ALL_FIGURES",
    "figure_cartel_leverage",
    "figure_hhi_concentration",
    "figure_hydrology_delivery",
    "figure_pricing_curve",
    "figure_resilience_interdiction",
    "figure_shapley_power",
    "render_all_figures",
]

#: The figure generators in canonical render order.
ALL_FIGURES = (
    "figure_hydrology_delivery",
    "figure_cartel_leverage",
    "figure_hhi_concentration",
    "figure_pricing_curve",
    "figure_resilience_interdiction",
    "figure_shapley_power",
)


def figure_hydrology_delivery(out_dir: Path) -> Path:
    """Per-settlement routing maxima against the network-wide bound.

    Each bar is what the network could route to that settlement if it served it
    alone; the dashed line is the whole-network routable volume. The bars are
    alternatives competing for the same aquifer yield, so their sum exceeds the
    line — drawing the line is what stops the chart being read additively.
    """
    metrics = assess_hydrology()
    delivery = cast("dict[str, float]", metrics["settlement_delivery"])
    network_delivery = cast("float", metrics["network_delivery"])
    settlements = sorted(delivery)
    values = [delivery[name] for name in settlements]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(settlements, values, color="#1e3a8a")
    ax.axhline(
        network_delivery,
        color="#b91c1c",
        linestyle="--",
        label=f"whole-network routable {network_delivery:.0f} (bars are alternatives, not addends)",
    )
    ax.set_ylabel("Max routed water (units / period)")
    ax.set_title("Desert network settlement delivery")
    ax.legend(fontsize="small")
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


def figure_pricing_curve(out_dir: Path) -> Path:
    """Linear demand curve with baseline/restricted clearing prices and the monopoly point."""
    metrics = assess_pricing()
    a = cast("float", metrics["a"])
    b = cast("float", metrics["b"])
    base_price = cast("float", metrics["baseline_price"])
    restricted_price = cast("float", metrics["restricted_price"])
    supply_base = cast("float", metrics["supply_baseline"])
    supply_restricted = cast("float", metrics["supply_restricted"])
    mono_price = cast("float", metrics["monopoly_price"])

    quantities = np.linspace(0.0, a / b, 200)
    prices = np.array([inverse_demand(q, a, b) for q in quantities])

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(quantities, prices, color="#0f172a", label="demand $p = a - bq$")
    ax.axhline(base_price, color="#2563eb", linestyle="--", label=f"baseline price {base_price:.1f}")
    ax.axhline(restricted_price, color="#b91c1c", linestyle="--", label=f"restricted price {restricted_price:.1f}")
    ax.axhline(mono_price, color="#0f766e", linestyle=":", label=f"monopoly price {mono_price:.1f}")
    ax.plot([supply_base], [base_price], "o", color="#2563eb")
    ax.plot([supply_restricted], [restricted_price], "o", color="#b91c1c")
    ax.set_xlabel("Water quantity (units / period)")
    ax.set_ylabel("Price")
    ax.set_title("Water scarcity pricing under cartel restriction")
    ax.legend(fontsize="small")
    ax.grid(linestyle=":", alpha=0.4)
    out_path = out_dir / "water_pricing_curve.png"
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def figure_resilience_interdiction(out_dir: Path) -> Path:
    """Bar chart of delivery retained after each single aqueduct interdiction."""
    metrics = assess_resilience()
    baseline = cast("float", metrics["baseline_delivery"])
    seq = cast("list[dict[str, object]]", metrics["interdiction_sequence"])

    labels = [str(entry["route"]) for entry in seq]
    after = [cast("float", entry["delivery_after"]) for entry in seq]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, after, color="#b45309")
    ax.axhline(baseline, color="#1e3a8a", linestyle="--", label=f"baseline {baseline:.0f}")
    for i, value in enumerate(after):
        ax.text(i, value + 1.0, f"{value:.0f}", ha="center", va="bottom")
    ax.set_ylabel("Routed water after cut (units / period)")
    ax.set_title("Greedy worst-case aqueduct interdiction")
    ax.legend(fontsize="small")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    out_path = out_dir / "resilience_route_criticality.png"
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def figure_shapley_power(out_dir: Path) -> Path:
    """Bar chart of each actor's exact Shapley value over the commodity portfolio."""
    metrics = assess_shapley()
    shapley = cast("dict[str, float]", metrics["shapley"])
    actors = sorted(shapley)
    values = [shapley[actor] for actor in actors]

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["#b91c1c" if actor == cast("str", metrics["top_actor"]) else "#475569" for actor in actors]
    ax.bar(actors, values, color=colors)
    for i, value in enumerate(values):
        ax.text(i, value + 0.03, f"{value:.3f}", ha="center", va="bottom")
    ax.set_ylabel("Shapley value")
    ax.set_title("Cooperative power over the commodity portfolio")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    out_path = out_dir / "cartel_shapley_power.png"
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
        "figure_pricing_curve": figure_pricing_curve,
        "figure_resilience_interdiction": figure_resilience_interdiction,
        "figure_shapley_power": figure_shapley_power,
    }
    return {name: renderer[name](out_dir) for name in ALL_FIGURES}
