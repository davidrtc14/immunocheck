from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import replace

from rank_bm25 import BM25Okapi

from immunocheck.domain.models import Evidence
from immunocheck.retrieval.tokenizer import tokenize_portuguese


class BM25Index:
    def __init__(
        self,
        evidence: Sequence[Evidence],
        *,
        tokenizer: Callable[[str], list[str]] = tokenize_portuguese,
    ) -> None:
        if not evidence:
            raise ValueError("O índice BM25 exige pelo menos uma evidência.")
        self._tokenizer = tokenizer
        # Chunks sem tokens (símbolos, tabelas) nunca casariam com uma consulta: ficam de fora.
        indexable = [(item, tokenizer(item.text)) for item in evidence]
        indexable = [(item, tokens) for item, tokens in indexable if tokens]
        if not indexable:
            raise ValueError("Nenhuma evidência contém tokens indexáveis.")
        self._evidence = tuple(item for item, _ in indexable)
        self._tokenized_corpus = tuple(tokens for _, tokens in indexable)
        self._index = BM25Okapi(self._tokenized_corpus)

    def search(self, query: str, *, top_k: int = 10) -> tuple[Evidence, ...]:
        if top_k <= 0:
            raise ValueError("top_k deve ser positivo.")
        query_tokens = self._tokenizer(query)
        if not query_tokens:
            return ()

        query_token_set = set(query_tokens)
        scores = self._index.get_scores(query_tokens)
        ranked = sorted(
            (
                (index, float(score))
                for index, score in enumerate(scores)
                if query_token_set.intersection(self._tokenized_corpus[index])
            ),
            key=lambda item: (-item[1], self._evidence[item[0]].chunk_id),
        )
        return tuple(
            replace(self._evidence[index], retrieval_score=score) for index, score in ranked[:top_k]
        )
