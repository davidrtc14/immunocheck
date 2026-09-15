# Handoff de continuidade — ImmunoCheck

Atualizado em 12/09/2026. Este arquivo resume o contexto necessário para outra
sessão do ChatGPT/Codex continuar o projeto sem depender do histórico desta conversa.

## Objetivo imutável

TCC de Ciência da Computação da UNIPÊ, sem orçamento, para verificar alegações
sobre vacinação humana. A resposta deve apresentar um veredito fundamentado e
fontes verificáveis. Toda ferramenta, modelo, API e dataset deve ser gratuito para
uso acadêmico. LGPD, ética em IA e direitos humanos fazem parte do desenho.

## Decisões aceitas

- Execução local em Ryzen 5 7500F, RTX 4060 de 8 GB e 32 GB de RAM.
- Telegram por long polling na v1; WhatsApp fora da v1.
- V1 recebe texto, imagem predominantemente textual e link; vídeo é trabalho futuro.
- Produção não persiste mensagens, imagens, URLs, respostas ou IDs de usuários.
- Qwen3-8B local como LLM principal; nenhuma LLM externa recebe conteúdo de usuário.
- BGE-M3 + BM25 + RRF é o retrieval adotado; reranker só entra se o experimento
  provar ganho útil.
- PostgreSQL + pgvector persiste apenas corpus e embeddings; interações não têm tabelas.
- Quatro vereditos: `SUPPORTED`, `REFUTED`, `MISLEADING` e `INSUFFICIENT_EVIDENCE`.
- Não oferecer diagnóstico, dosagem ou recomendação médica individual.

As justificativas completas estão em `docs/ARCHITECTURE_DECISIONS.md`.

## Estado no fim da Fase 1

O protótipo textual por CLI está funcional:

```text
texto → extração de alegação → BM25 → Qwen3-8B local
      → veredito JSON → validação de fonte/fidelidade/guardrails → resposta com citações
```

- Corpus piloto: sete documentos oficiais, 1.914 trechos processados localmente.
- Modelo: `qwen3:8b` no Ollama local, GGUF Q4_K_M, cerca de 6,19 GB de VRAM carregada.
- Casos de fumaça: alegação sustentada, alegação refutada, prompt injection ignorado e
  pedido médico fora de escopo abstido.
- Testes automatizados: 59 aprovados no encerramento da fase.
- Resultados e limitações: `docs/PROTOTYPE_VALIDATION.md`.

## Como executar

