# Retornos do segundo anotador — antes da adjudicação

`round_001.jsonl` preserva as 48 respostas inicialmente recebidas; `round_002.jsonl`
preserva as 48 respostas do formulário revisado. Não mesclar ou sobrescrever as
rodadas. São respostas humanas informadas pelo autor, não saídas do ImmunoCheck.

Os dados pessoais do primeiro formulário foram removidos. Usa-se o identificador
interno `usr_002-independente`, presente no revisado, para ambas as rodadas da
mesma revisora, conforme a continuidade informada pelo autor. Isso não certifica
identidade, profissão ou competência. A data 15/09/2026 é a declarada nos formulários.

O arquivo original da rodada 001 não estava mais disponível em Downloads no
momento desta importação. Seus campos foram recuperados do snapshot textual
previamente lido nesta tarefa; não alegar preservação byte a byte do original.
Justificativas, referências e dúvidas foram transcritas sem correção de conteúdo,
com normalização de quebras de linha e campos estruturados. O segundo formulário
foi lido diretamente. Não foram incluídos arquivos com dados pessoais no Git.

O revisado declara consulta ao catálogo/fontes e ausência de consulta aos rótulos
do primeiro anotador, pareceres ou respostas do sistema. Esse procedimento é
autodeclarado, não certificado pelo software. Registra cerca de cinco horas de
pesquisa, sem verificação externa dessa duração. Não calcular concordância entre
rodadas da mesma pessoa como se fosse independência entre humanos.

Na primeira rodada, 31/48 pares coincidem (kappa 0,527778); na revisada, 32/48
(kappa 0,555556). Há cinco mudanças de rótulo entre rodadas. Preservar ambos os
resultados e reportar que a segunda rodada sucedeu um pedido de conferência
documental. Não selecionar o maior kappa e ocultar o procedimento ou a rodada inicial.
Essas métricas são descritivas de uma amostra estratificada, com famílias correlatas
e primeira revisão assistida, não acurácia do sistema ou certificação do dataset.

Pendências do formulário revisado, sem correção automática:

- As observações finais dizem "catorze" itens insuficientes, mas enumeram 12 IDs.
  Os campos individuais contêm 11 `INSUFFICIENT_EVIDENCE`; o item 033, incluído
  nessa enumeração, está marcado `REFUTED`. Para a análise foram usados os campos
  individuais. Confirmar a intenção do item 033 na adjudicação.
- Nos itens 022/023, não foi localizado o documento referido. Ambos receberam
  `INSUFFICIENT_EVIDENCE`, apesar de rótulos primários conclusivos.
- Nos itens 001/015/018/024/026/033/039 há limites explícitos de acesso ao texto
  específico, uso de resumo, título ou outras fontes. Isso não invalida por si só
  um resumo diretamente pertinente, mas exige análise de suficiência e rastreabilidade.
- No item 048, a justificativa informa 51,7% confirmados e depois diz que a maior
  parte não foi confirmada. Essa inconsistência numérica deve ser corrigida por
  quem resolver o caso; a análise não alterou a resposta original.

Retornos ainda não foram incorporados a `items.jsonl`: existem 16 divergências
de rótulo e pendências de evidência. `label`, `primary_label`, famílias, splits,
corpus e manifesto de teste não foram alterados. Não houve congelamento ou
experimento. O pacote de adjudicação será entregue com ambos os julgamentos
visíveis; essa etapa já não é anotação cega e não substitui os pares originais.
