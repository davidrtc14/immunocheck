# Registro de desenvolvimento da v7 (ADR-054)

Cada versão testada no split de desenvolvimento do C7 (193 itens, 43 famílias) fica registrada aqui,
na ordem em que foi rodada, como pede o Adendo 1 do protocolo. Os registros brutos ficam em
`output/v7_runs/dev/` (fora do Git). As métricas vêm de `scripts/analyze_v7.py`. O Δ e o IC são
contra a configuração acumulada, com bootstrap pareado por família e 10.000 reamostras.

Legenda de recall: S / R / M / I = `SUPPORTED` / `REFUTED` / `MISLEADING` / `INSUFFICIENT_EVIDENCE`.

## 18/10 — Linhas de base

| Condição | Macro-F1 | Recall S / R / M / I | Erro grave | Falhas | P95 |
|---|---:|---|---:|---:|---:|
| v3 | 0,703 | 0,86 / 0,78 / 0,58 / 0,60 | 10,4% | 3,6% (`ModelOutputError`) | 17,7 s |
| `v5_fixed` | 0,656 | 0,76 / 0,74 / 0,31 / 0,88 | 6,3% | 0 | 15,1 s |

`v5_fixed` − v3: Δ macro-F1 = −0,047 (IC −0,114 a +0,025). 74 vereditos mudam entre as duas.

**Leitura:**
- **A v3 vence a `v5_fixed` no C7,** ao contrário do que aconteceu no v4. A v5 abstém bem nos relatos
  (34 de 36, contra 23 de 36 da v3), mas perde `MISLEADING` (15 de 48, contra 28 de 48).
- **Onde a v5 erra:** nos itens do corpus, o chunk de origem está entre as evidências recuperadas em
  94 de 151. Quando está, os 26 `MISLEADING` recebem do juiz 25 `CONTRADICTED`, 13 `ENTAILED` e 15
  `NOT_ADDRESSED` (contagem por proposição). Ou seja, o erro é de enquadramento, e é o alvo da C1.
- **Recuperação também limita:** 57 de 151 itens do corpus não recuperam o chunk de origem. Nenhuma
  das candidatas registradas trata disso diretamente.
- **Consequência para a regra:** a seleção progressiva parte da `v5_fixed`, como registrado. Para
  passar no critério P1 do teste (Δ ≥ +0,05 contra a v3), as candidatas precisam somar cerca de
  +0,10 de macro-F1 sobre a `v5_fixed`.

**Conferência:** a `v7` sem candidatas reproduziu a `v5_fixed` em 12 de 12 itens, com mesmos
vereditos e mesmos julgamentos.
