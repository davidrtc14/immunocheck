# Diagnóstico de profundidade do retrieval — calibração v2

A análise usa somente os 36 itens conclusivos da calibração e compara a mesma
busca densa BGE-M3 com a alegação original e com a alegação extraída na fase A.

## Cobertura de ao menos um chunk anotado

| Consulta | Hit@6 | Hit@10 | Hit@20 | Hit@60 |
|---|---:|---:|---:|---:|
| `original_claim_dense` | 55.6% | 63.9% | 69.4% | 83.3% |
| `phase_a_extracted_claim_dense` | 58.3% | 63.9% | 72.2% | 83.3% |
| `phase_a_extracted_claim_bm25` | 16.7% | 19.4% | 25.0% | 27.8% |
| `phase_a_extracted_claim_hybrid_rrf` | 36.1% | 52.8% | 63.9% | 75.0% |

## Limites

- Hit@k mede interseção com os chunks anotados, não toda evidência potencialmente válida.
- A análise não chama LLM, não altera o índice e não abre teste ou holdout.
- Aumentar top-k só será hipótese aceitável se houver ganho de cobertura mensurável.
