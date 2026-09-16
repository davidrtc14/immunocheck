# Devolutiva única e incorporação técnica

`TASKS.md` contém 22 casos pendentes: 16 divergências e seis conferências
documentais adicionais. Aprovar o desenvolvimento não preenche esses pareceres.
O original tem hash no recibo: devolva uma **cópia preenchida**, sem editá-lo.

## Devolver tudo junto

1. Preencher os sete campos de decisão de todos os casos na cópia de `TASKS.md`.
2. Usar os quatro rótulos em inglês ou `PENDENTE`; indicar ação `manter`,
   `corrigir`, `excluir` ou `pendente`. A ação refere-se ao tratamento do item,
   não obriga a conservar o primeiro rótulo. Pode corrigir rótulo sem mudar alegação.
3. Registrar justificativa própria, fontes efetivamente conferidas e trecho/página.
   Para decisões conclusivas, copiar também os IDs dos chunks conferidos na linha
   de fontes. Os candidatos não são evidência automaticamente aprovada.
   Para `INSUFFICIENT_EVIDENCE`, não incluir IDs de evidência conclusiva; explicar
   a busca e a insuficiência das fontes.
   Para rótulo conclusivo, introduzir os IDs efetivamente vistos com `Chunk
   conferido:` ou `Chunks conferidos:`. IDs descritos como candidatos, não abertos
   ou não verificados são deliberadamente ignorados pelo importador.
4. Usar código interno do responsável, sem nome civil ou instituição, e data
   `AAAA-MM-DD` ou `DD/MM/AAAA`. O código não certifica identidade ou expertise.
5. Correções materiais na alegação precisam de nova anotação. Exclusões também
   precisam de motivo, responsável e data; podem exigir substitutos para os mínimos.

Não escolher rótulos para alcançar cotas nem usar a LLM como adjudicadora.
Resumo de artigo não é automaticamente inválido: fundamentar sua suficiência
para a alegação específica. Conferir a inconsistência entre o caso 033 e o resumo
da rodada, além da justificativa do caso 048. Preservar as respostas originais.

## Comando local somente leitura

Na raiz do repositório:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\check_adjudication.py
.\.venv\Scripts\python.exe -X utf8 scripts\check_adjudication.py "C:\caminho\TASKS_preenchido.md"
```

O primeiro comando audita o original vazio; o segundo importa a cópia preenchida.
Campos podem continuar em linhas comuns; manter alegações, títulos e nomes dos sete campos.
Não adicionar seções no bloco de decisão. Comentários devem ficar na fundamentação.
O título do bloco pode ser o original `Decisão humana a preencher` ou a variante
`Decisão a preencher`; usar apenas um deles por caso. Uma resposta iniciada por
`Nenhuma` no campo de correção é tratada como ausência de mudança na alegação.

Também é aceito JSONL schema 1 com exatamente estes campos: `schema_version`,
`task_id`, `item_id`, `final_label`, `rationale`, `sources_checked`,
`evidence_chunk_ids`, `action`, `claim_correction`, `reviewer`, `reviewed_at`.
Campos textuais vazios podem ser `null`; chunks devem ser lista; datas são ISO.
IDs devem cobrir exatamente os 22 casos, sem duplicatas. Markdown é a opção usual.

## Garantias e limites

- Confere hashes dos arquivos arquivados e o snapshot primário.
- Recusa pacote incompleto, responsável/data inválidos, divergência sem decisão,
  evidência conclusiva ausente e chunks desconhecidos.
- Preserva rótulos primários e secundários; ambas as rodadas ficam arquivadas e a
  revisada é a usada nesta incorporação, sem selecionar a de maior concordância.
- Com decisões completas, confere o corpus contra seu manifesto e monta candidato
  apenas **em memória**, reportando hash, exclusões e prontidão estrutural.
  O objeto candidato conserva o ledger das decisões. Justificativas primárias
  continuam preservadas no snapshot original, mesmo se a final for corrigida.
- Não reequilibra classes/famílias, não escreve dataset, recibos ou banco, não
  chama modelos, não congela teste e não executa experimentos.

Uma auditoria pode corrigir erro compartilhado pelos anotadores. O campo opcional
`adjudication_basis=evidence_audit` registra esse caso com responsável/data, sem
falsificar divergência entre rótulos originais. Divergências usam
`annotation_disagreement`. Schemas antigos seguem válidos; correção sem registro
explícito continua rejeitada.

## Antes do congelamento

Além dos 22 casos, auditar humanamente o benchmark sintético: pertinência das
evidências de todos os itens, paráfrases/vazamento semântico entre famílias e
splits, limites de validade e procedimento real de anotação. Registrar responsável,
data, escopo, exceções e hashes do candidato final/corpus; discutir a validade com
o orientador conforme o protocolo. Após correções/exclusões, reconferir mínimos
por classe, cobertura secundária e split 60%/40%, sem separar uma família.

Prontidão estrutural não certifica auditoria humana, não autoriza publicar novos
pareceres e não encerra a Fase 5. Congelamento/experimentos dependem da reconciliação
e do aceite explícitos dos critérios do roadmap.
