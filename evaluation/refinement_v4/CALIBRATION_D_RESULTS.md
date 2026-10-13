# Resultados da calibração D1 + D2 (13/10/2026)

Execução única de cada condição nos 48 itens de calibração v4 (temperatura 0, semente 42),
conforme `CALIBRATION_D_PLAN.md`, registrado e commitado antes das inferências. Artefatos:
`results/calibration_v3_plain.jsonl`, `results/calibration_v4_grounded.jsonl`,
`results/calibration_d_analysis.json`. O holdout não foi tocado.

## Desempenho

| Condição | Macro-F1 | Recall S / R / M / I | Precisão das conclusões | Falhas | P95 |
|---|---|---|---|---|---|
| `v3_plain` | 0,450 | 1,00 / 0,75 / **0,00** / 0,33 | 0,500 (42 conclusões) | 1/48 | 16,8 s |
| `v4_grounded` (D1) | 0,542 | 0,92 / 0,83 / **0,00** / 0,75 | 0,618 (34 conclusões) | 1/48 | 19,9 s |

- D1 − v3: ΔMacro-F1 = **+0,092** (IC 95% por família **+0,026 a +0,171**).
- A v3 obteve 0,846 no confirmatório de 32 itens, mas 0,450 neste conjunto maior e menos
  moldado. A queda indica que o resultado anterior superestimava a robustez da v3.
- `MISLEADING` teve recall zero nas duas condições: as alegações do v4 não têm o molde
  "premissa → conclusão" e o roteador as envia ao gerador direto, que as classifica como
  `SUPPORTED`/`REFUTED`. Isso confirma que D4 (e D5, roteamento) são o gargalo real.

## Decisão pelos critérios pré-registrados

- **D1 não adotada.** Passou macro-F1 não inferior e ganho de precisão/macro-F1, mas falhou o
  terceiro critério: falhas técnicas ≤ 2% (observado 1/48 = 2,08%). A única falha é o item
  `ref4-0069` (`ModelOutputError` do código congelado da v3), idêntica na condição `v3_plain`;
  portanto não foi causada por D1. Pela regra escrita, o critério reprova por um item.
- **D2 adotada, com fraqueza.** Na base `v3_plain`, a validação cruzada por família deu
  macro-F1 0,480 contra 0,450 sem limiar: Δ = +0,0301, que atinge o critério (≥ 0,03) por
  0,0001, e o IC por família (−0,055 a +0,120) inclui zero. O limiar selecionado é
  `min_margin = 0,0024` (praticamente desprezível). Sobre a base `v4_grounded` D2 não ajuda
  (Δ aninhado = −0,016). Limiares gravados em `thresholds.json` (`base_condition: v3_plain`).

## Interpretação

O ganho de D1 é a evidência mais forte desta fase (IC favorável), mas a regra pré-registrada o
reprova por uma falha técnica compartilhada com a linha de base. Alterar o critério agora seria
mudar a regra depois de ver os dados; por isso a v4 permanece **sem** D1 por padrão
(`thresholds.json` indica a base; `PIPELINE_VERSION=v4` usa a v3 + D2). Uma emenda explícita,
datada, que leve D1 à confirmação no holdout (onde os gates da Fase F decidem a promoção) é
uma decisão do pesquisador, não do agente.

## Limitações

48 itens e 12 famílias: intervalos largos. Curadoria sem revisor externo. Limiares ajustados nos
mesmos itens (mitigado por validação cruzada por família). Uma execução por condição.
