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

- [x] 80–150 documentos catalogados e versionados.
- [x] Cobertura temática revisada.
- [x] 160 alegações com primeira revisão assistida; mínimo de 100 documentado.
- [x] Retorno do segundo anotador em pelo menos 30% (48 itens) e 22 decisões concluídas.
- [x] Divergências adjudicadas e famílias separadas entre os splits.
- [ ] Validade/evidências do benchmark sintético discutidas com o orientador.
- [x] Teste congelado antes do ajuste final.

**Aceite:** hashes, splits, rótulos, evidências e processo de revisão auditáveis.

**Estado:** iniciada em 01/09/2026. O plano de cobertura temática, o template JSONL e
o validador auditável do dataset fim a fim foram criados. O catálogo possui 114
entradas e o corpus ativo possui 80 documentos, 7.585 chunks e 7.585 embeddings.
Todos os mínimos temáticos foram atingidos. Há agora 160 alegações com primeira
revisão assistida e 48 retornos secundários recebidos. Ainda faltam sua incorporação,
adjudicação, auditoria de validade e congelamento;
por isso a Fase 5 permanece aberta.

Automação técnica em 15/09/2026: importação em lote de adjudicação Markdown/JSONL,
montagem de candidato em memória e auditoria somente leitura disponíveis em
`scripts/check_adjudication.py`. A ferramenta verifica proveniência, decisões,
corpus, chunks e mínimos estruturais sem escrever o dataset nem congelar teste.
O roteiro da devolutiva única está em
`evaluation/end_to_end/independent_review/adjudication/README.md`.
Os 22 pareceres e a auditoria semântica humana continuam pendentes; a Fase 6
não foi iniciada por essa automação.

Retorno parcial em 16/09/2026: uma cópia contém 18 decisões fechadas e quatro
pendentes. A conferência automática manteve uma quinta decisão fora do candidato
por ausência de chunk declarado como efetivamente conferido, apesar de haver IDs
candidatos no texto. As páginas locais solicitadas foram encontradas e devolvidas
para conclusão pelo mesmo responsável; um trecho que a própria decisão condicionou
à possível troca de rótulo também foi sinalizado. Os pareceres recebidos não foram
publicados nem incorporados ao dataset. Teste não congelado; Fase 5 ainda aberta.

Retorno revisado no mesmo dia: as 22 decisões ficaram completas, sem exclusões e
sem alteração material de alegações. O candidato em memória passou todos os gates
estruturais exceto a estratificação, pois os rótulos humanos finais produziram
40/49/31/40 itens por classe. Uma troca determinística de duas famílias completas,
oito itens ao todo, restaura as metas inteiras de 60%/40% sem usar previsões do
sistema e sem dividir famílias. O candidato reestratificado é estruturalmente
válido, mas continua local, não publicado, não incorporado e não congelado.
Uma triagem local BGE-M3 ranqueou os 40 pares desenvolvimento/teste mais próximos
para revisão humana. A maior similaridade foi 0,701121 e nenhuma família apareceu
nos dois splits; isso é diagnóstico, não limiar nem certificação de ausência de
vazamento. A interpretação técnica dos pares não identificou repetição do mesmo
fato-alvo. O autor autorizou em seguida a incorporação, a troca, a publicação
desidentificada dos pareceres e o congelamento. O manifesto
`evaluation/end_to_end/freeze_manifest.json` vincula por hash o dataset final, o
snapshot primário, as rodadas, as decisões e o corpus. A parte técnica da Fase 5
está concluída; a validade externa e a revisão das evidências com o orientador
continuam como gate acadêmico e limitação explícita, sem impedir iniciar os
experimentos de desenvolvimento da Fase 6.

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

Em 14/09/2026, o autor aprovou os 14 documentos do lote 008 para as lacunas
restantes. A versão com 80 documentos e 7.585 embeddings foi ativada no PostgreSQL;
todos os mínimos temáticos foram atingidos. As 14 fontes apareceram no top 10 das
consultas híbridas dirigidas, e o pgvector devolveu o próprio chunk consultado com
similaridade 1,000000. O parecer está em `corpus/reviews/batch_008.md`.

Atualização de 15/09/2026 da Fase 5: o lote experimental 001 contém 12 propostas
sintéticas, exclusivamente de desenvolvimento e ainda sem revisão humana.
O guia de anotação e o validador agora operacionalizam os mínimos por classe,
a separação de famílias, o split e a preservação dos rótulos independentes.
Não houve congelamento nem execução do teste definitivo.

Ainda em 15/09/2026, o autor aprovou conjuntamente o lote experimental 001.
Há 12 itens com primeira revisão assistida em `evaluation/end_to_end/items.jsonl`,
zero com segunda anotação e 12 novos candidatos de desenvolvimento no lote 002.
O rascunho do lote 001 foi preservado. O mínimo de 100 itens revisados e todos
os critérios humanos e de teste continuam pendentes.

Preparação conjunta de 15/09/2026: os lotes experimentais 003–012 estão disponíveis
para revisão junto ao lote 002 ainda pendente. O pool contém 160 propostas,
40 por classe, com split previsto 96/64 e hashes de revisão. Apenas 12 itens têm
primeira revisão assistida; 148 permanecem rascunhos e zero têm segunda anotação.
O índice é `evaluation/end_to_end/REVIEW_INDEX.md`. O benchmark é inteiramente
sintético e exige análise de validade com o orientador antes de ser considerado
definitivo. Nenhum experimento foi executado sobre os itens de teste previsto,
e não houve congelamento; a Fase 5 continua aberta.

