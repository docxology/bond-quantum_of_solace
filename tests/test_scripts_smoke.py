"""Subprocess smoke tests for the thin QUANTUM CLI scripts."""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / script), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


class TestGenerateAnalysis:
    def test_run_writes_artifacts(self, tmp_path: Path):
        result = _run("generate_analysis.py")
        assert result.returncode == 0, result.stderr
        assert (PROJECT_ROOT / "output" / "data" / "quantum_assessment.json").exists()
        assert (PROJECT_ROOT / "output" / "figures" / "hydrology_settlement_delivery.png").exists()

    def test_assessment_content(self):
        import json

        payload = json.loads((PROJECT_ROOT / "output" / "data" / "quantum_assessment.json").read_text())
        assert payload["hydrology"]["total_supply"] == 80.0


class TestRunMission:
    def test_brief(self):
        result = _run("run_mission.py", "brief")
        assert result.returncode == 0
        assert "QUANTUM" in result.stdout

    def test_recon(self):
        result = _run("run_mission.py", "recon", "map desert water")
        assert result.returncode == 0
        assert "total aquifer yield 80.0" in result.stdout

    def test_full(self):
        result = _run("run_mission.py", "full")
        assert result.returncode == 0
        assert "Successful" in result.stdout or "Success:" in result.stdout

    def test_unknown_phase(self):
        result = _run("run_mission.py", "bogus")
        assert result.returncode == 2
        assert "unknown phase" in result.stderr


class TestManuscriptVariablesScript:
    def test_run_writes_json(self):
        result = _run("z_generate_manuscript_variables.py")
        assert result.returncode == 0
        out = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
        assert out.exists()
        import json

        variables = json.loads(out.read_text())
        assert variables["BOND_CODENAME"] == "QUANTUM"


class TestManuscriptCrossReference:
    def test_every_prose_token_is_generated(self):
        """Every ``{{TOKEN}}`` in numbered manuscript sections must be producible."""
        import re

        variables = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
        token_values = set()
        if variables.exists():
            import json

            token_values = set(json.loads(variables.read_text()))
        pattern = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
        found: set[str] = set()
        for section in sorted((PROJECT_ROOT / "manuscript").glob("[0-9]*.md")):
            found.update(pattern.findall(section.read_text(encoding="utf-8")))
        missing = found - token_values
        assert not missing, f"manuscript tokens not generated: {sorted(missing)}"
