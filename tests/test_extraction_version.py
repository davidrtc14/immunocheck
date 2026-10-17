from __future__ import annotations

import pytest

from immunocheck.application.input_understanding import UnderstandingNormalizer
from immunocheck.bootstrap import build_understanding_normalizer, resolve_extraction_version


def test_extraction_v1_remains_the_default(monkeypatch) -> None:
    monkeypatch.delenv("EXTRACTION_VERSION", raising=False)
    assert resolve_extraction_version() == "v1"
    assert resolve_extraction_version(" V2 ") == "v2"
    with pytest.raises(ValueError, match="EXTRACTION_VERSION"):
        resolve_extraction_version("v3")


def test_understanding_normalizer_enables_vision_only_on_request(monkeypatch) -> None:
    pytest.importorskip("trafilatura")
    try:
        normalizer = build_understanding_normalizer(vision=False)
    except ValueError:
        pytest.skip("Tesseract ausente")
    assert isinstance(normalizer, UnderstandingNormalizer)
    assert normalizer.vision is None
    monkeypatch.setenv("EXTRACTION_VISION", "1")
    assert build_understanding_normalizer().vision is not None
