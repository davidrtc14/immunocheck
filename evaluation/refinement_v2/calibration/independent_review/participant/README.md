# Segunda anotação cega — calibração v2

Esta pasta contém 16 alegações (33,3% da calibração). O participante não recebe
rótulos, justificativas, evidências pré-associadas nem saídas do ImmunoCheck. A
seleção cobre as 12 famílias da calibração para produzir uma verificação realmente
independente da primeira revisão assistida.

O segundo anotador deve ser uma pessoa distinta do primeiro. Não consulte o
repositório, a revisão primária ou respostas do sistema durante a tarefa. Use o
catálogo completo e não ranqueado de `SOURCES.md`, leia o contexto pertinente e
registre julgamento próprio. Não use LLM para substituir esse julgamento.

## Procedimento

1. Classifique cada alegação como `SUPPORTED`, `REFUTED`, `MISLEADING` ou
   `INSUFFICIENT_EVIDENCE`.
2. Registre uma justificativa e as URLs/partes consultadas. Para insuficiência,
   descreva o que falta e a busca realizada.
3. Não tente reproduzir uma distribuição de classes. Divergências são legítimas.
4. Use um código interno sem nome, e-mail ou outro dado pessoal; registre a data.
5. Preencha `ANNOTATIONS.md` ou `tasks.jsonl`, nunca os dois. Devolva apenas a
   pasta `participant`.

`MISLEADING` exige uma parte factual relevante, mas com contexto, alcance ou
inferência materialmente distorcidos. Ausência de menção não equivale a refutação.
O material é sintético e serve a avaliação acadêmica, não aconselhamento médico.
