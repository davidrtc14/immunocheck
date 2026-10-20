# Resultados da Fase 20 — veredito v7 e cascata C6 (ADR-054, ADR-055)

Execução única em 20/10/2026, de 08:39 a 12:46, com o código, os conjuntos e o protocolo congelados em
`verdict_freeze.json` (conferido antes de cada condição e de novo depois da última). As seis execuções
rodaram em sequência, sem dividir a GPU, com o `qwen3:8b` (`500a1f067a9f`). A regra aplicada é a dos
Adendos 1 e 3 de `PROTOCOL.md`, por `scripts/analyze_v7_final.py`; o resumo numérico está em
`results_final.json`. Os registros por item ficam fora do Git, em `output/v7_runs/final/`, porque os
traces contêm trechos do corpus e texto derivado das alegações das agências.

## Decisão

**A cascata C6 (v3 → `v5_fixed`) passa pela via de segurança (S1–S4 e X1–X4) e substitui a v3 como
padrão do veredito.** Ela não passa pela regra original: o P1 exigia Δ macro-F1 ≥ +0,05, e o ganho foi
de +0,043. A `v5_fixed` isolada era só comparação e reprovaria de qualquer forma (P1, P3 e X3).

## Teste do C7 (207 itens, 43 famílias)

| Condição | Macro-F1 | Recall S / R / M / I | Erro grave | Falhas | P95 |
|---|---:|---|---:|---:|---:|
| v3 | 0,677 | 0,76 / 0,80 / 0,65 / 0,52 | 11,5% | 1,0% | 18,3 s |
| `v5_fixed` | 0,683 | 0,71 / 0,76 / 0,40 / 0,88 | 3,2% | 0 | 15,0 s |
| **C6** | **0,720** | 0,63 / 0,83 / 0,67 / 0,74 | **0,6%** | 1,0% | 26,5 s |

Contra a v3, bootstrap pareado por família (10.000 reamostras, semente 42):

| Condição | Δ macro-F1 (IC 95%) | Δ erro grave (IC 95%) |
|---|---|---|
| `v5_fixed` | +0,006 (−0,071 a +0,082) | −0,083 (−0,143 a −0,027) |
| C6 | **+0,043 (+0,011 a +0,080)** | **−0,109 (−0,157 a −0,066)** |

| Critério | `v5_fixed` | C6 |
|---|:---:|:---:|
| P1: Δ macro-F1 ≥ +0,05 e IC > 0 | ❌ | ❌ (+0,043) |
| P2: erro grave ≤ v3 + 0,02 | ✅ | ✅ |
| P3: recall de `MISLEADING` ≥ v3 | ❌ | ✅ |
| P4: P95 ≤ 45 s e falhas ≤ max(2%, v3) | ✅ | ✅ |
| S1: Δ macro-F1 ≥ 0 e IC ≥ −0,05 | — | ✅ |
| S2: Δ erro grave ≤ −0,03 e IC < 0 | — | ✅ |
| S3: recall de `MISLEADING` ≥ v3 | — | ✅ |
| S4: P95 ≤ 45 s e falhas ≤ max(2%, v3) | — | ✅ |

A `v5_fixed` verificou 57 respostas `SUPPORTED` da v3 e trocou 24. Dezessete trocas eliminam um erro
grave da v3: 15 acertam o rótulo (13 `INSUFFICIENT_EVIDENCE`, 1 `REFUTED` e 1 `MISLEADING`) e 2
alegações refutadas passam a abstenção. As outras 7 derrubam alegações verdadeiras: 4 viram `REFUTED`
e 3 viram `INSUFFICIENT_EVIDENCE`. Mediana de 15,9 s por item.

## Teste externo 2 (304 alegações reais checadas por agências brasileiras)

| Condição | Precisão das conclusões | Erro grave | Cobertura | Falhas | P95 |
|---|---:|---:|---:|---:|---:|
| v3 | 0,940 | 2,3% (7) | 38,2% | 0,3% | 16,2 s |
| `v5_fixed` | 0,931 | 1,7% | 23,7% | 0 | 13,3 s |
| **C6** | **0,991** | **0,3% (1)** | 35,2% | 0,3% | 17,0 s |

Contra a v3, bootstrap pareado por item (10.000 reamostras, semente 42):

| Condição | Δ precisão (IC 95%) | Δ erro grave (IC 95%) | Δ cobertura (IC 95%) | X1 | X2 | X3 | X4 |
|---|---|---|---|:---:|:---:|:---:|:---:|
| `v5_fixed` | −0,009 (−0,072 a +0,051) | −0,007 (−0,026 a +0,010) | −0,145 (−0,201 a −0,089) | ✅ | ✅ | ❌ | ✅ |
| C6 | +0,051 (+0,016 a +0,095) | −0,020 (−0,036 a −0,007) | −0,030 (−0,056 a −0,003) | ✅ | ✅ | ✅ | ✅ |

O conjunto é quase todo de alegações falsas (283 `REFUTED`, 20 `MISLEADING`, 1 `SUPPORTED`). Só 6
respostas da v3 foram verificadas; 5 viraram `INSUFFICIENT_EVIDENCE`, todas de alegações refutadas.

## Limitações

- **A regra da cascata foi desenhada olhando o desenvolvimento** (Adendo 3). O teste confirmou o
  efeito, mas a via de segurança foi acrescentada depois de a seleção registrada falhar, por decisão
  do pesquisador e antes de qualquer contato com o teste. O TCC deve apresentar as duas vias.
- **O recall de `SUPPORTED` cai** de 0,76 para 0,63 no C7: a verificação derruba também alegações
  verdadeiras, e 4 delas viram `REFUTED`, o erro inverso do erro grave.
- **A latência sobe:** P95 de 26,5 s no C7, contra 18,3 s da v3, porque a `v5_fixed` roda em cerca de
  um quarto dos itens. Continua dentro do limite de 45 s.
- **O C7 é sintético,** gerado por um LLM e revisado com assistência de LLM; o teste externo 2 é real,
  mas quase só de alegações falsas, e cobre pouco o caso `SUPPORTED`.
- **A cobertura no teste externo 2 é baixa** (35%): a maioria das alegações reais fica sem conclusão,
  sobretudo por falta de evidência no corpus.
- **Ruído de execução:** repetições da mesma configuração no desenvolvimento mudaram cerca de 10
  vereditos em 193 (Δ macro-F1 de +0,008).

## Próximo passo

Integrar a C6 como padrão do bot (texto e imagem), sem editar os módulos congelados, com testes da
montagem multimodal e uma passada de fumaça no Telegram ou na CLI.
