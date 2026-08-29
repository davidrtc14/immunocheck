from immunocheck.domain.models import Evidence
from immunocheck.retrieval.bm25 import BM25Index
from immunocheck.retrieval.tokenizer import tokenize_portuguese


def evidence(chunk_id: str, text: str) -> Evidence:
    return Evidence(
        chunk_id=chunk_id,
        text=text,
        source_name="Fonte oficial",
        document_title="Documento",
        url="https://example.gov.br/documento",
    )


def test_tokenizer_normalizes_case_and_accents() -> None:
    assert tokenize_portuguese("VACINAÇÃO contra HPV") == ["vacinacao", "contra", "hpv"]


def test_bm25_returns_lexically_matching_evidence_first() -> None:
    index = BM25Index(
        (
            evidence("influenza", "A vacina influenza utiliza vírus inativado."),
            evidence("hpv", "A vacinação contra HPV previne infecções persistentes."),
            evidence("sarampo", "A tríplice viral protege contra o sarampo."),
        )
    )

    results = index.search("HPV", top_k=2)

    assert results[0].chunk_id == "hpv"
    assert results[0].retrieval_score is not None
    assert all(result.chunk_id != "sarampo" for result in results)


def test_bm25_returns_empty_when_there_is_no_lexical_overlap() -> None:
    index = BM25Index((evidence("hpv", "Vacinação contra HPV."),))

    assert index.search("astronomia quasar") == ()
