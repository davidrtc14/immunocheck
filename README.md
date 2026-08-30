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
- Recuperação lexical e semântica, reranking condicionado a evidência experimental,
  geração local e verificação pós-geração.
- Nenhuma persistência de conteúdo ou identificadores de usuários em produção.

Vídeo, WhatsApp, cache conversacional, fine-tuning e hospedagem permanente são
trabalhos futuros.

## Estado

O corte vertical textual da Fase 1 está funcional: uma alegação percorre extração,
BM25 sobre o corpus piloto, Qwen3-8B local, validação estruturada, auditoria de
fidelidade e apresentação de fontes. A próxima fase implementará recuperação densa
e avaliação de retrieval. Consulte `docs/ROADMAP.md`.

## Executar o protótipo textual

Pré-requisitos locais: Python 3.12, Ollama ativo e o modelo gratuito `qwen3:8b`.
Os arquivos do corpus são gerados localmente e não são versionados.

```powershell
python scripts/download_pilot_corpus.py
python scripts/build_pilot_corpus.py
ollama pull qwen3:8b
python -m immunocheck.cli "A alegação sobre vacinação que será verificada"
```

O primeiro uso após carregar o computador é mais lento porque o modelo precisa ser
levado à memória. Nenhuma entrada é persistida pelo protótipo nem enviada a uma LLM
externa.

## Documentação

- `docs/PROJECT_BRIEF.md` — escopo e requisitos fixos.
- `docs/ARCHITECTURE.md` — visão de alto nível da pipeline.
- `docs/ARCHITECTURE_DECISIONS.md` — decisões e justificativas.
- `docs/RESEARCH_PROTOCOL.md` — corpus, dataset e avaliação.
- `docs/PRIVACY_AND_ETHICS.md` — LGPD, ética e direitos humanos.
- `docs/ROADMAP.md` — ordem de implementação e critérios de aceite.
- `docs/PROTOTYPE_VALIDATION.md` — evidências e limitações do teste ponta a ponta.

## Licença

O código-fonte é disponibilizado sob a licença MIT. Documentos, modelos e datasets
de terceiros mantêm suas próprias licenças e não são automaticamente redistribuíveis
sob a MIT.