Aprovação conjunta de 15/09/2026: o autor aceitou todos os lotes experimentais
002–012 sem exceções. Há agora 160 itens com primeira revisão assistida, 40 por
classe, split 96/64, zero segundas revisões. Os rascunhos foram preservados.
O pacote para segundo humano contém 48 tarefas sem respostas, selecionadas por
classe/split com semente registrada. Preparação não equivale a revisão realizada.
Não houve congelamento ou experimento no teste; a validade do benchmark sintético
continua sujeita ao orientador. Próxima ação humana: preencher o pacote independente.

Retorno humano recebido em 15/09/2026: duas rodadas da mesma revisora foram
preservadas em `evaluation/end_to_end/independent_review/returns/`. A versão
revisada declara consulta às fontes e ausência de acesso aos rótulos anteriores;
isso é autodeclaração, não certificação pelo software. São 48 respostas, 32
concordâncias e 16 divergências na rodada revisada (kappa 0,555556). A primeira
rodada tinha 31 concordâncias (kappa 0,527778) e não foi ocultada.
O pacote único `independent_review/adjudication/TASKS.md` contém 22 casos:
16 divergências e seis conferências adicionais. Os retornos continuam separados
de `items.jsonl`, com zero segundas revisões incorporadas ao arquivo final até
resolver as pendências. Nenhum rótulo, split, família, corpus ou teste foi alterado
ou congelado. A Fase 5 segue aberta para adjudicação, auditoria e congelamento.

## Fase 6 — Avaliação e entrega

- [x] Experimentos de retrieval.
- [x] Experimentos fim a fim no desenvolvimento.
- [x] Métricas finais de qualidade, segurança e desempenho textual.
- [x] Desempenho formal controlado de imagem, link e feedback local do Telegram.
- [x] Bootstrap e análise qualitativa de erros no desenvolvimento.
- [x] Revisão técnica LGPD/ética e direitos humanos.
- [ ] Definição institucional de papéis, base legal, canal do titular e CEP/CONEP quando aplicável.
- [x] Pacote fechado de perguntas e recomendações preparado para a decisão institucional.
- [x] Documentação de reprodução e roteiro de demonstração.
- [x] Ensaio automatizado local do roteiro de demonstração.
- [x] Preflight técnico completo do release candidate.
- [x] Ensaio ao vivo com o bot e o ambiente que serão usados na apresentação.

**Aceite:** resultados reproduzíveis, limitações explícitas e versão estável em
`main` pronta para apresentação.

**Estado em 17/09/2026:** o protocolo foi registrado antes das execuções e o
teste de 64 itens permanece selado. O baseline lexical e o retrieval foram
avaliados somente nos 96 itens de desenvolvimento, com bootstrap de 2.000
reamostragens por família. O baseline lexical atingiu macro-F1 0,610, revelando
risco de atalhos sintéticos. Em 72 consultas conclusivas, BGE-M3 superou o
híbrido no ponto estimado; o híbrido + reranker obteve o melhor nDCG@10 (0,615),
mas acrescentou mediana de 10,0 s em CPU. Resultados, intervalos e comandos estão
em `evaluation/results/development/README.md`. A primeira execução das quatro
condições fim a fim foi concluída nos 96 itens de desenvolvimento. A maior
estimativa de macro-F1 foi 0,446, sem superioridade conclusiva entre candidatas;
as condições auditadas tiveram recall zero para `MISLEADING`. A análise encontrou
omissão material no extrator de alegações, que será corrigida e avaliada em uma
v2 separada antes de qualquer execução no teste. A v2 recuperou as três entradas
fora do escopo e elevou o BGE-M3 sem auditor de macro-F1 0,381 para 0,577; o IC
95% pareado do ganho foi +0,114 a +0,281. O auditor elevou o recall de abstenção
de 0,125 para 0,625, mas reduziu macro-F1 para 0,528 e removeu seis previsões
`MISLEADING` corretas. O reranker não melhorou o resultado fim a fim e permanece
fora do caminho padrão.

Calibração de 17/09/2026: a variante v3 foi pré-registrada e executou somente o
auditor sobre as saídas densas congeladas da v2. Ela falhou os gates: macro-F1
0,405, recall zero de `MISLEADING` e delta pareado totalmente negativo contra a
v2 (IC 95% -0,212 a -0,024), apesar de recall de abstenção 0,708 e P95 de 11,6 s.
O candidato foi descartado, o auditor v2 foi restaurado provisoriamente e nenhuma
quarta variante será ajustada nos mesmos 96 itens. Antes do teste único, falta uma
decisão metodológica apoiada por validação externa ou por um conjunto de calibração
novo, além dos demais itens de qualidade, LGPD/ética e reprodução desta fase.

A matriz de decisão e a recomendação de segurança estão em
`docs/FINAL_CONFIGURATION_GATE.md`. Ela recomenda BGE-M3 + auditor v2, mas exige
ciência do orientador e autorização explícita antes da abertura irreversível do teste.

