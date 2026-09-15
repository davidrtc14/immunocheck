# Lote experimental 007 — Normas e limites de interpretação

Preparado em 15/09/2026. **12 propostas; todas pendentes de revisão humana.**
Split previsto: **desenvolvimento**. O teste ainda não está congelado.
Corpus de referência:
`sha256:d6cb49e72edbe28e0958b1e8be440e655c93c972af78383121c04687f2d984a7`.

As formulações são sintéticas: 9 baseadas em fatos de fontes e 3 cenários
fictícios indeterminados. Não são amostra de notícias reais, mensagens do Telegram
ou previsões do sistema. Datas e resultados de artigos se referem ao documento
citado, não a aconselhamento médico atual. O equilíbrio de rótulos é proposto,
nunca uma obrigação da revisão humana.

## Alegações e rótulos propostos

| ID | Alegação | Rótulo | Justificativa proposta / informação ausente |
| --- | --- | --- | --- |
| 0073 | O informe técnico de 2024 previu substituir os reforços com VOPb por VIP no esquema brasileiro contra poliomielite. | Sustentada | Descrição histórica da política, não prova de execução em cada sala. |
| 0074 | A Nota Técnica 20/2026 inclui BCG e hepatite B nas orientações de imunização de recém-nascidos em maternidades. | Sustentada | Preservar condições e recomendações específicas; não aconselhar caso individual. |
| 0075 | A Nota Técnica 64/2026 alterou a faixa de registro de dose única de VPC20, retirando o limite superior de sessenta anos. | Sustentada | Regra de registro em estratégias especiais, não expansão universal de indicação. |
| 0076 | O informe de 2024 determinou manter as duas doses de reforço com VOPb, sem substituição por VIP. | Refutada | O texto prevê substituição e logística reversa. |
| 0077 | A Nota Técnica 20/2026 exclui a vacina contra hepatite B de seu objetivo de imunização neonatal. | Refutada | A hepatite B aparece expressamente no objetivo. |
| 0078 | A Nota Técnica 64/2026 manteve o limite de menos de sessenta anos para o registro de dose única de VPC20. | Refutada | O quadro mostra retirada do limite superior. |
| 0079 | O esquema de poliomielite passou a usar exclusivamente VIP, então todas as vacinas orais do calendário foram abolidas. | Enganosa | Exclusividade restrita à poliomielite é ampliada a todo o calendário. |
| 0080 | A nota recomenda vacinação preferencialmente na maternidade, então uma dose aplicada fora dela é necessariamente inválida. | Enganosa | Preferência de local é transformada em exclusividade; o texto aborda ambos os cenários. |
| 0081 | A faixa de registro de dose única passou a incluir idade igual ou superior a cinco anos, então a nota recomenda VPC20 a qualquer pessoa dessa idade. | Enganosa | Regra administrativa real é ampliada a indicação clínica universal, omitindo grupos e estratégia. |
| 0082 | A unidade de saúde retirou todas as doses de VOPb no prazo da transição de 2024. | Evidência insuficiente | Cenário fictício sem registros locais de estoque, devolução e datas. |
| 0083 | A maternidade deste município aplicou BCG e hepatite B em todos os recém-nascidos no mês passado. | Evidência insuficiente | Cenário fictício sem maternidade identificada, registros ou denominador. |
| 0084 | A vacinação de VPC20 do posto já segue a correção de registro da Nota Técnica 64/2026. | Evidência insuficiente | Cenário fictício sem registros, população ou auditoria local. |

## Fontes e localização

- Família `polio_vip_transition`: [ms_polio_vip_2024](https://www.gov.br/saude/pt-br/vacinacao/informes/retirada-da-vacina-poliomielite-1-e-3-atenuada-e-adocao-do-esquema-exclusivo-com-vacina-poliomielite-1-2-e-3-inativada.pdf/@@download/file); chunks `ms_polio_vip_2024:p5:c1:f5ea6561ed4d`.
- Família `neonatal_maternity_policy`: [ms_nt20_imunizacao_recem_nascidos_2026](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/notas-tecnicas/2026/nota-tecnica-conjunta-no-20-2026-dpni-dahu-svsa-saes-ms.pdf/@@download/file); chunks `ms_nt20_imunizacao_recem_nascidos_2026:p1:c1:a0b988c3e7dd`, `ms_nt20_imunizacao_recem_nascidos_2026:p1:c3:16cdb7b8a611`.
- Família `vpc20_registry_special_strategy`: [ms_nt64_vpc20_2026](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/notas-tecnicas/2026/nota-tecnica-no-64-2026-dpni-svsa-ms.pdf/@@download/file); chunks `ms_nt64_vpc20_2026:p1:c1:1f4b7eb9c8d1`, `ms_nt64_vpc20_2026:p1:c2:881af5dcd88f`.

Os links são das fontes primárias do corpus. Os chunks conclusivos não são atribuídos
aos cenários fictícios: uma possibilidade geral não prova nem desmente um caso.
Não reproduzir texto integral com restrição de redistribuição; as frases acima
são formulações factuais originais, não citações literais das obras.

## Revisão e limitações

Ler o guia de anotação e o contexto das fontes. Revisar produto, população, tempo,
comparador e unidades; separar afirmações se a atomicidade for inadequada.
Em casos enganosos, identificar a premissa sustentada e a inferência distorcida;
corrigir rótulo ou excluir itens ambíguos sem tentar preservar cotas.

Famílias relacionadas foram mantidas no mesmo split. A revisão semântica humana
ainda precisa verificar essa atribuição, inclusive entre lotes. Os itens de uma
família não equivalem a observações independentes. Relatar origem sintética,
estilo de redação e correlação intrafamília; não extrapolar métricas para notícias
reais. Revisões de artigos refletem o recorte de suas buscas e limitações.

Aprovar ou corrigir **este lote** pelos IDs; até então nada entra em `items.jsonl`.
Aceite do autor é primeira revisão assistida, não segunda anotação ou revisão
especializada. Não executar a pipeline nem ajustar parâmetros usando itens de teste.
