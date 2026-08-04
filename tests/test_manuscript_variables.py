"""Tests for the QUANTUM manuscript variable token hydration."""

from pathlib import Path

import pytest
import yaml

from quantum_of_solace.analysis import run_quantum_assessment
from quantum_of_solace.manuscript_variables import DEFAULT_CONFIG_PATH, generate_variables, load_mission_config


def _write_config(path: Path, extra: dict | None = None) -> Path:
    data = {
        "paper": {
            "title": "Quantum of Solace: QUANTUM — Special-Agent Mission Software",
            "subtitle": "Water-Rights Cartels, Desert Hydrology, and Commodity Control",
            "version": "0.1.0",
            "date": "2026-08-04",
        },
        "keywords": ["water-rights cartel", "desert hydrology", "commodity-cartel graph"],
    }
    if extra:
        data.update(extra)
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


class TestLoadMissionConfig:
    def test_load(self, tmp_path: Path):
        config_path = _write_config(tmp_path / "config.yaml")
        config = load_mission_config(config_path)
        assert config["paper"]["title"].startswith("Quantum of Solace")

    def test_not_a_mapping(self, tmp_path: Path):
        path = tmp_path / "bad.yaml"
        path.write_text("- just\n- a\n- list\n", encoding="utf-8")
        with pytest.raises(ValueError):
            load_mission_config(path)

    def test_default_path_exists(self):
        assert DEFAULT_CONFIG_PATH.exists()


class TestGenerateVariables:
    def test_default(self):
        variables = generate_variables()
        assert variables["BOND_CODENAME"] == "QUANTUM"
        assert variables["RESULT_BORDER_DELIVERY"] == "65.0"
        assert variables["RESULT_AGG_LEVERAGE"].startswith("3.")
        assert variables["RESULT_AGG_HHI"] == "3925.0"
        assert "water" in variables["CARTEL_COMMODITIES"]

    def test_assessment_and_now_override(self, tmp_path: Path):
        config_path = _write_config(tmp_path / "config.yaml")
        assessment = run_quantum_assessment()
        variables = generate_variables(config_path=config_path, assessment=assessment, now="2030-01-01")
        assert variables["CONFIG_DATE"] == "2030-01-01"
        assert variables["GENERATION_TIMESTAMP"] == "2030-01-01"
        assert variables["HYDRO_TOTAL_SUPPLY"] == "80.0"

    def test_all_tokens_are_strings(self, tmp_path: Path):
        config_path = _write_config(tmp_path / "config.yaml")
        variables = generate_variables(config_path=config_path)
        for token, value in variables.items():
            assert isinstance(value, str), f"{token} should be a string"
