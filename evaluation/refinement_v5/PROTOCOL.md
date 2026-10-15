# Protocolo v5 — decomposição da alegação, NLI por proposição e agregação determinística

Registrado em 14/10/2026, **antes de qualquer inferência da v5** (ADR-049). Linha experimental
**exploratória**: não há conjunto novo e lacrado; o holdout v4 já foi revelado (ADR-048) e seus
erros foram lidos na análise que motivou este desenho. Nenhum resultado desta linha pode ser
apresentado como confirmação.

## Motivação (diagnóstico sobre artefatos já versionados)

Erros da v3 em `results/calibration_v3_plain.jsonl` e `results/holdout_v3_plain.jsonl` (42 de 96):

1. `MISLEADING` → `REFUTED`/`SUPPORTED` (cerca de 20): o roteador depende do molde
   "premissa → então → conclusão"; 47/48 alegações de calibração foram para `GENERAL_SIMPLE`.
2. `INSUFFICIENT_EVIDENCE` fora do corpus → `REFUTED` (cerca de 11): evidência de sujeito vizinho
   (outro país, produto ou desfecho) tratada como contradição.
3. Evento individual não detectado (cerca de 6).

O retrieval não é o gargalo dominante neste benchmark: doc_hit@15 = 0,94 e chunk_hit@15 = 0,89
na calibração (`results/retrieval_ablation_calibration.json`); vários erros citaram o trecho-ouro.

## Hipótese

Decompor a alegação em proposições com papel, tipo e escopo, julgar cada proposição contra a
evidência (com verificação determinística de escopo e de trecho literal) e agregar por regra
explícita reduz os três padrões acima e torna o veredito mais estável sob paráfrase.

## Desenho da v5 (`PIPELINE_VERSION=v5`, opt-in)

1. **Extração estruturada** (LLM, think desligado): `in_scope`, `canonical_claim`,
   `claim_kind` (`GENERAL` | `INDIVIDUAL_EVENT`), proposições (1–3) com `role`
   (`CORE` | `PREMISE` | `CONCLUSION`) e `type` (`FACT` | `CAUSAL` | `UNIVERSAL` | `NORMATIVE`),
   consulta em inglês. Exemplos few-shot genéricos, escritos sem consultar os itens v4.
2. **Atalho determinístico:** `INDIVIDUAL_EVENT` → `INSUFFICIENT_EVIDENCE`.
3. **Retrieval:** denso BGE-M3 sobre a alegação canônica (condição base) ou fusão RRF de
   alegação canônica + cada proposição + consulta EN (`+multiquery`); reranker opcional
   (`+reranker`).
4. **NLI conjunto por proposição** (LLM): `scope_match` (sujeito, população, produto, lugar,
   período), `relation` (`ENTAILED` | `CONTRADICTED` | `NOT_ADDRESSED`), trecho literal e referência.
   Pós-regras determinísticas: relação conclusiva sem trecho literal verificável no chunk citado
   → `NOT_ADDRESSED`; `CONTRADICTED` com algum `scope_match` falso → `NOT_ADDRESSED`.
5. **Agregação determinística:**
   - uma proposição: `ENTAILED` → `SUPPORTED`; `CONTRADICTED` → `REFUTED`; senão `INSUFFICIENT`;
   - todas `ENTAILED` → `SUPPORTED`;
   - alguma `CORE`/`PREMISE` `ENTAILED` e alguma `CONCLUSION` `CONTRADICTED` → `MISLEADING`;
   - alguma `CORE`/`PREMISE` `ENTAILED` e alguma `CONCLUSION` dos tipos `CAUSAL`/`UNIVERSAL`/
     `NORMATIVE` `NOT_ADDRESSED` → `MISLEADING`;
   - alguma `CORE`/`PREMISE` `ENTAILED` e alguma outra `CORE`/`PREMISE` `CONTRADICTED` → `MISLEADING`;
   - alguma proposição `CONTRADICTED` e nenhuma `ENTAILED` → `REFUTED`;
   - demais casos → `INSUFFICIENT_EVIDENCE`.
6. **Explicação** curta gerada pelo LLM a partir das proposições e trechos verificados;
   `correct_fact`/`omitted_or_distorted` vêm dos trechos verificados; citações = chunks dos
   trechos verificados (metadados do corpus). Guarda de orientação individual (ADR-044) ao final.
7. Uma nova tentativa em `ModelOutputError` por chamada.

## Dados

