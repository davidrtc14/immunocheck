# Corpus

O catálogo versionado registra proveniência e situação de cada documento. Os
arquivos brutos ficam em `corpus/raw/`, que é ignorado pelo Git para evitar
redistribuição acidental, crescimento excessivo do repositório e perda de controle
sobre licenças e versões.

## Estados do catálogo

- `candidate`: fonte oficial identificada, ainda não validada localmente.
- `downloaded`: arquivo obtido e hash calculado.
- `validated`: extração revisada e documento aprovado para indexação.
- `rejected`: documento excluído, com justificativa nas observações.

O corpus piloto começa com documentos oficiais sobre normas gerais, calendário,
segurança, eventos adversos, HPV e COVID-19. A inclusão no catálogo não implica
automaticamente aprovação para o corpus definitivo.
Os trechos processados também são reproduzíveis, mas ficam fora do Git com os
arquivos brutos.

Para reproduzir o corpus e auditar sua cobertura:

1. execute `python scripts/download_corpus.py` para baixar candidatos sem apagar
   recibos anteriores (use `--document-id ID` para um lote explícito);
2. execute `python scripts/build_pilot_corpus.py`;
3. consulte `corpus/processed/validation_report.json`;
4. execute `python scripts/audit_corpus_coverage.py` para comparar os documentos
   validados com as metas temáticas.

Uma indisponibilidade de fonte é registrada sem interromper o download das
demais. O coletor desta pasta opera somente sobre o catálogo fixo e seus domínios
oficiais permitidos; ele não deve ser reutilizado diretamente para links enviados
por usuários, que exigem controles adicionais contra SSRF.

## Resultado do piloto em 29/08/2026

- sete documentos validados: 755 páginas, 1.675.261 caracteres e 1.914 trechos;
- uma fonte da OPAS permaneceu candidata porque o servidor recusou o download
  automatizado com HTTP 403;
- uma consulta real sobre dose única de HPV recuperou no topo o Calendário
  Nacional de Vacinação 2026, confirmando o funcionamento básico do BM25.

Esses números validam o corte vertical; não substituem as métricas de relevância
que serão calculadas com consultas e julgamentos anotados na fase experimental.

## Primeiro lote da Fase 5 em 01/09/2026

O lote 001 adicionou 14 candidatos ao catálogo. Treze foram baixados e tiveram a
extração técnica conferida; um manual permaneceu candidato por falhas de TLS/HTTP
nos portais oficiais. Um PDF da OMS foi rejeitado porque a própria obra proíbe
revisão, resumo e reprodução sem permissão. Três páginas da OPAS permanecem fora
do índice enquanto sua condição específica de uso estiver incerta.

Os nove documentos restantes aguardam uma única aprovação humana em lote no arquivo
`corpus/reviews/batch_001.csv`. Materiais de checagem de fatos podem apoiar o corpus,
mas nenhuma alegação do teste final pode ser derivada deles.
