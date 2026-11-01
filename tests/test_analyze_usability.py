import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from analyze_usability import _score, sus


def test_sus_extremes_and_neutral() -> None:
    assert sus([5, 1] * 5) == 100.0
    assert sus([1, 5] * 5) == 0.0
    assert sus([3] * 10) == 50.0


def test_sus_known_respondent() -> None:
    assert sus([4, 2, 4, 2, 3, 3, 4, 2, 4, 2]) == 70.0


def test_score_parses_sheet_values() -> None:
    assert _score("5.0") == 5
    assert _score("1 — Discordo totalmente") == 1
    assert _score("Não recebi essa resposta") is None
