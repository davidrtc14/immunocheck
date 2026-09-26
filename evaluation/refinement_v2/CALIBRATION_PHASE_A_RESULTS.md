# Resultado — calibração v2, fase A

Execução concluída em 26/09/2026 no plano e código congelados pelo commit
`c0389e3`. Foram avaliados os 48 itens adjudicados, sem carregar o teste da v1 nem
criar ou abrir o holdout v2.

## Resultado principal

| Métrica | v1 denso + auditor | v2 separada sem auditor |
|---|---:|---:|
| Macro-F1 | 0,430 | 0,373 |
| Balanced accuracy | 0,458 | 0,458 |
| Recall `SUPPORTED` | 0,583 | 0,750 |
| Recall `REFUTED` | 0,583 | 0,083 |
| Recall `MISLEADING` | 0,000 | 0,000 |
| Recall `INSUFFICIENT_EVIDENCE` | 0,667 | 1,000 |
| Precisão de abstenção | 0,286 | 0,316 |
| Citação relevante | 0,500 | 0,500 |
| Falha técnica | 0,000 | 0,000 |
| Latência mediana | 9,17 s | 8,14 s |
| P95 | 12,41 s | 14,74 s |

A candidata produziu nove `SUPPORTED`, um `REFUTED`, nenhum `MISLEADING` e 38
abstenções. Ela recuperou quatro acertos adicionais entre os 12 casos insuficientes
e dois entre os sustentados, mas perdeu seis acertos `REFUTED` e não resolveu a
classe `MISLEADING`.

O delta pareado de macro-F1 foi −0,057. O bootstrap por família com 2.000
reamostragens resultou em intervalo percentil de 95% de −0,157 a +0,053; portanto,
não há evidência de ganho e a estimativa pontual é desfavorável.

## Gates pré-registrados

| Gate | Resultado | Limite | Estado |
|---|---:|---:|---|
| Delta de macro-F1 | −0,057 | ≥ 0,08 | Falhou |
| Recall `MISLEADING` | 0,000 | ≥ 0,40 | Falhou |
| Precisão de abstenção | 0,316 | ≥ 0,45 | Falhou |
| Citação relevante | 0,500 | ≥ 0,60 | Falhou |
| Maior queda de recall | 0,500 | ≤ 0,05 | Falhou |
| Falha técnica | 0,000 | ≤ 0,02 | Passou |
| P95 textual | 14,74 s | ≤ 20 s | Passou |

Como cinco dos sete gates falharam, a condição com auditor factual não é elegível e
não foi executada. A candidata não deve substituir a configuração congelada da v1.

## Rastreabilidade

- snapshot adjudicado: SHA-256
  `9cd26e96b7d5ee35ddb32ebf7a36914b3349db81c3e21d4f4476cf4cf66e09f8`;
- checkpoint: SHA-256
  `6735a67e361c3e83cace85610275221f658c98db52877c333fb5df8dc041ce6b`;
- relatório JSON: SHA-256
  `c047c2b5e0443e417ce6ede6668acbd5d4160421a5b994ac0aab9c90e8b2e3a3`;
- modelo: `qwen3:8b`, local, temperatura 0, semente 42;
- retrieval compartilhado: BGE-M3 denso, top 6;
- falhas técnicas: 0/48;
- inferências do teste v1 e do holdout v2: zero.

## Interpretação limitada

O novo gate de suficiência foi excessivamente conservador neste conjunto e bloqueou
quase toda a classe `REFUTED` e toda a classe `MISLEADING`. Isso não demonstra que a
separação conceitual seja inútil em geral; demonstra que esta implementação e estes
prompts não satisfazem os critérios do protótipo. Qualquer hipótese posterior deve
ser registrada como nova iteração e não pode reclassificar esta execução como
sucesso.

