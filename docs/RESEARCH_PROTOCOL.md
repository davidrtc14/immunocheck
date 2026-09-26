# Protocolo de pesquisa e avaliação

> Protocolo original preservado para rastreabilidade. Ele orientou as comparações
> da v1 e não foi reescrito após os resultados. A questão-síntese do trabalho completo
> e a linha confirmatória v3 estão consolidadas em `docs/TCC_DELIVERY_PACKAGE.md`.

## Pergunta de pesquisa

Em que medida a recuperação híbrida e a verificação pós-geração melhoram a
acurácia, a fidelidade e a qualidade das citações de um sistema RAG local para
checagem de alegações sobre vacinação humana em português?

## Separação dos conjuntos

### Corpus de conhecimento

- Meta: 80 a 150 documentos oficiais e científicos.
- Resultado esperado: aproximadamente 3.000 a 10.000 chunks.
- Prioridade: Ministério da Saúde/PNI, Anvisa, OMS, OPAS e revisões científicas.
- Cada documento terá proveniência, versão, data de publicação, data de coleta,
  URL, licença/condição de uso e hash.
- Fact-checkers podem inspirar alegações de avaliação, mas não podem fornecer a
  resposta pronta no corpus para o mesmo item.

### Dataset de avaliação

- Meta desejável: 160 alegações, 40 por classe.
- Mínimo aceitável documentado: 100, 25 por classe.
- Classes: `SUPPORTED`, `REFUTED`, `MISLEADING` e `INSUFFICIENT_EVIDENCE`.
- Split estratificado: 60% desenvolvimento/validação e 40% teste congelado.
- Nenhum prompt, limiar ou hiperparâmetro será ajustado após examinar o teste.
- Cada item terá alegação atômica, rótulo, justificativa e chunks/documentos de
  evidência relevantes.

## Anotação

- Um anotador principal revisará todos os itens.
- Um segundo anotador revisará independentemente pelo menos 30%.
- Será reportada concordância interanotadores, preferencialmente Cohen's kappa.
- Divergências serão adjudicadas por pessoa com conhecimento em vacinação,
  preferencialmente profissional de saúde.
- Se revisão especializada não estiver disponível, isso será limitação explícita.

## Experimentos

### Recuperação

1. Dense-only.
2. Dense + BM25 com RRF.
3. Melhor configuração anterior + reranker.

Métricas: Recall@5, Recall@10, MRR e nDCG@10, usando julgamentos de relevância
query–chunk. Embedding e chunking permanecem fixos durante a comparação principal.

### Pipeline fim a fim

1. Qwen3-8B sem RAG.
2. Qwen3-8B com a melhor recuperação validada.
3. Configuração 2 com verificação pós-geração.

Métricas: Macro-F1, F1 por classe, matriz de confusão, taxa de abstenção,
faithfulness, correção e completude de citações. Resultados terão intervalos de
confiança por bootstrap e análise qualitativa dos principais erros.

## Desempenho operacional

Hardware de referência: Ryzen 5 7500F, 32 GB DDR5 e RTX 4060 de 8 GB.

| Métrica | Meta inicial de engenharia |
|---|---:|
| Confirmação de processamento no Telegram | até 2 s |
| Latência P95 de texto/link | até 45 s |
| Latência P95 de imagem | até 60 s |
| Requisições concluídas sem erro | pelo menos 95% |
| Pico de VRAM | até 7,5 GB |
| Pico de RAM | até 24 GB |

As metas não representam propriedades universais do modelo. O relatório apresentará
mediana, P95, dispersão, aquecimento, versões e configuração exata. O benchmark terá
ao menos 30 execuções representativas por modalidade quando a pipeline estiver
estável.

## Ameaças à validade

- Dataset pequeno e domínio específico.
- Mudança temporal das recomendações de vacinação.
- Subjetividade da classe `MISLEADING`.
- Cobertura incompleta do corpus.
- Dependência de OCR em conteúdo degradado.
- Possível viés institucional e geográfico das fontes.
- Resultados de desempenho limitados ao hardware de referência.
- Propostas de avaliação de 15/09/2026 inteiramente sintéticas e baseadas nas
  próprias fontes do corpus; proximidade lexical e padrões de formulação podem
  facilitar a tarefa. Benchmark controlado não demonstra desempenho em notícias
  espontâneas; revisar essa validade com o orientador antes do congelamento.
- Correlação entre versões da mesma família e entre fontes compartilhadas. Reportar
  contagem de famílias e análise de sensibilidade da incerteza por família; 160
  itens não equivalem necessariamente a 160 observações independentes.
- O preparador conhece os candidatos de ambos os splits. Nenhuma previsão orientou
  a construção; futuros ajustes precisam usar somente desenvolvimento, com
  registro dessa limitação e sem execução exploratória sobre o teste.