Execução definitiva de 18/09/2026: após confirmação do gate, a configuração
BGE-M3 + auditor v2 foi executada uma única vez nos 64 itens de teste e vinculada
ao commit `52ab0bd`. Obteve macro-F1 0,416 (IC 95% 0,308–0,507), acurácia 0,469,
recall de abstenção 0,750, recall zero de `MISLEADING`, mediana 9,43 s, P95 12,42 s
e zero falhas técnicas. Não haverá ajuste pós-teste. O resultado permite concluir
a prova de conceito, mas não sustenta implantação pública. Naquele momento ainda
faltavam desempenho multimodal, pendências institucionais LGPD/ética e ensaio final
de demonstração; o primeiro item foi concluído no registro seguinte.

Desempenho operacional de 18/09/2026: o protocolo foi publicado no commit
`b80828a` antes de 90 medições controladas. Imagem e link tiveram 30 execuções
completas cada, sem falhas; os P95 foram 10,29 s e 9,07 s, respectivamente. O
feedback local do adaptador Telegram teve P95 de 0,015 ms em 30 execuções. O pico
conservador do sistema inteiro foi 20,28 GiB de RAM e 6,83 GiB de VRAM. As metas
foram atendidas no laboratório. Link e Telegram não incluíram rede externa, e as
imagens foram tipográficas; por isso o resultado não caracteriza internet, Bot API
ou fotos difíceis. O relatório está em
`evaluation/results/performance/OPERATIONAL_PERFORMANCE_REPORT.md`. Permanecem como
gates humanos a definição institucional LGPD/CEP e o ensaio final de apresentação.

Ensaio automatizado de 18/09/2026: texto, imagem, link controlado e recusa de vídeo
passaram pelo adaptador de Telegram em memória. Os três fluxos aceitos enviaram o
feedback antes da pipeline, preservaram todas as seções da resposta e respeitaram o
limite de mensagem; duraram entre 7,55 s e 7,80 s. O registro está em
`evaluation/results/demo/AUTOMATED_REHEARSAL_REPORT.md`. A execução ao vivo com a
Bot API, o token e a apresentação falada permanece como tarefa humana anterior à banca.

Preflight de release de 18/09/2026: o commit `1b56d22` passou nas 18 verificações
técnicas obrigatórias. Foram validados Git limpo e sincronizado, política de arquivos,
benchmark congelado, corpus com 7.585 chunks, índice BGE-M3, artefatos finais,
Qwen3-8B, Tesseract, Docker, Compose, PostgreSQL, Ruff e a suíte com 327 testes
aprovados. A classificação formal é `release_candidate_blocked_by_human_gates`:
tecnicamente pronto, mas sem promoção a `main` até decisão institucional e ensaio ao
vivo. O relatório está em `evaluation/results/release/RELEASE_CANDIDATE_STATUS.md`.

Ensaio ao vivo de 20–21/09/2026: os quatro fluxos funcionais foram exercitados pela
Bot API real no computador de referência. Texto, imagem tipográfica controlada e
link produziram respostas completas; vídeo recebeu recusa clara. Uma imagem com
título e rodapé metalinguísticos falhou na extração da alegação e ficou registrada
como limitação. Duas confirmações de processamento excederam o objetivo de dois
segundos, além de uma indisponibilidade transitória recuperada pelo backoff. Na
repetição instrumentada do commit `33b5dfa`, texto, imagem e link receberam feedback
em 2,743 s, 0,712 s e 0,699 s, sempre antes da pipeline. Como dois segundos é um
objetivo operacional e não um SLA sobre a API externa, a extrapolação isolada de
0,743 s foi aceita como ressalva não bloqueante. O gate ao vivo está fechado, sem
promessa de latência de rede. O registro desidentificado está em
`evaluation/results/demo/LIVE_TELEGRAM_REHEARSAL_REPORT.md`.

Preflight final de 21/09/2026: após o fechamento do ensaio e a correção do caminho
relativo da própria CLI de auditoria, o commit `b3754b8` passou novamente nas 18
verificações técnicas obrigatórias, com Ruff aprovado e 333 testes aprovados. A
classificação permaneceu `release_candidate_blocked_by_human_gates`, agora somente
por `institutional_lgpd_cep_decision`. Nenhum teste final de qualidade foi
reexecutado.

Preparação institucional de 21/09/2026: as fontes oficiais foram revalidadas e uma
solicitação pronta para encaminhamento ao orientador foi criada em
`docs/INSTITUTIONAL_DECISION_REQUEST.md`. O documento antecipa todas as decisões
técnicas possíveis, separa os campos que dependem da instituição e fornece um bloco
desidentificado para registrar o retorno. Isso não fecha o gate: continuam
necessárias as respostas institucionais sobre CEP/CONEP, agentes de tratamento, base
legal, canal do titular e incidente.

Revisão externa incorporada em 21/09/2026: o pacote passou a tratar explicitamente
possível transferência internacional pelo Telegram, operação exclusiva pelo autor
com fixtures pré-definidas, resposta a dado sensível acidental e prazo institucional.
Também foram incluídos a Resolução CNS nº 674/2022 e o Ofício Circular CONEP nº
17/2022, preservando a formulação correta: TCC não recebe dispensa apenas por ser
atividade de ensino, mas o enquadramento integral nas hipóteses normativas continua
dependendo de confirmação institucional. O gate permanece aberto.