- Calibração: 48 itens `split=development` de `evaluation/refinement_v4/items.jsonl`.
- Avaliação final: os 96 itens v4 (calibração + holdout já revelado).
- Paráfrases (`paraphrases.jsonl`): duas variantes por item (coloquial e formal), rótulo herdado,
  redigidas com apoio de IA e revisadas pelo pesquisador para preservar o fato-alvo.
- **Desenvolvimento iterativo (prompts, few-shot) somente na calibração e nas suas paráfrases.**
  Antes da execução final, prompts e código são congelados por hash em `freeze.json`.

## Condições da ablação final (execução única, temperatura 0, seed 42)

`v3` | `v5_base` | `v5_multiquery` | `v5_multiquery_reranker` | `v5_multiquery_think`.
Condições com reranker/think só entram se o P95 medido na calibração for ≤ 45 s; a exclusão
será registrada.

## Métricas

- Primárias: macro-F1 em 4 classes nos 96 itens; Δ contra a v3 com IC 95% por bootstrap pareado
  por família (2.000 reamostragens, `evaluation/ablation.py`).
- Consistência sob paráfrase: fração de itens com o mesmo veredito nas três formas
  (original, coloquial, formal); macro-F1 por forma.
- Recall por classe, precisão das conclusões, recall/precisão de abstenção, falhas técnicas,
  latência mediana e P95.
- Secundária: macro-F1 em 3 classes, com `REFUTED` + `MISLEADING` agrupados como "não sustentada",
  para separar erro de raciocínio de ambiguidade de fronteira.

## Regra de decisão

A melhor condição v5 só passa a padrão do bot se, nos 96 itens, todas as condições valerem:

1. Δ macro-F1 vs. v3 ≥ +0,05 e limite inferior do IC por família > 0;
2. consistência sob paráfrase ≥ a da v3;
3. nenhuma queda > 0,10 no recall de `SUPPORTED` ou `REFUTED`;
4. precisão de abstenção ≥ 0,50;
5. falhas técnicas ≤ 2 (em 96);
6. P95 ≤ 45 s.

Caso contrário a v5 fica opt-in e o resultado é relatado como negativo ou exploratório.
A escolha da "melhor condição" é feita pelo maior macro-F1 entre as que satisfazem 3–6.

## Ameaças à validade declaradas

Holdout revelado; benchmark sintético; curadoria sem revisor externo; paráfrases geradas com
apoio de IA; 24 famílias (IC largos); uma execução por condição; possível viés do desenho
para os padrões de erro observados.

## Adendo 1 (14/10/2026, antes das inferências de avaliação)

No teste de fumaça com uma alegação sintética fora do conjunto, a mesma entrada produziu vereditos
diferentes em duas execuções seguidas (temperatura 0, seed 42), o que indica não determinismo do
Ollama entre chamadas. Por isso acrescenta-se uma métrica descritiva, sem gate:

- **Estabilidade entre execuções:** fração de itens com o mesmo veredito em duas execuções da mesma
  condição e da mesma entrada. Para a v3, compara-se a nova execução das formas originais com os
  registros v4 já versionados (`calibration_v3_plain`, `holdout_v3_plain`). Para a melhor condição
  v5, a fase final inclui uma segunda execução (`--tag run2`) das formas originais.

Executor: `scripts/run_v5_experiment.py`. A linha de base da v3 (288 entradas) roda na fase `dev`
porque a v3 está congelada e não é ajustada.

## Adendo 2 (14/10/2026): mudanças da iteração na calibração

Três iterações de `v5_multiquery`, somente no split de calibração (48 itens + 96 paráfrases).
Artefatos: `results/dev/v5_multiquery_development_iter{1,2,3}.jsonl`.

| Iteração | Mudança | Macro-F1 (original) | Consistência |
|---|---|---|---|
| iter1 | desenho registrado | 0,377 | 0,688 |
| iter2 | `scope_match` (5 booleanos) → `scope_conflict` (conflito nomeado); prompt de extração passa a preferir uma única proposição | 0,583 | 0,604 |
| iter3 | **remoção da pós-regra de escopo** (acertou 1 e errou 15 de 16 rebaixamentos na iter2); números verificados contra toda a evidência recuperada, e não só contra o trecho citado; extração obrigada a cobrir a alegação inteira; NLI instruído sobre proposições absolutas | 0,688 | 0,729 |

Desvio declarado: a pós-regra "CONTRADICTED com escopo divergente → NOT_ADDRESSED", descrita no
desenho original, foi removida por evidência da calibração. A distinção de escopo permanece como
instrução do NLI. As regras de agregação não mudaram. A partir daqui, prompts e código ficam
congelados para a execução final (`freeze.json`).
