# Plano de melhorias ImmunoCheck v4 (retrieval, vereditos, fontes)

> Plano de execução para o agente de IA. Leia as regras de execução antes de qualquer alteração.

## Context

A v3 (BGE-M3 denso top 15, roteador, decisor direto/relacional, seleção de citações) foi promovida
com macro-F1 0,846 num confirmatório de **apenas 32 itens sintéticos / 8 famílias**. Os limites reais:

- **Retrieval:** R@10 denso = 0,625 (≈38% das consultas sem chunk anotado no top 10). O reranker
  deu +0,094 R@10 / +0,19 MRR no desenvolvimento, mas não está em produção. O híbrido RRF atual
  piora o denso. A consulta é a alegação crua; chunks não têm contexto (título/seção); HTML/XML
  sempre citam "p. 1"; metadados (tema, tipo, data) são ignorados; nenhum sinal numérico
  (score, margem) alimenta a abstenção.
- **Vereditos:** a v3 não tem verificador de fidelidade nem guarda de orientação médica individual
  (só existiam na v1). A explicação e `correct_fact` não são conferidos contra o texto; as citações
  são escolhidas depois do veredito. `MISLEADING` é a classe mais fraca (0,625; 0 na v1).
  `confidence` do extrator é calculado e descartado. Risco de truncamento (num_ctx 8192) sem contagem
  de tokens.
- **Fontes:** 80 docs validados (34 do catálogo ainda não validados); 55% dos chunks vêm do
  Ministério da Saúde; 13% sem `publication_date`; licenças conflitantes/`to_verify`; sem OCR de
  PDF escaneado; sem noção de vigência ou hierarquia de evidência.
- **Validade científica:** benchmark 100% sintético, atalhos lexicais (baseline macro-F1 0,61),
  gabarito v3 curado por IA + pesquisador, sem especialista externo.

Objetivo: resultado defensável no TCC, melhorando recuperação, qualidade/segurança do veredito e
qualidade das fontes, **sem violar as restrições do AGENTS.md**.

## Regras de execução (obrigatórias para o agente)

1. Ler `docs/PROJECT_BRIEF.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/ROADMAP.md` antes de agir.
2. Mudança de modelo/pipeline/desenho experimental exige **ADR prévia** (próximas: ADR-044+).
3. **Não reexecutar** conjuntos congelados (teste v1, holdout/confirmatório v3). Usar dados novos.
4. **Não editar** `text_components.py` e módulos congelados por hash (`CANDIDATE_FREEZE.md`);
   criar módulos novos e a opção `PIPELINE_VERSION=v4` (opt-in). v3 permanece padrão até v4 passar
   gates pré-registrados.
5. Branch `feat/v4-<tema>` a partir de `develop`; Conventional Commits em português; sem force push.
6. Gates e hipóteses registrados **antes** de rodar cada experimento; relatar resultados negativos.
7. Sem dados reais de usuário, sem textos de fact-checkers originários dos itens de avaliação,
   sem enviar conteúdo a serviços externos.
8. Testes proporcionais ao risco; rodar a suíte inteira antes de cada commit.

## Fase A: Instrumentação e dados (pré-requisito de tudo)

- **A1. Métricas em nível de documento e de "suficiência"** em `src/immunocheck/evaluation/retrieval.py`
  (hoje só chunk-level: `recall_at_k`, `reciprocal_rank`, `ndcg_at_k`). Adicionar Doc-Recall@k,
  Hit@k por documento e cobertura de evidência (já há 23/24 itens com chunk do mesmo documento,
  logo a métrica por chunk subestima o retrieval).
- **A2. Harness de ablação** (um script, uma tabela): cada técnica ligada/desligada sobre o mesmo
  conjunto, com bootstrap pareado por família (reusar `_family_bootstrap` e
  `_paired_iteration_bootstrap` em `evaluation/development_end_to_end.py`).
- **A3. Novo conjunto v4 (lacrado)**: ≥ 96 itens, ≥ 24 famílias, 4 classes balanceadas, **sem
  moldes repetitivos** (mitigar baseline lexical), incluindo alegações realistas reescritas a partir
  de padrões públicos de desinformação (sem copiar texto de fact-checkers), com itens de
  abstenção "fora do corpus" e "evento individual". Dividir em calibração (≈ 48) e holdout (≈ 48+).
  Segunda anotação em ≥ 50% e idealmente um revisor externo à IA (orientador/profissional de saúde).
  Reusar `benchmark_freeze.py`, `annotation_agreement.py`, `adjudication.py`,
  `validate_end_to_end_dataset.py`.
