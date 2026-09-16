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
