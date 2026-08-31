# Roadmap

## Fase 0 — Fundação

- [x] Repositório local e remoto criados.
- [x] Branch `develop` criada.
- [x] Brief, arquitetura, decisões, protocolo e política de privacidade consolidados.
- [x] `.gitignore`, `.env.example`, pacote Python e teste mínimo criados.
- [x] Python 3.12 acessível no ambiente de desenvolvimento.
- [ ] Docker Desktop e Compose acessíveis.
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

- [ ] PostgreSQL + pgvector e migrations.
- [ ] Catálogo e controle de versões do corpus.
- [ ] Chunking estrutural e metadados de proveniência.
- [x] Dense + BM25 + RRF.
- [x] Dataset piloto de relevância query–chunk.
- [x] Experimento piloto de reranking.
- [x] Métricas de retrieval reproduzíveis.

**Aceite:** melhor configuração escolhida exclusivamente a partir do conjunto de
desenvolvimento, com relatório de métricas e latência.

## Fase 3 — Telegram

- [ ] Adaptador por long polling.
- [ ] Feedback de processamento em até 2 segundos.
- [ ] Formatação acessível de veredito e fontes.
- [ ] Tratamento de erros e indisponibilidade local.
- [ ] Confirmação de ausência de persistência e logs de conteúdo.

**Aceite:** fluxo de texto funciona no Telegram sem armazenar interações.

## Fase 4 — Imagem e link

- [ ] OCR local com pré-processamento e limiar de qualidade.
- [ ] Rejeição transparente de OCR insuficiente.
- [ ] Downloader seguro e proteção contra SSRF.
- [ ] Extração de HTML e PDF textual.
- [ ] Limites de tamanho, timeout e redirecionamento testados.

**Aceite:** exemplos válidos de imagem e link percorrem a mesma pipeline de texto;
entradas inseguras ou ilegíveis são recusadas.

## Fase 5 — Corpus e dataset definitivos

- [ ] 80–150 documentos catalogados e versionados.
- [ ] Cobertura temática revisada.
- [ ] 160 alegações como meta; mínimo de 100 documentado.
- [ ] Segundo anotador em pelo menos 30%.
- [ ] Teste congelado antes do ajuste final.

**Aceite:** hashes, splits, rótulos, evidências e processo de revisão auditáveis.

## Fase 6 — Avaliação e entrega

- [ ] Experimentos de retrieval.
- [ ] Experimentos fim a fim.
- [ ] Métricas de qualidade, segurança e desempenho.
- [ ] Bootstrap e análise qualitativa de erros.
- [ ] Revisão LGPD/ética e consulta institucional quando aplicável.
- [ ] Documentação de reprodução e roteiro de demonstração.

**Aceite:** resultados reproduzíveis, limitações explícitas e versão estável em
`main` pronta para apresentação.
