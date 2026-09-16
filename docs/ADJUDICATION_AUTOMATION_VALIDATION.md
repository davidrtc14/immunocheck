# Validação da automação de adjudicação — 15/09/2026

Unidade técnica da Fase 5, sem conclusão da fase e sem alteração de modelos,
retrieval, banco, canal, política de persistência ou condições experimentais.

## Entregas

- Importador de cópia humana preenchida em Markdown ou JSONL, incluindo decisões
  ainda pendentes, com cobertura exata do pacote e validação de identificadores/data.
- Montagem de candidato em memória com rótulos originais preservados, ledger de
  decisões/exclusões e bloqueio de correções textuais que exigem nova anotação.
- Validador estrutural compartilhado entre carregamento e candidatos, com motivo
  explícito para auditoria documental de erro compartilhado pelos anotadores.
- CLI somente leitura com hashes de proveniência, conferência de corpus quando
  houver pacote completo e relatório de prontidão estrutural, nunca congelamento.
- Orientação para devolutiva única e auditoria humana geral antes do congelamento.

## Verificações executadas

```powershell
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check src/immunocheck/evaluation/end_to_end.py src/immunocheck/evaluation/adjudication.py scripts/check_adjudication.py tests/test_adjudication.py
.\.venv\Scripts\python.exe -X utf8 -m pytest -q -p no:cacheprovider --basetemp output/pytest-adjudication-integrity-final
.\.venv\Scripts\python.exe -X utf8 scripts/check_adjudication.py
.\.venv\Scripts\python.exe -X utf8 scripts/validate_end_to_end_dataset.py
git diff --check
```

Resultado: **273 testes aprovados**, um teste PostgreSQL pulado por ausência de
`IMMUNOCHECK_TEST_DATABASE_URL`; lint aprovado e quatro arquivos Python alterados
com formatação aprovada. A checagem global de formatação também foi tentada e
encontrou diferenças preexistentes em arquivos não envolvidos na unidade;
esses arquivos foram preservados, não reformulados para ampliar o diff.

Os 37 testes novos cobrem importação real do pacote vazio, formatos inválidos,
datas/códigos, alterações silenciosas de alegação, cobertura/duplicatas,
correção de erro compartilhado sem falsificar divergência, exclusão, abstenção,
preservação de rótulos, serialização, evidências desconhecidas e caminho completo
da CLI com snapshot/corpus adulterados. Pareceres completos usados nos testes são
fixtures artificiais isoladas, não decisões atribuídas a pessoas reais.

## Evidência observada sobre o pacote real

- 160 itens permanecem com primeira revisão, 40 por classe, split 96/64.
- 48 respostas secundárias recebidas e zero aplicadas ao dataset autoritativo.
- 22 decisões humanas continuam pendentes; nenhum candidato real foi montado.
- Concordância da rodada revisada permanece 32/48, κ = 5/9, antes da adjudicação.
- Hash normalizado do snapshot primário permanece
  `b3e587898c71c48995fa7c06a3e42c67a022e7bba54147ea78c694dc09401f73`.
- Arquivos arquivados, seleção, rascunhos, corpus, banco e modelos não foram alterados.
- Não houve chamada a LLM, ajuste de prompt/limiar, congelamento ou experimento.

## Pendências que o software não resolve

Devolver o pacote humano completo e registrar auditoria semântica de evidências,
famílias/splits, procedimento e validade do benchmark. Se decisões alterarem
contagens, reconciliar mínimos/estratificação sem manipular rótulos ou separar
famílias. Prontidão estrutural não certifica identidade, expertise, cegamento,
validade científica ou pertinência das fontes. Publicação de novos pareceres e
aceite final de congelamento exigem a autoridade correspondente.

## Retorno parcial validado em 16/09/2026

