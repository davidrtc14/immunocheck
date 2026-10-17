# Resultados da Fase 18: correção da v5 e confirmação em teste externo (17/10/2026)

Execução única de cada condição, com código congelado (`freeze.json`, commit `c42d783`), na ordem
do protocolo: 96 itens v4 em três formas (288 entradas) para `v5_fixed` e `v5_fixed_qwen36`, e 150
itens externos (12 `SUPPORTED`, 53 `MISLEADING`, 85 `REFUTED`) para as quatro condições.
Artefatos: `results/final/*_run1.jsonl` e `results/final/analysis.json`
(`scripts/analyze_v6.py --phase final`). Nos registros externos, o rastro dos 96 itens do suplemento
sem licença de redistribuição não traz a alegação canônica nem as proposições (`text_redacted`); a
análise não usa esses campos e dá resultado idêntico aos registros completos, que ficam só na
máquina local. Regra: `PROTOCOL.md`, seção "Regra de decisão", com o
Adendo 1.

## Decisão

**Nenhuma condição foi promovida; a v3 continua padrão.** A `v5_fixed` passa nos cinco critérios do
v4, mas reprova no teste externo em X3 (queda de cobertura de 0,147, acima de 0,10) e em X1 (limite
inferior do IC da precisão das conclusões em −0,083, abaixo de −0,08). A `v5_fixed_qwen36` passa em
X1, mas reprova em X3 e no critério 5 do v4.

### Teste externo (contra a v3)

| Condição | Precisão das conclusões | Erro grave | Cobertura | Falhas | P95 | X1 | X2 | X3 | X4 |
|---|---|---|---|---|---|---|---|---|---|
| v3 (padrão) | 0,861 | 5,8% (8/138) | 0,527 | 2 | 17,3 s | — | — | — | — |
| v5_multiquery | 0,875 | 2,9% (4/138) | 0,373 | 0 | 13,7 s | ❌ | ✅ | ❌ | ✅ |
| v5_fixed | 0,877 | 2,9% (4/138) | 0,380 | 0 | 13,7 s | ❌ | ✅ | ❌ | ✅ |
| v5_fixed_qwen36 | **0,898** | **2,2% (3/138)** | 0,393 | 0 | 25,3 s | ✅ | ✅ | ❌ | ✅ |

Diferenças contra a v3 com IC 95% (bootstrap por item, 10.000 reamostras):

| Condição | Δ precisão | Δ erro grave | Δ cobertura |
|---|---|---|---|
| v5_multiquery | +0,014 (−0,086 a +0,115) | −0,029 (−0,075 a +0,015) | −0,153 (−0,247 a −0,060) |
| v5_fixed | +0,016 (−0,083 a +0,116) | −0,029 (−0,075 a +0,015) | −0,147 (−0,240 a −0,053) |
| v5_fixed_qwen36 | +0,038 (−0,059 a +0,133) | −0,036 (−0,080 a +0,007) | −0,133 (−0,233 a −0,033) |

`v5_multiquery` não podia ser promovida por regra (Adendo 1) e entra só como comparação.

### Conjunto v4 (exploratório; critério 3 descritivo pelo Adendo 1)

| Condição | Macro-F1 original | Δ vs v3 (IC por família) | Consistência | Recall S / R / M / I | Precisão da abstenção | Falhas (original) | P95 | Critérios 1, 2, 4, 5, 6 |
|---|---|---|---|---|---|---|---|---|
| v3 | 0,490 | — | 0,635 | 1,00 / 0,79 / 0,08 / 0,33 | 0,73 | 2 | 18,3 s | — |
| v5_multiquery (Fase 16) | 0,653 | +0,162 (+0,037 a +0,275) | 0,656 | 0,88 / 0,83 / 0,29 / 0,71 | 0,61 | 0 | 14,8 s | — |
| v5_fixed | 0,637 | +0,146 (+0,020 a +0,256) | 0,646 | 0,83 / 0,88 / 0,25 / 0,71 | 0,59 | 2 | 14,9 s | ✅ ✅ ✅ ✅ ✅ |
| v5_fixed_qwen36 | **0,716** | **+0,226 (+0,061 a +0,369)** | **0,760** | 0,71 / 0,88 / 0,46 / 0,83 | 0,63 | 3 | 27,2 s | ✅ ✅ ✅ ❌ ✅ |

