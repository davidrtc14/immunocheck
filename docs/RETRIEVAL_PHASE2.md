# Fase 2 — Retrieval e ingestão

## Objetivo

Comparar recuperação lexical, densa e híbrida de forma reproduzível antes de escolher
o caminho final do RAG. A presença de BGE-M3 e RRF na arquitetura é uma hipótese,
não evidência de superioridade.

## Unidade 2.1 — Dense retrieval local

Implementada em 30/08/2026:

- BGE-M3 na revisão `b28ce2a6fcc9c75ef1c0619575d0ec19af760082`;
- Sentence Transformers 6.0.0;
- execução do embedder somente em CPU;
- embeddings normalizados com 1.024 dimensões;
- similaridade de cosseno por produto escalar;
- índice local associado ao SHA-256 exato do corpus;
- falha explícita se corpus, modelo, revisão, dimensão ou IDs divergirem;
- Reciprocal Rank Fusion com constante 60 e deduplicação por `chunk_id`.

O Qwen3-8B ocupa cerca de 6,19 GB dos 8 GB de VRAM. Manter BGE-M3 em CPU evita
concorrência por VRAM e recarga do gerador entre retrieval e resposta.

## Medições do piloto

Hardware: Ryzen 5 7500F, RTX 4060 de 8 GB e 32 GB de RAM.

| Operação | Resultado observado |
|---|---:|
| Indexar 1.914 chunks em CPU | 1.027,96 s |
| Tamanho do índice comprimido | 7.318.139 bytes |
| Carregar BGE-M3 em CPU | 7,15 s |
| Embedding denso de uma consulta, modelo aquecido | 0,11–0,19 s |
| Busca BM25 | 0,008–0,010 s |
| Busca híbrida, incluindo novo embedding | 0,11–0,13 s |

Os valores são medições de engenharia com três consultas curadas, não benchmark
estatístico. Mediana, P95, memória e dispersão exigem o executor experimental e pelo
menos 30 repetições representativas.

## Implicações

- Indexação completa é uma tarefa offline; o serviço online reutiliza os vetores.
- O corpus definitivo exigirá indexação incremental por hash de documento/chunk.
- O modelo de embeddings deve permanecer carregado em CPU durante o serviço para
  evitar aproximadamente sete segundos adicionais na primeira consulta.
- O índice piloto pode ficar em arquivo local; pgvector entra após o esquema de
  proveniência e o protocolo de atualização incremental estarem definidos.
- Nenhuma configuração será promovida para produção antes das métricas de relevância.

## Unidade 2.2 — Infraestrutura da avaliação de retrieval

Implementada e anotada em 31/08/2026:

- 12 alegações piloto atômicas com revisão humana registrada;
- schema JSONL versionado e validação contra os IDs do corpus;
- planilha local com candidatos obtidos por BM25, dense e RRF;
- Recall@5, Recall@10, MRR e nDCG@10 com relevância binária;
- deduplicação dos rankings para impedir inflação de métricas;
- relatório JSON reproduzível com rankings, métricas e latência por sistema;
- bloqueio do experimento enquanto houver consulta sem revisão humana.

A planilha contém 476 pares consulta–chunk candidatos. Esse pool reduz o trabalho
de leitura, mas pode omitir evidências relevantes; por isso o anotador deve consultar
a fonte e pode incluir chunks fora do pool. O executor só aceita o gabarito quando
todos os itens possuem revisão registrada.

## Unidade 2.3 — Comparação piloto

Executada em 31/08/2026 após revisão humana das 12 consultas:

| Sistema | Recall@5 | Recall@10 | MRR | nDCG@10 | Mediana | P95 |
|---|---:|---:|---:|---:|---:|---:|
| BM25 | 0,417 | 0,583 | 0,394 | 0,436 | 9,91 ms | 12,11 ms |
| BGE-M3 dense | 0,750 | 0,917 | 0,440 | 0,553 | 122,78 ms | 135,08 ms |
| BM25 + BGE-M3 + RRF | 0,750 | 0,917 | 0,505 | 0,604 | 131,09 ms | 150,59 ms |

O híbrido empatou com o dense em Recall@5 e Recall@10, mas apresentou melhor MRR
e nDCG@10, indicando ordenação superior no piloto. O dense deixou a evidência do
item 006 na posição 11; o híbrido deixou a evidência do item 011 na posição 11.
Assim, os métodos falharam em consultas diferentes e a fusão não aumentou o recall
em relação ao dense nesse conjunto.

As latências possuem apenas 12 amostras aquecidas por sistema. São adequadas para
comparação exploratória, não para o benchmark operacional final de pelo menos 30
execuções representativas. O relatório bruto permanece em `runs/`, fora do Git.

Durante a análise, a geração de candidatos foi alinhada ao executor: ambos usam 60
resultados de entrada por método e constante RRF 60. A planilha exibe os 20 primeiros
candidatos de cada componente e do ranking fundido.

## Unidade 2.4 — Experimento piloto de reranking

Executada em 31/08/2026 com:

- `BAAI/bge-reranker-v2-m3`, revisão
  `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e` e licença Apache-2.0;
- execução somente em CPU e `max_length=512`;
- reranking dos 20 primeiros resultados híbridos para produzir o top 10;
- modelo com 2.293.242.108 bytes no cache local;
- pico de working set do processo de 3.696.939.008 bytes.

| Sistema | Recall@5 | Recall@10 | MRR | nDCG@10 | Mediana | P95 |
|---|---:|---:|---:|---:|---:|---:|
| Híbrido RRF | 0,750 | 0,917 | 0,505 | 0,604 | 135,60 ms | 146,79 ms |
| Híbrido + reranker | 0,917 | 1,000 | 0,588 | 0,691 | 11.129,59 ms | 11.359,02 ms |

O reranker melhorou a posição da evidência em sete consultas, manteve três e piorou
duas. Ele recuperou no top 10 a evidência do item 011, ausente no top 10 híbrido. O
custo incremental mediano do cross-encoder foi de 10.989,23 ms.

O ganho é relevante para um sistema de saúde, mas a latência aumentou em cerca de
82 vezes em relação ao retrieval híbrido. A decisão do piloto é manter o reranker
como candidato para a avaliação ampliada, sem ativá-lo como padrão até medir a
pipeline completa com Qwen e confirmar a meta de P95 de até 45 segundos.

## Próxima ação

Concluir o modelo de persistência, proveniência e atualização incremental antes da
migração para PostgreSQL + pgvector.
