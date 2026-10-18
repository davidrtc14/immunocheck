from __future__ import annotations

from collections import Counter

import numpy as np

from immunocheck.evaluation.contrastive_set import (
    INSUFFICIENT,
    MISLEADING,
    ORIGIN_INDIVIDUAL,
    ORIGIN_OUTSIDE,
    REFUTED,
    SUPPORTED,
    Candidate,
    SourceChunk,
    assemble,
    copy_overlap,
    gate_corpus_payload,
    gate_individual_payload,
    gate_outside_payload,
    is_candidate_chunk,
    max_similarity,
    near_duplicates,
    quote_in_chunk,
    sample_chunks,
    split_documents,
)

CHUNK_TEXT = (
    "A vacina contra rotavírus foi incorporada ao calendário em 2006. Estudos de efetividade "
    "mostraram redução de 70% nas internações por diarreia em menores de 5 anos depois da "
    "introdução, com maior efeito nas regiões com cobertura vacinal acima de 80%. A proteção é "
    "maior contra formas graves da doença do que contra quadros leves, segundo a revisão."
)
SOURCE = SourceChunk("doc1:p1:c1", "doc1", CHUNK_TEXT, "eficacia")


def _payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "usable": True,
        "evidence_quote": "redução de 70% nas internações por diarreia em menores de 5 anos",
        "supported": "Depois que a vacina do rotavírus chegou, caíram uns 70% as internações "
        "de crianças pequenas por diarreia.",
        "refuted": "A vacina do rotavírus não mudou nada nas internações de crianças por diarreia.",
        "misleading": "A vacina do rotavírus acabou com a diarreia em todas as crianças do país.",
        "misleading_subtype": "overgeneralization",
        "sustained_part": "Houve redução de 70% nas internações.",
        "distortion": "Generaliza a redução para o fim da diarreia em todas as crianças.",
    }
    payload.update(overrides)
    return payload


def test_candidate_chunk_filter() -> None:
    assert is_candidate_chunk(CHUNK_TEXT)
    assert not is_candidate_chunk("Texto curto sobre vacina.")
    references = "\n".join(f"[{n}] Autor et al. Vaccine 2020;{n}:1-10." for n in range(1, 12))
    assert not is_candidate_chunk(references + " vacina" * 20)
    assert not is_candidate_chunk("Texto longo sobre futebol e clima. " * 20)


def test_sample_chunks_caps_per_document_and_is_deterministic() -> None:
    chunks = [
        SourceChunk(f"doc{d}:p1:c{i}", f"doc{d}", CHUNK_TEXT, "t")
        for d in range(3)
        for i in range(5)
    ]
    first = sample_chunks(chunks, per_document=2, seed=7)
    assert len(first) == 6
    assert Counter(chunk.document_id for chunk in first) == {"doc0": 2, "doc1": 2, "doc2": 2}
    assert first == sample_chunks(chunks, per_document=2, seed=7)


def test_copy_overlap_and_quote() -> None:
    assert copy_overlap(CHUNK_TEXT.split(". ")[1], CHUNK_TEXT) == 1.0
    assert copy_overlap("Caíram as internações de crianças pequenas.", CHUNK_TEXT) == 0.0
    assert quote_in_chunk("Reducao de 70%  nas internacoes por diarreia", CHUNK_TEXT)
    assert not quote_in_chunk("redução de 90% nas internações por diarreia", CHUNK_TEXT)
    assert not quote_in_chunk("70%", CHUNK_TEXT)


def test_corpus_payload_accepts_the_three_versions() -> None:
    report = gate_corpus_payload(_payload(), SOURCE)
    assert {candidate.label for candidate in report.accepted} == {SUPPORTED, REFUTED, MISLEADING}
    misleading = next(c for c in report.accepted if c.label == MISLEADING)
    assert misleading.subtype == "overgeneralization" and misleading.distortion


