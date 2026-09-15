# Instruções ao segundo anotador

Anote individualmente as alegações de ANNOTATIONS.md, sem consultar os rótulos do
primeiro anotador, pareceres do projeto ou respostas do ImmunoCheck. Não use LLM
para substituir seu julgamento. A ordem e os códigos foram embaralhados.
Este é um benchmark acadêmico controlado, com formulações sintéticas; não é uma
amostra de mensagens reais nem um serviço de aconselhamento médico.

Receba somente esta pasta `participant`. O repositório público contém propostas
de resposta: não o consulte durante a anotação. Informe se já viu rótulos ou
justificativas destes itens; a ausência deles neste pacote não prova cegamento.
O primeiro autor não pode ser o segundo anotador.

## Como preencher

1. Leia a proposição inteira, respeitando produto, população, território e data.
   Não complete dados ausentes nem avalie a pessoa que teria publicado o conteúdo.
2. Consulte diretamente o corpus listado em SOURCES.md, incluindo contexto,
   páginas e tabelas pertinentes. Peça ao responsável acesso ao snapshot local
   para documentos indisponíveis na web, respeitando suas licenças. Não use
   evidências posteriores ao recorte temporal para substituir o que era válido nele.
3. Preencha rótulo, justificativa própria, URLs e trechos/páginas em ANNOTATIONS.md.
   Para falta de evidência, descreva a informação ausente e a busca feita. Ausência
   de menção, por si só, não refuta. Não persiga uma distribuição de classes.
4. Registre dúvidas, tempo aproximado total, data e um identificador interno
   sem nome civil, e-mail ou outros dados pessoais. Devolva o formulário ao autor.
   tasks.jsonl é alternativa estruturada opcional; use apenas um dos formulários.
5. As respostas originais serão preservadas. Discordar é permitido: concordância
   será calculada antes de discutir divergências. Não combine respostas com o autor.

## Rótulos

| Rótulo | Critério |
| --- | --- |
| SUPPORTED | A evidência sustenta diretamente a proposição e seu escopo. |
| REFUTED | A evidência contradiz diretamente a proposição central. |
| MISLEADING | Há parte factual relevante sustentada, mas contexto, alcance ou inferência foi distorcido materialmente. Explicitar ambas as partes. |
| INSUFFICIENT_EVIDENCE | Corpus e informação disponível não permitem sustentar nem contradizer com segurança. Não significa verdadeiro ou falso. |

Se não houver parte factual relevante sustentada, não escolher MISLEADING apenas
porque uma afirmação falsa menciona um tema verdadeiro. Marcar ambiguidades para
adjudicação posterior. Fontes conclusivas precisam sustentar o julgamento, não
apenas mencionar vacinação. Não usar normas gerais para provar evento específico.

O catálogo é completo e não ranqueado por alegação; inclui referências, não cópias
dos documentos. A avaliação se refere ao snapshot do corpus, não a uma busca sem
limites na internet. Registrar indisponibilidade e não adivinhar.