Uma cópia preenchida e suas correções foram lidas localmente, sem versionar o
conteúdo humano. O parser foi ajustado para a variante de título usada no formulário,
para distinguir “nenhuma correção” de alteração material e, principalmente, para
aceitar como evidência apenas chunks explicitamente marcados como conferidos.
Mencionar um ID como candidato não examinado não o promove mais silenciosamente.

A CLI reconheceu as 22 tarefas, mantendo o snapshot primário e as duas rodadas
inalterados. Quatro decisões estavam declaradas pendentes e uma decisão conclusiva
não tinha chunk efetivamente conferido. Os documentos locais requisitados foram
verificados por hash, chunk e extração independente das páginas dos PDFs; uma
devolutiva técnica foi produzida em `output/`, fora do Git, para que o mesmo humano
conclua o julgamento. Um trecho adicional que a própria decisão humana declarou
capaz de mudar seu rótulo também foi localizado e sinalizado, sem alteração pela IA.

Regressão depois desses ajustes: **277 testes aprovados**, um teste PostgreSQL
pulado por ausência de `IMMUNOCHECK_TEST_DATABASE_URL`; lint e `git diff --check`
aprovados. O dataset autoritativo continua com zero segundas revisões incorporadas,
e `test_frozen` continua falso.

## Pacote concluído e reestratificação proposta em 16/09/2026

A segunda devolutiva resolveu os 22 casos sem exclusões ou mudanças materiais nas
alegações. A montagem em memória preservou rótulos primários/secundários e registrou
adjudicação somente nas 16 divergências; confirmações documentais concordantes
permanecem no ledger, sem fabricar `adjudication_basis`.

As decisões resultaram em 40/49/31/40 itens nas quatro classes. Os splits antigos
ficaram 24/16, 30/19, 18/13 e 24/16, respectivamente. Uma busca determinística por
troca mínima de famílias encontrou um par de quatro itens por lado, restaurando
24/16, 29/20, 19/12 e 24/16. A seleção usa a semente 20260916 e hash como desempate;
não consulta previsões, respostas ou métricas do sistema. O relatório completo,
incluindo hashes e gates humanos, está em `output/PRE_FREEZE_CANDIDATE_REPORT.md`.

O candidato reestratificado passou a validação estrutural, mas permaneceu somente
em memória e não foi congelado. A cobertura secundária após a troca continua em 48
itens: por classe e desenvolvimento/teste, 7/5, 12/9, 1/2 e 8/4.

## Triagem semântica pré-congelamento

O script `scripts/audit_benchmark_semantics.py` aplica somente a troca proposta em
memória, gera embeddings das alegações com BGE-M3 local na revisão fixa
`b28ce2a6fcc9c75ef1c0619575d0ec19af760082` e ranqueia pares entre desenvolvimento
e teste por cosseno normalizado. Ele recusa família presente nos dois splits e não
altera arquivos, rótulos ou modelos.

A execução sobre a proposta produziu identidade
`88118da91882a6701c9e29abb18bb366ded0336cbb5588b0942ae69338f4d03c`, 40 pares para
revisão e máximo 0,701121. Os grupos mais recorrentes refletem moldes genéricos de
causalidade/falha local, revisões de influenza em populações diferentes, estudos de
plataformas de mRNA, e duas famílias distintas sobre poliomielite. Nenhum resultado
é tratado automaticamente como vazamento ou aprovação: não foi definido limiar nem
houve ajuste por desempenho do sistema.

A leitura técnica dos 40 pares não identificou repetição do mesmo fato-alvo entre
splits e recomenda não reagrupar itens nessa etapa. O risco residual mais relevante
é outro: construções sintéticas repetidas podem permitir atalhos lexicais sem que
haja paráfrase factual. A Fase 6 deve, portanto, comparar o pipeline com um baseline
lexical simples e registrar essa limitação na análise de validade.

Ainda faltam interpretação humana dos pares, análise de validade do benchmark
sintético, aceite do orientador e autorização de publicação/incorporação dos novos
pareceres.
