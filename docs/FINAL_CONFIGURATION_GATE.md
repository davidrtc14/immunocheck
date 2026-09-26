# Gate da configuração final

> Registro histórico da seleção da v1 antes de seu teste congelado. A v3 posterior
> usou dados novos e protocolo próprio; a configuração demonstrável atual está em
> `docs/V3_INTEGRATION.md`.

Data: 18/09/2026. Este registro transforma o impasse do auditor em uma decisão
explícita antes da execução única no teste congelado. Nenhum item de teste foi
carregado para preparar esta recomendação.

**Estado:** gate concluído e teste executado uma única vez no commit `52ab0bd`.
Este documento permanece como registro anterior à abertura; o resultado está em
`evaluation/results/test/FINAL_TEST_REPORT.md`.

## Alternativas já avaliadas no desenvolvimento

| Configuração | Macro-F1 | Recall `MISLEADING` | Recall de abstenção | P95 | Situação |
|---|---:|---:|---:|---:|---|
| BGE-M3 sem auditor LLM | 0,577 | 0,474 | 0,125 | 9,4 s | Melhor classificação; baixa proteção contra conclusão indevida. |
| BGE-M3 + auditor v2 | 0,528 | 0,158 | 0,625 | 11,3 s | Mais conservadora; converte muitas conclusões em abstenção. |
| BGE-M3 + auditor factual v3 | 0,405 | 0 | 0,708 | 11,6 s | Descartada pelos gates pré-registrados. |

O auditor v2 alterou 39 das 96 previsões densas: 12 ficaram corretas, 19 deixaram
de estar corretas e oito continuaram erradas. Entre os 19 itens de referência
`MISLEADING`, seis classificações corretas viraram `INSUFFICIENT_EVIDENCE`. Esse
resultado reduz utilidade e macro-F1, mas não transforma esses seis casos em uma
afirmação falsa: produz uma recusa conservadora.

## Recomendação técnica e acadêmica

Recomenda-se **BGE-M3 + auditor v2** para a execução definitiva, condicionada à
ciência do orientador. A razão não é superioridade estatística — ela não existe —,
mas prioridade de segurança: em um protótipo de saúde, uma abstenção excessiva é
preferível a apresentar como conclusiva uma resposta cuja fundamentação foi
reprovada. O trabalho deve declarar simultaneamente que:

1. o denso sem auditor teve melhor macro-F1 e melhor reconhecimento de
   `MISLEADING` no desenvolvimento;
2. o auditor foi escolhido por recall de abstenção, não por acurácia geral;
3. falsos positivos de abstenção limitam utilidade e não podem ser descritos como
   “maior confiabilidade” sem essa ressalva;
4. gerador e auditor usam o mesmo Qwen3-8B e não são independentes;
5. a v3 negativa e todos os intervalos permanecem no relatório.

Desligar o auditor seria defensável apenas se o objetivo fosse maximizar a métrica
de classificação. Isso contraria a prioridade de abstenção segura adotada desde o
início e exigiria substituir a ADR-014 antes do teste.

## Configuração a congelar após o aceite

- retrieval: BGE-M3 denso, top 6, sem RRF e sem reranker;
- extrator: v2 com guarda de integridade de alegações curtas;
- gerador e auditor: Qwen3-8B local, temperatura 0, seed 42;
- auditor: prompt v2 restaurado, com guarda de orientação médica;
- corpus: versão e hashes já vinculados ao manifesto do benchmark;
- quatro classes, citações programáticas e fontes parciais em abstenções;
- código: commit de congelamento a registrar depois deste gate;
- teste: 64 itens, uma única execução, sem ajustes posteriores.

## Aprovação necessária

- [x] Orientador ciente do trade-off entre macro-F1, `MISLEADING` e abstenção.
- [x] Configuração BGE-M3 + auditor v2 aceita como escolha de segurança.
- [x] Autorizada a execução única nos 64 itens de teste.
- [x] Confirmado que resultados do teste não provocarão novo ajuste nesta versão.

Registro da decisão: confirmação explícita do autor na conversa do projeto.

Data e responsável: 18/09/2026 — autor do projeto, após ciência do orientador.

Sem esse aceite, é permitido continuar testes automatizados, documentação e ensaio
de demonstração com dados sintéticos, mas não abrir o conjunto de teste.
