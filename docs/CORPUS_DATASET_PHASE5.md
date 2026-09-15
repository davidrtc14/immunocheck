# Fase 5 — Corpus e dataset definitivos

## Objetivo e ponto de partida

A fase começou em 01/09/2026 com sete documentos validados, 1.914 chunks e 12
consultas piloto de retrieval. Esse material prova o funcionamento da pipeline, mas
não oferece cobertura suficiente para avaliar alegações compostas como composição,
efeitos alegados e segurança de diferentes vacinas.

O objetivo desta fase é chegar a 80–150 documentos e 100–160 alegações auditáveis,
sem usar mensagens reais de usuários e sem contaminar o teste com ajustes do sistema.

## Ordem de execução

1. Selecionar documentos em lotes de 10–20 segundo `corpus/coverage_plan.csv`.
2. Priorizar inicialmente composição/fabricação, segurança/farmacovigilância e
   alegações causais recorrentes, lacunas expostas pelo teste multimodal.
3. Registrar cada candidato em `corpus/catalog.csv`, inclusive licença, data de acesso
   e justificativa; inclusão como candidato não equivale a aprovação.
4. Baixar, extrair e revisar qualidade, proveniência, data, duplicidade e cobertura.
5. Publicar uma nova versão do corpus e reconstruir BM25, embeddings e manifesto.
6. Produzir alegações atômicas reescritas no dataset fim a fim, sempre separadas do
   corpus de conhecimento.
7. Revisar 100% com o anotador principal e pelo menos 30% de forma independente.
8. Adjudicar divergências e congelar o split de teste antes do ajuste final.

## Cobertura documental

Cada documento recebe um tema primário. As metas do plano somam mínimo de 80 e máximo
de 140 documentos, dentro do intervalo metodológico; temas secundários podem ser
registrados nas notas do catálogo. A seleção prioriza Ministério da Saúde/PNI, Anvisa,
OMS, OPAS e literatura científica revisada por pares. Fact-checkers não entram como
evidência para itens derivados deles.

Uma fonte só passa a `validated` após conferência humana do título, instituição,
versão, data, conteúdo extraído, condição de uso e utilidade temática. Páginas
dinâmicas, duplicatas, materiais sem proveniência e textos opinativos são rejeitados
com justificativa preservada.

## Dataset fim a fim

O arquivo futuro `evaluation/end_to_end/items.jsonl` seguirá o template versionado.
O validador impõe:

- IDs e alegações sem duplicidade;
- alegações atômicas e com até 600 caracteres;
- quatro rótulos e splits `development`/`test`;
- chunks existentes para todo veredito conclusivo;
- ausência de evidência conclusiva para `INSUFFICIENT_EVIDENCE`;
- responsável, data e justificativa em todo item revisado;
- segunda revisão completa e adjudicação de divergências;
- mínimo de 100 itens, quatro classes e 30% de segunda revisão no modo `--ready`.

O template não é dado de avaliação e não deve ser contado. Rótulos serão definidos
por leitura das fontes, nunca pela resposta atual do ImmunoCheck.

## Critérios que ainda impedem o fechamento

O corpus atingiu 80 documentos validados e todos os mínimos temáticos; essa parte
documental está concluída e auditada. Permanecem pendentes:

- O dataset definitivo ainda não foi anotado.
- O segundo anotador e eventual adjudicador ainda precisam ser formalizados.
- O split de teste ainda não foi criado nem congelado.

Consequentemente, a Fase 5 continua em andamento, agora concentrada na construção e
revisão do dataset experimental.

Em 14/09/2026, o autor aprovou os 14 documentos do lote 008, escolhidos para preencher
as sete lacunas temáticas restantes. Os documentos passaram pela obtenção, extração,
auditoria de licença e detecção de duplicidade, somando 566.342 caracteres e 596
chunks. O catálogo possui 114 entradas e o corpus ativo passou a 80 documentos, com
ressalvas explícitas de vigência, generalização, causalidade e conflitos de interesse.
O parecer está em `corpus/reviews/batch_008.md`.

Em 14/09/2026, o autor aprovou conjuntamente a auditoria dos sete documentos legados
que ainda possuíam licença `to_verify`. Dois PDFs declaram CC BY-NC-SA 4.0; três
páginas declaram CC BY-ND 3.0; um PDF concede reprodução não comercial com
atribuição; e a Instrução Normativa é tratada como ato oficial nos termos do art.
8º, IV, da Lei nº 9.610/1998.

A correção de proveniência gerou a versão
`sha256:8dfd3d854c8855f71f34d6b5c9bba8e04acb106f43127f2a78659a2ea43d6dc9`,
com os mesmos 66 documentos, 6.989 chunks e 6.989 embeddings. Os sete documentos
tiveram apenas metadados atualizados, nenhum texto foi reprocessado e todos os
vetores foram reutilizados. O parecer e as restrições estão em
`corpus/reviews/license_audit_001.md`.

