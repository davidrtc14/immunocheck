# Achados diagnósticos — calibração v2, fase A

Data: 26/09/2026. Esta auditoria é posterior ao resultado congelado da fase A e usa
somente os 48 itens de calibração. Nenhuma previsão do teste v1 ou do holdout v2 foi
carregada.

## Onde a candidata falhou

As 48 decisões receberam uma atribuição primária exclusiva:

| Estágio | Itens |
|---|---:|
| Acerto conclusivo | 7 |
| Abstenção correta | 12 |
| Risco de integridade na extração | 5 |
| Evidência anotada ausente do top 6 | 14 |
| Gate rejeitou apesar de preservar evidência anotada | 8 |
| Gate não selecionou a evidência anotada recuperada | 2 |

O problema é multietapas. Alterar apenas o prompt do gate ignoraria os 14 misses de
retrieval; trocar apenas o retrieval ignoraria dez falhas observáveis do gate.

## Profundidade e modalidade de retrieval

Nos 36 itens conclusivos, usando a alegação extraída da fase A:

| Retrieval | Hit@6 | Hit@10 | Hit@20 | Hit@60 |
|---|---:|---:|---:|---:|
| BGE-M3 denso | 58,3% | 63,9% | 72,2% | 83,3% |
| BM25 | 16,7% | 19,4% | 25,0% | 27,8% |
| Híbrido RRF | 36,1% | 52,8% | 63,9% | 75,0% |

A alegação original obteve Hit@20 de 69,4%, contra 72,2% da extraída. Logo, a
extração não explica o déficit agregado de retrieval, embora cinco itens tenham
risco lexical individual. BM25 e RRF ficaram abaixo do denso neste conjunto.

## Próxima hipótese controlada

A próxima iteração mudará somente a profundidade do BGE-M3 denso de top 6 para top
20, mantendo extração da fase A, modelo, prompts, gate, classificador e ausência de
auditor. O ganho potencial de cobertura é cinco itens conclusivos. O custo esperado
é maior contexto e possível aumento de latência; ambos serão medidos pelos mesmos
gates.

Nenhuma mudança de prompt será combinada nessa iteração. Se top 20 não superar os
gates, seu resultado será preservado como falha e uma hipótese de gate deverá ser
registrada separadamente.

