# Resultado — citações hierárquicas v3

Execução exploratória concluída em 26/09/2026 no plano e código congelados pelo
commit `4a8f60b`. O estágio preservou os 48 vereditos da candidata roteada, não
executou auditor factual e não carregou teste final ou holdout.

## Resultado principal

| Métrica | v1 densa + auditor | v3 roteada + citações hierárquicas |
|---|---:|---:|
| Macro-F1 | 0,430 | 0,725 |
| Balanced accuracy | 0,458 | 0,729 |
| Recall `SUPPORTED` | 0,583 | 0,917 |
| Recall `REFUTED` | 0,583 | 0,833 |
| Recall `MISLEADING` | 0,000 | 0,417 |
| Recall `INSUFFICIENT_EVIDENCE` | 0,667 | 0,750 |
| Precisão de abstenção | 0,286 | 0,750 |
| Citação relevante por ID exato | 0,500 | 0,722 |
| Falha técnica | 0,000 | 0,000 |
| Latência mediana | 9,17 s | 14,40 s |
| P95 | 12,41 s | 18,72 s |

O delta de macro-F1 foi +0,295, com intervalo percentil de 95% por família entre
+0,165 e +0,469. A seleção hierárquica elevou a citação exata de 17/36 para 26/36,
sem alterar nenhum veredito.

## Gates

| Gate | Resultado | Limite | Estado |
|---|---:|---:|---|
| Delta de macro-F1 | +0,295 | ≥ 0,08 | Passou |
| Recall `MISLEADING` | 0,417 | ≥ 0,40 | Passou |
| Precisão de abstenção | 0,750 | ≥ 0,45 | Passou |
| Citação relevante | 0,722 | ≥ 0,60 | Passou |
| Maior queda de recall | −0,083 | ≤ 0,05 | Passou |
| Falha técnica | 0,000 | ≤ 0,02 | Passou |
| P95 textual | 18,72 s | ≤ 20 s | Passou |

Todos os sete gates de calibração foram satisfeitos. A candidata torna-se elegível
para congelamento e avaliação confirmatória em dados novos. Isso ainda não é
validação independente: a arquitetura foi motivada por erros observados nesta mesma
calibração e não deve ser promovida ao bot nem apresentada como desempenho final.

## Rastreabilidade

- plano: SHA-256
  `791e23db0c41469224c3bee324404666fa7348869f5a253e600f92ae8d8cb00c`;
- checkpoint: SHA-256
  `756c874be73294e1de6f7c9bc27ed4eae74b7eb5774c77638caf30fe246e56a8`;
- relatório JSON: SHA-256
  `df7db1f38b899c62ba0aad112063bf67a83e1254b46d87b043fc8e213d9e8012`;
- modelo: `qwen3:8b`, local, temperatura 0, semente 42;
- mudanças de veredito em relação à candidata roteada: zero;
- inferências do teste final e do holdout: zero.

O próximo passo obrigatório é congelar código, prompts, roteamento, expansão, corpus
e hashes antes de construir um conjunto confirmatório de famílias novas. O teste da
v1 permanece definitivamente fechado.