## Execução do lote documental 001

Em 01/09/2026 foram catalogadas 14 novas fontes oficiais. O coletor incremental
preservou os recibos existentes e obteve 13 fontes. Nove passaram pela revisão
técnica de extração e condição de uso e foram aprovadas conjuntamente pelo autor; três
páginas da OPAS ficaram retidas por incerteza de licença; um PDF da OMS foi
rejeitado por restrição expressa; e o manual CRIE permaneceu candidato após falhas
seguras de HTTP/TLS. A trilha completa está em `corpus/reviews/batch_001.csv`.

O campo obrigatório `primary_theme` agora é propagado ao manifesto e aos chunks.
O relatório `corpus/coverage_report.md` é gerado pelo script de auditoria e torna as
lacunas temáticas mensuráveis. A aprovação do lote não congela o dataset nem permite
derivar itens de teste das páginas de checagem de fatos.

A publicação resultante possui 16 documentos e 2.675 chunks na versão
`sha256:9aaa8323aefc9186e22dce3c79cb8ad73b0bda4fe3426c8c101221048dfd7510`.
O índice BGE-M3 reutilizou 1.914 embeddings com IDs textualmente estáveis e gerou
761 novos em 381,27 segundos, sempre em CPU e modo offline. Consultas diagnósticas
colocaram em primeiro lugar a fonte esperada para componentes, autismo, alegação de
vacinas experimentais e conservação por temperatura. Esses testes são fumaça e não
substituem o conjunto de avaliação congelado.

Depois da validação do artefato local, os 2.675 embeddings foram importados e a nova
versão foi ativada no PostgreSQL. O ranking denso top 10 do pgvector coincidiu
exatamente com o índice NumPy local na consulta de fumaça sobre chumbo na vacina
contra gripe.

## Execução do lote documental 002

Em 06/09/2026 foram examinados 20 candidatos: 19 novos e a retomada do CRIE,
agora obtido no espelho oficial DIVE/SC. Cinco PDFs foram aprovados pelo autor
após a auditoria e promovidos para `validated`; 14 materiais ficaram retidos e
um download foi recusado por não retornar PDF. O catálogo possui 41 entradas:
21 validadas, 17 baixadas aguardando decisão, duas candidatas e uma rejeitada.

Os cinco aprovados possuem licença CC BY-NC-SA 4.0 explícita. Treze HTMLs ficaram
retidos por avisos conflitantes de licença e um calendário por problemas de
estrutura/edição e licença pendente. O informe de dengue retornou HTML de acesso
restrito em vez de PDF e permanece candidato.

O parecer conjunto, os cuidados e os pontos de leitura estão em
`corpus/reviews/batch_002.md`; decisões e responsável em `batch_002.csv`; hashes
e métricas em `batch_002.audit.json`. A rotina `scripts/audit_corpus_batch.py`
é offline e não promove fontes nem publica índices.

Em 07/09/2026, a versão
`sha256:5e21bdfbe417e471ce7ac1c34d0d239c79fb619a751228cd3616b9772da09f31`
foi ativada com 21 documentos, 3.532 chunks e 3.532 embeddings. Foram reutilizados
2.675 vetores e gerados 857 novos. Consultas diagnósticas recuperaram cada novo
documento no top 10 híbrido, e o ranking denso top 10 do pgvector coincidiu com o
NumPy no caso VSR. Auditoria de licença dos sete documentos legados marcados
`to_verify` também deve anteceder o fechamento desta fase.

## Execução do lote documental 003

Em 07/09/2026 foram catalogados 12 candidatos oficiais do Ministério da Saúde.
Onze PDFs foram obtidos e passaram por auditoria técnica, de permissão de uso e
amostragem visual: 309 páginas e 720 chunks potenciais. Cinco declaram CC
BY-NC-SA 4.0 e seis permitem expressamente reprodução com atribuição e sem
finalidade comercial. A nota técnica de febre amarela retornou HTTP 404 e ficou
retida.

Em 09/09/2026, os 11 PDFs foram aprovados conjuntamente pelo autor e promovidos
para `validated`. A versão
`sha256:8e605597e2cc3d55a09cffbb7dde6396d5df34452b22179dee0fa65585959364`
foi ativada com 32 documentos, 4.252 chunks e 4.252 embeddings. O BGE-M3
reutilizou 3.532 vetores e gerou 720 em CPU, offline, em 356,41 segundos.

