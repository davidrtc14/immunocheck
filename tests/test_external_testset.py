from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    DatasetStatus,
    load_end_to_end_items,
)

ROOT = Path(__file__).parents[1]
EXTERNAL = ROOT / "evaluation" / "refinement_v6" / "external"


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_external_testset", ROOT / "scripts" / "build_external_testset.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = _load_builder()


def _candidate(claim, verdict, *, source="xfact", key="k", redistributable=True):
    return builder.Candidate(
        source=source,
        source_key=key,
        claim=claim,
        source_label="x",
        verdict=verdict,
        agency="agencia",
        claim_date=None,
        review_url=None,
        redistributable=redistributable,
    )


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Verdadeiro", "SUPPORTED"),
        ("Falso", "REFUTED"),
        ("falso", "REFUTED"),
        ("Errado", "REFUTED"),
        ("Enganoso", "MISLEADING"),
        ("Sem contexto", "MISLEADING"),
        ("Exagerado", "MISLEADING"),
        ("não_é_bem_assim", "MISLEADING"),
        ("ENGANOSO: trecho fora de contexto.", "MISLEADING"),
        ("É FALSO vídeo que afirma algo", "REFUTED"),
        ("São FALSAS as afirmações", "REFUTED"),
        ("Insustentável", None),
        ("Impossível provar", None),
        ("Contextualizando", None),
    ],
)
def test_agency_label_mapping(label, expected):
    assert builder.map_agency_label(label) == expected


def test_xfact_label_mapping_discards_unclassifiable():
    assert builder.map_xfact_label("true") == "SUPPORTED"
    assert builder.map_xfact_label("mostly true") == "SUPPORTED"
    assert builder.map_xfact_label("partly true/misleading") == "MISLEADING"
    assert builder.map_xfact_label("mostly false") == "REFUTED"
    assert builder.map_xfact_label("complicated/hard to categorise") is None
    assert builder.map_xfact_label("other") is None


def test_vaccination_filter_keeps_human_vaccines_only():
    assert builder.is_vaccination_claim("A vacina da febre amarela contém mercúrio.")
    assert builder.is_vaccination_claim("Imunizantes contra covid alteram o DNA.")
    assert not builder.is_vaccination_claim("Vacina antirrábica para cães foi suspensa.")
    assert not builder.is_vaccination_claim("The vaccine causes autism.")
    assert not builder.is_vaccination_claim("O governo cortou verbas da saúde.")


@pytest.mark.parametrize(
    ("claim", "reason"),
    [
        ("Vídeo mostra enfermeira desmaiando após tomar vacina", "media_artifact"),
        ("Em publicação nas redes, alega-se que vacinas matam", "media_artifact"),
        ("Lula recusou a compra da vacina contra a dengue", "political_actor"),
        ("É falso que a vacina cause autismo nas crianças", "verdict_or_review_text"),
        ("Uma notícia garante que Cuba produziu uma vacina eficaz", "media_artifact"),
        ("Vacinas de base RNA alteram o código genético de quem ......", "truncated"),
        ("A vacina (...) não funciona (...) nunca funcionou", "fragmented_quote"),
        ("A vacina funciona mesmo contra o sarampo?", "question"),
        ("Vacina mata", "too_short"),
        ("A vacina contra o sarampo deve ser tomada em duas doses", None),
    ],
)
def test_exclusion_rules(claim, reason):
    assert builder.exclusion_reason(claim) == reason


def test_near_duplicate_detection():
    assert builder.is_near_duplicate(
        "Vacinas causam autismo em crianças.",
        "vacinas causam autismo nas crianças",
        jaccard=0.6,
        ratio=0.8,
    )
    assert not builder.is_near_duplicate(
        "A vacina da febre amarela contém mercúrio.",
        "A vacina contra o sarampo deve ser tomada em duas doses.",
        jaccard=0.6,
        ratio=0.8,
    )


def test_selection_drops_evaluation_duplicates_and_conflicting_groups():
    report = builder.BuildReport()
    candidates = [
        _candidate("Vacinas contra covid causam infertilidade em mulheres", "REFUTED", key="1"),
        _candidate("A vacina contra o sarampo deve ser tomada em duas doses", "SUPPORTED", key="2"),
        _candidate("A vacina contra o sarampo deve ser tomada em 2 doses", "REFUTED", key="3"),
        _candidate("A vacina da febre amarela contém mercúrio demais", "REFUTED", key="4"),
        _candidate(
            "A vacina da febre amarela contém mercúrio demais!",
            "REFUTED",
            source="factckbr_extended",
            key="5",
            redistributable=False,
        ),
    ]
    selected = builder.select_candidates(
        candidates, ["Vacinas contra a covid causam infertilidade nas mulheres."], report
    )
    assert [item.source_key for item in selected] == ["4"]
    assert report.excluded["near_duplicate_of_existing_evaluation"] == 1
    assert report.excluded["near_duplicate_label_conflict"] == 2
    assert report.excluded["near_duplicate_internal"] == 1


