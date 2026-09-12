# PostgreSQL e pgvector

## Papel no sistema

O PostgreSQL persiste somente o corpus documental, sua proveniência e embeddings
gerados localmente. Mensagens, imagens, URLs enviadas, respostas e identificadores de
usuários não possuem tabelas no schema.

A configuração de referência usa PostgreSQL 17 e pgvector 0.8.6 na imagem oficial
`pgvector/pgvector:0.8.6-pg17-bookworm`. PostgreSQL, pgvector e Psycopg são open
source e não exigem serviço pago ou conta externa.

## Schema

- `corpus_versions`: manifesto integral, hashes, estado e versão ativa;
- `corpus_documents`: metadados e proveniência por documento e versão;
- `corpus_chunks`: texto, páginas, hashes, metadados de citação e `tsvector` em
  português;
- `chunk_embeddings`: vetor BGE-M3 de 1.024 dimensões, modelo e revisão exatos;
- `immunocheck_schema_migrations`: histórico e checksum das migrations aplicadas.

Chaves estrangeiras sempre incluem `corpus_version`, impedindo que chunks ou vetores
de snapshots diferentes sejam misturados. Apenas uma versão pode estar `ACTIVE`.

## Estratégia de busca

O pgvector usa distância de cosseno (`<=>`) e busca exata. HNSW e IVFFlat não entram
nesta fase: o corpus projetado tem apenas 3 mil a 10 mil chunks e índices aproximados
trocam recall por velocidade, o que adicionaria outra variável ao experimento. Essa
decisão deve ser reavaliada com medição, não por preferência.

O `tsvector`/GIN é infraestrutura lexical auxiliar, não substitui o BM25 do experimento
principal. A comparação já definida continua usando o mesmo tokenizer e os mesmos
rankings para evitar mudança metodológica silenciosa.

## Inicialização local

Pré-requisito: Docker Desktop com Docker Compose v2 acessível no `PATH`.

```powershell
Copy-Item .env.example .env
docker compose up -d postgres
$env:DATABASE_URL = "postgresql://immunocheck:immunocheck-local-only@localhost:5432/immunocheck"
.\.venv\Scripts\python.exe scripts\migrate_database.py
```

O serviço publica a porta somente em `127.0.0.1`. A senha padrão é exclusivamente
local e deve ser trocada se o banco deixar a máquina de desenvolvimento.

## Publicação de uma versão

Na primeira migração do corpus legado, os chunks e o índice denso precisam ser
reconstruídos porque o JSONL passa a conter a nova proveniência:

```powershell
.\.venv\Scripts\python.exe scripts\build_pilot_corpus.py
.\.venv\Scripts\python.exe scripts\build_dense_index.py --offline
.\.venv\Scripts\python.exe scripts\import_corpus_database.py
.\.venv\Scripts\python.exe scripts\import_dense_embeddings.py
.\.venv\Scripts\python.exe scripts\import_corpus_database.py --activate
```

A importação do corpus e a troca da versão ativa ocorrem em uma transação. Repetir a
importação da mesma versão é idempotente; uma versão igual com contagens ou hash
divergentes é rejeitada. A ativação também é recusada enquanto não existir um conjunto
completo de embeddings para todos os chunks da versão.

O construtor denso é incremental: vetores anteriores só são reutilizados quando o
modelo e a revisão coincidem e o `chunk_id` permanece igual. Como o ID contém o hash
do texto, qualquer alteração textual força novo embedding. `--full-rebuild` oferece a
reconstrução integral de controle.

## Migrations

Arquivos em `database/migrations/` são aplicados em ordem contígua. O SHA-256 de cada
arquivo é registrado; editar uma migration já aplicada interrompe o processo. Novas
mudanças devem criar `0002_...sql`, `0003_...sql` e assim por diante.

A migration `0002_allow_jats_xml.sql` amplia somente o formato documental aceito
por `corpus_documents`, permitindo `xml` além de `pdf` e `html`. Isso viabiliza
artigos integrais em JATS obtidos de repositórios científicos autorizados, sem
alterar as tabelas de interações — que continuam inexistentes.

O teste de integração só executa quando uma base exclusiva é fornecida:

```powershell
$env:IMMUNOCHECK_TEST_DATABASE_URL = $env:DATABASE_URL
.\.venv\Scripts\python.exe -m pytest tests\test_postgres_integration.py -q
```

Não aponte esse teste para uma base que contenha dados alheios ao projeto.

## Validação local de referência

Executada em 31/08/2026 no hardware do projeto:

- PostgreSQL 17.11 e pgvector 0.8.6 em Docker Desktop;
- migration `0001` aplicada e validada pelo teste de integração;
- versão `sha256:09c6e41299a9450ce9340009e116a68b9f771df9e899540aae17bb209b6b7222`
  ativada;
