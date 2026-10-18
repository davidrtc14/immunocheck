# Conjunto contrastivo C7 — relatório de construção (ADR-052)

Congelado em 18/10/2026, antes de qualquer execução do veredito sobre ele. Regras e emendas em
`PROTOCOL.md`; hashes em `freeze.json`; números brutos em `build_report.json` e `review_report.json`.
As alegações são sintéticas e foram geradas pelo `mistral-small3.2` (Apache 2.0, local), que nunca
é usado pelo bot. Os trechos do corpus não são versionados.

## Distribuição

| Rótulo | Desenvolvimento | Teste | Total |
|---|---:|---:|---:|
| `SUPPORTED` | 49 | 51 | 100 |
| `REFUTED` | 54 | 46 | 100 |
| `MISLEADING` | 48 | 52 | 100 |
| `INSUFFICIENT_EVIDENCE` | 42 | 58 | 100 |
| **Total** | **193** | **207** | **400** |

- **Famílias:** 86 documentos de origem, 43 no desenvolvimento e 43 no teste. Nenhum documento
  aparece nos dois splits.
- **Origem dos itens:**
  - 300 de chunks do corpus: uma versão por chunk, fiel, contradita ou distorcida;
  - 80 relatos de caso individual;
  - 20 fatos de documentos baixados mas fora do corpus, sendo 12 de um único documento
    (`cdc_hpv_doses_review_2022`).
- **Subtipos de `MISLEADING`:** salto causal (36), falsa implicação (27), generalização excessiva (19) e
  ressalva omitida (18).

## Portões

Foram 578 chunks do corpus, 200 chunks de fora do corpus e 134 chunks para relatos. O gerador não
falhou em nenhuma chamada.

| Portão | Descartes |
|---|---:|
| Chunk sem fato utilizável (corpus / fora) | 254 / 41 |
| Trecho citado inexistente (corpus / fora) | 16 / 3 |
| Sem menção a vacina (versões do corpus / fora / relatos) | 20 / 37 / 4 |
| Cópia de 4-gramas acima de 30% (versões do corpus / fora) | 5 / 3 |
| Número sem forma equivalente na fonte (`SUPPORTED`) | 2 |
| Quase duplicata (cosseno BGE-M3 ≥ 0,92) | 73 |
| Portão 8, coberto pelo corpus segundo o juiz LLM (fatos de fora) | 93 (69 `supports`, 19 `partial`, 5 `contradicts`) |

Os portões deixaram 1.143 candidatos, e a montagem tomou um item por chunk até 100 por classe.

## Taxa de erro de rótulo

Toda a revisão foi **assistida por LLM, sob responsabilidade do pesquisador** (emenda de 18/10). Ela
não é uma revisão humana independente. Os ICs são de Wilson, com 95%.

| Rodada | Grupo | Revisados | Erros | Taxa | IC 95% |
|---|---|---:|---:|---:|---|
| 1 | `SUPPORTED` (corpus) | 20 | 0 | 0,00 | 0,00–0,16 |
| 1 | `REFUTED` (corpus) | 20 | 0 | 0,00 | 0,00–0,16 |
| 1 | `MISLEADING` (corpus) | 20 | 0 | 0,00 | 0,00–0,16 |
| 1 | `INSUFFICIENT_EVIDENCE`, relatos | 11 | 0 | 0,00 | 0,00–0,26 |
| 1 | `INSUFFICIENT_EVIDENCE`, fatos de fora | 9 | 7 | 0,78 | 0,45–0,94 |
| 2 | `INSUFFICIENT_EVIDENCE`, fatos de fora (todos, depois do portão 8) | 20 | 0 | 0,00 | 0,00–0,16 |

- **Classe `INSUFFICIENT_EVIDENCE` no conjunto final:** a taxa ponderada pelas origens (0,8 relatos e
  0,2 fatos de fora) é 0. Os 9 fatos de fora revisados na rodada 1, inclusive os 7 errados, foram
  todos descartados pelo portão 8.
- **Correções da rodada 1:** as 7 correções eram de fatos de fora; nenhum deles ficou no conjunto.
- **Itens revisados no conjunto:** 87 de 400 (`status: reviewed`). Os outros estão como `draft`.

## Limitações

- **Revisão assistida por LLM.** Um modelo de linguagem conferindo rótulos gerados por outro modelo
  de linguagem pode compartilhar os mesmos pontos cegos. Os rótulos de `REFUTED` e `MISLEADING`
  têm 0 erros em 20 em cada classe, mas o limite superior do IC é 16%.
- **`INSUFFICIENT_EVIDENCE` é sobretudo de casos particulares.** São 80 relatos e 20 fatos de fora do
  corpus. Esses 20 se concentram num documento sobre doses da vacina de HPV, e vários são vagos ("Os
  estudos…", "a vacina"), o que não é o estilo de uma mensagem real. Na prática, a classe mede mais a
  abstenção diante de relatos do que diante de assuntos ausentes do corpus. O teste externo 2 cobre
  em parte essa lacuna.
- **O portão 8 é mais rigoroso que a revisão.** Na conferência, ele descartou os 7 erros e também os
  2 acertos. Com isso, sobrevivem poucos fatos de fora e, provavelmente, os mais específicos.
- **Ampliações durante a construção:** o limite de chunks por documento passou de 6 para 8 no corpus
  e para todos nos documentos de fora. A remontagem mudou a divisão de alguns documentos entre
  desenvolvimento e teste. Tudo isso ocorreu antes de qualquer inferência e está registrado no
  protocolo.
- **Ameaças já declaradas no protocolo:** alegações sintéticas; `SUPPORTED` potencialmente fácil de
  recuperar; viés de estilo do gerador.

## Teste externo 2

Foi montado e congelado na mesma fase, sem inferência: são 304 alegações de checagens de 2020 a 2024,
do feed ClaimReview do Data Commons. Dessas, 283 são `REFUTED`, 20 `MISLEADING` e 1 `SUPPORTED`.
Veja `external2/build_report.json` e `external2/SOURCES.md`.
