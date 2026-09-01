from __future__ import annotations

import io

import pytest
from PIL import Image

from immunocheck.application.content_normalizer import ContentExtractionError
from immunocheck.infrastructure.ocr import OCRQualityPolicy, _parse_tsv, inspect_image


def image_bytes(*, image_format: str = "PNG", size: tuple[int, int] = (100, 50)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, "white").save(buffer, format=image_format)
    return buffer.getvalue()


def test_image_inspection_validates_real_format_and_dimensions() -> None:
    info = inspect_image(image_bytes(), declared_media_type="image/png")

    assert info.media_type == "image/png"
    assert (info.width, info.height) == (100, 50)


def test_image_inspection_rejects_declared_type_mismatch() -> None:
    with pytest.raises(ContentExtractionError, match="não corresponde"):
        inspect_image(image_bytes(), declared_media_type="image/jpeg")


def test_image_inspection_rejects_pixel_limit_before_full_processing() -> None:
    with pytest.raises(ContentExtractionError, match="12 megapixels"):
        inspect_image(image_bytes(size=(101, 100)), maximum_pixels=10_000)


def test_tsv_parser_accepts_legible_text_and_preserves_lines() -> None:
    raw = (
        "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tconf\ttext\n"
        "5\t1\t1\t1\t1\t1\t92.5\tVacina\n"
        "5\t1\t1\t1\t1\t2\t90.0\tprotege\n"
        "5\t1\t1\t1\t2\t1\t88.0\tcontra\n"
        "5\t1\t1\t1\t2\t2\t91.0\tdoenças\n"
    ).encode()

    text = _parse_tsv(raw, OCRQualityPolicy())

    assert text == "Vacina protege\ncontra doenças"


def test_tsv_parser_accepts_short_but_clear_factual_claim() -> None:
    raw = (
        "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tconf\ttext\n"
        "5\t1\t1\t1\t1\t1\t94.0\tVacina\n"
        "5\t1\t1\t1\t1\t2\t92.0\tmata\n"
        "5\t1\t1\t1\t1\t3\t91.0\tbebês\n"
    ).encode()

    assert _parse_tsv(raw, OCRQualityPolicy()) == "Vacina mata bebês"


def test_tsv_parser_rejects_low_confidence_or_short_ocr() -> None:
    raw = (
        "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tconf\ttext\n"
        "5\t1\t1\t1\t1\t1\t12.0\ttexto\n"
        "5\t1\t1\t1\t1\t2\t10.0\tquase\n"
        "5\t1\t1\t1\t1\t3\t11.0\tilegível\n"
        "5\t1\t1\t1\t1\t4\t9.0\taqui\n"
    ).encode()

    with pytest.raises(ContentExtractionError, match="qualidade insuficiente"):
        _parse_tsv(raw, OCRQualityPolicy())
