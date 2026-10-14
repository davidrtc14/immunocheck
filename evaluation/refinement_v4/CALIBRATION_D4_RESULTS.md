# Resultados D4/D5 na calibração v4 (13/10/2026)

Execução única nos 48 itens de calibração, conforme `CALIBRATION_D4_PLAN.md` (registrado e
commitado antes da inferência). Artefatos: `results/calibration_v4_d4.jsonl`,
`results/calibration_d4_analysis.json`. Holdout intocado.

## Desempenho

| Condição | Macro-F1 | Recall S / R / M / I | Precisão das conclusões | P95 |
|---|---|---|---|---|
| `v4_grounded` | 0,542 | 0,92 / 0,83 / 0,00 / 0,75 | 0,618 | 19,9 s |
| `v4_d4` | 0,593 | 0,58 / 0,33 / **0,67** / 0,75 | 0,559 | 33,4 s |

Δ macro-F1 = +0,051 (IC 95% por família −0,092 a +0,170, inclui zero).

Matriz (esperado → previsto) de `v4_d4`: `MISLEADING` 8 corretos de 12; porém 7 dos 12
`REFUTED` e 4 dos 12 `SUPPORTED` foram convertidos em `MISLEADING`, e 3 abstenções esperadas
também. Houve 1 abstenção técnica (saída inválida tratada) e nenhuma exceção.

## Decisão pelos critérios pré-registrados

Falhou 1 de 6: precisão das conclusões 0,559 < 0,568 (piso = base − 0,05) por 0,009. Passaram:
recall de `MISLEADING` (0,67 ≥ 0,33), macro-F1 ≥ base + 0,03, recall de abstenção (0,75), ausência
de exceções e P95. **`v4_d4` não é adotada.**

Mesmo sem esse critério o resultado é ambíguo: o ganho de `MISLEADING` foi pago com a perda de
recall de `REFUTED` (0,83 → 0,33) e `SUPPORTED` (0,92 → 0,58). O gerador relacional, ao poder
converter qualquer conclusão em `MISLEADING`, sinaliza distorção em excesso.

## Diagnóstico de D5 (sem gate)

O roteador enviou 47 das 48 alegações a `GENERAL_SIMPLE`/`UNANCHORED_SPECIFIC_EVENT` e nenhuma a
`PREMISE_CONCLUSION`: as 11 de 12 alegações `MISLEADING` roteadas como simples confirmam a
hipótese de que o molde explícito não se aplica ao conjunto v4. Dos eventos individuais
esperados como abstenção, só 3 de 12 foram roteados como `UNANCHORED_SPECIFIC_EVENT`.

## Limitações

48 itens; curadoria sem revisor externo; uma execução; o diagnóstico usa os mesmos itens que
motivaram o desenho (risco de otimismo).