## Fase 7 — Refinamento de acurácia v2 (encerrada sem promoção)

- [x] Congelamento metodológico da v1 preservado, sem reabrir o teste final.
- [x] Hipótese e gates da nova linha experimental pré-registrados.
- [x] Diagnóstico automatizado por estágio sobre o desenvolvimento histórico.
- [x] Construção do novo conjunto de calibração (48 propostas em 12 famílias).
- [x] Revisão humana primária assistida dos 48 itens incorporada sem exceções.
- [x] Segunda revisão cega de 16 itens por pessoa distinta.
- [x] Implementação opt-in do gate separado de suficiência da evidência.
- [x] Implementação opt-in da classificação separada da auditoria de fidelidade.
- [x] Comparação controlada com a configuração v1 no novo conjunto.
- [ ] Congelamento da candidata e do novo holdout independente (mínimo de 32 itens).
- [ ] Execução confirmatória única e relatório de promoção ou rejeição.
- [x] Encerramento negativo consolidado após nenhuma candidata satisfazer os gates.

**Aceite:** candidata avaliada em dados novos, com macro-F1 pelo menos 0,08 acima da
v1 no mesmo conjunto de calibração, recall de `MISLEADING` de pelo menos 0,40,
precisão de abstenção de pelo menos 0,45 e taxa de citação relevante de pelo menos
0,60, sem regressão de recall por classe superior a 0,05. O protocolo completo está
em `evaluation/REFINEMENT_V2_PROTOCOL.md`.

**Estado em 22/09/2026:** a auditoria dos 96 registros históricos encontrou 19
regressões e 12 recuperações produzidas pelo auditor. A classe `MISLEADING` teve 16
erros em 19 itens (84,2%), e seis extrações apresentaram recall lexical abaixo de
0,8. A interseção entre citações e evidências anotadas esteve presente em 39 dos 72
itens conclusivos. O diagnóstico não carregou registros do teste e não autoriza nova
calibração nos dados antigos. A próxima unidade de trabalho é construir o conjunto
novo de calibração antes de alterar a pipeline. O gate institucional da Fase 6
continua aberto para disponibilização pública e promoção a `main`, mas não impede
pesquisa técnica local, desidentificada e sem participantes externos.

Preparação de 22/09/2026: o novo pacote de calibração contém 48 propostas em
rascunho, com 12 itens por classe, 12 famílias ausentes do teste v1 e 24 chunks de
evidência rastreáveis em 12 documentos. Cada família contém um caso de cada classe
para testar distinções semânticas dentro do mesmo tema. O validador confirmou
estrutura, equilíbrio, novidade nominal das famílias e existência das referências no
corpus. Isso ainda não é dado de avaliação: falta a revisão humana primária integral
e uma segunda revisão cega de ao menos 15 itens. O holdout v2 não foi criado, para
que seu conteúdo não influencie a implementação da candidata.

Implementação estrutural de 22/09/2026: a candidata experimental agora separa
suficiência, classificação conclusiva e fidelidade. Um gate insuficiente encerra o
fluxo antes do classificador; quando suficiente, somente os chunks pertinentes seguem
para a classificação em três classes. IDs desconhecidos e decisões suficientes sem
fontes falham de forma segura. O auditor factual não recebe autoridade para trocar o
rótulo. A configuração é acessível apenas por builders de refinamento e não alterou o
bot nem a v1. Nenhuma inferência foi executada nos 48 rascunhos; a revisão humana
era o próximo gate antes da calibração naquele marco.

Revisão primária incorporada em 22/09/2026: o retorno final apresentado aprovou as
12 famílias e os 48 itens sem exceções e declara consulta direta às 12 fontes. A
proposta original foi preservada, e um snapshot revisado separado registra rótulo
primário, justificativa, código do papel revisor e data. O comprovante e seu hash
preservam a declaração, sem tratar identidade ou leitura como certificadas pelo
software. Uma reconciliação técnica registra que a família 10 trata de crença ou
endosso da desinformação, que a fonte da família 12 combina revisão sistemática e
modelagem, e que a correspondência direta cobre 36 rótulos conclusivos; os 12 itens
insuficientes dependem da ausência de contexto individual. Uma seleção cega de 16
itens, quatro por classe e cobrindo as 12 famílias, está pronta para uma pessoa
distinta. Nenhuma inferência foi executada e o holdout v2 continua inexistente.

Tentativa de segunda anotação recebida em 23/09/2026: as 16 respostas coincidiram
com os rótulos primários (concordância 1,0; kappa 1,0). O autor esclareceu que os
julgamentos eram do orientador e que uma IA apenas revisou a redação e procurou
falhas. O resultado foi preservado por hash como consistência do mesmo revisor, não
como concordância interavaliadores: a primeira revisão também foi atribuída ao
orientador e o protocolo exige pessoa distinta. Nenhum rótulo foi incorporado. O
pacote foi regenerado com declaração explícita de humanidade e independência.

Segunda devolução recebida em 23/09/2026: o código desidentificado `rv0067` declarou
ser pessoa distinta, não ter consultado os rótulos primários e não ter substituído o
julgamento por LLM. As 16 tarefas foram preenchidas, com resultado provisório de 12
concordâncias e quatro divergências (75%; kappa 0,667). A tarefa 010, contudo, teve
a alegação modificada durante o preenchimento. Para não assumir equivalência
semântica nem enviesar o rótulo, o retorno ainda não foi incorporado; foi emitida uma
correção pontual apenas para o texto original dessa tarefa.

