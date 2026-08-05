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

    #: Quantity phrases that assert a magnitude or a ratio without a token.
    #:
    #: A bare-decimal scan is blind to prose numerals, which is exactly how "a
    #: minority of the dams" (the cartel holds 2 of 3), "a quarter of the
    #: region's water" and "several times its size" (the converted share is
    #: below the holding share) survived earlier review. Every phrase below
    #: makes a claim that must instead be carried by a computed token.
    QUANTITY_PHRASES = (
        r"\bminority\b",
        r"\bmajority\b",
        r"\ba quarter of\b",
        r"\ba third of\b",
        r"\ba fifth of\b",
        r"\bhalf (?:of|the)\b",
        r"\bseveral times\b",
        r"\bmany times\b",
        r"\borders? of magnitude\b",
        r"\btwice (?:as|the)\b",
        r"\bdouble the\b",
        r"\bfar (?:more|less|greater|smaller) than\b",
        r"\bvastly\b",
        r"\boverwhelming(?:ly)?\b",
        r"\bdisproportionate(?:ly)?\b",
    )

    @staticmethod
    def _to_prose(text: str) -> str:
        """Reduce markdown to narrative prose for the metric gates.

        Four things are stripped, each because it is markup rather than a
        sentence making a claim: fenced code blocks, inline code spans (a pinned
        `requires-python >= 3.10` is a version constraint, not a measurement),
        figure includes with their attribute braces, and document cross-
        references of the form `§5.3`. Everything else — every ordinary
        sentence in every numbered section — is scanned.
        """
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`\n]*`", "", text)
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)(?:\{[^}]*\})?", "", text)
        text = re.sub(r"§\s*\d+(?:\.\d+)*", "", text)
        return re.sub(r"\{\{[A-Z0-9_]+\}\}", "TOKEN", text)

    @classmethod
    def _prose(cls, section: Path) -> str:
        return cls._to_prose(section.read_text(encoding="utf-8"))

    @staticmethod
    def _bare_decimals(prose: str) -> list[str]:
        return re.findall(r"(?<![\w.])\d+\.\d+(?![\w])", prose)

    def test_the_decimal_gate_rejects_a_hand_authored_metric(self):
        """Negative control: a bare decimal in a sentence must be detected.

        A scan that stopped matching would otherwise pass every section
        silently. The second assertion documents the stripped forms, so
        widening the exemptions shows up here as a deliberate edit.
        """
        assert self._bare_decimals(self._to_prose("The network delivers 120.0 units per period."))
        assert not self._bare_decimals(self._to_prose("Pinned to `>= 3.10`, described in §5.3, yielding TOKEN."))

    def test_prose_carries_no_bare_decimal_metrics(self):
        """No numbered section states a measurement as a bare decimal literal.

        Scans **every** numbered section, not just the results: the inverted
        leverage claim lived in `04_conclusion.md`, which the earlier
        results-only scan never opened. Integers survive (section numbering,
        list ordinals, definitional thresholds such as the unit-elastic 1).
        """
        offenders: dict[str, list[str]] = {}
        for section in self._sections():
            stray = self._bare_decimals(self._prose(section))
            if stray:
                offenders[section.name] = stray
        assert not offenders, f"hand-authored decimal metrics in prose: {offenders}"

    def test_prose_carries_no_untokenised_quantity_claims(self):
        """No numbered section asserts a magnitude in words instead of a token.

        This gate is lexical, and its limits are stated rather than implied: it
        cannot tell whether the *value* inside a token is right, and it only
        catches the phrase forms listed in `QUANTITY_PHRASES`. What it does
        guarantee is that this specific family of prose-only quantity claims —
        the family that produced three of this package's false statements —
        fails the suite instead of shipping.
        """
        pattern = re.compile("|".join(self.QUANTITY_PHRASES), re.IGNORECASE)
        offenders: dict[str, list[str]] = {}
        for section in self._sections():
            hits = pattern.findall(self._prose(section))
            if hits:
                offenders[section.name] = hits
        assert not offenders, f"untokenised quantity claims in prose: {offenders}"

    def test_the_quantity_gate_rejects_the_claims_it_was_written_for(self):
        """Negative control: the historical false sentences must trip the gate.

        Without this, a gate whose pattern list silently stopped matching would
        stay green forever. These are the exact strings that shipped.
        """
        pattern = re.compile("|".join(self.QUANTITY_PHRASES), re.IGNORECASE)
        historical_false_claims = (
            "Owning a minority of the dams is enough to remove a quarter of the region's water.",
            "a partial holding converts into a share of regional supply several times its size",
            "a cartel with minority dam ownership and a lead in high-value commodities",
            "leaving TOKEN units still flowing — a majority of supply lost",
            "the price moves far more than the volume",
        )
        undetected = [claim for claim in historical_false_claims if not pattern.search(claim)]
        assert not undetected, f"the gate no longer catches its own founding cases: {undetected}"