def test_corpus_payload_gates() -> None:
    assert gate_corpus_payload(_payload(usable=False), SOURCE).rejected["chunk_sem_fato"] == 1
    fake_quote = gate_corpus_payload(
        _payload(evidence_quote="frase que não existe no chunk"), SOURCE
    )
    assert fake_quote.rejected["trecho_inexistente"] == 1
    same = gate_corpus_payload(_payload(refuted=_payload()["supported"]), SOURCE)
    assert same.rejected["versoes_iguais"] == 1
    number = gate_corpus_payload(
        _payload(supported="A vacina do rotavírus derrubou em 95% as internações de crianças."),
        SOURCE,
    )
    assert number.rejected["numero_sem_fonte"] == 1
    assert SUPPORTED not in {c.label for c in number.accepted}
    copied = gate_corpus_payload(_payload(supported=CHUNK_TEXT[:150]), SOURCE)
    assert copied.rejected["copia_SUPPORTED"] == 1
    no_vaccine = gate_corpus_payload(
        _payload(refuted="As internações por diarreia de crianças não mudaram em nada."), SOURCE
    )
    assert no_vaccine.rejected["sem_vacina_REFUTED"] == 1
    subtype = gate_corpus_payload(_payload(misleading_subtype="exagero"), SOURCE)
    assert subtype.rejected["subtipo_invalido"] == 1


def test_outside_and_individual_payloads() -> None:
    outside = SourceChunk("ms_bcg#3", "ms_bcg", CHUNK_TEXT, "vacinas", ORIGIN_OUTSIDE)
    ok = gate_outside_payload(
        {
            "usable": True,
            "claim": "Depois da vacina do rotavírus, as internações por diarreia caíram uns 70%.",
            "evidence_quote": "redução de 70% nas internações por diarreia",
        },
        outside,
    )
    assert ok.accepted[0].label == INSUFFICIENT and ok.accepted[0].origin_type == ORIGIN_OUTSIDE
    assert not gate_outside_payload({"usable": True, "claim": "x"}, outside).accepted
    story = gate_individual_payload(
        {
            "claim": "Minha sobrinha tomou a vacina do rotavírus e no dia seguinte ficou com febre alta."
        },
        SOURCE,
    )
    assert story.accepted[0].origin_type == ORIGIN_INDIVIDUAL
    assert gate_individual_payload({"claim": "curto"}, SOURCE).rejected["relato_vazio"] == 1


def test_near_duplicates_and_max_similarity() -> None:
    vectors = np.array([[1, 0], [0.99, 0.01], [0, 1]], dtype=np.float32)
    assert near_duplicates(vectors, threshold=0.92) == {1}
    corpus = np.array([[1, 0], [0.6, 0.8]], dtype=np.float32)
    assert np.allclose(max_similarity(vectors[[0, 2]], corpus), [1.0, 0.8])


def test_split_documents_is_balanced_by_theme_and_deterministic() -> None:
    themes = {f"a{i}": "tema_a" for i in range(4)} | {f"b{i}": "tema_b" for i in range(3)}
    split = split_documents(themes, seed=1)
    assert split == split_documents(themes, seed=1)
    assert Counter(split[d] for d in themes if d.startswith("a")) == {"development": 2, "test": 2}
    assert abs(Counter(split.values())["development"] - Counter(split.values())["test"]) <= 1


def test_assemble_takes_one_item_per_chunk_and_balances_labels() -> None:
    candidates = []
    for index in range(12):
        source = SourceChunk(f"d:c{index}", "d", CHUNK_TEXT, "t")
        candidates += [
            Candidate(label, f"{label} {index}", source, "corpus_chunk")
            for label in (SUPPORTED, REFUTED, MISLEADING)
        ]
    selected = assemble(candidates, per_label=3, seed=3)
    assert len({c.source.chunk_id for c in selected}) == len(selected) == 9
    assert Counter(c.label for c in selected) == {SUPPORTED: 3, REFUTED: 3, MISLEADING: 3}
