# Consolidação do refinamento de acurácia v2

## Decisão executiva

A linha experimental v2 foi encerrada **sem promoção de candidata** em 26/09/2026.
Nenhuma configuração satisfez simultaneamente os critérios pré-registrados de
acurácia, segurança de abstenção, qualidade de citação, estabilidade por classe e
latência. A configuração v1 permanece congelada como única prova de conceito
demonstrável, com a limitação crítica de recall zero para `MISLEADING` no teste
final já documentado.

O holdout v2 não foi criado. Essa ausência é deliberada: pelo protocolo, ele só
seria construído depois que uma candidata passasse todos os gates de calibração e
fosse congelada. Usá-lo para escolher entre candidatas transferiria a calibração
para o conjunto confirmatório.

## Evidência comparativa

As condições fim a fim abaixo foram avaliadas nos mesmos 48 itens novos, agrupados
em 12 famílias e balanceados nas quatro classes. Os intervalos foram calculados por
reamostragem de famílias, porque os quatro itens de uma família não são observações
independentes.

| Condição | Macro-F1 | `MISLEADING` | `INSUFFICIENT_EVIDENCE` | Citação relevante | P95 | Gates |
|---|---:|---:|---:|---:|---:|---:|
| v1 densa + auditor | 0,430 | 0,000 | 0,667 | 0,500 | 12,41 s | referência |
| v2 separada, top 6 | 0,373 | 0,000 | 1,000 | 0,500 | 14,74 s | 2/7 |
| v2 separada, top 20 | 0,376 | 0,000 | 0,583 | 0,139 | 17,98 s | 1/7 |
| decisão direta, top 6 | 0,472 | 0,250 | 0,083 | 0,472 | 10,12 s | 3/7 |

O melhor ponto estimado de macro-F1 foi a decisão direta, mas o delta contra a v1
foi apenas +0,042, abaixo do mínimo de +0,08, com intervalo percentil de 95% entre
−0,090 e +0,190. Além disso, a condição concluiu indevidamente em 11 dos 12 casos
que exigiam abstenção. Portanto, o ganho pontual não caracteriza melhora segura.

Duas triagens adicionais foram interrompidas antes de uma nova avaliação fim a fim:

- MMR reduziu Hit@6 de 21/36 para 12/36 e a cobertura de `MISLEADING` de 6/12
  para 3/12; passou apenas o gate de latência.
- O gate de suficiência v2 aceitou 36/36 itens conclusivos, mas também 12/12 itens
  insuficientes; passou quatro de seis gates e não autorizou o classificador.

## O que os resultados permitem concluir

1. **Recuperar mais trechos não basta.** O top 20 elevou a cobertura bruta da
   evidência anotada, mas piorou citações, robustez estrutural e resultado fim a fim.
2. **Diversidade vetorial não equivale a pertinência factual.** O MMR retirou
   evidências relevantes que já estavam no top 6.
3. **Suficiência é o gargalo central desta implementação.** O gate original foi
   excessivamente conservador; a revisão seguinte foi excessivamente permissiva.
4. **Remover guardrails melhora classes conclusivas às custas da segurança.** A
   decisão direta reconheceu mais `SUPPORTED`, `REFUTED` e `MISLEADING`, mas quase
   eliminou a abstenção correta.
5. **A incerteza é material.** Os intervalos por família não sustentam superioridade
   estável da melhor candidata sobre a v1.

Essas conclusões se aplicam ao corpus, ao conjunto sintético orientado por fontes,
ao Qwen3-8B local e às implementações avaliadas. Elas não demonstram impossibilidade
geral de melhorar RAG ou LLMs para verificação de vacinação.

## Critério de parada e integridade metodológica

Novas alterações de prompt orientadas pelos mesmos 48 itens foram suspensas. Após
várias comparações, continuar ajustando a partir dos erros observados aumentaria a
chance de sobreajuste e enfraqueceria a validade do trabalho. Também não serão
combinadas manualmente saídas de condições diferentes item a item.

A linha pode ser reaberta em trabalho futuro somente com hipótese nova e dados
independentes, por exemplo:

- anotações separadas para cobertura, relação lógica, escopo e suficiência;
- modelo local de entailment ou reranker treinado para pertinência factual, após
  validação de custo e licença;
- conjunto externo maior, com alegações reais desidentificadas e revisão humana;
- avaliação explícita de calibração e seletividade, além de macro-F1.

Essas opções não integram a v1 e não autorizam uso público. Qualquer estudo com
participantes, dados pessoais ou interações reais continua condicionado às decisões
institucionais de ética e LGPD.

## Estado para o TCC

O resultado negativo deve ser apresentado como achado experimental, não ocultado
nem reinterpretado como sucesso. O sistema demonstra integração técnica de entrada,
RAG, LLM local, citações e guardrails; a avaliação mostra, contudo, que a acurácia e
a distinção de conteúdo enganoso ainda são insuficientes para um serviço público de
checagem em saúde.

Assim, a contribuição defensável é dupla: um protótipo local, gratuito e
reprodutível, e uma avaliação controlada que identifica limites concretos da
arquitetura em hardware doméstico. O próximo marco do projeto deve ser a
consolidação dos resultados e artefatos de entrega do TCC, não uma nova rodada de
otimização no mesmo conjunto.
