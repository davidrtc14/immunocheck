# Arquitetura de alto nível

## Pipeline online

```text
Telegram
   ↓
Validação de tipo, tamanho e segurança
   ↓
Normalização por modalidade
   ├── texto → texto normalizado
   ├── imagem → pré-processamento + OCR local
   └── link → download seguro + extração local
   ↓
Filtro de escopo e extração da alegação principal
   ↓
Retrieval híbrido sobre corpus versionado
   ├── dense retrieval com BGE-M3
   └── BM25 lexical
   ↓
Reciprocal Rank Fusion + deduplicação
   ↓
Reranker opcional, se validado experimentalmente
   ↓
Teste de suficiência e conflito da evidência
   ↓
Qwen3-8B local gera veredito estruturado
   ↓
Validação de schema, citações, fidelidade e linguagem médica
   ↓
Resposta acessível + fontes verificáveis ou abstenção
```

O corte vertical da Fase 1 usa somente BM25 como baseline. Dense retrieval e RRF
entram na Fase 2 e só serão adotados no caminho final após avaliação reproduzível.

## Pipeline de ingestão

```text
Documento aprovado
  → extração de texto/OCR quando necessário
  → limpeza sem alterar o conteúdo factual
  → segmentação estrutural
  → chunks com contexto hierárquico
  → metadados e proveniência
  → embedding e índice lexical
  → validação e publicação da versão do corpus
```

## Fronteiras de confiança

- Entrada de usuário, página externa e texto de documentos são dados não confiáveis.
- Somente documentos aprovados entram no corpus.
- A LLM não cria objetos de citação; seleciona IDs de evidência existentes.
- A aplicação converte IDs válidos em referências legíveis.
- Toda conclusão sem cobertura suficiente deve resultar em abstenção.

## Componentes

- Adaptador Telegram: recebimento, feedback de processamento e resposta.
- Normalizadores: texto, OCR e extração segura de links.
- Ingestão: loaders, limpeza, chunking e catálogo do corpus.
- Retrieval: dense, BM25, RRF e reranker opcional.
- Verificação: extração de alegação, suficiência, geração e fidelidade.
- Avaliação: datasets congelados, métricas, latência e relatórios.
- Persistência: documentos, chunks, embeddings e dados experimentais curados.

## Estado e persistência

O caminho online é stateless entre requisições. Estado efêmero necessário durante
uma única análise vive apenas em memória ou em arquivos temporários eliminados ao
final. PostgreSQL armazena o corpus e dados de experimentos offline, nunca conteúdo
de usuários reais.