- 7 documentos, 1.914 chunks e 1.914 embeddings de 1.024 dimensões;
- top 10 de uma consulta de fumaça idêntico entre o índice NumPy local e o pgvector;
- 22,47 ms para a consulta exata no PostgreSQL já aquecido.

A latência é uma única medição funcional e não substitui o benchmark de pelo menos
30 execuções previsto no protocolo de pesquisa.

## Atualização do lote 001 da Fase 5

Em 01/09/2026, a versão
`sha256:9aaa8323aefc9186e22dce3c79cb8ad73b0bda4fe3426c8c101221048dfd7510`
foi importada e ativada com 16 documentos, 2.675 chunks e 2.675 embeddings. O ranking
denso top 10 de uma consulta sobre chumbo na vacina contra gripe foi idêntico entre o
índice NumPy local e o pgvector. Essa é uma verificação funcional única; as medições
distribucionais continuam reservadas para a Fase 6.

## Atualização do lote 002 da Fase 5

Em 07/09/2026, a versão
`sha256:5e21bdfbe417e471ce7ac1c34d0d239c79fb619a751228cd3616b9772da09f31`
foi importada e ativada com 21 documentos, 3.532 chunks e 3.532 embeddings. A
versão anterior permaneceu `ARCHIVED`. O ranking denso top 10 de uma consulta
sobre vacinação materna contra VSR foi idêntico no índice NumPy e no pgvector.
Essa comparação é um teste funcional; não substitui o benchmark da Fase 6.

## Atualização do lote 003 da Fase 5

Em 09/09/2026, a versão
`sha256:8e605597e2cc3d55a09cffbb7dde6396d5df34452b22179dee0fa65585959364`
foi importada e ativada com 32 documentos, 4.252 chunks e 4.252 embeddings. A
versão anterior permaneceu `ARCHIVED`. O ranking denso top 10 de uma consulta sobre
segurança da vacina contra dengue foi idêntico entre o índice NumPy local e o
pgvector. Essa comparação é um teste funcional; não substitui o benchmark da Fase 6.

## Atualização do lote 004 da Fase 5

Em 10/09/2026, a migration `0002_allow_jats_xml.sql` foi aplicada e a versão
`sha256:2a2ed2ce976165327677dd7f238d31407a93cdb3428f9e449bc25a7a955e92cc`
foi importada e ativada com 40 documentos, 5.313 chunks e 5.313 embeddings. A
versão anterior permaneceu `ARCHIVED`. A versão ativa contém 9 documentos HTML,
27 PDF e 4 XML. O ranking denso top 10 de uma consulta sobre tiomersal e autismo
foi idêntico entre o índice NumPy local e o pgvector.

## Atualização do lote 005 da Fase 5

Em 10/09/2026, a versão
`sha256:f15c0ebd67783ccf16552c5230b230c73cde02ccd42a9888102510c5cf4e0119`
foi importada e ativada com 50 documentos, 6.079 chunks e 6.079 embeddings. A
versão anterior permaneceu `ARCHIVED`. O construtor incremental reutilizou 5.313
vetores e gerou 766 em CPU e modo offline, em 552,95 segundos. Uma busca exata por
cosseno no pgvector, usando um chunk do relatório pneumocócico como consulta,
devolveu esse mesmo chunk em primeiro lugar com similaridade 1,000000. Esta é uma
verificação funcional; o benchmark distribucional permanece para a Fase 6.

## Atualização do lote 006 da Fase 5

Em 12/09/2026, a versão
`sha256:253c380014fb96f32be9dd3f47629ee055d1218bff85c594c757f8891d6754cb`
foi importada e ativada com 58 documentos, 6.479 chunks e 6.479 embeddings. A
versão anterior permaneceu `ARCHIVED`. O construtor incremental reutilizou 6.079
vetores e gerou 400 em CPU e modo offline, em 264,25 segundos. Uma busca exata por
cosseno no pgvector, usando um chunk da revisão sobre vacinação e doenças
autoimunes, devolveu o próprio chunk em primeiro lugar com similaridade 1,000000.
Esta é uma verificação funcional; o benchmark distribucional permanece para a
Fase 6.

## Atualização do lote 007 da Fase 5

Em 12/09/2026, a versão
`sha256:26171e1196a3672e6a82711ab8c644e5bd662dc079fb275b087f013592c104e4`
foi importada e ativada com 66 documentos, 6.989 chunks e 6.989 embeddings. A
versão anterior permaneceu `ARCHIVED`. O construtor incremental reutilizou 6.479
vetores e gerou 510 em CPU e modo offline, em 305,55 segundos. Uma busca exata por
cosseno no pgvector, usando um chunk da revisão sobre Guillain-Barré como consulta,
devolveu o próprio chunk em primeiro lugar com similaridade 1,000000. Esta é uma
verificação funcional; o benchmark distribucional permanece para a Fase 6.