Preparação da adjudicação em 23/09/2026: os três desacordos com alegações intactas
foram auditados contra os chunks vinculados. A recomendação técnica preserva
`MISLEADING` nos itens em que uma premissa real foi usada para afirmar causalidade
universal (tarefas 003 e 011) e `INSUFFICIENT_EVIDENCE` no caso individual de
coqueluche sem investigação (tarefa 012). Não houve decisão humana final, alteração
de rótulo ou inferência da pipeline. A tarefa 010 continua isolada até a correção do
segundo revisor; depois será produzido um único pacote de adjudicação.

Correção e consolidação em 24/09/2026: `rv0067` classificou novamente a tarefa 010
usando o texto original exato e escolheu `INSUFFICIENT_EVIDENCE`, em concordância
com o primeiro rótulo. A segunda anotação independente foi aceita e arquivada por
hash. A concordância final antes da adjudicação é 13/16 (81,25%), com kappa de Cohen
0,75; restam apenas as divergências 003, 011 e 012. Um pacote único com as três
decisões foi preparado, sem executar a pipeline, alterar o snapshot ou criar holdout.

Adjudicação concluída em 26/09/2026: o autor aprovou em lote as três recomendações
do pacote técnico. As tarefas 003 e 011 permaneceram `MISLEADING`, e a tarefa 012
permaneceu `INSUFFICIENT_EVIDENCE`; nenhum rótulo primário foi alterado. Um snapshot
separado registra as 16 segundas anotações e as três decisões, mantendo o snapshot
primário intacto. A calibração v2 está pronta para as três condições pré-registradas;
o holdout continua inexistente e nenhuma inferência havia sido executada nesse marco.

Plano experimental da fase A registrado em 26/09/2026: a configuração definitiva
da v1 e a candidata separada sem auditor serão comparadas nos mesmos 48 itens, com
extração e retrieval denso top 6 compartilhados. O auditor factual só será executado
se todos os sete gates já documentados forem satisfeitos. O script usa checkpoint
incremental, bootstrap por família e bloqueia o teste v1 e o holdout v2.

Fase A executada em 26/09/2026: a v1 obteve macro-F1 0,430 e a candidata separada
sem auditor, 0,373 (delta −0,057; IC percentil por família −0,157 a +0,053). A
candidata teve recall zero de `MISLEADING`, recall 0,083 de `REFUTED` e 38/48
abstenções. Falhou cinco dos sete gates; apenas falha técnica zero e P95 de 14,74 s
passaram. Conforme o plano congelado, a fase B com auditor factual não foi executada,
o holdout continuou fechado e a candidata não foi promovida.

Diagnóstico pós-fase A em 26/09/2026: entre os 36 itens conclusivos, o top 6 denso
continha evidência anotada em 21 (58,3%); houve 14 misses atribuídos ao retrieval,
oito rejeições do gate apesar de evidência anotada, duas seleções inadequadas e cinco
riscos de extração. BGE-M3 denso top 20 elevou a cobertura para 72,2%, superando BM25
(25,0%) e híbrido RRF (63,9%). A ADR-030 registra como próxima iteração a mudança
isolada de top 6 para top 20, sem alterar prompts nem executar auditor.

Iteração top 20 executada em 26/09/2026: a mudança isolada elevou o recall de
`REFUTED` para 0,417, mas manteve recall zero de `MISLEADING`, reduziu balanced
accuracy para 0,396 e produziu quatro IDs inválidos no gate, todos contidos pelo
guardrail. O macro-F1 foi 0,376: +0,003 sobre a candidata top 6 e −0,054 contra a
baseline (IC percentil por família −0,184 a +0,079). Apenas o gate de P95 passou.
A candidata não foi promovida, o auditor não foi executado e o holdout v2 permanece
inexistente. A próxima hipótese deverá combinar recuperação ampla com seleção de
contexto compacto, sem voltar a enviar 20 trechos diretamente à LLM.

Triagem MMR de 26/09/2026: a seleção determinística de seis entre 20 candidatos
densos teve P95 inferior a 0,5 ms, mas derrubou Hit@6 global de 21/36 para 12/36 e
a cobertura de `MISLEADING` de 6/12 para 3/12. Não houve nenhum novo hit e nove
itens antes cobertos foram perdidos. Apenas um de cinco gates passou; por isso a
hipótese foi descartada antes de qualquer chamada de LLM. Teste e holdout seguiram
fechados. O resultado reforça que diversidade vetorial não equivale a pertinência
factual para as alegações do benchmark.

Decisão direta top 6 executada em 26/09/2026: retirar gate e auditor elevou o
macro-F1 para 0,472 e recuperou 11/12 `SUPPORTED`, 10/12 `REFUTED` e 3/12
`MISLEADING`, com P95 de 10,12 s. Em contrapartida, só 1/12 casos insuficientes foi
abstido corretamente. O delta sobre a baseline foi +0,042 (IC percentil por família
−0,090 a +0,190), e apenas três de sete gates passaram. A candidata não foi
promovida e o holdout não foi criado. A calibração agora delimitou os dois extremos:
gate separado excessivamente conservador e gerador direto excessivamente conclusivo.

