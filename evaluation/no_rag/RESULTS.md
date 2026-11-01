# Resultados: linha de base sem recuperação (ADR-058)

Execução única em 01/11/2026, conforme `PROTOCOL.md`: teste do C7 (207 itens) e teste externo 2
(304 itens), sem falhas técnicas. Números completos em `results.json`; registros por item em
`output/no_rag_runs/`, fora do Git. A v7 (C6) é a execução única de 20/10.

## Teste do C7 (4 classes, gerado do corpus)

| Condição | Macro-F1 | Erro grave | Recall S / R / M / I | P95 |
|---|---|---|---|---|
| v3 | 0,677 | 11,5% | 0,77 / 0,80 / 0,65 / 0,52 | 18,3 s |
| **v7** | **0,720** | **0,6%** | 0,63 / 0,83 / 0,67 / 0,74 | 26,5 s |
| Sem RAG | 0,477 | 7,1% | 0,67 / 0,96 / 0,19 / 0,26 | 3,6 s |

- **v7 − sem RAG:** macro-F1 +0,243 (IC 95% pareado por família: 0,176 a 0,311); erro grave
  −6,4 p.p. (IC: −11,1 a −2,3). Os dois intervalos excluem zero: contribuição detectada.
- Sem os trechos, o modelo quase não reconhece "enganosa" (10 de 52) e responde "refutada" a 41
  alegações enganosas e a 28 que o corpus não permite decidir. Ele raramente se abstém (15 de 207).
- Acurácia exata nas conclusões: v7 0,719 (146 conclusões), v3 0,671 (164), sem RAG 0,458 (192).

## Teste externo 2 (304 checagens reais; 283 refutadas, 20 enganosas, 1 sustentada)

| Condição | Precisão binária | Acurácia exata nas conclusões | Erro grave | Cobertura |
|---|---|---|---|---|
| v3 | 0,940 | 0,819 (116) | 2,3% | 38,2% |
| **v7** | **0,991** | 0,860 (107) | **0,3%** | 35,2% |
| Sem RAG | 0,983 | 0,907 (300) | 1,3% | 98,7% |
| Trivial "refutada" | 0,997 | 0,931 (304) | 0,0% | 100% |

- **v7 − sem RAG (bootstrap por item):** precisão +0,007 (IC: −0,018 a 0,030); erro grave
  −1,0 p.p. (IC: −2,6 a 0,3); cobertura −63,5 p.p. (IC: −69,1 a −57,6). Só a cobertura difere com
  segurança, e a favor do modelo sem RAG.
- O modelo sem RAG conhece os mitos vacinais mais divulgados e acerta 97,5% das refutadas que
  conclui, mas não acerta nenhuma das 20 enganosas: chama 19 de refutadas e 1 de sustentada.
- Nenhuma condição supera o classificador trivial em acurácia exata. O conjunto é tão
  desbalanceado que mede quase só se o sistema evita dar uma falsa como sustentada.

## Leitura

- A recuperação contribui onde a decisão depende do conteúdo das fontes: no C7, separar
  "enganosa" de "refutada", abster-se quando o corpus não decide e evitar erros graves. Ali o
  ganho é grande e o intervalo de confiança exclui zero.
- No teste externo 2, quase todo de mitos conhecidos, o conhecimento do próprio modelo basta para
  refutar e cobre muito mais alegações. A v7 se abstém em 65% dos casos porque o corpus de 44
  documentos não cobre a maioria delas; isso é uma limitação de cobertura do corpus, não do método.
- Só a v7 exibe fontes rastreáveis. A condição sem RAG dá vereditos sem nenhuma evidência
  verificável pelo usuário, o que é incompatível com o objetivo do trabalho mesmo quando acerta.
- O C7 foi gerado do próprio corpus e favorece a v7; o teste externo 2 favorece a condição sem RAG.
  Os dois resultados juntos delimitam a contribuição da recuperação, sem um conjunto neutro.
