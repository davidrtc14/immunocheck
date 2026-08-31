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

## Próxima unidade

Criar um dataset piloto query–chunk com revisão humana e implementar Recall@5,
Recall@10, MRR e nDCG@10 para comparar:

1. BM25;
2. BGE-M3 dense-only;
3. BGE-M3 + BM25 com RRF.

## Unidade 2.2 — Infraestrutura da avaliação de retrieval

Implementada em 31/08/2026, com anotação humana pendente:

- 12 alegações piloto atômicas, mantidas como `draft`;
- schema JSONL versionado e validação contra os IDs do corpus;
- planilha local com candidatos obtidos por BM25, dense e RRF;
- Recall@5, Recall@10, MRR e nDCG@10 com relevância binária;
- deduplicação dos rankings para impedir inflação de métricas;
- relatório JSON reproduzível com rankings, métricas e latência por sistema;
- bloqueio do experimento enquanto houver consulta sem revisão humana.

A planilha contém 428 pares consulta–chunk candidatos. Esse pool reduz o trabalho
de leitura, mas pode omitir evidências relevantes; por isso o anotador deve consultar
a fonte e pode incluir chunks fora do pool. Resultados métricos só serão registrados
após o preenchimento do gabarito.

## Próxima ação

Revisar os candidatos, registrar os chunks relevantes e então executar a comparação
piloto. A decisão sobre retrieval híbrido e reranker continua condicionada aos
resultados, não à preferência arquitetural.
