# Diagnóstico pós-calibração — fase A

## Resultado executivo

- Itens analisados: 48.
- Evidência anotada apareceu no top 6 em 21/36 itens conclusivos (58.3%).
- O gate preservou evidência anotada em 18/36 (50.0%).
- Extração exata: 29/48; perdas de marcador material: 0.

## Atribuição primária exclusiva

| Estágio | Itens | Proporção |
|---|---:|---:|
| `correct_conclusive` | 7 | 14.6% |
| `correct_insufficient_evidence` | 12 | 25.0% |
| `extraction_integrity_risk` | 5 | 10.4% |
| `retrieval_miss` | 14 | 29.2% |
| `sufficiency_rejection_with_annotated_evidence` | 8 | 16.7% |
| `sufficiency_selection_miss` | 2 | 4.2% |

## Abstenção por classe esperada

| Classe | Abstenções | Total | Taxa |
|---|---:|---:|---:|
| `SUPPORTED` | 3 | 12 | 25.0% |
| `REFUTED` | 11 | 12 | 91.7% |
| `MISLEADING` | 12 | 12 | 100.0% |
| `INSUFFICIENT_EVIDENCE` | 12 | 12 | 100.0% |

## Interpretação

`retrieval_miss` significa que nenhum ID anotado apareceu no top 6. Quando o
retrieval encontrou a evidência e a candidata se absteve, o diagnóstico separa
seleção incorreta do gate de rejeição apesar de evidência anotada preservada.
Extração tem precedência quando perde conteúdo material; portanto as categorias
somam exatamente 48 sem contar um item duas vezes.

## Limitações

- Interseção de IDs mede cobertura da evidência anotada, não relevância exaustiva de todos os chunks recuperados.
- Atribuição por estágio é diagnóstica e não demonstra causalidade isolada.
- O diagnóstico não carrega teste v1 nem holdout v2 e não altera os resultados da fase A.
