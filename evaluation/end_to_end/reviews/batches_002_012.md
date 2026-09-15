# Primeira revisão assistida — lotes experimentais 002–012

Registrada em 15/09/2026 após a aprovação explícita do autor: “aprovo tudo, pode
seguir”, em resposta ao índice de todos os lotes preparados. Nenhuma exceção ou
correção foi indicada. Identificador interno: `project_author`.

## Escopo e rastreabilidade

Aceitos os 148 itens `e2e-0013` a `e2e-0160`, com alegações, rótulos propostos,
recortes e referências dos pareceres. As propostas são as publicadas no commit
`61a87871481845c2d8697f58f70f16177a645d89` e permanecem inalteradas em `batches/`.
O aceite anterior dos 12 itens do lote 001 permanece preservado, inclusive suas
justificativas e notas. Não reescrever o histórico como aprovação independente.

Nos 148 itens foram preenchidos `status=reviewed`, `primary_label`, identificador,
data e justificativas baseadas nas notas aceitas. São 37 itens por classe,
84 de desenvolvimento e 64 de teste previsto. O conjunto passa a 160 itens,
40 por classe e split 96/64. `review_pool.jsonl` reproduz `items.jsonl`.

Corpus inalterado:
`sha256:d6cb49e72edbe28e0958b1e8be440e655c93c972af78383121c04687f2d984a7`.
Os hashes dos arquivos promovidos foram atualizados no manifesto de revisão;
os hashes das propostas originais foram preservados. `test_frozen=false`.

## Limites e próximo procedimento

- Aceite assistido e não cego: justificativas foram redigidas pelo agente e aceitas,
  não transcritas de análises independentes do autor. Não comprova leitura de cada
  fonte, competência especializada ou correção científica de todos os rótulos.
- Nenhuma resposta do ImmunoCheck foi usada para rotular os itens. O teste previsto
  não foi executado e não houve ajuste da pipeline nesta unidade.
- Zero segundas anotações, divergências coletadas, adjudicações ou congelamento.
- Benchmark totalmente sintético e dependente por famílias; manter auditoria
  semântica e consulta ao orientador antes de tratá-lo como definitivo.

A seleção independente contém 48 tarefas, 12 por classe: sete de desenvolvimento
e cinco de teste por classe. Isso aproxima o split na amostra (28/20), cobre os
oito estratos e perfaz 30% do dataset; não exige 30% exatos em cada estrato.
O método usa teto do total e maiores restos por estrato, semente 20260915,
ordem estável por ID e embaralhamento reprodutível. Não seleciona por facilidade
ou resultados do sistema. Seleção por item não elimina correlação por famílias.

Entregar somente `independent_review/participant/` a outro humano. O mapeamento
fica fora dessa pasta, em `selection_manifest.json`; o repositório público contém
rótulos, portanto o procedimento deve registrar exposição prévia. Não atribuir
cegamento apenas à ausência dos rótulos no formulário. Preservar respostas
originais, calcular concordância antes da adjudicação e então resolver divergências.
Preparar o pacote não realiza a segunda anotação nem conclui a Fase 5.
