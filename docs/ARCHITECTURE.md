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

O BM25 isolado foi o baseline da Fase 1. Após a comparação piloto da Fase 2, o caminho
online passou a usar BGE-M3 em CPU e BM25 com RRF; o modo lexical isolado permanece
disponível para ablação e diagnóstico. O reranker continua desligado por padrão.

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
- Ausência de menção nunca é tratada como contradição.
- Em abstenções, referências parciais são rotuladas como não conclusivas.
- Conteúdos com várias alegações informam que a v1 analisou somente a principal.

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

Cada carga no PostgreSQL mantém a versão integral do manifesto. Documentos, chunks e
embeddings usam chaves compostas com `corpus_version`; somente um snapshot pode ficar
ativo. O pgvector começa com busca exata por cosseno para preservar recall e a
reprodutibilidade no tamanho de corpus previsto.

O adaptador Telegram usa long polling e conserva o offset somente em memória. Texto e
`chat_id` existem apenas durante o atendimento da atualização; não há repositório,
tabela ou arquivo para interações. Respostas são enviadas em texto simples, com links
programáticos e previews desativados.

Na Fase 4, fotos e documentos de imagem são validados com Pillow, pré-processados com
OpenCV e reconhecidos pelo Tesseract via memória. Links usam um cliente HTTPS próprio que
fixa a conexão ao IP público previamente validado e repete essa validação após cada
redirecionamento. HTML e PDF textual são extraídos em memória e convergem para o mesmo
normalizador e a mesma pipeline do texto.
