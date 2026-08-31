# Versionamento e proveniência do corpus

## Objetivo

Cada construção manual do corpus produz uma versão identificável, íntegra e
reproduzível antes de qualquer carga no PostgreSQL. O mecanismo não atualiza fontes
automaticamente e não armazena conteúdo de usuários.

## Artefatos locais

`scripts/build_pilot_corpus.py` publica em `corpus/processed/`:

- `chunks.jsonl`: texto segmentado e proveniência necessária para rastrear a fonte;
- `validation_report.json`: ação e resultado de cada documento na construção;
- `manifest.json`: versão do corpus, parâmetros, hashes e inventário documental.

Esses arquivos permanecem fora do Git porque contêm cópias processadas de documentos
de terceiros. O catálogo `corpus/catalog.csv`, o código e os schemas implícitos nos
testes são versionados.

## Identidade da versão

`corpus_version` é um SHA-256 calculado sobre:

1. versão do schema;
2. versões e parâmetros de extração/chunking;
3. hash canônico de `chunks.jsonl`;
4. registros documentais ordenados por `document_id`.

O horário de geração e o resumo de mudanças não participam da identidade. Assim, a
mesma entrada e a mesma configuração geram a mesma versão, mesmo em execuções
diferentes.

## Proveniência mínima

O manifesto registra, para cada documento: instituição, título, tipo, formato, datas
de publicação/coleta/download, URL catalogada e URL final, condição de uso, tipo e
tamanho do conteúdo, SHA-256 bruto, parâmetros de construção, avisos de extração e
IDs dos chunks. Cada chunk carrega seu próprio SHA-256, o hash do documento e os
metadados necessários para citação e auditoria.

`license_status` documenta a condição conhecida; ele não concede licença nem autoriza
redistribuição. Documentos só entram no corpus quando o catálogo os marca como
`validated` e existe recibo íntegro do download.

## Atualização incremental manual

O construtor compara o manifesto anterior com catálogo, recibos e configuração:

- `added`: documento validado sem versão anterior;
- `reprocessed`: conteúdo, formato ou configuração de processamento mudou;
- `metadata_updated`: conteúdo idêntico, mas metadados/proveniência mudaram;
- `reused`: conteúdo e metadados permanecem idênticos;
- `removed`: documento anterior não está mais aprovado na versão atual.

Chunks inalterados são reutilizados somente depois da validação do hash do arquivo,
do inventário de IDs e do hash de cada texto. Mudanças apenas bibliográficas atualizam
a proveniência sem repetir a extração. Uma falha interrompe toda a construção; não há
publicação parcial intencional.

## Publicação e compatibilidade

Cada arquivo é escrito em caminho temporário e substituído atomicamente. O manifesto
é publicado por último e funciona como marcador de commit da versão. Consumidores
devem conferir `chunks_sha256` antes da carga.

A primeira execução após a adoção deste formato reprocessa o corpus legado, pois ele
não possui manifesto. Como o arquivo JSONL ganha campos e serialização canônica, o
índice denso local anterior deve ser reconstruído antes de novos experimentos, ainda
que os textos e IDs permaneçam iguais.
