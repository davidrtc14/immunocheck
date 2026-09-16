# Handoff de continuidade — ImmunoCheck

Atualizado em 15/09/2026. Este arquivo resume o contexto necessário para outra
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

**Publicação pendente:** o commit local `73e7915` contém retornos humanos,
relatórios e adjudicação ainda não publicada. O push para o repositório público
foi bloqueado pela revisão automática por ausência de autorização específica
para esse conteúdo. Não tentar novamente, contornar o bloqueio ou interpretar
aprovação metodológica como consentimento para publicação. Solicitar autorização
explícita e verificar a permissão da revisora para compartilhar seus pareceres,
mesmo com identificador interno. O remoto permanece em `fede76d`.

Estado atual após retorno revisado do segundo humano: 48 respostas recebidas,
duas rodadas da mesma revisora, preservadas sem dados pessoais em
`evaluation/end_to_end/independent_review/returns/`. A independência e consulta
às fontes são declaradas no revisado, não certificadas pelo software. Na rodada
inicial houve 31 concordâncias e kappa 0,527778; na revisada, 32 e kappa 0,555556.
Cinco rótulos mudaram entre rodadas. Não ocultar a primeira ou tratar as duas
como revisores independentes distintos. O original inicial não estava mais em
Downloads; os campos foram recuperados do snapshot textual desta tarefa.

Próxima ação: preencher `independent_review/adjudication/TASKS.md`, pacote único
com 22 casos (16 divergências e seis conferências adicionais). Não pedir outra
revisão integral dos 48 itens. As duas anotações estão visíveis na adjudicação;
não chamá-la anotação cega. Registrar decisão humana, fundamento, responsável
interno e data por item. Os arquivos brutos não alteraram `items.jsonl`: esse
arquivo final ainda tem zero segundas revisões incorporadas enquanto há pendências.
`--ready` deve continuar recusando-o. Não registrar adjudicador inexistente ou
aceitar automaticamente a primeira/segunda anotação. Mudanças materiais nas
alegações exigem nova anotação do item; mudanças de classes podem exigir
reconciliação do split/famílias sem forçar cotas. A Fase 5 permanece aberta.

`src/immunocheck/evaluation/annotation_agreement.py` valida pares e calcula
concordância/kappa nominal antes da adjudicação; o script
`scripts/report_annotation_agreement.py` reproduz uma rodada e confere o hash
do dataset primário usado na seleção. `review_receipt.json` registra recebimento,
hashes e pendências; não é congelamento. `selection_manifest.json` conserva
o snapshot de preparação; seus campos de conclusão não são o estado atual.
O corpus de 80 documentos e 7.585 chunks, banco, modelos, prompts, famílias e
splits não mudaram. Não foi executada a pipeline sobre o teste previsto.

Os registros abaixo são históricos, anteriores ao retorno do segundo anotador.

Validação do recebimento: 236 testes aprovados, Ruff e diff sem apontamentos.
Um teste PostgreSQL não foi executado por ausência de base exclusiva configurada;
esta unidade não alterou banco. Foram testados pares completos, IDs/alegações,
datas, códigos internos, preservação das rodadas, kappa, casos degenerados,
hashes e 22 formulários de decisão vazios. O dataset primário segue válido contra
os chunks locais e ainda é recusado como pronto. Temporários não versionados:
`output/pytest-annotation-round002` e `output/pytest-annotation-round002-final`.
Não reutilizar esses diretórios sem considerar a limpeza automática do pytest.

Atualização histórica de 15/09/2026: o autor aprovou explicitamente todos os lotes
experimentais 002–012 (“aprovo tudo, pode seguir”). Há 160 itens com primeira
revisão assistida em `items.jsonl` e `review_pool.jsonl`, 40 por classe, split
96/64, zero segundas revisões. Propostas JSONL originais permanecem imutáveis;
não pedir novamente sua aprovação. Registro em `reviews/batches_002_012.md`.
O corpus e o banco não mudaram; nenhum teste previsto foi executado ou congelado.