Triagem do gate de suficiência v2 em 26/09/2026: aliases curtos eliminaram falhas
estruturais e a regra para extrapolações reconheceu como suficientes todos os 36
casos conclusivos, mas também todos os 12 casos que exigiam abstenção. A seleção de
evidência anotada permaneceu em 50%; quatro de seis gates passaram. Nenhuma chamada
ao classificador ou auditor foi feita. O gate não foi promovido, e novos ajustes de
prompt sobre esta mesma calibração ficam suspensos para limitar sobreajuste. A v1
congelada continua sendo o único protótipo demonstrável, com suas limitações já
documentadas.

Encerramento em 26/09/2026: nenhuma condição passou todos os critérios de promoção.
Os dois itens não marcados acima não são pendências operacionais: eram etapas
condicionais que não foram autorizadas pelos resultados. Criar o holdout ou executar
uma confirmação apesar da falha nos gates violaria o protocolo. A ADR-034 encerra a
linha sem promoção, preserva a v1 congelada e direciona o trabalho para consolidação
acadêmica. Consulte `evaluation/refinement_v2/CONSOLIDATION_REPORT.md`.

## Fase 8 — Candidata roteada v3 e confirmação documental

- [x] Decisão relacional com guarda de evento específico avaliada.
- [x] Roteamento estrutural entre especialistas avaliado.
- [x] Seleção dedicada e expansão hierárquica de citações avaliadas.
- [x] Sete gates de calibração satisfeitos sem abrir teste ou holdout.
- [x] Congelamento formal de código, prompts, corpus e hashes da candidata.
- [x] Construção e curadoria documental de conjunto confirmatório com famílias novas.
- [x] Execução confirmatória única e decisão de promoção ou rejeição.

**Concluída em 26/09/2026:** a candidata roteada com citações hierárquicas obteve
macro-F1 0,846 contra 0,482 da v1 em 32 itens e oito famílias novas. O recall
`MISLEADING` foi 0,625, a precisão de abstenção 1,000, a citação exata 0,833, a
falha técnica zero e o P95 19,35 s. Os oito gates passaram; a candidata foi
aprovada para integração controlada ao protótipo, sem alterar automaticamente o bot.
Por decisão metodológica proporcional ao prazo do TCC, a curadoria confirmatória é
feita pelo pesquisador com apoio de IA e evidência rastreável, sem alegação de
revisão clínica independente. Essa limitação deve acompanhar qualquer resultado.

## Fase 9 — Integração controlada da v3 ao protótipo

- [x] Expor a pipeline v3 por builder opt-in, preservando a v1 para comparação.
- [x] Executar testes de regressão, privacidade e formatação das quatro classes.
- [x] Medir texto, imagem e link no caminho real sem reutilizar o conjunto confirmatório.
- [x] Atualizar o bot local e o roteiro de demonstração somente após o preflight.

**Concluída em 26/09/2026:** a v3 foi integrada sem alterar os componentes
congelados, passou a ser o padrão local e mantém a v1 como reversão explícita. A
suíte teve 409 aprovações e uma integração PostgreSQL opcional ignorada; o ensaio
controlado aprovou texto, imagem, link e rejeição de vídeo. Consulte
`docs/V3_INTEGRATION.md`. O teste ao vivo com o bot real permanece uma preparação
manual para a apresentação, não uma fase de desenvolvimento nem fonte de calibração.

## Fase 10 — Consolidação acadêmica e pacote de entrega

- [x] Alinhar a documentação operacional vigente com a arquitetura v3 integrada.
- [x] Consolidar problema, método, arquitetura, resultados e ameaças à validade.
- [x] Separar claramente resultados históricos da configuração demonstrável atual.
- [x] Registrar um índice de evidências e comandos de reprodução para o TCC.
- [x] Proteger por teste as afirmações documentais essenciais sobre a versão ativa.

**Objetivo:** transformar os artefatos técnicos e experimentais já concluídos em um
pacote coerente para redação e apresentação do TCC, sem reexecutar testes congelados,
recalibrar modelos ou declarar encerrado o gate institucional LGPD/CEP.

**Concluída em 26/09/2026:** o pacote `docs/TCC_DELIVERY_PACKAGE.md` consolida a
questão-síntese, objetivos, método executado, arquitetura, resultados, ameaças à
validade, ética e índice de evidências. O guia de reprodução e a revisão de
privacidade foram alinhados à v3, registros históricos receberam rotulagem explícita
e testes automatizados protegem as afirmações essenciais. Nenhum conjunto de
qualidade foi reexecutado e o gate institucional continua aberto.

## Fase 11 — Manuscrito-base e preparação da defesa

- [x] Produzir manuscrito acadêmico-base com capítulos e referências primárias.
- [x] Vincular resultados numéricos aos artefatos experimentais correspondentes.
- [x] Preparar narrativa de defesa com tempo, demonstração e perguntas críticas.
- [x] Manter campos pessoais/institucionais como placeholders explícitos.
- [x] Validar que manuscrito e defesa não exageram validade ou estado regulatório.

**Objetivo:** oferecer material editável para a escrita final e para a apresentação,
sem presumir template institucional não fornecido, autoria clínica, aprovação ética
ou resultado além do que os artefatos reproduzíveis sustentam.

