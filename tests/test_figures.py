"""Tests for the QUANTUM figure generators."""

from pathlib import Path

from quantum_of_solace.figures import (
    ALL_FIGURES,
    figure_cartel_leverage,
    figure_hhi_concentration,
    figure_hydrology_delivery,
    figure_pricing_curve,
    figure_resilience_interdiction,
    figure_shapley_power,
    render_all_figures,
)


def _png_ok(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0 and path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


class TestFigures:
    def test_hydrology_delivery(self, tmp_path: Path):
        path = figure_hydrology_delivery(tmp_path)
        assert path.name == "hydrology_settlement_delivery.png"
        assert _png_ok(path)

    def test_cartel_leverage(self, tmp_path: Path):
        path = figure_cartel_leverage(tmp_path)
        assert path.name == "water_cartel_leverage.png"
        assert _png_ok(path)

    def test_hhi_concentration(self, tmp_path: Path):
        path = figure_hhi_concentration(tmp_path)
        assert path.name == "cartel_hhi_concentration.png"
        assert _png_ok(path)

    def test_pricing_curve(self, tmp_path: Path):
        path = figure_pricing_curve(tmp_path)
        assert path.name == "water_pricing_curve.png"
        assert _png_ok(path)

    def test_resilience_interdiction(self, tmp_path: Path):
        path = figure_resilience_interdiction(tmp_path)
        assert path.name == "resilience_route_criticality.png"
        assert _png_ok(path)

    def test_shapley_power(self, tmp_path: Path):
        path = figure_shapley_power(tmp_path)
        assert path.name == "cartel_shapley_power.png"
        assert _png_ok(path)

    def test_render_all(self, tmp_path: Path):
        out_dir = tmp_path / "nested" / "figures"
        rendered = render_all_figures(out_dir)
        assert set(rendered) == set(ALL_FIGURES)
        assert len(rendered) == 6
        for path in rendered.values():
            assert _png_ok(path)

    def test_byte_deterministic(self, tmp_path: Path):
        first = render_all_figures(tmp_path / "a")
        second = render_all_figures(tmp_path / "b")
        for name, path_a in first.items():
            path_b = second[name]
            assert path_a.read_bytes() == path_b.read_bytes()
