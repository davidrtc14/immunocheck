# Resultados do holdout v4 (execução única, 13/10/2026)

Protocolo, gates e congelamento (hashes e commit) registrados antes da inferência em
`HOLDOUT_PROTOCOL.md` e `holdout_freeze.json`. 48 itens, 12 famílias, uma execução por condição
(temperatura 0, semente 42). Artefatos: `results/holdout_v3_plain.jsonl`,
`results/holdout_v4_candidate.jsonl`, `results/holdout_analysis.json`.

## Resultado

| Condição | Macro-F1 | Recall S / R / M / I | Precisão das conclusões | Citação relevante | Falhas | P95 |
|---|---|---|---|---|---|---|
| v3 (linha de base) | **0,577** | 0,92 / 0,83 / 0,33 / 0,33 | 0,595 | 0,694 | 1 | 17,1 s |
| v4 candidata (v3 + D1) | 0,487 | 0,92 / 0,67 / 0,08 / 0,50 | 0,541 | 0,639 | 0 | 22,7 s |

Δ macro-F1 (candidata − v3) = **−0,089** (IC 95% por família −0,194 a +0,008).

## Gates

| Gate | Resultado |
|---|---|
| 1. Macro-F1 absoluto ≥ 0,45 | passou (0,487) |
| 2. Ganho sobre a v3 ≥ +0,05 | **falhou** (−0,089) |
| 3. Abstenção: recall ≥ 0,50 e precisão ≥ 0,50 | passou (0,50 e 0,545) |
| 4. Precisão das conclusões ≥ v3 | **falhou** (0,541 < 0,595) |
| 5. Queda de recall de S e R ≤ 0,10 | **falhou** (R: 0,83 → 0,67) |
| 6. Falhas técnicas ≤ 2 | passou (0) |
| 7. P95 ≤ 45 s | passou (22,7 s) |
| 8. Citação relevante ≥ 0,50 e ≥ v3 − 0,05 | **falhou** (0,639 < 0,644) |

**4 de 8 gates falharam; a candidata v4 não é promovida. A v3 permanece como padrão.**

## Leitura

- A ancoragem D1, que na calibração elevou o macro-F1 em +0,09, não se repetiu no holdout:
  houve piora (−0,09), com IC que quase exclui o zero. O ganho da calibração foi, portanto,
  em parte otimismo de seleção.
- D1 aumentou a abstenção (recall 0,33 → 0,50) como projetado, mas ao custo de converter
  conclusões corretas em abstenção (`REFUTED` 0,83 → 0,67) e de perder `MISLEADING` (4/12 → 1/12).
- Na v3, o recall de `MISLEADING` foi 0,33 no holdout e 0,00 na calibração: instável com 12
  itens por classe; as duas medidas estão abaixo do 0,625 do confirmatório de 32 itens.
- A v3 caiu de macro-F1 0,846 (confirmatório, 32 itens com moldes) para 0,577 aqui e 0,450 na
  calibração do mesmo conjunto v4. O conjunto v4, mais variado em redação, indica que a
  estimativa anterior era otimista.

## Limitações

Curadoria sem revisor externo nem segunda anotação; 48 itens e 12 famílias (intervalos largos);
conjunto sintético; uma execução por condição; itens de `MISLEADING` e abstenção sensíveis à
redação.