No diretório do repositório:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\immunocheck.exe "Na vacinação de rotina, adolescentes de 9 a 14 anos devem receber três doses da vacina HPV."
```

Se os artefatos locais não existirem, execute primeiro:

```powershell
.\.venv\Scripts\python.exe scripts\download_pilot_corpus.py
.\.venv\Scripts\python.exe scripts\build_pilot_corpus.py
.\.venv\Scripts\python.exe scripts\build_dense_index.py --offline
ollama pull qwen3:8b
```

`corpus/raw/`, `corpus/processed/`, modelos e `.venv/` são deliberadamente ignorados
pelo Git. Não versionar nem registrar conteúdo de usuários.

## Estado da Fase 2

Concluído:

- BGE-M3 dense, BM25 e RRF;
- avaliação piloto revisada de retrieval e reranker;
- métricas reproduzíveis de relevância e latência;
- manifesto determinístico, proveniência e atualização incremental manual do corpus.
- PostgreSQL 17.11 e pgvector 0.8.6 validados no Docker Desktop, com 7 documentos,
  1.914 chunks e 1.914 embeddings na versão ativa do corpus;
- ranking top 10 idêntico entre índice NumPy e pgvector em consulta de fumaça.

## Estado da Fase 3

O adaptador Telegram por long polling, o feedback anterior à pipeline, os comandos de
ajuda e privacidade, a formatação de respostas e o tratamento sanitizado de falhas estão
implementados. Os testes automatizados confirmam que conteúdo e identificadores não são
persistidos nem incluídos nos logs de erro.

O fluxo textual foi executado com um bot real em 31/08/2026. Um falso negativo do extrator
foi corrigido removendo o uso de autoconfiança não calibrada como barreira anterior ao
retrieval. A medição formal de latência em múltiplas execuções permanece para a Fase 6.
Não registrar o token ou mensagens reais como evidência.

## Estado da Fase 4

Concluídos OCR local com Pillow, OpenCV e Tesseract; qualidade e rejeição transparente;
download HTTPS com IP fixado e proteção contra SSRF; extração em memória de HTML, texto e
PDF; integração de imagem e link ao Telegram e à mesma pipeline. Os testes e ensaios de
referência estão em `docs/MULTIMODAL_PHASE4.md`.

Próxima fase: ampliar e revisar o corpus e o dataset definitivos sem usar interações reais
do Telegram como dados de pesquisa.

## Estado da Fase 5

Os lotes documentais 001 a 008 foram publicados. O catálogo possui 114 entradas e o
snapshot local publicado possui 80 documentos, 7.585 chunks e versão
`sha256:d6cb49e72edbe28e0958b1e8be440e655c93c972af78383121c04687f2d984a7`.
No lote 008, o construtor incremental reutilizou 6.989 vetores BGE-M3 e gerou 596 em
CPU e modo offline, em 376,15 segundos.

O snapshot e os 7.585 embeddings foram importados no PostgreSQL, e a nova versão foi
ativada somente após a verificação de completude. Nas 14 consultas dirigidas, 12
fontes novas ficaram em primeiro lugar e duas em segundo; todas ficaram no top 10.
Uma busca exata no pgvector devolveu o próprio chunk consultado com similaridade
1,000000. A cobertura documental mínima está concluída. A Fase 5 continua aberta
para o dataset de pelo menos 100 alegações, segunda anotação e congelamento do teste.

## Instruções para a próxima sessão

Atualização de 14/09/2026: o lote 007 está aprovado, publicado e validado. Oito
artigos foram promovidos, quatro documentos da OMS permaneceram retidos e uma
duplicata foi rejeitada. Esse era o estado anterior ao lote 008 e permanece como
histórico auditável, não como contagem atual.

A auditoria dos sete documentos legados com licença `to_verify` foi aprovada e
publicada em 14/09/2026. Todos foram mantidos com classificações e restrições
explícitas; a versão de proveniência está registrada em
`corpus/reviews/license_audit_001.md`.

Atualização adicional de 14/09/2026: os 14 documentos do lote 008 foram aprovados,
publicados e validados. O corpus ativo possui 80 documentos e todos os mínimos
temáticos foram atingidos. O parecer, os conflitos declarados, os hashes e os testes
dirigidos estão em `corpus/reviews/batch_008.md`. Continuam pendentes o dataset
definitivo, a segunda anotação e o congelamento do teste. A migration `0002` permite
documentos XML JATS no PostgreSQL; não editar
migrations já aplicadas.
Validação final em 15/09/2026: 184 testes aprovados — 183 na suíte geral e um em
base PostgreSQL exclusiva e descartável —, e Ruff sem apontamentos. O teste geral
usou `-p no:cacheprovider --basetemp output/pytest-batch008-final` para evitar o
diretório temporário global inacessível nesta sessão. A base de teste foi removida.

1. Leia integralmente `AGENTS.md`, `docs/PROJECT_BRIEF.md`,
   `docs/ARCHITECTURE_DECISIONS.md`, `docs/ROADMAP.md` e este arquivo.
2. Trabalhe na branch `develop` e preserve alterações existentes.
3. Antes de qualquer mudança de arquitetura, atualize a ADR correspondente.
4. Siga a política de commit, push e merge vigente em `AGENTS.md`.
5. Ao concluir uma unidade, execute testes, Ruff e os critérios de aceite aplicáveis.