A próxima etapa é coletar a anotação de OUTRO humano. O pacote está em
`evaluation/end_to_end/independent_review/participant/`, com formulário Markdown,
JSONL alternativo e catálogo completo não ranqueado de 80 documentos. Entregar
somente essa pasta, nunca o mapa de seleção ou links ao repositório com propostas.
Registrar exposição prévia e procedimento: esconder respostas no pacote não
certifica cegamento. A seleção contém 48 itens (12/classe, 7 dev + 5 teste por classe),
semente 20260915, arredondamento por maiores restos, hash do snapshot e mapeamento
em `independent_review/selection_manifest.json`. Este mapa é somente para auditoria.

`src/immunocheck/evaluation/second_annotation.py` reproduz seleção e textos do
pacote sem LLM ou escrita de arquivos. Campos vazios não contam como anotações.
Não preencher respostas por IA, registrar revisor inexistente ou interpretar
aprovação do autor como anotação independente. Manter retornos brutos separados
até calcular concordância/kappa pré-adjudicação e resolver divergências.

O benchmark é 100% sintético; revisão assistida e correlação por famílias exigem
auditoria de validade com o orientador antes do congelamento. `--ready` deve
recusar o dataset atual por ausência de segunda revisão. A Fase 5 permanece aberta;
não iniciar avaliação final da Fase 6 nem merge para main antes dos aceites.
`review_pool_manifest.json` continua de revisão, com `test_frozen=false` e hashes
SHA-256 normalizados em LF. Os relatos abaixo são históricos.

Validação desta unidade: 219 testes aprovados, Ruff sem apontamentos, diff sem
erros de whitespace e 160 itens aceitos estruturalmente contra o corpus local.
Um teste PostgreSQL foi ignorado por falta de `IMMUNOCHECK_TEST_DATABASE_URL`;
não houve mudança de banco. A suíte confirma seleção determinística/estratificada,
campos de resposta vazios, preservação das propostas e recusa por falta de segunda
revisão. Temporários não versionados: `output/pytest-e2e-second-review` e
`output/pytest-e2e-second-review-final`. Não reutilizar esses caminhos sem considerar
que pytest pode limpar seu conteúdo.

Histórico de 15/09/2026: o autor aprovou conjuntamente o lote
experimental 001. `evaluation/end_to_end/items.jsonl` contém 12 itens com primeira
revisão assistida, não cegada, com rótulos originais preservados. O registro é
`evaluation/end_to_end/reviews/batch_001.md`; não alterar o rascunho original.
O lote experimental 002 contém 12 novas propostas, ainda `draft`, nos temas HPV,
alumínio e BCG. Próxima ação: obter aprovação ou correções desse lote antes de
promover seus itens. Nenhum segundo anotador, teste ou congelamento está registrado.
Os relatos abaixo preservam o histórico anterior à aprovação do lote 001.

Validação desta atualização: 197 testes aprovados, Ruff sem apontamentos e os
dois arquivos aceitos estruturalmente contra o corpus: 12 revisados em
`items.jsonl` e 12 rascunhos no lote 002. Um teste PostgreSQL não foi executado
por ausência de configuração de base exclusiva; não houve alteração no banco.
Temporários não versionados: `output/pytest-e2e-batch002`.

Atualização de 15/09/2026: foi preparado o lote **experimental** 001, distinto
dos lotes documentais, com 12 candidatos sintéticos de desenvolvimento e zero
itens revisados. Leia `evaluation/end_to_end/ANNOTATION_GUIDE.md` e
`evaluation/end_to_end/batches/batch_001.md`. A próxima ação é obter a revisão
do autor sobre os rótulos e evidências, sem converter propostas em revisão por
conta própria. A segunda anotação precisa de outro humano e cegamento; aprovação
do autor não a substitui. Não executar ou ajustar com o teste definitivo antes
do congelamento. O corpus ativo não mudou.

Validação dessa unidade: 194 testes aprovados na suíte geral, um teste de
integração PostgreSQL não executado por ausência da variável de base exclusiva,
Ruff sem apontamentos e 12 itens aceitos na validação estrutural contra o corpus.
O teste automatizado confirma rejeição do lote no modo de revisão obrigatória.
Temporários da suíte: `output/pytest-e2e-batch001`, não versionados. Não houve
migration nem mudança de índice ou banco nesta unidade.

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
