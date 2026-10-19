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

## 19/10 — C1, versão 3 (`PARTIAL` sem exagero literal vira abstenção)

| Condição | Macro-F1 | Recall S / R / M / I | Erro grave | Falhas | P95 |
|---|---:|---|---:|---:|---:|
| `v7+C1` v3 | 0,684 | 0,86 / 0,57 / 0,50 / 0,86 | 8,3% | 0 | 16,0 s |

Δ contra a `v5_fixed`: +0,028 (IC −0,014 a +0,075); Δ do erro grave: +0,0208 (12 de 144 itens não
`SUPPORTED`, contra 9 de 144). Passa no macro-F1, mas o erro grave excede o limite de +0,02 por um
item: reprovada pela regra. Contra a v3: −0,019 (IC −0,093 a +0,059).

**A hipótese da versão 2 estava errada.** Com o novo campo do trace, só 1 `PARTIAL` foi rejeitado por
falta de exagero literal (18 foram verificados). As negações que viram `SUPPORTED` vêm do próprio juiz,
que escolhe `ENTAILED` para "a dose única não protegeu contra a doença" ou "não disponibiliza todas as
vacinas" citando um trecho que afirma o contrário, apesar da instrução nova no prompt. A `v5_fixed`
julga esses itens `CONTRADICTED`; o prompt de enquadramento da C1 piora a atenção à negação.

**Mudança para a versão 4:** uma trava em código substitui a confiança no prompt. Se a proposição e o
trecho citado divergem na presença de negação ("não", "nenhum", "nunca", "jamais" e, para trechos em
inglês, "not", "never", "none", "cannot", "n't"), `ENTAILED` e `PARTIAL` viram `NOT_ADDRESSED`. Sem
saber o que a negação nega, o código não inverte para `CONTRADICTED`; só abstém. O trace passa a
guardar o trecho citado, para que análises futuras não dependam de reexecutar o modelo.

## 19/10 — C1, versão 4 (trava de negação) e decisão da C1

| Condição | Macro-F1 | Recall S / R / M / I | Erro grave | Falhas | P95 |
|---|---:|---|---:|---:|---:|
| `v7+C1` v4 | 0,644 | 0,67 / 0,59 / 0,48 / 0,86 | 3,5% | 0 | 16,1 s |

Δ contra a `v5_fixed`: −0,011 (IC −0,059 a +0,038); Δ do erro grave: −0,028. Contra a v3: −0,059
(IC −0,126 a +0,012). Reprovada no macro-F1.

A trava resolveu o erro grave (o menor de todas as condições até aqui), mas disparou em 23 julgamentos
e derrubou o recall de `SUPPORTED` de 0,86 para 0,67: trechos com negação sustentam proposições
afirmativas ("não há associação com autismo" sustenta "a vacina é segura quanto ao autismo") e vice-versa,
e a comparação por presença de palavra não distingue esses casos.

**Decisão: C1 rejeitada.** Em quatro versões, cada ajuste trocou um tipo de erro por outro: o
`PARTIAL` sobe o recall de `MISLEADING` (de 0,31 para 0,48–0,52), mas desloca `REFUTED` e
`SUPPORTED`, e nenhuma versão passou nos dois critérios. Uma quinta versão ajustaria o juiz ao próprio
split de desenvolvimento. A configuração acumulada continua sendo a `v5_fixed`, e a seleção segue para
a C4, na ordem registrada.

## 19/10 — Nota: C1 v5 executada em paralelo, depois da rejeição

Por um erro de coordenação, duas sessões de trabalho rodaram a seleção ao mesmo tempo neste checkout.
Enquanto a entrada acima rejeitava a C1 na v4 e iniciava a C4, a outra sessão rodou uma quinta
versão (commit `fe7353d`, tag `c1v5`): o léxico de negação do inglês ("no", "non", "without", "nor")
passa a valer só para trechos detectados como inglês, porque os falsos alarmes da v4 vinham de trechos
como "no increased risk" e "non-Asian".

| Condição | Macro-F1 | Recall S / R / M / I | Erro grave | Falhas | P95 |
|---|---:|---|---:|---:|---:|
| `v7+C1` v5 | 0,658 | 0,73 / 0,59 / 0,48 / 0,86 | 4,2% | 0 | 27,0 s* |