- **A4. Baseline lexical** (`lexical_baseline.py`) no v4 para provar ausência de atalhos.

## Fase B: Correções de segurança e robustez (baixo risco, sem experimento)

Entram em `develop` mesmo que a v4 não seja promovida (são defeitos, não ganhos de acurácia).

- **B1. Guarda de orientação médica individual na saída da v3**: reaproveitar
  `PERSONAL_MEDICAL_ADVICE` (text_components.py:863-871) num pós-filtro determinístico novo
  (módulo próprio, aplicado em `routed_pipeline.py` na montagem final), com testes.
- **B2. Orçamento de contexto**: contar tokens antes de chamar o Ollama; truncar evidência por
  chunk (não o prompt) e limitar texto vindo de link/OCR antes do extrator (`ollama.py` num_ctx 8192;
  link até 50.000 e OCR até 12.000 caracteres chegam sem limite). Teste com entrada longa.
- **B3. Página/âncora real para HTML/XML** (`chunker.py`, `html_extractor.py`, `xml_extractor.py`,
  `presentation.py:43-44`): citar seção/parágrafo em vez de "p. 1". Requer reingestão incremental
  (reuso de embeddings pelo `chunk_id`).
- **B4. Segurança do bot**: rate limit por chat (em memória, sem persistir identificadores) e
  allowlist opcional por variável de ambiente (`telegram.py`).
- **B5. Pequenas dívidas**: `_ancestors` quadrático em `xml_extractor.py:59-73`; `BM25Index` falha
  com chunk sem tokens; `--top-k` da CLI ignorado na v3; duplicidade de `input_limits`.

## Fase C: Retrieval (experimentos em ordem de impacto esperado)

Todos medidos no calibração v4 com a A2; promoção só se melhorar Doc-Recall@15 e/ou nDCG@10
com IC pareado favorável e latência dentro do alvo do projeto (P95 texto/link ≤ 45 s).

1. **C1. Reranker em produção** (`reranker.py`, `bge-reranker-v2-m3`): denso top 30 → rerank → top 10/15.
   Já medido: nDCG@10 0,461 → 0,615. Custo ≈ 10 s na CPU e 3,97 GB de RAM (cabe em 24 GB).
   O gate de 20 s era do refinamento; o alvo de engenharia é 45 s, reavaliar na ADR.
   Reutilizar `RerankingRetriever`; hoje só scripts o usam (`bootstrap.py` não importa).
2. **C2. Contexto no chunk**: prefixar título do documento/seção ao texto embutido (e ao BM25).
   Chunking por seção/parágrafo, permitindo cruzar páginas com sobreposição (`chunker.py` hoje
   nunca atravessa páginas). Reindexar via `corpus_versioning.py`.
3. **C3. Reescrita de consulta**: gerar 2–3 consultas (PT + EN, termos de vacina/doença/população)
   com o Qwen local, fusão por RRF. Isso ataca o corpus misto PT/EN e a alegação coloquial.
4. **C4. Híbrido corrigido**: trocar `rank_bm25` por (a) BM25 com stopwords + stemming PT, ou
   (b) pesos lexicais esparsos nativos do BGE-M3; fusão ponderada (denso > lexical) em vez de RRF
   simétrico (que perdeu: R@10 0,583 vs 0,625).
5. **C5. Diversificação por documento** (cap de N chunks por documento no contexto final) para
   reduzir domínio do Ministério da Saúde; MMR já falhou, então usar cap determinístico.
6. **C6. Filtros/boost por metadado**: `primary_theme`, `document_type`, vigência. Hoje o runtime lê
   só 7 campos (`pilot_corpus.py:49-69`); expor os demais.
7. **C7. Sinais numéricos**: expor score top-1, margem top-1/top-2 e cobertura para a abstenção (Fase D).

## Fase D: Vereditos (módulos novos, v4 opt-in)

- **D1. Ancoragem verificável**: o LLM deve devolver **trechos literais** (span) dos chunks que
  sustentam `explanation`/`correct_fact`/`omitted_or_distorted`; o código verifica por substring
  normalizada e rebaixa para `INSUFFICIENT_EVIDENCE` (ou remove o campo) se não houver. É
  determinístico, não repete o erro do auditor v3 (segundo classificador LLM que piorou
  `MISLEADING`) e mantém "citações montadas pelo corpus".
