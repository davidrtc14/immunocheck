# Resultado — roteamento estrutural v3

Execução exploratória concluída em 26/09/2026 no plano congelado pelo commit
`ed9fe2d`. O roteador realizou 48 chamadas locais sobre a forma das alegações e
reutilizou as saídas já registradas dos dois especialistas. Teste final e holdout
permaneceram fechados.

## Resultado principal

| Métrica | v1 densa + auditor | v3 roteada |
|---|---:|---:|
| Macro-F1 | 0,430 | 0,725 |
| Balanced accuracy | 0,458 | 0,729 |
| Recall `SUPPORTED` | 0,583 | 0,917 |
| Recall `REFUTED` | 0,583 | 0,833 |
| Recall `MISLEADING` | 0,000 | 0,417 |
| Recall `INSUFFICIENT_EVIDENCE` | 0,667 | 0,750 |
| Precisão de abstenção | 0,286 | 0,750 |
| Citação relevante | 0,500 | 0,444 |
| Falha técnica | 0,000 | 0,000 |
| P95 | 12,41 s | 13,26 s |

O delta de macro-F1 foi +0,295. O intervalo percentil de 95% por família foi de
+0,165 a +0,469, inteiramente acima de zero. A matriz de confusão registrou 11/12
`SUPPORTED`, 10/12 `REFUTED`, 5/12 `MISLEADING` e 9/12 abstenções corretas.

## Gates

| Gate | Resultado | Limite | Estado |
|---|---:|---:|---|
| Delta de macro-F1 | +0,295 | ≥ 0,08 | Passou |
| Recall `MISLEADING` | 0,417 | ≥ 0,40 | Passou |
| Precisão de abstenção | 0,750 | ≥ 0,45 | Passou |
| Citação relevante | 0,444 | ≥ 0,60 | Falhou |
| Maior queda de recall | −0,083 | ≤ 0,05 | Passou |
| Falha técnica | 0,000 | ≤ 0,02 | Passou |
| P95 textual | 13,26 s | ≤ 20 s | Passou |

Seis dos sete gates passaram. A candidata não é promovida porque qualidade de
citação é requisito substantivo, não acabamento de interface.

## Rastreabilidade e próximo passo

- plano: SHA-256
  `2260dc0d7ed9f97ed4165d2905374f2c4a6d23afc4606e4ee19782d725542cd5`;
- checkpoint: SHA-256
  `08932ba351535e472a5ba3d109f026e884b6448a6c7fe7f4f1821055e34099c6`;
- relatório JSON: SHA-256
  `cfb1e0e547f5c1f4490128f27348f6fa9f36052b37b6f8eca7d70ff8af4866f9`;
- modelo: `qwen3:8b`, local, temperatura 0, semente 42;
- inferências do teste final e do holdout: zero.

O próximo experimento pode alterar somente a seleção de citações, preservando
integralmente os 48 vereditos. Como o top 15 contém evidência anotada em 25/36 casos
conclusivos, o teto observado é 0,694. Um seletor precisa atingir ao menos 22/36 e
manter P95 abaixo de 20 s. O resultado continuará exploratório até confirmação em
dados novos.
