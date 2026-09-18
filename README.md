# ImmunoCheck

Sistema acadêmico, gratuito e local para verificar alegações sobre vacinação
humana com LLM, RAG e fontes oficiais verificáveis.

## Objetivo

O ImmunoCheck receberá conteúdo por Telegram nos formatos texto, imagem
predominantemente textual e link. A pipeline recuperará evidências de um corpus
versionado e responderá com:

- `SUPPORTED` — sustentada pelas evidências;
- `REFUTED` — refutada pelas evidências;
- `MISLEADING` — parcialmente correta, mas omissa ou descontextualizada;
- `INSUFFICIENT_EVIDENCE` — evidência insuficiente para concluir.

A resposta apresentará explicação em linguagem acessível e referências que o
usuário possa verificar. O sistema não oferece aconselhamento médico individual.

## Escopo da v1

- Execução local em computador doméstico.
- Telegram por long polling.
- Texto, prints/cards por OCR e links HTTPS públicos.
- Corpus prioritariamente formado por Ministério da Saúde, PNI, Anvisa, OMS,
  OPAS e literatura científica selecionada.
- Recuperação semântica local; reranking mantido somente para ablação offline,
  geração local e verificação pós-geração.
- Nenhuma persistência de conteúdo ou identificadores de usuários em produção.

Vídeo, WhatsApp, cache conversacional, fine-tuning e hospedagem permanente são
trabalhos futuros.

## Estado

O corte vertical textual da Fase 1 está funcional. Na Fase 2, o índice BGE-M3 local
e a fusão BM25+dense por RRF já foram implementados. Na Fase 6, o BGE-M3 isolado
teve o melhor equilíbrio fim a fim no desenvolvimento. O reranker melhorou ranking,
mas não a classificação completa e duplicou a latência; permanece apenas como
ablação. A calibração factual do auditor falhou e a configuração conservadora v2 foi
avaliada uma única vez no teste: macro-F1 0,416 e recall zero de `MISLEADING`. O
resultado limita o projeto a protótipo acadêmico, sem implantação pública. O corpus possui manifesto,
proveniência e atualização incremental manual. A persistência PostgreSQL+pgvector,
suas migrations, importação e busca exata foram validadas no Docker local. Consulte
`docs/ROADMAP.md`.

O adaptador Telegram foi testado com um bot real. Texto, imagem textual e link HTTPS
convergem para a mesma pipeline; OCR, download com proteção contra SSRF e extração de
HTML/PDF foram validados na Fase 4. O caminho real usa BGE-M3 e informa
quando analisa somente a alegação principal ou quando as fontes exibidas são parciais.
A parte técnica da Fase 5 está concluída e os experimentos de desenvolvimento da
Fase 6 estão em andamento. Consulte `docs/ROADMAP.md`.

## Executar o protótipo textual

Pré-requisitos locais: Python 3.12, Ollama ativo e o modelo gratuito `qwen3:8b`.
Os arquivos do corpus são gerados localmente e não são versionados.

```powershell
python scripts/download_pilot_corpus.py
python scripts/build_pilot_corpus.py
python scripts/build_dense_index.py --offline
ollama pull qwen3:8b
python -m immunocheck.cli "A alegação sobre vacinação que será verificada"
```

O primeiro uso após carregar o computador é mais lento porque o modelo precisa ser
levado à memória. Nenhuma entrada é persistida pelo protótipo nem enviada a uma LLM
externa.

Após a primeira geração, o índice denso reutiliza embeddings cujo `chunk_id` — e,
portanto, o hash do texto — não mudou. Use `--full-rebuild` somente quando precisar
recalcular todos os vetores; `--offline` impede qualquer consulta ao repositório do
modelo e exige que os pesos já estejam no cache local.

## Executar pelo Telegram

Depois de criar um bot com o BotFather, defina o token apenas na sessão local e inicie
o long polling:

```powershell
$env:TELEGRAM_BOT_TOKEN = Read-Host "Token do bot" -MaskInput
python -m immunocheck.telegram
```

Consulte `docs/TELEGRAM.md` antes do teste operacional. O conteúdo é processado
localmente pelo ImmunoCheck, mas a mensagem também é tratada pelo Telegram para ser
entregue ao bot.

## Documentação

- `docs/PROJECT_BRIEF.md` — escopo e requisitos fixos.
- `docs/ARCHITECTURE.md` — visão de alto nível da pipeline.
- `docs/ARCHITECTURE_DECISIONS.md` — decisões e justificativas.
- `docs/RESEARCH_PROTOCOL.md` — corpus, dataset e avaliação.
- `docs/PRIVACY_AND_ETHICS.md` — LGPD, ética e direitos humanos.
- `docs/REPRODUCTION_AND_DEMO.md` — instalação limpa, reprodução e roteiro de banca.
- `docs/FINAL_CONFIGURATION_GATE.md` — decisão registrada antes da abertura do teste.
- `evaluation/results/test/FINAL_TEST_REPORT.md` — resultado definitivo e limitações.
- `docs/ROADMAP.md` — ordem de implementação e critérios de aceite.
- `docs/PROTOTYPE_VALIDATION.md` — evidências e limitações do teste ponta a ponta.
- `docs/RETRIEVAL_PHASE2.md` — implementação, medições e decisões da recuperação.
- `docs/CORPUS_VERSIONING.md` — manifesto, proveniência e atualização incremental.
- `docs/DATABASE.md` — PostgreSQL, pgvector, migrations e publicação do corpus.
- `docs/TELEGRAM.md` — execução, privacidade e validação do adaptador Telegram.
- `docs/MULTIMODAL_PHASE4.md` — OCR, links seguros, limites e evidências da Fase 4.
- `docs/CORPUS_DATASET_PHASE5.md` — cobertura, anotação e critérios operacionais da Fase 5.
- `evaluation/retrieval/README.md` — protocolo operacional da anotação piloto.
- `evaluation/end_to_end/README.md` — schema e revisão do dataset fim a fim.

## Licença

O código-fonte é disponibilizado sob a licença MIT. Documentos, modelos e datasets
de terceiros mantêm suas próprias licenças e não são automaticamente redistribuíveis
sob a MIT.
