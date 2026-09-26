# Resultado — triagem do gate de suficiência v2

Execução concluída em 26/09/2026 no plano e código congelados pelo commit
`7802366`. Foram avaliados os 48 itens apenas pelo gate binário; não houve chamadas
ao classificador ou auditor, nem carregamento do teste v1 ou do holdout v2.

## Resultado

O gate v2 classificou **todos os 48 itens como suficientes**.

| Métrica | Gate original | Gate v2 |
|---|---:|---:|
| Recall de suficiência, 36 conclusivos | 0,278 | 1,000 |
| Recall de insuficiência, 12 abstentivos | 1,000 | 0,000 |
| Recall de suficiência em `MISLEADING` | 0,000 | 1,000 |
| Seleção de chunk anotado nos conclusivos | 0,500 | 0,500 |
| Falha técnica | 0,000 | 0,000 |
| Latência mediana do gate | — | 3,95 s |
| P95 do gate | — | 4,67 s |

Os aliases curtos eliminaram erros de referência, mas a instrução explícita para
extrapolações deslocou o gate ao extremo oposto: nenhuma entrada recebeu decisão
insuficiente. A seleção de chunks anotados também não melhorou.

## Gates pré-registrados

| Gate | Resultado | Limite | Estado |
|---|---:|---:|---|
| Recall de suficiência | 1,000 | ≥ 0,70 | Passou |
| Recall de insuficiência | 0,000 | ≥ 0,67 | Falhou |
| Suficiência em `MISLEADING` | 1,000 | ≥ 0,67 | Passou |
| Seleção de chunk anotado | 0,500 | ≥ 0,60 | Falhou |
| Falha técnica | 0,000 | ≤ 0,02 | Passou |
| P95 do gate | 4,67 s | ≤ 8 s | Passou |

Quatro dos seis gates passaram. Conforme o plano, nenhuma classificação fim a fim
foi executada e o gate v2 não foi promovido.

## Rastreabilidade e decisão

- plano: SHA-256
  `ac49ebe59f4ac9a8b0d2f9e673113567e60e079585a44d8c07c55a111e69db37`;
- checkpoint: SHA-256
  `4cfb055a657de64266667b833323eeed68066a100fea56c4a066bd1afb38c6ca`;
- relatório JSON: SHA-256
  `39cb02096589b121ddc0a2e04ff975f05c71c6b11dea547e01712417e7a3ecb3`;
- inferências do teste v1 e do holdout v2: zero.

Os dois gates testados delimitam extremos incompatíveis: o original aceita 10/36
casos conclusivos e preserva 12/12 abstenções; o v2 aceita 36/36 conclusivos e
preserva 0/12 abstenções. Uma nova alteração de redação orientada pelos mesmos 48
itens aumentaria o risco de sobreajuste. A decisão metodologicamente segura é não
promover nenhum deles e manter a v1 congelada enquanto os resultados negativos são
incorporados à documentação acadêmica.
