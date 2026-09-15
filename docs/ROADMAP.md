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
o validador auditável do dataset fim a fim foram criados. O catálogo possui 114
entradas e o corpus ativo possui 66 documentos, 6.989 chunks e 6.989 embeddings. O
lote 008 propõe os 14 documentos necessários para o mínimo temático, mas aguarda
decisão humana. Também faltam anotar pelo menos 100 alegações, executar a segunda
revisão e congelar o teste; por isso nenhum item de aceite da fase foi marcado como
concluído.

Em 06/09/2026, cinco PDFs do lote 002 foram aprovados pelo autor; outros 14 materiais
ficaram retidos e um candidato não retornou PDF. Em 07/09/2026, a nova versão foi
publicada e validada no PostgreSQL. O parecer completo está em
`corpus/reviews/batch_002.md`.

Em 09/09/2026, os 11 PDFs do lote 003 foram aprovados e publicados; uma nota
técnica permaneceu retida por HTTP 404. A versão com 32 documentos foi ativada no
PostgreSQL após a importação completa dos embeddings. Consultas dirigidas
recuperaram os 11 documentos no top 10 híbrido e o pgvector coincidiu com o NumPy
na verificação densa. O parecer está em `corpus/reviews/batch_003.md`.

Em 09/09/2026, oito documentos do lote 004 foram aprovados conjuntamente e quatro
foram mantidos retidos. Em 10/09/2026, a versão com 40 documentos foi ativada no
PostgreSQL após a importação de 5.313 embeddings. As oito fontes novas apareceram
no top 10 de consultas dirigidas; o parecer está em `corpus/reviews/batch_004.md`.

Em 10/09/2026, o lote 005 foi preparado com 12 candidatos. Dez fontes abertas foram
coletadas e auditadas, somando 766 chunks potenciais; duas páginas da FDA ficaram
retidas por falha segura de validação TLS. O autor aprovou conjuntamente as dez
fontes coletadas, e a versão com 50 documentos e 6.079 embeddings foi ativada no
PostgreSQL. Todas as fontes novas apareceram no top 10 de consultas dirigidas. O
parecer está em `corpus/reviews/batch_005.md`.

Em 12/09/2026, o lote 006 examinou dez candidatos para comunicação, alegações
causais, populações especiais, eficácia e epidemiologia. O autor aprovou oito fontes
e reteve duas por licença não declarada no XML ou HTTP 404 no endpoint integral. A
versão com 58 documentos e 6.479 embeddings foi ativada no PostgreSQL; todas as
fontes novas ficaram em primeiro lugar nas consultas híbridas dirigidas. O parecer
está em `corpus/reviews/batch_006.md`.

Em 12/09/2026, o autor aprovou conjuntamente as decisões do lote 007: oito artigos
foram promovidos, quatro PDFs da OMS sem licença explícita nos bytes permaneceram
retidos e uma duplicata exata foi rejeitada. A versão com 66 documentos e 6.989
embeddings foi ativada no PostgreSQL; todas as fontes novas ficaram em primeiro
lugar nas consultas híbridas dirigidas. O parecer está em
`corpus/reviews/batch_007.md`.

Em 14/09/2026, o autor aprovou a auditoria dos sete documentos legados com licença
`to_verify`. Todos foram mantidos com metadados e restrições explícitos. A versão de
proveniência preservou 66 documentos e 6.989 embeddings, reutilizando todos os
vetores sem reprocessar texto. A decisão está em
`corpus/reviews/license_audit_001.md`.

Em 14/09/2026, o lote 008 foi preparado com 14 candidatos para as lacunas restantes.
Todos passaram pela auditoria técnica e jurídica, somando 596 chunks potenciais sem
duplicata detectada. Os 14 estão propostos para aprovação, com ressalvas de vigência,
generalização e conflitos registradas. Eles ainda não foram promovidos nem publicados;
o parecer está em `corpus/reviews/batch_008.md`.

## Fase 6 — Avaliação e entrega

- [ ] Experimentos de retrieval.
- [ ] Experimentos fim a fim.
- [ ] Métricas de qualidade, segurança e desempenho.
- [ ] Bootstrap e análise qualitativa de erros.
- [ ] Revisão LGPD/ética e consulta institucional quando aplicável.
- [ ] Documentação de reprodução e roteiro de demonstração.

**Aceite:** resultados reproduzíveis, limitações explícitas e versão estável em
`main` pronta para apresentação.