Δ contra a `v5_fixed`: +0,002 (IC −0,038 a +0,046); Δ do erro grave: −0,021. Contra a v3: −0,045.
\* A execução dividiu a GPU com a C4 (tag `c4`) desde 15:27; a latência não é comparável.

**A rejeição da C1 se mantém.** A v5 também não passaria no critério de seleção, e ela não muda a
decisão nem a ordem da seleção; fica registrada por transparência, já que foi executada. Resumo das
cinco versões contra a `v5_fixed` (0,656; erro grave 6,3%):

| Versão | Macro-F1 | Δ | Erro grave | Recall de `MISLEADING` |
|---|---:|---:|---:|---:|
| v1 | 0,584 | −0,072 | 3,5% | 0,79 |
| v2 | 0,669 | +0,013 | 11,1% | 0,52 |
| v3 | 0,684 | +0,028 | 8,3% | 0,50 |
| v4 | 0,644 | −0,011 | 3,5% | 0,48 |
| v5 | 0,658 | +0,002 | 4,2% | 0,48 |

O mesmo compartilhamento de GPU vale para o início da C4 (tag `c4`): a latência dela entre 15:27 e
o fim da C1 v5 também está inflada.

## 19/10 — C4 (queda para a v3 quando a decomposição falha)

| Condição | Macro-F1 | Recall S / R / M / I | Erro grave | Falhas | P95 |
|---|---:|---|---:|---:|---:|
| `v7+C4` | 0,664 | 0,80 / 0,74 / 0,31 / 0,88 | 6,3% | 0 | 27,7 s* |

\* Dividiu a GPU com a C1 v5 durante parte da execução; a latência não é comparável.

A decomposição não falhou em nenhum dos 193 itens, então a queda para a v3 nunca foi acionada e a taxa
de falhas continuou em 0, como na `v5_fixed`. O critério da C4 é reduzir as falhas técnicas; sem falhas
para reduzir, **a C4 não entra**. A configuração acumulada continua sendo a `v5_fixed`. O mecanismo fica
no código e pode ser reavaliado se o teste externo 2 mostrar falhas de decomposição.

**Ruído de execução.** Como a C4 não agiu, esta execução equivale a repetir a `v5_fixed`: mesmo assim,
10 vereditos mudaram e o macro-F1 variou +0,008 (IC −0,018 a +0,034), com o mesmo erro grave. Essa é a
variação entre execuções do modelo local, e o limite de +0,02 da regra de seleção fica cerca de 2,5
vezes acima dela.

## 19/10 — C2 (chunks vizinhos como contexto do juiz)

| Condição | Macro-F1 | Recall S / R / M / I | Erro grave | Falhas | P95 |
|---|---:|---|---:|---:|---:|
| `v7+C2` | 0,664 | 0,71 / 0,72 / 0,35 / 0,93 | 4,9% | 0 | 16,1 s |

Δ contra a `v5_fixed`: +0,008 (IC −0,049 a +0,068); Δ do erro grave: −0,014. Contra a repetição da
`v5_fixed` (execução da C4): +0,000. **Não entra:** o ganho é do tamanho do ruído de execução e fica
abaixo de +0,02. Com mais texto, o juiz abstém mais (recall de `INSUFFICIENT_EVIDENCE` de 0,88 para
0,93) e sustenta menos (`SUPPORTED` de 0,76 para 0,71), sem recuperar `MISLEADING`.

## 19/10 — C3 (`qwen3.6` só no juiz): interrompida por latência

Os cinco primeiros itens levaram 33,9 s, 36,1 s, 43,7 s, 45,3 s e 49,3 s. O `qwen3.6` (23 GB, 76% em
CPU) não cabe na GPU com o `qwen3:8b`, e o Ollama troca de modelo a cada chamada do juiz, o que torna a
C3 mais lenta que o `qwen3.6` no pipeline todo, ao contrário do previsto. Com dois de cinco itens acima
de 45 s, o critério de P95 não tem como ser cumprido; a execução foi interrompida para não gastar duas
horas de GPU. O Adendo 2 do protocolo substitui a C3 pela C3b (`qwen3.6` no pipeline inteiro), antes de
qualquer contato com o teste.