Consultas dirigidas recuperaram os 11 documentos novos no top 10 híbrido, e o
ranking denso top 10 do pgvector coincidiu com o NumPy no caso de segurança da
dengue. A lacuna para o mínimo temático caiu a 48 documentos. O lote amplia normas,
comunicação/equidade, vacinas específicas, segurança e epidemiologia, mas não
substitui o futuro lote de evidência causal revisada por pares. O parecer e as
limitações estão em `corpus/reviews/batch_003.md`.

## Execução do lote documental 004

Em 09/09/2026 foram examinados 12 candidatos para as lacunas de eficácia,
alegações causais, populações especiais e vacinas específicas. Dez documentos
foram coletados e auditados; duas páginas do CDC recusaram a coleta automatizada.
O parecer propôs oito aprovações, somando 1.061 chunks, e quatro retenções por falta
de licença aberta ou de bytes auditáveis. O autor aprovou conjuntamente essas
decisões em 09/09/2026.

Em 10/09/2026, a versão
`sha256:2a2ed2ce976165327677dd7f238d31407a93cdb3428f9e449bc25a7a955e92cc`
foi ativada com 40 documentos, 5.313 chunks e 5.313 embeddings. O BGE-M3 reutilizou
4.252 vetores e gerou 1.061 em CPU, offline, em 508,95 segundos. A publicação exigiu
a migration `0002`, que permite XML JATS no catálogo persistido sem alterar a
política de dados. Consultas dirigidas recuperaram as oito fontes no top 10 e o
pgvector coincidiu com o NumPy na consulta sobre tiomersal e autismo. O relatório
técnico e os guardrails por fonte estão em `corpus/reviews/batch_004.md`.

## Execução do lote documental 005

Em 10/09/2026 foram examinados 12 candidatos voltados a composição, eficácia,
populações especiais e vacinas específicas. Nove artigos XML JATS e um relatório
integral em PDF foram coletados e auditados: 147 páginas/unidades documentais,
721.446 caracteres e 766 chunks potenciais, sem duplicatas exatas. Duas páginas
regulatórias da FDA ficaram retidas porque o coletor não conseguiu validar a cadeia
TLS; a verificação de certificado não foi desativada.

O autor aprovou conjuntamente os dez documentos coletados, todos com licença aberta
explícita. As ressalvas incluem distinção entre imunogenicidade e efetividade clínica,
heterogeneidade, risco de viés, recortes populacionais, conflitos declarados e caráter
modelado de parte do relatório pneumocócico.

A versão
`sha256:f15c0ebd67783ccf16552c5230b230c73cde02ccd42a9888102510c5cf4e0119`
foi ativada com 50 documentos, 6.079 chunks e 6.079 embeddings. O BGE-M3
reutilizou 5.313 vetores e gerou 766 em CPU, offline, em 552,95 segundos. Consultas
dirigidas recuperaram as dez fontes novas no top 10 híbrido, e uma busca exata no
pgvector devolveu o próprio chunk consultado com similaridade 1,000000. A lacuna
para o mínimo temático caiu a 30 documentos. O parecer completo está em
`corpus/reviews/batch_005.md`.

## Execução do lote documental 006

Em 12/09/2026 foram examinados dez candidatos para comunicação, alegações causais,
populações especiais, eficácia e epidemiologia. Nove XML JATS foram coletados e
auditados, somando 430.407 caracteres e 434 chunks potenciais. Não houve duplicata
exata dentro do lote nem contra o corpus validado.

O autor aprovou conjuntamente oito fontes, somando 400 chunks, e manteve duas
retidas. O artigo da Revista Panamericana sobre coqueluche não declara licença nos
bytes coletados; o manuscrito sobre hospitalizações por rotavírus não retornou XML
integral. A decisão e os guardrails por fonte estão em
`corpus/reviews/batch_006.md`.

A versão
`sha256:253c380014fb96f32be9dd3f47629ee055d1218bff85c594c757f8891d6754cb`
foi ativada com 58 documentos, 6.479 chunks e 6.479 embeddings. O BGE-M3
reutilizou 6.079 vetores e gerou 400 novos em CPU, offline, em 264,25 segundos.
Consultas dirigidas colocaram cada fonte nova em primeiro lugar no ranking híbrido;
uma busca vetorial exata no pgvector devolveu o próprio chunk consultado com
similaridade 1,000000. A lacuna para o mínimo temático caiu de 30 para 22
documentos.

## Execução do lote documental 007

Em 12/09/2026 foram coletados e auditados 13 candidatos voltados às lacunas de
normas, composição e fabricação, segurança e vacinas específicas. Todos passaram
pela extração técnica, totalizando 1.203.329 caracteres e 1.243 chunks potenciais.

