# Resultado — calibração v2.1, retrieval denso top 20

Execução concluída em 26/09/2026 no plano e código congelados pelo commit
`3439f60`. Foram reutilizadas as extrações dos 48 itens adjudicados; nenhuma nova
chamada de extração foi feita e nenhum item do teste v1 ou do holdout v2 foi
carregado.

## Resultado principal

| Métrica | v1 denso + auditor | v2 top 6 | v2.1 top 20 |
|---|---:|---:|---:|
| Macro-F1 | 0,430 | 0,373 | 0,376 |
| Balanced accuracy | 0,458 | 0,458 | 0,396 |
| Recall `SUPPORTED` | 0,583 | 0,750 | 0,583 |
| Recall `REFUTED` | 0,583 | 0,083 | 0,417 |
| Recall `MISLEADING` | 0,000 | 0,000 | 0,000 |
| Recall `INSUFFICIENT_EVIDENCE` | 0,667 | 1,000 | 0,583 |
| Precisão de abstenção | 0,286 | 0,316 | 0,250 |
| Citação relevante | 0,500 | 0,500 | 0,139 |
| Falha técnica | 0,000 | 0,000 | 0,083 |
| Latência mediana | 9,17 s | 8,14 s | 12,16 s* |
| P95 | 12,41 s | 14,74 s | 17,98 s* |

\* Proxy pré-registrado: tempo compartilhado da fase A (extração + retrieval top
6) somado às novas chamadas de decisão. O retrieval top 20 foi medido à parte e
substitui, em vez de se somar, ao retrieval anterior.

A candidata top 20 produziu sete `SUPPORTED`, 12 `REFUTED`, um `MISLEADING` e 28
abstenções. O único `MISLEADING` previsto era, na referência, um caso de evidência
insuficiente; portanto, o recall correto da classe continuou em zero. Embora o
recall de `REFUTED` tenha subido de 0,083 para 0,417, a candidata perdeu acertos em
`SUPPORTED` e em evidência insuficiente. A balanced accuracy caiu de 0,458 para
0,396.

O ganho de macro-F1 sobre a candidata top 6 foi apenas +0,003. Contra a baseline
congelada, o delta foi −0,054 e o bootstrap pareado por família teve intervalo
percentil de 95% de −0,184 a +0,079. Não há evidência de melhora global.

## Falhas técnicas

Quatro itens (`ref2-cal-0002`, `0005`, `0007` e `0012`) falharam porque o gate de
suficiência devolveu um identificador que não pertencia aos 20 trechos fornecidos.
O guardrail rejeitou corretamente a saída e converteu o resultado em abstenção.
Isso indica que ampliar o prompt de seis para 20 trechos aumentou a dificuldade de
cópia fiel de IDs para o modelo local; não é falha do índice denso.

## Gates pré-registrados

| Gate | Resultado | Limite | Estado |
|---|---:|---:|---|
| Delta de macro-F1 | −0,054 | ≥ 0,08 | Falhou |
| Recall `MISLEADING` | 0,000 | ≥ 0,40 | Falhou |
| Precisão de abstenção | 0,250 | ≥ 0,45 | Falhou |
| Citação relevante | 0,139 | ≥ 0,60 | Falhou |
| Maior queda de recall | 0,167 | ≤ 0,05 | Falhou |
| Falha técnica | 0,083 | ≤ 0,02 | Falhou |
| P95 textual | 17,98 s | ≤ 20 s | Passou |

Somente um dos sete gates passou. A condição com auditor factual não é elegível,
não foi executada e a v2.1 top 20 não deve substituir a v1 nem a candidata top 6.

## Rastreabilidade e conclusão

- plano: SHA-256
  `55ce90da27f64ebe25716004467cd49afc2dddf84bf70f4dc75f489795a1fa3f`;
- snapshot adjudicado: SHA-256
  `9cd26e96b7d5ee35ddb32ebf7a36914b3349db81c3e21d4f4476cf4cf66e09f8`;
- checkpoint: SHA-256
  `8f196abcece368be644c835b41d0def0b9f618e7583bca4c82f1f0325ef7e0a1`;
- relatório JSON: SHA-256
  `f6e6ca293d947bfeea2c4c58e85b9c9522b96aa803ecb1d715114166037d708e`;
- modelo: `qwen3:8b`, local, temperatura 0, semente 42;
- inferências do teste v1 e do holdout v2: zero.

O experimento isola uma conclusão útil: maior cobertura bruta de retrieval não
resolve a decisão `MISLEADING` e, ao enviar 20 trechos diretamente ao gate, piora
seleção de citações e robustez estrutural. A próxima hipótese não deve aumentar
novamente `top_k`; deve reduzir e organizar o contexto entregue à LLM, mantendo a
recuperação ampla apenas como conjunto candidato.