- **D2. Abstenção calibrada**: combinar `confidence` do extrator (hoje descartada), score/margem do
  retrieval e voto do LLM; limiares escolhidos na calibração (curva precisão/recall de abstenção),
  congelados antes do holdout.
- **D3. Consistência**: self-consistency (k=3, temperatura baixa) apenas quando o veredito for
  `REFUTED`/`MISLEADING` ou houver baixa margem; discordância → abstenção. Medir custo de latência.
- **D4. `MISLEADING`**: exemplos few-shot no decisor relacional (novo módulo), mais casos
  `MISLEADING` no v4 (ex.: dado real tirado de contexto, causalidade indevida, generalização
  populacional). Meta: recall ≥ 0,70 sem perder precisão de abstenção.
- **D5. Robustez de roteamento**: avaliar o roteador isoladamente (acurácia por rota) e reforçar a
  rota `UNANCHORED_SPECIFIC_EVENT` (falha no item 0031).
- Não usar outro LLM nem serviço externo; Qwen3-8B segue como único modelo.

## Fase E: Fontes e corpus

- **E1.** Validar/decidir os 34 documentos não validados (19 downloaded, 13 candidate) com o fluxo
  de lote existente (`audit_corpus_batch.py`, parecer em `corpus/reviews/`, aprovação humana).
- **E2. Análise de lacunas orientada por falhas**: para cada item do calibração v4 sem evidência
  no top 15, classificar causa (corpus ausente, chunk ruim, consulta ruim). Só então coletar
  novos documentos (OMS, CDC, Anvisa/bulas, SBIm/SBP, Cochrane/revisões sistemáticas), respeitando
  licenças e a regra de não incluir fact-checkers.
- **E3. Metadados de qualidade**: `evidence_tier` (diretriz/normativa > revisão sistemática > estudo
  primário), `superseded`/vigência, preencher `publication_date` dos 1.008 chunks sem data (ou exibir
  `access_date`). Usar na C6 e na exibição.
- **E4.** Resolver licenças `to_verify` (8) e conflitantes (13) antes de qualquer redistribuição;
  manter corpus bruto fora do Git.
- **E5. OCR de PDF escaneado** no ingest (Tesseract já existe em `infrastructure/ocr.py`).

## Fase F: Confirmação e TCC

1. Escolher a configuração v4 **somente** no calibração; congelar (hash) e registrar ADR.
2. Execução única no holdout v4, com os 8+ gates pré-registrados (macro-F1, ganho sobre v3,
   recall `MISLEADING`, precisão de abstenção, citação, falhas, latência).
3. Relatar tabela de ablação completa (inclusive negativos), IC por família, limites de validade.
4. Atualizar `docs/ROADMAP.md`, `TCC_MANUSCRIPT_DRAFT.md` (capítulos de metodologia/resultados/limitações)
   e `HANDOFF.md`. Se não passar nos gates, v3 permanece e o resultado negativo entra no TCC.

## Prioridade sugerida (se o tempo for curto)

1. B1, B2, B3 (segurança/correção). 2. A1–A3 (sem isso nenhum ganho é defensável). 3. C1 + C2.
4. D1 + D2. 5. E1–E3. O restante (C3–C6, D3–D5) se sobrar tempo.

## Verificação

- `pytest` completo (hoje 409 aprovados, 1 ignorado) a cada unidade; novos testes por módulo.
- `scripts/release_preflight.py` ao fim de cada fase.
- Ablação (A2) e relatórios em `evaluation/refinement_v4/` com hashes de congelamento.
- Ensaio real: `scripts/rehearse_demo.py` com Ollama/Telegram usando só entradas sintéticas.
- Conferência de diff antes de commit: sem `.env`, corpus bruto, modelos ou banco local.

## Arquivos críticos

`src/immunocheck/bootstrap.py`, `application/routed_pipeline.py`, `application/text_components.py`
(somente leitura/congelado), `retrieval/{dense,bm25,rrf,reranker,document_expansion,mmr}.py`,
`ingestion/{chunker,html_extractor,xml_extractor,corpus_versioning}.py`,
`infrastructure/{ollama,ocr,web_content}.py`, `telegram.py`, `presentation.py`,
`evaluation/{retrieval,development_end_to_end,benchmark_freeze}.py`,
`docs/{ARCHITECTURE_DECISIONS,ROADMAP,TCC_MANUSCRIPT_DRAFT}.md`.

