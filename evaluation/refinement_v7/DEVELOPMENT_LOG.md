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

## 18/10 — C1, versão 1 (relação `PARTIAL` livre)

| Condição | Macro-F1 | Recall S / R / M / I | Erro grave | Falhas | P95 |
|---|---:|---|---:|---:|---:|
| `v7+C1` v1 | 0,584 | 0,39 / 0,35 / 0,79 / 0,86 | 3,5% | 0 | 16,6 s |

Δ contra a `v5_fixed`: −0,072 (IC −0,131 a −0,014). Reprovada.

O recall de `MISLEADING` foi de 0,31 para 0,79, mas o juiz passou a usar `PARTIAL` como meio-termo:
26 `SUPPORTED` e 28 `REFUTED` viraram `MISLEADING`. Entre os `SUPPORTED`, havia paráfrases exatas,
como "recomendada pela OMS para meninas entre 9 e 13 anos".

**Mudança para a versão 2:**
- o juiz precisa copiar em `overreach` as palavras exatas da proposição que vão além do trecho; o
  código confere que elas estão na proposição e, se não estiverem, o `PARTIAL` vira `ENTAILED`;
- o prompt diz que paráfrase e arredondamento não impedem `ENTAILED`, que `PARTIAL` é raro, e que
  negar ou inverter o trecho é `CONTRADICTED`.

## 19/10 — C1, versão 2 (`overreach` literal; sem ele, `ENTAILED`)

| Condição | Macro-F1 | Recall S / R / M / I | Erro grave | Falhas | P95 |
|---|---:|---|---:|---:|---:|
| `v7+C1` v2 | 0,669 | 0,84 / 0,52 / 0,52 / 0,86 | 11,1% | 0 | 17,4 s |

Δ contra a `v5_fixed`: +0,013 (IC −0,037 a +0,066); Δ do erro grave: +0,049. Reprovada nos dois
critérios (mínimo de +0,02 no macro-F1; erro grave até +0,02). Contra a v3: −0,034.

O recall de `MISLEADING` subiu de 0,31 para 0,52 (o subtipo `false_implication` foi a 8 de 13), mas
o de `REFUTED` caiu de 0,74 para 0,52. O dano principal: 10 `REFUTED` saíram `SUPPORTED` (5 na
`v5_fixed`). Em 6 deles, a alegação é uma negação ("não reduziu a prevalência", "não protegeu contra
a doença") que a `v5_fixed` julgou `CONTRADICTED` e a v2 julgou `ENTAILED`. A hipótese mais provável
é a regra de queda da v2: o juiz marcou `PARTIAL` sem exagero literal válido e o código converteu em
`ENTAILED`. O trace não guardava o rótulo cru, então isso não pôde ser conferido.

**Mudança para a versão 3:**
- um `PARTIAL` sem `overreach` literal válido vira `NOT_ADDRESSED` (abstenção), não `ENTAILED`; o
  trace marca `overreach_rejected` para a conta poder ser feita;
- o prompt diz que uma proposição com negação que o trecho não tem (ou o contrário) nunca é
  `ENTAILED`.
