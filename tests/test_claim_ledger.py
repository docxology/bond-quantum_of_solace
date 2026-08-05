"""Bind `data/claim_ledger.yaml` to the live assessment.

The ledger records the package's headline numeric claims with the module that
produces each one. Left alone, such a file decays silently: a model changes,
the ledger keeps asserting the old number, and the "evidence registry" becomes
a record of a lie. These tests re-derive every entry from the running code, so
drift fails the suite instead of accumulating.

Each ledger entry must also name a manuscript token, and that token must both
exist and render the same number — otherwise the ledger and the paper could
disagree while each looked internally consistent.
"""

from pathlib import Path

import pytest
import yaml

from quantum_of_solace.manuscript_variables import generate_variables

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = PROJECT_ROOT / "data" / "claim_ledger.yaml"

#: Bibtex keys defined in the manuscript bibliography, for attribution checking.
BIB_PATH = PROJECT_ROOT / "manuscript" / "references.bib"


def _ledger() -> dict:
    with open(LEDGER_PATH, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert isinstance(data, dict), "claim ledger must be a YAML mapping"
    return data


class TestLedgerShape:
    def test_ledger_is_not_empty(self):
        """A ledger with no claims would make every check below vacuous."""
        claims = _ledger()["claims"]
        assert len(claims) >= 7, f"expected the full claim set, found {len(claims)}"

    def test_every_claim_is_fully_specified(self):
        for entry in _ledger()["claims"]:
            for field in ("id", "claim", "value", "token", "evidence", "determinism"):
                assert field in entry, f"claim {entry.get('id')!r} is missing {field!r}"
            assert entry["determinism"] is True

    def test_claim_ids_are_unique(self):
        ids = [entry["id"] for entry in _ledger()["claims"]]
        assert len(ids) == len(set(ids))


class TestLedgerValuesMatchTheLiveAssessment:
    def test_every_claimed_value_is_reproduced_by_its_token(self):
        """Re-derive each ledger value from the running code, not from a cache."""
        variables = generate_variables()
        mismatches: list[str] = []
        for entry in _ledger()["claims"]:
            token = entry["token"]
            if token not in variables:
                mismatches.append(f"{entry['id']}: token {token!r} is not generated")
                continue
            live = float(variables[token])
            claimed = float(entry["value"])
            tolerance = float(entry.get("tolerance", 1e-9))
            if abs(live - claimed) > tolerance:
                mismatches.append(f"{entry['id']}: ledger {claimed} vs live {live} (token {token})")
        assert not mismatches, "claim ledger has drifted from the code:\n  " + "\n  ".join(mismatches)

    def test_leverage_claim_is_a_share(self):
        """The leverage entry specifically must stay inside the unit interval.

        A value above 1 would mean the horizon-volume denominator regressed to
        a per-period rate — the exact defect the dimensional fix removed.
        """
        entry = next(e for e in _ledger()["claims"] if e["id"] == "quantum.water_cartel.aggregate_leverage")
        assert 0.0 < float(entry["value"]) < 1.0


class TestAlgorithmAttributions:
    def test_every_attribution_cites_a_real_bibtex_key(self):
        """Attributions point at `references.bib` keys, not at free-text guesses."""
        bib = BIB_PATH.read_text(encoding="utf-8")
        attributions = _ledger()["algorithm_attributions"]
        assert len(attributions) >= 9
        for row in attributions:
            key = row["reference"]
            assert f"{{{key}," in bib, f"attribution {row['algorithm']!r} cites unknown bib key {key!r}"

    def test_every_attribution_names_an_importable_symbol(self):
        import importlib

        for row in _ledger()["algorithm_attributions"]:
            module_name, _, attribute = row["module"].rpartition(".")
            module = importlib.import_module(f"quantum_of_solace.{module_name}")
            target = getattr(module, attribute, None)
            if target is None:  # a method on one of the module's classes
                target = next(
                    (
                        getattr(obj, attribute)
                        for obj in vars(module).values()
                        if isinstance(obj, type) and hasattr(obj, attribute)
                    ),
                    None,
                )
            assert target is not None, f"{row['module']} does not resolve to a symbol"
            assert callable(target), f"{row['module']} resolves to a non-callable"


@pytest.mark.parametrize("path", [LEDGER_PATH, BIB_PATH])
def test_evidence_files_exist(path: Path):
    assert path.is_file(), f"{path} is missing"
