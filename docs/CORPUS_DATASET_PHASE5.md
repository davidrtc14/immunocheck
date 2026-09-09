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

- O catálogo ainda não possui 80 documentos validados.
- A cobertura temática foi auditada, mas nenhum mínimo por tema foi fechado.
- O dataset definitivo ainda não foi anotado.
- O segundo anotador e eventual adjudicador ainda precisam ser formalizados.
- O split de teste ainda não foi criado nem congelado.

Consequentemente, a Fase 5 está em andamento e nenhum item de aceite foi declarado
concluído.

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

## Preparação do lote documental 004

Em 09/09/2026 foram examinados 12 candidatos para as lacunas de eficácia,
alegações causais, populações especiais e vacinas específicas. Dez documentos
foram coletados e auditados; duas páginas do CDC recusaram a coleta automatizada.
O parecer propõe oito aprovações, que somariam 1.061 chunks potenciais, e quatro
retenções por falta de licença aberta ou de bytes auditáveis.

O lote permanece **aguardando aprovação humana conjunta**. Nenhum candidato do
lote 004 foi promovido, indexado ou importado no PostgreSQL, e o corpus ativo
continua com 32 documentos e 4.252 chunks. O relatório técnico e os guardrails
por fonte estão em `corpus/reviews/batch_004.md`.
