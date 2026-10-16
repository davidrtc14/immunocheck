from __future__ import annotations

import io
from collections import Counter
from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader

from immunocheck.evaluation import extraction_benchmark as bench
from immunocheck.evaluation.end_to_end import load_end_to_end_items

ITEMS_PATH = Path(__file__).parents[1] / "evaluation/refinement_v4/items.jsonl"
FONTS_AVAILABLE = all((bench.FONT_DIR / name).is_file() for name in bench.FONTS_USED)
needs_fonts = pytest.mark.skipif(not FONTS_AVAILABLE, reason="fontes do Windows ausentes")


@pytest.fixture(scope="module")
def cases():
    return bench.build_cases(load_end_to_end_items(ITEMS_PATH, require_reviewed=True))


def _case(cases, modality, template, item="ref4-0039"):
    return next(
        case
        for case in cases
        if case.parent_item_id == item and case.modality == modality and case.template == template
    )


def test_one_case_per_item_and_template(cases) -> None:
    templates = sum(len(group) for group in bench.MODALITY_TEMPLATES.values())
    assert len(cases) == 96 * templates
    assert len({case.case_id for case in cases}) == len(cases)
    assert Counter(case.item_split for case in cases) == {
        "development": 48 * templates,
        "test": 48 * templates,
    }


def test_distractors_come_from_other_families_of_the_same_split(cases) -> None:
    items = {item.claim: item for item in load_end_to_end_items(ITEMS_PATH, require_reviewed=True)}
    for case in cases[:: len(cases) // 40]:
        assert case.target_claim not in case.distractors
        for distractor in case.distractors:
            assert items[distractor].claim_family != case.claim_family
            assert items[distractor].split.value == case.item_split


@needs_fonts
def test_image_rendering_is_deterministic_and_valid(cases) -> None:
    for template in bench.IMAGE_TEMPLATES:
        case = _case(cases, "image", template)
        first, second = bench.render_image(case), bench.render_image(case)
        assert first.data == second.data
        with Image.open(io.BytesIO(first.data)) as image:
            assert image.size == (first.width, first.height)
            assert first.width * first.height <= 12_000_000


def test_pages_contain_the_claim_and_distractors(cases) -> None:
    case = _case(cases, "link", "news_article")
    page = bench.render_page(case)
    html = page.body.decode("utf-8")
    assert bench._escape(case.target_claim) in html
    assert bench._escape(case.distractors[0]) in html
    long_page = bench.render_page(_case(cases, "link", "long_page")).body.decode("utf-8")
    assert long_page.index(bench._escape(case.target_claim)) > 6_000


def test_pdf_keeps_accents_on_the_second_page(cases) -> None:
    case = _case(cases, "link", "pdf_report")
    reader = PdfReader(io.BytesIO(bench.render_page(case).body))
    assert len(reader.pages) == 3
    text = " ".join((reader.pages[1].extract_text() or "").split())
    assert bench.substring_cer(case.target_claim, text) < 0.02


def test_messages_and_texts_embed_the_claim_or_link(cases) -> None:
    message = bench.render_message(_case(cases, "message", "comment_with_link"))
    assert bench.BENCHMARK_HOST in message and " " in message
    for template in bench.TEXT_TEMPLATES:
        case = _case(cases, "text", template)
        assert bench.substring_cer(case.target_claim, bench.render_text(case)) == 0.0


def test_substring_cer_ignores_surrounding_text() -> None:
    assert bench.substring_cer("A vacina protege", "Maria 10:42 a vacina protege hoje") == 0.0
    assert bench.substring_cer("abcd", "zzabxdzz") == pytest.approx(0.25)
    assert bench.substring_cer("abc", "") == 1.0
    assert bench.substring_cer("vacinação", "VACINACAO", strip_accents=True) == 0.0
    with pytest.raises(ValueError):
        bench.substring_cer("  ", "x")


def test_markers_preserved_detects_lost_numbers_and_negations() -> None:
    claim = "A vacina não reduz em 50% os casos."
    assert bench.markers_preserved(claim, "a vacina nao reduz em 50% os casos")
    assert not bench.markers_preserved(claim, "A vacina reduz em 50% os casos.")
    assert not bench.markers_preserved(claim, "A vacina não reduz em 5% os casos.")
