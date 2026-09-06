# Roadmap

## Fase 0 — Fundação

- [x] Repositório local e remoto criados.
- [x] Branch `develop` criada.
- [x] Brief, arquitetura, decisões, protocolo e política de privacidade consolidados.
- [x] `.gitignore`, `.env.example`, pacote Python e teste mínimo criados.
- [x] Python 3.12 acessível no ambiente de desenvolvimento.
- [x] Docker Desktop e Compose acessíveis.
- [x] Ollama e Tesseract detectados no computador.
- [x] Ambiente virtual criado e teste mínimo aprovado.
- [x] Estratégia de branches confirmada no remoto.

**Aceite:** documentação coerente, nenhum segredo versionado, `pytest` aprovado e
ferramentas essenciais detectadas.

## Fase 1 — Corte vertical de texto

- [x] Definir contratos internos da pipeline.
- [x] Implementar orquestrador mínimo com abstenção segura e fontes programáticas.
- [x] Catalogar 5–10 documentos oficiais piloto.
- [x] Extrair, limpar e segmentar o corpus piloto.
- [x] Implementar e validar o baseline BM25.
- [x] Integrar Qwen3-8B local.
- [x] Gerar resposta estruturada com citações válidas.
- [x] Implementar abstenção e guardrails médicos.
- [x] Testar ponta a ponta inicialmente por linha de comando.

**Aceite:** uma alegação textual percorre toda a pipeline e produz resposta
rastreável ou abstenção, com testes automatizados.

O dense retrieval permanece na Fase 2, onde será comparado ao baseline BM25 antes
da adoção do desenho híbrido.

## Fase 2 — Retrieval e ingestão completos

- [x] PostgreSQL + pgvector e migrations.
- [x] Catálogo e controle de versões do corpus.
- [x] Chunking estrutural e metadados de proveniência.
- [x] Dense + BM25 + RRF.
- [x] Dataset piloto de relevância query–chunk.
- [x] Experimento piloto de reranking.
- [x] Métricas de retrieval reproduzíveis.

**Aceite:** melhor configuração escolhida exclusivamente a partir do conjunto de
desenvolvimento, com relatório de métricas e latência.

## Fase 3 — Telegram

- [x] Adaptador por long polling.
- [x] Feedback de processamento anterior à pipeline, com objetivo de até 2 segundos.
- [x] Formatação acessível de veredito e fontes.
- [x] Tratamento de erros e indisponibilidade local.
- [x] Confirmação automatizada de ausência de persistência e logs de conteúdo.

**Aceite:** fluxo de texto funciona no Telegram sem armazenar interações.

**Estado:** fluxo textual executado com um bot real em 31/08/2026 e regressão do extrator
corrigida. A medição formal da distribuição da latência de feedback permanece para o
protocolo de desempenho da Fase 6; o adaptador já mede cada envio e sinaliza violações do
objetivo de dois segundos sem registrar conteúdo ou identificadores.

## Fase 4 — Imagem e link

- [x] OCR local com pré-processamento e limiar de qualidade.
- [x] Rejeição transparente de OCR insuficiente.
- [x] Downloader seguro e proteção contra SSRF.
- [x] Extração de HTML e PDF textual.
- [x] Limites de tamanho, timeout e redirecionamento testados.

**Aceite:** exemplos válidos de imagem e link percorrem a mesma pipeline de texto;
entradas inseguras ou ilegíveis são recusadas.

**Estado:** aceite técnico executado em 31/08/2026 com imagem sintética, HTML público,
PDF textual em memória e testes de rejeição. Limiares de OCR e distribuições de latência
serão avaliados formalmente na Fase 6.

## Fase 5 — Corpus e dataset definitivos

- [ ] 80–150 documentos catalogados e versionados.
- [ ] Cobertura temática revisada.
- [ ] 160 alegações como meta; mínimo de 100 documentado.
- [ ] Segundo anotador em pelo menos 30%.
- [ ] Teste congelado antes do ajuste final.

**Aceite:** hashes, splits, rótulos, evidências e processo de revisão auditáveis.

**Estado:** iniciada em 01/09/2026. O plano de cobertura temática, o template JSONL e
o validador auditável do dataset fim a fim foram criados. O primeiro lote elevou o
catálogo para 22 documentos: 16 validados, 3 baixados retidos por licença, 2
candidatos bloqueados por download e 1 rejeitado por restrição de uso. Nenhum
item acima foi marcado como concluído: ainda faltam ampliar e validar o corpus, anotar
as alegações, executar a segunda revisão e congelar o teste.

Em 06/09/2026, o lote 002 elevou o catálogo a 41 entradas, sem alterar os 16
documentos ativos. Foram propostos cinco PDFs para revisão humana; outros 14
materiais ficaram retidos e um candidato não retornou PDF. O parecer completo
está em `corpus/reviews/batch_002.md`. Preparação não equivale a publicação.

## Fase 6 — Avaliação e entrega

- [ ] Experimentos de retrieval.
- [ ] Experimentos fim a fim.
- [ ] Métricas de qualidade, segurança e desempenho.
- [ ] Bootstrap e análise qualitativa de erros.
- [ ] Revisão LGPD/ética e consulta institucional quando aplicável.
- [ ] Documentação de reprodução e roteiro de demonstração.

**Aceite:** resultados reproduzíveis, limitações explícitas e versão estável em
`main` pronta para apresentação.