Critério 3 (descritivo): a queda de recall de `SUPPORTED` passa de 0,10 nas duas condições (0,17 e
0,29).

## Leitura

- **A v5 erra menos quando conclui, mas conclui menos.** No teste externo, as variantes v5 cortam o
  erro grave pela metade (de 5,8% para 2,9%, e 2,2% com o `qwen3.6`) e têm precisão das conclusões
  igual ou maior que a v3, mas se abstêm em 61% a 63% dos itens, contra 47% da v3. A regra
  registrada pedia as duas coisas ao mesmo tempo, e a queda de cobertura passou do limite em todas.
  As diferenças de precisão e de erro grave têm IC que inclui zero: com 150 itens, o teste externo não
  separa as condições nessas métricas.
- **As correções tolerantes quase não mudam o comportamento.** Contra a `v5_multiquery`, a
  `v5_fixed` mudou 1 veredito no teste externo e, no v4, os rebaixamentos ficaram em 11 casos
  (6 por trecho e 5 por número). A perda de recall de `SUPPORTED` no v4 não veio dessas regras: os
  três casos de ref4-0078 caíram por falha técnica (ver abaixo).
- **O `qwen3.6` como juiz é o melhor resultado de veredito do projeto,** com macro-F1 de 0,716 no v4
  e consistência de 0,760 entre formas, e a melhor precisão e o menor erro grave no externo. O custo é
  latência (P95 de 25 a 27 s, contra 14 a 15 s) e menos recall de `SUPPORTED` no v4 (0,71).
- **O teste externo é difícil para todas as condições.** O recall de `SUPPORTED` foi 0,25 em todas
  (3 de 12), e boa parte das alegações externas cai fora do que o corpus cobre: até a v3 se abstém em
  quase metade.

## Defeito encontrado depois do congelamento

Todas as falhas técnicas das condições `v5_fixed` são `ValueError` da regra tolerante de números:
5 entradas na `v5_fixed` e 7 na `v5_fixed_qwen36` no v4 (ref4-0078 nas três formas, ref4-0085
coloquial, ref4-0096 e, só no `qwen3.6`, ref4-0047 formal e ref4-0063), nenhuma no teste externo. A
expressão do número aceitava quebra de linha como separador de milhar, e uma tabela da evidência
("50\n100\n150…") virava um único número inválido. O defeito foi encontrado ao investigar as falhas,
depois da execução final; as execuções **não** foram repetidas.

Efeito na decisão: nenhum. Sem o defeito, a `v5_fixed` continuaria aprovada no v4 e reprovada no
externo, onde não houve falhas; a `v5_fixed_qwen36` provavelmente passaria no critério 5 (as três
falhas da forma original são do defeito), mas continuaria reprovada em X3. A correção entrou depois
(ver histórico da ADR-051), com teste, e não muda os números acima.

## Ameaças à validade

- **Não determinismo entre dias:** na mesma configuração, a alegação canônica da v5 mudou em 23 das
  288 entradas v4 em relação à execução da Fase 16 (as duas execuções da Fase 16, no mesmo dia, foram
  idênticas). Parte das diferenças entre a `v5_fixed` e a `v5_multiquery` no v4 vem disso, e não das
  regras. Por isso a calibração usou uma referência rodada no mesmo dia.
- O v4 já tinha sido revelado: os números do v4 são exploratórios.
- O teste externo tem 150 itens, só 12 `SUPPORTED`, e rótulos de agências mapeados para três
  classes; 96 itens são reconstruídos localmente a partir de URL e hash, sem redistribuição.
- A cobertura temática do corpus sobre o teste externo é parcial; o estrato `covered` (103 itens)
  tem resultados semelhantes ao geral.

## Próximos passos possíveis (fora desta fase)

- Investigar por que a v5 se abstém mais no teste externo (recuperação ou rebaixamento) antes de
  qualquer nova regra; a precisão alta sugere que o ganho possível está na cobertura.
- Considerar o `qwen3.6` como juiz numa linha futura, com uma regra que pese o erro grave contra a
  cobertura de forma explícita.
