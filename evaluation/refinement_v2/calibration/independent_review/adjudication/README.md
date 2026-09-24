# Adjudicação em lote — calibração v2

`TASKS.md` reúne as três divergências da segunda anotação independente. A tarefa
010 não aparece porque sua correção passou a concordar com o rótulo primário.

O responsável humano deve conferir os três casos e preencher os sete campos de
cada decisão. As recomendações técnicas são apoio explícito, não decisões finais.
É permitido aprovar os três casos de uma vez, desde que o responsável assuma a
decisão, use um código interno desidentificado e registre a data.

Para rótulo conclusivo, a linha de fontes deve conter `Chunk conferido:` ou
`Chunks conferidos:` seguida dos IDs efetivamente verificados. Para
`INSUFFICIENT_EVIDENCE`, deixar a lista de chunks conclusivos vazia e explicar a
informação que falta. Não alterar o texto das alegações.

Conferência local, somente leitura:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\check_refinement_adjudication.py
.\.venv\Scripts\python.exe -X utf8 scripts\check_refinement_adjudication.py `
  "C:\caminho\TASKS_preenchido.md"
```

O comando não modifica dataset, não executa a pipeline e não congela o holdout.

