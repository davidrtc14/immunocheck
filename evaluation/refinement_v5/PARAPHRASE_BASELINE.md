# Linha de base da v3 sob paráfrase (14/10/2026)

Execução única da v3 congelada (padrão do bot) sobre os 96 itens v4 em três formas: original,
paráfrase coloquial e paráfrase formal (`paraphrases.jsonl`, rótulo herdado). Temperatura 0,
seed 42. Artefatos: `results/dev/v3_all_run1.jsonl` e `results/dev/v3_baseline_analysis.json`.

| Forma | n | Macro-F1 | Macro-F1 (3 classes) | Recall S / R / M / I | Precisão/recall de abstenção | Falhas | P95 |
|---|---|---|---|---|---|---|---|
| Original | 96 | 0,490 | 0,660 | 1,00 / 0,79 / 0,08 / 0,33 | 0,73 / 0,33 | 2 | 18,3 s |
| Coloquial | 96 | 0,648 | 0,748 | 0,88 / 0,79 / 0,38 / 0,58 | 0,82 / 0,58 | 1 | 18,2 s |
| Formal | 96 | 0,569 | 0,712 | 0,96 / 0,83 / 0,21 / 0,42 | 0,83 / 0,42 | 0 | 17,8 s |

- **Consistência sob paráfrase: 0,635.** Em 35 dos 96 itens, a v3 dá vereditos diferentes para
  redações que expressam o mesmo fato. Essa é a medida direta da instabilidade relatada.
- **Estabilidade entre execuções: 0,948.** As formas originais repetiram o veredito dos registros
  v4 em 91 de 96 itens. O não determinismo do Ollama existe, mas pesa menos que a sensibilidade
  à redação.
- A forma original tem o pior desempenho. As alegações v4 foram reescritas de propósito para
  derrotar o baseline lexical (ADR-045), e essa redação menos natural parece prejudicar a v3.
- O padrão de erro se mantém nas três formas: `MISLEADING` vira `REFUTED`/`SUPPORTED` e as
  abstenções fora do corpus viram `REFUTED`. O macro-F1 em 3 classes (0,66–0,75) mostra que
  boa parte da perda está na fronteira `REFUTED`/`MISLEADING`.

Limitações: paráfrases redigidas com apoio de IA e ainda sem a conferência do pesquisador
(`PARAPHRASE_REVIEW.md`); uma execução; conjunto sintético.
