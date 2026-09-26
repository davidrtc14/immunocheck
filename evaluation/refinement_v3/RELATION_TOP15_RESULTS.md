# Resultado — candidata relacional v3, denso top 15

Execução exploratória concluída em 26/09/2026 no código e plano congelados pelo
commit `4facf84`. Foram reutilizados os 48 itens de calibração e os resultados densos
já registrados; teste final e holdout permaneceram fechados.

## Resultado principal

| Métrica | v1 densa + auditor | v3 relacional top 15 |
|---|---:|---:|
| Macro-F1 | 0,430 | 0,469 |
| Balanced accuracy | 0,458 | 0,521 |
| Recall `SUPPORTED` | 0,583 | 0,500 |
| Recall `REFUTED` | 0,583 | 0,000 |
| Recall `MISLEADING` | 0,000 | 0,833 |
| Recall `INSUFFICIENT_EVIDENCE` | 0,667 | 0,750 |
| Precisão de abstenção | 0,286 | 0,692 |
| Citação relevante | 0,500 | 0,556 |
| Falha técnica | 0,000 | 0,000 |
| P95 | 12,41 s | 12,28 s |

A candidata reconheceu 10/12 casos `MISLEADING` e 9/12 casos insuficientes, mas não
reconheceu corretamente nenhum dos 12 casos `REFUTED`: dez foram chamados de
`MISLEADING` e dois receberam abstenção. O mecanismo que preserva verdade parcial
passou a tratar contradições simples como se sempre contivessem uma premissa válida.

O delta de macro-F1 foi +0,039, abaixo do gate de +0,08. O intervalo percentil de
95% por família foi de −0,081 a +0,175 e inclui regressão.

## Gates

| Gate | Resultado | Limite | Estado |
|---|---:|---:|---|
| Delta de macro-F1 | +0,039 | ≥ 0,08 | Falhou |
| Recall `MISLEADING` | 0,833 | ≥ 0,40 | Passou |
| Precisão de abstenção | 0,692 | ≥ 0,45 | Passou |
| Citação relevante | 0,556 | ≥ 0,60 | Falhou |
| Maior queda de recall | 0,583 | ≤ 0,05 | Falhou |
| Falha técnica | 0,000 | ≤ 0,02 | Passou |
| P95 textual | 12,28 s | ≤ 20 s | Passou |

Quatro dos sete gates passaram. A condição não é promovida e não autoriza criar ou
abrir holdout.

## Rastreabilidade e próximo diagnóstico

- plano: SHA-256
  `1de78e03e0163649371a1e65e0b6df465f500a612250f5cbd1c816331e69572a`;
- checkpoint: SHA-256
  `0fc34bdaee6cfa845e351c2b7b35c7263a5bdfebc5e84dd5775aa77d7436e60e`;
- relatório JSON: SHA-256
  `e2c338c6fe69bbddb29231320728a6125777a44fea3afd6c37b098a94c6eaca2`;
- modelo: `qwen3:8b`, local, temperatura 0, semente 42;
- inferências do teste final e do holdout: zero.

O experimento demonstra complementaridade, não superioridade isolada: a decisão
direta anterior preserva `SUPPORTED` e `REFUTED`, enquanto a decisão relacional
preserva `MISLEADING` e abstenção. A próxima hipótese deve rotear por forma da
alegação antes da decisão, em vez de forçar um único prompt a resolver todos os
tipos. Qualquer desempenho nessa mesma calibração continuará exploratório e exigirá
confirmação em dados novos.
