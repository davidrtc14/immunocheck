# Resultado — decisão direta densa top 6

Execução concluída em 26/09/2026 no plano e código congelados pelo commit
`2d63a77`. Foram reutilizadas integralmente as extrações e os seis chunks da fase A;
as 48 novas chamadas foram feitas apenas ao gerador direto de quatro classes. Teste
v1 e holdout v2 permaneceram fechados.

## Resultado principal

| Métrica | v1 denso + auditor | Direto top 6 sem auditor |
|---|---:|---:|
| Macro-F1 | 0,430 | 0,472 |
| Balanced accuracy | 0,458 | 0,521 |
| Recall `SUPPORTED` | 0,583 | 0,917 |
| Recall `REFUTED` | 0,583 | 0,833 |
| Recall `MISLEADING` | 0,000 | 0,250 |
| Recall `INSUFFICIENT_EVIDENCE` | 0,667 | 0,083 |
| Precisão de abstenção | 0,286 | 0,500 |
| Citação relevante | 0,500 | 0,472 |
| Falha técnica | 0,000 | 0,000 |
| Latência mediana | 9,17 s | 7,51 s |
| P95 | 12,41 s | 10,12 s |

A candidata produziu 12 `SUPPORTED`, 27 `REFUTED`, sete `MISLEADING` e apenas duas
abstenções. Acertou 11/12 sustentadas, 10/12 refutadas e 3/12 enganosas, mas somente
1/12 casos de evidência insuficiente. O ganho de sensibilidade conclusiva veio,
portanto, acompanhado de conclusões indevidas em 11 dos 12 casos que exigiam
abstenção.

O delta de macro-F1 contra a baseline foi +0,042, abaixo do mínimo de +0,08. O
bootstrap pareado por família teve intervalo percentil de 95% de −0,090 a +0,190,
incluindo tanto regressão quanto ganho.

## Gates pré-registrados

| Gate | Resultado | Limite | Estado |
|---|---:|---:|---|
| Delta de macro-F1 | +0,042 | ≥ 0,08 | Falhou |
| Recall `MISLEADING` | 0,250 | ≥ 0,40 | Falhou |
| Precisão de abstenção | 0,500 | ≥ 0,45 | Passou |
| Citação relevante | 0,472 | ≥ 0,60 | Falhou |
| Maior queda de recall | 0,583 | ≤ 0,05 | Falhou |
| Falha técnica | 0,000 | ≤ 0,02 | Passou |
| P95 textual | 10,12 s | ≤ 20 s | Passou |

Três dos sete gates passaram. A condição não é promovida e não autoriza criar o
holdout v2.

## Rastreabilidade e interpretação

- plano: SHA-256
  `26846d6e48f8dcd801ab52913c8818187dc78c02d74c67c6e9142428b8219cb9`;
- checkpoint: SHA-256
  `ec69fcef4dab7d81373f3829b09cfe748be4911bbe4bcbad47a3aa52dbf3cc42`;
- relatório JSON: SHA-256
  `686c5124da2bf1a7b6724850ee3eb32b68432f9ad09a839b6aef04335b3f09ad`;
- modelo: `qwen3:8b`, local, temperatura 0, semente 42;
- inferências do teste v1 e do holdout v2: zero.

Os extremos estão agora medidos: o gate separado abstém demais, enquanto a decisão
direta abstém de menos. A próxima hipótese tecnicamente justificável deve calibrar
a suficiência entre esses extremos, sem alterar novamente retrieval ou simplesmente
remover guardrails. Isso exige um desenho novo e pré-registrado; combinar resultados
por inspeção item a item configuraria sobreajuste.