def test_selection_excludes_political_speech_identified_by_review_url():
    report = builder.BuildReport()
    candidate = builder.Candidate(
        source="factckbr_extended",
        source_key="u",
        claim="Tínhamos impedimento, a vacina precisava passar pela Anvisa antes",
        source_label="Falso",
        verdict="REFUTED",
        agency="noticias.uol.com.br",
        claim_date=None,
        review_url="https://noticias.uol.com.br/2021/05/13/checagem-live-bolsonaro-pfizer.htm",
        redistributable=False,
    )
    assert builder.select_candidates([candidate], [], report) == []
    assert report.excluded["political_actor"] == 1


def test_supplement_sampling_is_deterministic_and_stratified():
    candidates = [
        _candidate(f"alegação {index}", label, key=str(index), redistributable=False)
        for index, label in enumerate(["REFUTED"] * 10 + ["MISLEADING"] * 6 + ["SUPPORTED"] * 2)
    ]
    first = builder.sample_supplement(candidates, room=9, report=builder.BuildReport())
    second = builder.sample_supplement(
        list(reversed(candidates)), room=9, report=builder.BuildReport()
    )
    assert {item.source_key for item in first} == {item.source_key for item in second}
    assert Counter(item.verdict for item in first) == {
        "SUPPORTED": 2,
        "MISLEADING": 3,
        "REFUTED": 4,
    }


def test_manifest_entry_omits_claim_text():
    item = builder.make_item(
        _candidate("A vacina da gripe causa gripe grave", "REFUTED", redistributable=False),
        "ext6s-0001",
        set(),
    )
    entry = builder.manifest_entry(item)
    assert "claim" not in entry and "notes" not in entry
    assert entry["claim_sha256"] == hashlib.sha256(item["claim"].encode()).hexdigest()


def test_topic_coverage_heuristic():
    tags = {"covid19", "hpv"}
    assert builder.corpus_topic_coverage("Vacina da Pfizer altera DNA", tags) == "covered"
    assert builder.corpus_topic_coverage("Vacina contra hantavírus", tags) == "not_covered"
    assert builder.corpus_topic_coverage("Vacinas matam", tags) == "generic_vaccination"


def test_frozen_items_follow_end_to_end_schema():
    items = load_end_to_end_items(EXTERNAL / "items.jsonl")
    assert items
    assert all(item.split is DatasetSplit.TEST for item in items)
    assert all(item.status is DatasetStatus.DRAFT for item in items)
    assert {item.label.value for item in items} <= {"SUPPORTED", "REFUTED", "MISLEADING"}
    raw = _jsonl(EXTERNAL / "items.jsonl")
    assert {row["external_source"] for row in raw} <= {"xfact", "factckbr"}
    assert all(len(row["claim"]) <= builder.MAX_CLAIM_CHARS for row in raw)


def test_frozen_set_size_and_labels():
    items = _jsonl(EXTERNAL / "items.jsonl")
    manifest = _jsonl(EXTERNAL / "supplement_manifest.jsonl")
    assert 60 <= len(items) + len(manifest) <= builder.TARGET_TOTAL
    labels = Counter(row["label"] for row in [*items, *manifest])
    assert set(labels) == {"SUPPORTED", "REFUTED", "MISLEADING"}
    assert all("claim" not in row for row in manifest)
    ids = [row["item_id"] for row in [*items, *manifest]]
    assert len(ids) == len(set(ids))


def test_frozen_items_do_not_repeat_existing_evaluation_claims():
    existing = builder.collect_evaluation_claims(ROOT / "evaluation", exclude=EXTERNAL)
    assert len(existing) > 400
    for row in _jsonl(EXTERNAL / "items.jsonl"):
        assert not any(
            builder.is_near_duplicate(
                row["claim"],
                other,
                jaccard=builder.EVAL_JACCARD,
                ratio=builder.EVAL_RATIO,
            )
            for other in existing
        ), row["item_id"]


def test_corpus_catalog_has_no_fact_checker_sources():
    catalog = builder.load_catalog(ROOT / "corpus" / "catalog.csv")
    assert builder.fact_checker_hits(builder.corpus_urls(catalog, None)) == []
    assert builder.fact_checker_hits(["https://www.aosfatos.org/noticias/x"]) == [
        "https://www.aosfatos.org/noticias/x"
    ]


def test_freeze_hashes_match_versioned_files():
    freeze = json.loads((EXTERNAL / "freeze.json").read_text(encoding="utf-8"))
    for relative, expected in freeze["sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative


def test_reconstructed_supplement_matches_manifest_when_available():
    path = builder.SUPPLEMENT_PATH
    if not path.is_file():
        pytest.skip("Suplemento não reconstruído localmente (fonte sem redistribuição).")
    freeze = json.loads((EXTERNAL / "freeze.json").read_text(encoding="utf-8"))
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest() == freeze["reconstructed_supplement_sha256"]
    )
    rows = _jsonl(path)
    manifest = _jsonl(EXTERNAL / "supplement_manifest.jsonl")
    assert [row["item_id"] for row in rows] == [row["item_id"] for row in manifest]
    for row, entry in zip(rows, manifest, strict=True):
        assert builder.claim_sha256(row["claim"]) == entry["claim_sha256"]
