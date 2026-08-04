"""Tests for the QUANTUM figure generators."""

from pathlib import Path

from quantum_of_solace.figures import (
    ALL_FIGURES,
    figure_cartel_leverage,
    figure_hhi_concentration,
    figure_hydrology_delivery,
    render_all_figures,
)


class TestFigures:
    def test_hydrology_delivery(self, tmp_path: Path):
        path = figure_hydrology_delivery(tmp_path)
        assert path.exists()
        assert path.stat().st_size > 0
        assert path.name == "hydrology_settlement_delivery.png"

    def test_cartel_leverage(self, tmp_path: Path):
        path = figure_cartel_leverage(tmp_path)
        assert path.exists()
        assert path.name == "water_cartel_leverage.png"

    def test_hhi_concentration(self, tmp_path: Path):
        path = figure_hhi_concentration(tmp_path)
        assert path.exists()
        assert path.name == "cartel_hhi_concentration.png"

    def test_render_all(self, tmp_path: Path):
        out_dir = tmp_path / "nested" / "figures"
        rendered = render_all_figures(out_dir)
        assert set(rendered) == set(ALL_FIGURES)
        for path in rendered.values():
            assert path.exists()