**Concluída em 27/09/2026:** `docs/TCC_MANUSCRIPT_DRAFT.md` organiza problema,
fundamentação, método, arquitetura, resultados, discussão, ética e conclusão em um
texto acadêmico editável. `docs/DEFENSE_PLAN.md` converte o mesmo recorte em uma
apresentação de 12–15 minutos, com demonstração limitada, contingência e respostas
a perguntas críticas. Os números permanecem ligados aos artefatos experimentais,
os campos pessoais continuam explícitos e testes impedem a remoção acidental das
principais limitações. Nenhum template institucional foi presumido.

## Fase 12 — Plano v4, Fase B: segurança e robustez

- [x] B1. Pós-filtro determinístico contra orientação médica individual na saída da v3.
- [x] B2. Orçamento de contexto do LLM e limite de texto de link/OCR antes do extrator.
- [x] B3. Âncoras de seção/parágrafo para HTML/XML no código de ingestão e apresentação.
- [x] B4. Rate limit por chat em memória e allowlist opcional no bot.
- [x] B5. Dívidas: `_ancestors` quadrático, BM25 com chunk sem tokens, `--top-k` na v3 e
  duplicidade de `input_limits`.

**Objetivo:** corrigir defeitos de segurança e robustez sem alterar a candidata v3
congelada (`text_components.py`, `document_expansion.py`, corpus e índice) nem executar
qualquer experimento.

**Estado em 13/10/2026 (branch `feat/v4-seguranca-robustez`):** todos os itens estão
implementados e testados (450 testes aprovados, 1 ignorado por depender de PostgreSQL).
Pendência declarada de B3: o corpus local **não foi reingerido**. Os `chunk_id` não mudam
(ainda usam `p1`), mas as linhas de HTML/XML ganharão o campo `section` e o
`build_key` desses documentos mudou para forçar o reprocessamento. Reingerir altera os
hashes de `chunks.jsonl` e dos índices registrados em `CANDIDATE_FREEZE.md`; por isso a
reingestão fica para decisão explícita, e até lá fontes HTML/XML ainda exibem "p. 1".
O orçamento de contexto (B2) só altera prompts que antes estouravam o `num_ctx` e eram
truncados em silêncio pelo Ollama; prompts que cabem passam inalterados.

## Fase 13 — Plano v4, Fase A: instrumentação e dados

- [x] A1. Métricas em nível de documento e de suficiência de evidência.
- [x] A2. Harness de ablação com bootstrap pareado por família.
- [x] A3. Conjunto v4 lacrado (96 itens, 24 famílias), com curadoria do pesquisador apoiada
  por IA. **Segunda anotação e revisor externo dispensados por decisão do pesquisador**
  (prazo do TCC; mesma política da ADR-040) e declarados como limitação; o pacote cego
  continua disponível em `evaluation/refinement_v4/second_annotation/`.
- [x] A4. Baseline lexical (aprovado na 2ª redação; 1ª reprovada e preservada).

**Concluída em 13/10/2026 com limitação declarada** (sem validação independente nem
concordância entre anotadores). Achado da A2: nenhuma técnica de retrieval superou o denso
top 15 na calibração (efeito de teto: Doc-Recall@15 = 0,93).

## Fase 14 — Plano v4, Fase D (parcial): D1 e D2 calibrados

- [x] D1. Ancoragem verificável implementada (`application/grounding.py`) e calibrada.
- [x] D2. Abstenção calibrada implementada (`application/abstention.py`) e calibrada.
- [~] D4/D5 (`MISLEADING`, roteamento): testadas em `v4_d4`; não adotadas (ver
  `CALIBRATION_D4_RESULTS.md`). D3 (consistência): não iniciada.

**Resultado (13/10/2026):** ver `evaluation/refinement_v4/CALIBRATION_D_RESULTS.md`. A v3 cai de
0,846 (confirmatório) para 0,450 no conjunto v4 de calibração; `MISLEADING` tem recall zero. D1
melhora o macro-F1 em +0,092 mas reprova um critério pré-registrado por uma falha técnica
herdada; D2 tem ganho marginal e estatisticamente inconclusivo. Fase não concluída.

## Fase 15 — Plano v4, Fase F: confirmação no holdout

- [x] Candidata congelada por hashes e gates registrados antes da execução.
- [x] Execução única no holdout v4 (48 itens) para a v3 e para a candidata v4.
- [x] Tabela de ablação completa e resultados negativos relatados.
- [x] Resultado: gates 4/8 reprovados; **v3 permanece como padrão**.

**Concluída em 13/10/2026.** Macro-F1 0,487 (candidata) contra 0,577 (v3), Δ −0,089 (IC por
família −0,194 a +0,008). Ver `evaluation/refinement_v4/HOLDOUT_RESULTS.md`. Limitações: sem
revisor externo, 48 itens, conjunto sintético. As Fases C, E e D3–D5 do plano v4 não foram
executadas além dos experimentos de ablação e calibração já relatados.

## Fase 16 — Linha exploratória v5 (decomposição e agregação determinística)

- [x] Protocolo e ADR-049 registrados antes das inferências.
- [x] Conjunto de paráfrases (2 por item v4) com validador.
- [x] Linha de base de consistência da v3 sob paráfrase.
- [x] Módulos v5 (extração estruturada, NLI por proposição, agregação, multiconsulta) com testes.
- [x] Iteração somente na calibração; congelamento por hash.
- [x] Ablação final única nos 96 itens + paráfrases e decisão pela regra pré-registrada.

