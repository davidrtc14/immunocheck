"""D4/D5: caminho dedicado a MISLEADING e resiliência a saídas inválidas do LLM (v4 opt-in)."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from immunocheck.application.abstention import SignalRecorder
from immunocheck.application.ports import VerdictGenerator
from immunocheck.application.text_components import ModelOutputError, StructuredChatClient
from immunocheck.domain.models import DraftVerdict, Evidence, ExtractedClaim, Verdict

TECHNICAL_ABSTENTION = (
    "A análise automática não produziu uma resposta válida para esta alegação, "
    "então o sistema se abstém de concluir."
)

# Exemplos ilustrativos e inventados (tétano); não derivam de nenhum item de avaliação.
FEW_SHOT_BLOCK = """

Exemplos ilustrativos do formato e do critério (não os repita; use apenas os trechos recebidos):

Exemplo 1. Alegação: "A vacina contra tétano gera memória imunológica, então uma única dose protege
pelo resto da vida." Trechos: [E1] "A vacina induz memória imunológica contra a toxina tetânica."
[E2] "Após o esquema primário, recomenda-se reforço a cada 10 anos, pois a proteção diminui com o
tempo." Análise correta: claim_scope GENERAL, specific_event_investigated false, premise_supported
true, material_overstatement true, relation PARTIAL_WITH_DISTORTION, source_refs ["E1","E2"],
correct_fact null, omitted_or_distorted "Omite que a proteção diminui e exige reforço a cada 10
anos." (a parte verdadeira existe, mas a conclusão generaliza o alcance).

Exemplo 2. Alegação: "A vacina contra tétano deve ser aplicada somente uma vez na vida." Trecho:
[E1] "Após o esquema primário, recomenda-se reforço a cada 10 anos." Análise correta: premise_supported
false, material_overstatement false, relation CONTRADICTED, source_refs ["E1"], correct_fact
"Recomenda-se reforço a cada 10 anos." (não há parte verdadeira que gere a distorção).

Exemplo 3. Alegação: "Recomenda-se reforço da vacina contra tétano a cada 10 anos." Trecho: [E1]
"Após o esquema primário, recomenda-se reforço a cada 10 anos." Análise correta: relation SUPPORTED,
premise_supported true, material_overstatement false, campos corretivos null.

Marque PARTIAL_WITH_DISTORTION apenas quando os trechos sustentarem uma parte real da alegação e
a conclusão da alegação for mais ampla, mais certa ou diferente do que eles permitem."""


@dataclass(frozen=True, slots=True)
class PromptAugmentingClient:
    """Acrescenta texto ao prompt de sistema sem editar os geradores congelados da v3."""

    delegate: StructuredChatClient
    extra: str

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        max_output_tokens: int,
    ) -> dict[str, Any]:
        return self.delegate.chat(
            system_prompt=system_prompt + self.extra,
            user_prompt=user_prompt,
            schema=schema,
            max_output_tokens=max_output_tokens,
        )


@dataclass(frozen=True, slots=True)
class CombinedVerdictGenerator:
    """Direto decide; o relacional só pode converter uma conclusão em MISLEADING.

    A v3 enviava alegações sem molde explícito "premissa → conclusão" ao gerador direto,
    que raramente produz MISLEADING. A abstenção do direto nunca é revertida.
    """

    direct: VerdictGenerator
    relation: VerdictGenerator

    def generate(self, claim: ExtractedClaim, evidence: Sequence[Evidence]) -> DraftVerdict:
        direct = self.direct.generate(claim, evidence)
        if direct.verdict is Verdict.INSUFFICIENT_EVIDENCE:
            return direct
        relational = self.relation.generate(claim, evidence)
        if relational.verdict is Verdict.MISLEADING and relational.source_ids:
            return relational
        return direct


@dataclass(frozen=True, slots=True)
class ResilientVerdictGenerator:
    """Transforma saída inválida do LLM em abstenção explícita, contada pelo experimento."""

    delegate: VerdictGenerator
    recorder: SignalRecorder

    def generate(self, claim: ExtractedClaim, evidence: Sequence[Evidence]) -> DraftVerdict:
        try:
            return self.delegate.generate(claim, evidence)
        except ModelOutputError:
            self.recorder._state.technical_abstention = True
            return DraftVerdict(Verdict.INSUFFICIENT_EVIDENCE, TECHNICAL_ABSTENTION, ())


def describe_few_shot() -> str:
    """Resumo auditável do bloco few-shot para os artefatos do experimento."""
    return json.dumps({"examples": 3, "characters": len(FEW_SHOT_BLOCK), "topic": "tetano"})
