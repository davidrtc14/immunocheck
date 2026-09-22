# Auditoria de erros no desenvolvimento v2

## Escopo e integridade metodológica

Esta auditoria usa exclusivamente os 96 itens de desenvolvimento e as saídas já
registradas da iteração v2. As previsões e métricas do teste não são carregadas nem
usadas para escolher alterações. O resultado identifica gargalos observáveis e prepara uma nova
linha experimental com dados independentes.

## Resultado executivo

- Condição analisada: `dense_with_auditor`.
- Acurácia: 0.562 (54/96).
- Erros: 42.
- Latência mediana: 9046 ms; P95: 11314 ms.

## Atribuição primária

Cada item recebe uma única categoria diagnóstica. `extraction_integrity_risk`
pode incluir uma decisão final correta, mas cuja alegação extraída perdeu conteúdo
relevante; por isso, a soma das demais categorias não equivale necessariamente ao
total de erros de classificação.

| Categoria | Itens | Proporção |
|---|---:|---:|
| `auditor_regression` | 19 | 19.8% |
| `classification_error_with_relevant_evidence` | 3 | 3.1% |
| `correct` | 50 | 52.1% |
| `evidence_grounding_miss` | 2 | 2.1% |
| `extraction_integrity_risk` | 6 | 6.2% |
| `false_conclusion_on_insufficient_evidence` | 7 | 7.3% |
| `over_abstention_with_evidence` | 5 | 5.2% |
| `over_abstention_without_evidence` | 3 | 3.1% |
| `technical_failure` | 1 | 1.0% |

## Erros por classe de referência

| Classe | Erros | Total | Taxa de erro |
|---|---:|---:|---:|
| `INSUFFICIENT_EVIDENCE` | 9 | 24 | 37.5% |
| `MISLEADING` | 16 | 19 | 84.2% |
| `REFUTED` | 7 | 29 | 24.1% |
| `SUPPORTED` | 10 | 24 | 41.7% |

## Evidência e decisão

- Itens conclusivos: 72.
- Citação com interseção na evidência anotada: 39.
- Acurácia quando há interseção: 59.0%.
- Acurácia quando não há interseção: 48.5%.

## Extração

- Extração idêntica à alegação original: 75.
- Recall lexical abaixo de 0,8: 6.
- Perda de marcador material: 0.
- Recall lexical médio: 0.967.

## Efeito do auditor

- `auditor_recovery`: 12.
- `auditor_regression`: 19.
- `changed_still_wrong`: 8.
- `unchanged_correct`: 42.
- `unchanged_wrong`: 15.

## Decisão para a próxima iteração

A iteração seguinte não será calibrada nos 96 itens antigos. Será criado um novo
conjunto de calibração com famílias inéditas, acompanhado de um holdout independente.
A primeira hipótese a testar é separar suficiência da evidência, classificação do
conteúdo e fidelidade da explicação, evitando que o auditor transforme discordância de
rótulo em abstenção automática.

## Limitações

- Citação sem interseção com a evidência anotada não distingue falha de retrieval de falha de seleção ou citação do gerador.
- A atribuição é diagnóstica e usa somente a iteração v2 do desenvolvimento já encerrado.
- Nenhum resultado desta auditoria autoriza ajuste adicional nos 96 itens antigos ou reabertura do teste congelado.