O autor aprovou conjuntamente oito artigos novos, somando 510 chunks e com licenças
Creative Commons explícitas. Quatro *position papers* da OMS foram mantidos retidos
porque os PDFs coletados não contêm licença ou permissão de reutilização. Um nono
artigo aberto, duplicata bruta exata de `eclinm_rotavirus_global_2025`, foi rejeitado
para evitar peso duplicado no retrieval. A trilha está em
`corpus/reviews/batch_007.md`.

A versão
`sha256:26171e1196a3672e6a82711ab8c644e5bd662dc079fb275b087f013592c104e4`
foi ativada com 66 documentos, 6.989 chunks e 6.989 embeddings. O BGE-M3
reutilizou 6.479 vetores e gerou 510 novos em CPU, offline, em 305,55 segundos.
Consultas dirigidas colocaram cada fonte nova em primeiro lugar no ranking híbrido;
uma busca vetorial exata no pgvector devolveu o próprio chunk consultado com
similaridade 1,000000. A lacuna para o mínimo temático caiu de 22 para 14
documentos.

## Execução do lote documental 008

Em 14/09/2026 foram coletados e auditados 14 candidatos: quatro fontes normativas,
duas de eficácia, duas de populações especiais, duas de epidemiologia, duas de
alegações causais, uma de vacina específica e uma de comunicação/equidade. Não houve
falha técnica nem duplicata; as licenças e bases de reutilização foram explicitadas.

O autor aprovou conjuntamente os 14 documentos. A revisão de vacinas de mRNA
em imunocomprometidos foi financiada pela Moderna e contou com empregados da
empresa; a revisão pneumocócica regional recebeu grant independente da Pfizer; e a
revisão de influenza declara relações de autores com fabricantes e comitês. Esses
vínculos não implicam rejeição automática, mas exigem triangulação e permanecem nos
metadados.

A versão
`sha256:d6cb49e72edbe28e0958b1e8be440e655c93c972af78383121c04687f2d984a7`
foi ativada com 80 documentos, 7.585 chunks e 7.585 embeddings. O BGE-M3 reutilizou
6.989 vetores e gerou 596 em CPU e modo offline, em 376,15 segundos. Nas consultas
híbridas dirigidas, 12 fontes ficaram em primeiro lugar e duas em segundo; todas
apareceram no top 10. A busca exata no pgvector devolveu o próprio chunk consultado
com similaridade 1,000000. A lacuna temática mínima chegou a zero. A trilha de
decisão está em `corpus/reviews/batch_008.md`.

## Preparação do lote experimental 001

Em 15/09/2026 foram preparados 12 candidatos sintéticos para desenvolvimento,
três propostas por classe, com evidências referenciadas no snapshot do lote 008.
São nove formulações baseadas em fontes e três cenários fictícios indeterminados;
não são mensagens de usuários nem previsões do sistema. Todos continuam `draft`.

O parecer para revisão está em `evaluation/end_to_end/batches/batch_001.md` e
o procedimento em `evaluation/end_to_end/ANNOTATION_GUIDE.md`. O validador exige
no aceite 25 itens por classe, split 60%/40%, separação por famílias e preservação
do primeiro rótulo para concordância pré-adjudicação. Também recusa identificadores
iguais nas duas revisões, sem pretender certificar identidade ou cegamento.

Estado: 12 candidatos; zero revisados; mínimo de 100 e meta de 160 ainda pendentes.
Esse lote calibra o manual, não demonstra qualidade em notícias reais. A Fase 5
continua aberta para revisão humana, ampliação, segunda anotação e congelamento.

## Aprovação do lote experimental 001 e preparação do 002

Em 15/09/2026, o autor aprovou conjuntamente os 12 itens do lote experimental 001.
Os rótulos aceitos, justificativas assistidas, datas e identificação interna do
autor foram registrados em `evaluation/end_to_end/items.jsonl`. O rascunho foi
preservado; a trilha e as limitações estão em
`evaluation/end_to_end/reviews/batch_001.md`. Esse aceite é primeira revisão
assistida e não prova revisão independente das fontes nem competência especializada.

O lote 002 propõe mais 12 itens sintéticos de desenvolvimento sobre HPV, alumínio
e BCG, com evidências rastreáveis e três cenários fictícios indeterminados. Todos
permanecem pendentes em `evaluation/end_to_end/batches/batch_002.jsonl`. O corpus
não mudou, e nenhuma previsão do sistema foi usada para anotação ou seleção.

Estado atual: 12 itens com primeira revisão, 12 candidatos pendentes e zero com
segunda anotação. Faltam 88 itens revisados para o mínimo de 100, além da revisão
independente e do teste estratificado congelado. Itens de calibração sintéticos
não serão usados para alegar representatividade de notícias reais.
