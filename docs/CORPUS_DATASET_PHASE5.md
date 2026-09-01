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
- A cobertura temática ainda não foi auditada no corpus ampliado.
- O dataset definitivo ainda não foi anotado.
- O segundo anotador e eventual adjudicador ainda precisam ser formalizados.
- O split de teste ainda não foi criado nem congelado.

Consequentemente, a Fase 5 está em andamento e nenhum item de aceite foi declarado
concluído.
