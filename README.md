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

O projeto está na Fase 0: fundação, documentação, validação do ambiente e
definição dos critérios de aceite. Consulte `docs/ROADMAP.md`.

## Documentação

- `docs/PROJECT_BRIEF.md` — escopo e requisitos fixos.
- `docs/ARCHITECTURE.md` — visão de alto nível da pipeline.
- `docs/ARCHITECTURE_DECISIONS.md` — decisões e justificativas.
- `docs/RESEARCH_PROTOCOL.md` — corpus, dataset e avaliação.
- `docs/PRIVACY_AND_ETHICS.md` — LGPD, ética e direitos humanos.
- `docs/ROADMAP.md` — ordem de implementação e critérios de aceite.

## Licença

O código-fonte é disponibilizado sob a licença MIT. Documentos, modelos e datasets
de terceiros mantêm suas próprias licenças e não são automaticamente redistribuíveis
sob a MIT.
