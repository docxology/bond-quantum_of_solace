"""Subprocess smoke tests for the thin QUANTUM CLI scripts."""

import re
import subprocess
import sys
from pathlib import Path

from quantum_of_solace.manuscript_variables import generate_variables

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / script), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


class TestGenerateAnalysis:
    def test_run_writes_artifacts(self):
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
        assert "Success: True" in result.stdout
        assert "Film quantum_of_solace / QUANTUM" in result.stdout
        assert result.stdout.count("lesson:") == 6

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
    """Bind manuscript prose to the live token generator, not to a stale artifact."""

    @staticmethod
    def _sections() -> list[Path]:
        return sorted((PROJECT_ROOT / "manuscript").glob("[0-9]*.md"))

    @staticmethod
    def _tokens_in(sections: list[Path]) -> set[str]:
        pattern = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
        found: set[str] = set()
        for section in sections:
            found.update(pattern.findall(section.read_text(encoding="utf-8")))
        return found

    def test_scan_set_is_not_empty(self):
        """A vacuous scan (no sections, or no tokens) must fail, not pass."""
        sections = self._sections()
        assert len(sections) >= 8, f"expected the full numbered section set, found {len(sections)}"
        assert len(self._tokens_in(sections)) >= 20

    def test_every_prose_token_is_generated(self):
        """Every ``{{TOKEN}}`` in numbered sections must be produced live."""
        produced = set(generate_variables())
        assert produced, "generate_variables() produced no tokens"
        missing = self._tokens_in(self._sections()) - produced
        assert not missing, f"manuscript tokens not generated: {sorted(missing)}"

    def test_results_prose_carries_no_bare_decimal_metrics(self):
        """Results prose states measurements through tokens, never as literals.

        Integers survive (section numbering, list ordinals); a bare decimal in
        the results narrative is a hand-authored metric that escaped the token
        pipeline.
        """
        results = (PROJECT_ROOT / "manuscript" / "03_results.md").read_text(encoding="utf-8")
        detokenised = re.sub(r"\{\{[A-Z0-9_]+\}\}", "TOKEN", results)
        # Strip figure paths, which legitimately carry no numerals but may in future.
        detokenised = re.sub(r"!\[[^\]]*\]\([^)]*\)\{[^}]*\}", "", detokenised)
        stray = re.findall(r"(?<![\w.])\d+\.\d+(?![\w])", detokenised)
        assert not stray, f"hand-authored decimal metrics in results prose: {stray}"
