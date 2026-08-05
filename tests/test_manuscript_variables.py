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
        assert variables["RESULT_AGG_HHI"] == "3925.0"
        assert "water" in variables["CARTEL_COMMODITIES"]

    def test_leverage_token_is_a_horizon_share(self):
        """Aggregate leverage is a share in [0, 1], not a period-inflated ratio."""
        variables = generate_variables()
        leverage = float(variables["RESULT_AGG_LEVERAGE"])
        assert 0.0 < leverage < 1.0
        # The token must equal withheld volume / horizon demand exactly.
        withheld = float(variables["CARTEL_WITHHELD_VOLUME"])
        horizon_demand = float(variables["CARTEL_HORIZON_DEMAND"])
        assert withheld / horizon_demand == pytest.approx(leverage, abs=5e-4)
        assert float(variables["RESULT_AGG_LEVERAGE_PCT"]) == pytest.approx(leverage * 100.0, abs=0.05)

    def test_deepened_tokens(self):
        variables = generate_variables()
        # Numeric comparison, not lexicographic string comparison.
        assert float(variables["PRICE_RESTRICTED"]) > float(variables["PRICE_BASELINE"])
        assert "highland_aquifer->border_town" in variables["RESIL_CRITICAL_ROUTE"]
        assert variables["RESIL_BASELINE"] == "80.0"
        assert variables["SHAPLEY_TOP_ACTOR"] == "quantum"
        assert variables["SHAPLEY_TOTAL"] == "7.0"
        assert variables["PRICE_DWL"] == "4050.0"

    def test_setup_parameter_tokens(self):
        """Setup parameters the manuscript cites are tokens, not prose numerals."""
        variables = generate_variables()
        assert variables["HYDRO_AQUIFER_COUNT"] == "3"
        assert variables["HYDRO_SETTLEMENT_COUNT"] == "2"
        assert variables["CARTEL_DAM_COUNT"] == "3"
        assert variables["CARTEL_CONTROLLED_DAMS"] == "2"
        assert variables["CARTEL_RESTRICTION_PCT"] == "50"
        assert variables["CARTEL_PERIODS"] == "12"
        assert variables["PRICE_DEMAND_A"] == "100"
        assert variables["PRICE_DEMAND_B"] == "0.25"
        assert variables["PRICE_MARGINAL_COST"] == "10"
        assert variables["MISSION_SEED"] == "0"
        assert variables["SHAPLEY_WEIGHTS"] == "copper 1, grain 1, lithium 2, water 3"

    def test_hhi_band_tokens_match_the_measured_value(self):
        """The concentration band is classified in code, not asserted in prose."""
        variables = generate_variables()
        assert float(variables["RESULT_AGG_HHI"]) > float(variables["HHI_HIGH_THRESHOLD"])
        assert variables["RESULT_AGG_HHI_BAND"] == "highly concentrated"
        assert variables["HHI_HIGH_THRESHOLD"] == "2500"
        assert variables["HHI_MODERATE_THRESHOLD"] == "1500"

    def test_delivery_tokens_respect_the_supply_bound(self):
        """The headline delivery token can never exceed the aquifer-yield token."""
        variables = generate_variables()
        assert float(variables["HYDRO_NETWORK_DELIVERY"]) <= float(variables["HYDRO_TOTAL_SUPPLY"])
        assert float(variables["RESIL_BASELINE"]) <= float(variables["HYDRO_TOTAL_SUPPLY"])
        # The per-settlement maxima are alternatives; their sum legitimately
        # exceeds the bound, which is why prose must never add them.
        per_settlement = float(variables["RESULT_BORDER_DELIVERY"]) + float(variables["RESULT_VALLEY_DELIVERY"])
        assert per_settlement > float(variables["HYDRO_NETWORK_DELIVERY"])

    def test_leverage_conversion_tokens_are_derived_not_asserted(self):
        """Ownership, leverage and their ratio must agree to the rendered digits."""
        variables = generate_variables()
        ownership = float(variables["CARTEL_OWNERSHIP_PCT"])
        leverage = float(variables["RESULT_AGG_LEVERAGE_PCT"])
        ratio = float(variables["CARTEL_LEVERAGE_OWNERSHIP_RATIO"])
        assert ratio == pytest.approx(leverage / ownership, abs=5e-3)
        # 2 of 3 dams is a controlling share; the conversion still lands below 1.
        assert ownership > 50.0
        assert ratio < 1.0

    def test_retention_tokens_are_distinct(self):
        """Mean and worst-case retention are separate tokens with distinct values."""
        variables = generate_variables()
        assert float(variables["RESIL_INDEX"]) > float(variables["RESIL_WORST_RETENTION"])
        assert int(variables["RESIL_CRITICAL_COUNT"]) + int(variables["RESIL_REDUNDANT_COUNT"]) == int(
            variables["RESIL_ROUTE_COUNT"]
        )

    def test_elasticity_token_matches_the_demand_parameters(self):
        """PRICE_ELASTICITY must be p/(b*q) at the rendered baseline, not b*p/q."""
        variables = generate_variables()
        price = float(variables["PRICE_BASELINE"])
        quantity = float(variables["PRICE_SUPPLY_BASELINE"])
        slope = float(variables["PRICE_DEMAND_B"])
        assert float(variables["PRICE_ELASTICITY"]) == pytest.approx(price / (slope * quantity), abs=5e-4)

    def test_interdiction_sequence_tokens(self):
        """The interdiction narrative's step count and loss share are computed."""
        variables = generate_variables()
        assert variables["RESIL_SEQ_STEPS"] == "3"
        loss = float(variables["RESIL_SEQ_LOSS"])
        baseline = float(variables["RESIL_BASELINE"])
        assert float(variables["RESIL_SEQ_LOSS_FRAC"]) == pytest.approx(100.0 * loss / baseline, abs=0.05)
        assert float(variables["RESIL_SEQ_DELIVERY_AFTER"]) == pytest.approx(baseline - loss, abs=0.05)

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
