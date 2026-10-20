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
Retrieval denso BGE-M3 sobre corpus versionado
   ↓
Top 15 chunks deduplicados
   ↓
Roteamento pela forma da alegação
   ├── proposição simples → decisão direta no top 6
   ├── premissa-conclusão → decisão relacional no top 15
   └── evento específico sem âncora → abstenção
   ↓
Qwen3-8B local gera veredito estruturado em quatro classes
   ↓
Seleção inicial de citações → expansão no documento → seleção final
   ↓
Validação de schema, IDs de fonte e linguagem médica
   ↓
Resposta acessível + fontes verificáveis ou abstenção
```

O BM25 isolado foi o baseline da Fase 1. A avaliação formal da Fase 6 escolheu BGE-M3
isolado para o caminho online. BM25, RRF e reranker permanecem disponíveis somente
para ablação e diagnóstico; o reranker não converteu seu ganho de ranking em melhora
fim a fim e duplicou a latência.

Esse é o caminho da v3. Desde a ADR-055, o padrão é a v7: a v3 responde primeiro e, só quando ela
responde `SUPPORTED`, a `v5_fixed` (decomposição, juiz por proposição e agregação determinística)
verifica a mesma entrada; se a verificação não sustentar, vale a resposta dela. A montagem fica em
`bootstrap_bot.py`, sem editar os módulos congelados. A v3 (`PIPELINE_VERSION=v3`) e a v1 congelada,
com top 6 e auditor de fidelidade (`PIPELINE_VERSION=v1`), permanecem selecionáveis para reprodução
e reversão; nenhuma é silenciosamente reescrita pela integração.

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
- Conteúdos com várias alegações informam que o protótipo analisou somente a principal.

## Componentes

- Adaptador Telegram: recebimento, feedback de processamento e resposta.
- Normalizadores: texto, OCR e extração segura de links.
- Ingestão: loaders, limpeza, chunking e catálogo do corpus.
- Retrieval online: BGE-M3 denso. BM25, RRF e reranker permanecem disponíveis
  somente para reprodução e ablações offline.
- Verificação: extração, roteamento, geração especializada e citações hierárquicas.
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