Critérios de aceite: suíte completa e Ruff aprovados; relatórios com IC por família,
consistência sob paráfrase, latência e limitações; decisão aplicada conforme
`evaluation/refinement_v5/PROTOCOL.md`. Resultado é exploratório, não confirmatório.

**Concluída em 15/10/2026 como resultado exploratório.** A melhor variante (`v5_multiquery`) obteve
macro-F1 0,653 contra 0,490 da v3 nas 96 alegações originais (IC por família +0,037 a +0,275), mas
reprovou o critério de queda de recall de `SUPPORTED` (0,12 > 0,10); nenhuma variante passou a
regra e a v3 permanece padrão. Limitação: a conferência humana das paráfrases
(`PARAPHRASE_REVIEW.md`) segue pendente. Ver `evaluation/refinement_v5/RESULTS.md`.

## Fase 17 — Extração multimodal medida (ADR-050)

- [x] Benchmark sintético com gabarito automático (capturas, fotos de tela, memes, páginas, PDF,
  mensagens com link e texto encaminhado), com modelos de desenvolvimento e reservados.
- [x] Linha de base de desenvolvimento da extração atual (CER e concordância do veredito).
- [x] Regra de decisão registrada antes das mudanças.
- [x] Camada de compreensão da entrada: OCR em várias passadas com filtro de interface, legenda e
  link na mensagem, conteúdo principal da página com seleção da alegação, limpeza de texto
  encaminhado; alternativa de OCR por visão condicionada à latência.
- [x] Execução final única, nos itens `test` e com os modelos reservados, e decisão pela regra
  (17/10/2026): ganho de +0,10 na concordância, mas reprovação no G6 (falhas 2,19% > 2%); v1
  continua padrão e a v2 fica opt-in. Ver `evaluation/extraction_v1/RESULTS.md`.

Critérios de aceite: suíte completa e Ruff aprovados; relatório com CER, concordância do veredito
por modalidade e modelo, IC por família, latência P95 e limitações; decisão aplicada conforme
`evaluation/extraction_v1/PROTOCOL.md`.

## Fase 18 — Correção da v5 e confirmação em teste externo (ADR-051)

- [x] Teste externo de agências de checagem montado por regra e congelado sem inferência.
- [x] Protocolo e regra de decisão registrados antes das inferências.
- [x] Correções da v5 (trecho tolerante, normalização de números) só na calibração v4; congelamento.
- [x] Execução única: v4 (96 itens) para `v5_fixed`; externo (150) para v3, v5, `v5_fixed` e, se
  couber, `v5_fixed_qwen36`.
- [x] Decisão pela regra pré-registrada (17/10/2026): nenhuma condição promovida; a v3 continua
  padrão. Ver `evaluation/refinement_v6/RESULTS.md`.

Critérios de aceite: suíte completa e Ruff aprovados; relatório com precisão das conclusões, erro
grave, cobertura, IC, estratificação por cobertura do corpus e limitações; decisão aplicada conforme
`evaluation/refinement_v6/PROTOCOL.md`.

## Fase 19 — Nova base de avaliação do veredito (ADR-052)

- [x] Diagnóstico dos erros da v5 nos registros da Fase 18 e protocolo registrado antes da geração.
- [x] Gerador contrastivo com portões automáticos e testes.
- [x] Conjunto C7 gerado (alvo de 400 itens) e dividido por documento.
- [x] Revisão de 80 itens e taxa de erro de rótulo por classe. Desvio declarado: a revisão foi
  assistida por LLM, não humana; houve uma rodada 2 com os 20 fatos de fora do corpus depois do
  portão 8.
- [x] Teste externo 2 montado por regra e congelado.
- [x] Teste do C7 congelado por hash antes de qualquer execução do veredito.
- [x] Link reclassificado como protótipo experimental (ADR-053).

Critérios de aceite: suíte completa e Ruff aprovados nos módulos novos; relatório do conjunto com
distribuição, portões, taxa de erro de rótulo e limitações; congelamento registrado antes da Fase 20.

## Fase 20 — Veredito v7 (ADR-054)

- [x] Adendo com candidatas e regra de decisão registrado antes de qualquer execução nos conjuntos.
- [x] Linhas de base (v3 e `v5_fixed`) no desenvolvimento do C7.
- [x] Seleção progressiva das candidatas C1–C5 no desenvolvimento, com registro de cada versão
  (nenhuma aprovada; C3 trocada pela C3b no Adendo 2).
- [x] Adendo 3 (ADR-055): cascata C6 e via de promoção por segurança, registrados antes do teste.
- [x] Execução da C6 no desenvolvimento, para latência e falhas reais.
- [ ] Configuração congelada por hash até 31/10.
- [ ] Execução única no teste do C7 e no teste externo 2, com as condições v3, `v5_fixed` e C6.
- [ ] Decisão de promoção pela regra e relatório de resultados.

Critérios de aceite: suíte completa e Ruff aprovados nos módulos novos; candidatas desligadas por
padrão e sem edição de arquivos congelados; `DEVELOPMENT_LOG.md` e `verdict_freeze.json` registrados
antes do teste; `RESULTS.md` com todos os critérios e limitações.
