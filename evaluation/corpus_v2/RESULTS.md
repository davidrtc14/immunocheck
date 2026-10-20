# Resultados da Fase 21 — corpus v2 (ADR-056)

Execução única em 20/10/2026, com o código, o corpus v2 (`sha256:77b65faa…`, 89 documentos e 7.845
trechos), o executor, a análise e o protocolo congelados em `freeze.json`, conferido antes e depois da
execução, junto com o congelamento da Fase 20. Condição: a C6 (padrão v7) com o corpus v2, comparada
com a C6 com o corpus v1 da execução única da Fase 20, sem reexecução. A regra é a de `PROTOCOL.md`,
aplicada por `scripts/analyze_corpus_v2.py`; o resumo numérico está em `results.json`. Os registros
por item ficam fora do Git, em `output/corpus_v2_runs/`.

## Decisão

**O corpus v2 não foi adotado.** Ele reprovou no E1 (ganho de cobertura de +0,010, com IC 95% de
−0,013 a +0,033, abaixo dos +0,03 exigidos) e passou nos demais critérios. Pela regra, o corpus v1
(`sha256:d6cb49e7…`, 80 documentos) continua padrão do bot; os artefatos do v2 ficam guardados
localmente em `corpus/processed_v2/`, fora do Git.

## Teste externo 2 (304 alegações reais)

| Corpus | Precisão das conclusões | Erro grave | Cobertura | Falhas | P95 |
|---|---:|---:|---:|---:|---:|
| v1 | 0,991 | 0,3% (1) | 35,2% | 0,3% | 17,0 s |
| v2 | 0,991 | 0,3% (1) | 36,2% | 0,3% | 16,7 s |

Bootstrap pareado por item (10.000 reamostras, semente 42): cobertura +0,010 (−0,013 a +0,033);
precisão +0,000 (−0,000 a +0,002); erro grave 0,000.

As três conclusões novas vieram todas de alegações com tema coberto pelo corpus (`covered`: de 60 para
63 de 158); as de vacinação genérica ficaram em 43 de 136. Os documentos novos foram usados: 83 das
343 fontes citadas e 42 das respostas citaram o lote 009, mas quase sempre em alegações que o corpus v1
já concluía.

## Teste do C7 (207 itens)

| Corpus | Macro-F1 | Erro grave | Recall S / R / M / I | Falhas | P95 |
|---|---:|---:|---|---:|---:|
| v1 | 0,720 | 0,6% | 0,63 / 0,83 / 0,67 / 0,74 | 1,0% | 26,5 s |
| v2 | 0,710 | 0,6% | 0,63 / 0,83 / 0,63 / 0,74 | 1,0% | 26,8 s |

Bootstrap pareado por família: Δ macro-F1 −0,010 (−0,033 a +0,010), dentro do ruído de execução
medido na Fase 20; Δ erro grave 0,000. Seis vereditos mudaram: duas enganosas passaram a refutadas,
duas insuficientes antes refutadas voltaram a insuficientes e duas insuficientes viraram conclusivas
(uma enganosa, uma refutada). O lote 009 apareceu em 4 respostas.

| Critério | Resultado |
|---|:---:|
| E1: cobertura Δ ≥ +0,03 e IC > 0 | ❌ (+0,010) |
| E2: precisão, limite inferior do IC ≥ −0,05 | ✅ |
| E3: erro grave Δ ≤ +0,01 | ✅ |
| K1: macro-F1, limite inferior do IC ≥ −0,05 | ✅ |
| K2: erro grave Δ ≤ +0,02 | ✅ |
| O1: P95 ≤ 45 s e falhas dentro do limite | ✅ |

## Interpretação

A hipótese da fase era que a baixa cobertura em alegações reais vinha de lacunas temáticas do corpus.
O resultado não a sustenta: nove documentos sobre os temas que faltavam entraram nas respostas, mas
mudaram pouco a decisão de concluir. As abstenções nas alegações reais parecem depender mais da forma
das alegações (vagas, genéricas ou sobre eventos e pessoas específicas que nenhum documento oficial
trata) e do critério conservador da pipeline do que da ausência do tema no corpus. Investigar essa
causa por análise de erros fica como trabalho futuro.

## Limitações

- **Reuso dos conjuntos:** os dois conjuntos já tinham sido usados na Fase 20; a seleção dos documentos
  foi cega aos itens, mas os agregados eram conhecidos.
- **Lote pequeno:** nove documentos (260 trechos, 3,4% do corpus); um lote maior poderia ter outro
  efeito, que esta execução não mede.
- **Gabarito do C7 derivado do corpus v1:** trocas a partir de `INSUFFICIENT_EVIDENCE` podem refletir
  evidência nova real, e não erro.
- **Campo `section`:** o construtor passou a preencher a seção de 1.899 trechos antigos; o campo só
  aparece na exibição das fontes e não entra nos prompts nem nos embeddings, e os textos e vetores do
  v1 continuaram idênticos.
