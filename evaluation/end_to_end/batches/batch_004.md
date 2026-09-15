# Lote experimental 004 — Vacinação materna

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
| 0037 | Na revisão de ensaios de 2023, a vacinação materna contra influenza reduziu casos de influenza confirmados em laboratório em lactentes. | Sustentada | Preservar o desfecho laboratorial e o conjunto de ensaios. |
| 0038 | A metanálise de 2025 encontrou maior concentração de anticorpos contra coqueluche no sangue do cordão de filhos de gestantes vacinadas. | Sustentada | Resultado imune de grupo, não garantia individual. |
| 0039 | A estratégia do Ministério da Saúde descreve a passagem pela placenta de anticorpos maternos produzidos após a vacinação contra VSR. | Sustentada | Mecanismo passivo específico para VSR. |
| 0040 | A revisão de vacinas maternas de 2023 encontrou redução significativa de toda influenza clinicamente confirmada em lactentes. | Refutada | A análise de influenza clinicamente confirmada em lactentes não foi significativa. |
| 0041 | A metanálise de coqueluche na gestação de 2025 foi composta exclusivamente por ensaios randomizados. | Refutada | Foram incluídos ensaios e estudos caso-controle. |
| 0042 | Na estratégia de VSR em gestantes, a eficácia relatada contra doença grave do lactente foi de 100%. | Refutada | O trecho apresenta estimativas inferiores a 100% e intervalos de confiança. |
| 0043 | A revisão encontrou proteção contra influenza confirmada em laboratório, então a vacinação materna elimina qualquer síndrome respiratória no bebê. | Enganosa | Um desfecho específico é ampliado a todas as síndromes respiratórias. |
| 0044 | Maior concentração de anticorpos no cordão foi observada, portanto nenhum bebê de mãe vacinada pode desenvolver coqueluche. | Enganosa | Resposta de grupo é convertida em proteção absoluta. |
| 0045 | Anticorpos passam pela placenta após vacinação materna contra VSR, então o bebê fica protegido de todos os vírus respiratórios. | Enganosa | Mecanismo específico é extrapolado a qualquer vírus. |
| 0046 | A campanha de vacinação das gestantes reduziu todas as internações respiratórias dos recém-nascidos do município. | Evidência insuficiente | Cenário fictício sem série temporal, comparação ou causas das internações. |
| 0047 | Os bebês nascidos na maternidade ficaram protegidos contra coqueluche porque suas mães receberam a vacina. | Evidência insuficiente | Cenário fictício sem histórico, intervalo, exposição ou evidência de desfecho; não inferir garantia individual. |
| 0048 | A vacina contra VSR aplicada às gestantes da unidade preveniu o episódio de bronquiolite deste bebê. | Evidência insuficiente | Cenário fictício sem agente, investigação ou dados individuais; não atribuir prevenção causal de um episódio. |

## Fontes e localização

- Família `maternal_influenza_trials`: [bmjgh_maternal_vaccines_rct_review_2023](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10619060/fullTextXML); chunks `bmjgh_maternal_vaccines_rct_review_2023:p1:c2:bd70d92bb0e9`, `bmjgh_maternal_vaccines_rct_review_2023:p1:c3:e5c5b5f6530d`.
- Família `maternal_pertussis_evidence`: [vaccines_pertussis_pregnancy_meta_2025](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12298825/fullTextXML); chunks `vaccines_pertussis_pregnancy_meta_2025:p1:c1:328860666e49`, `vaccines_pertussis_pregnancy_meta_2025:p1:c2:2a5c14b76470`.
- Família `maternal_rsv_transfer`: [ms_vsr_gestantes_2026](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/estrategia-de-vacinacao-contra-o-virus-sincicial-respiratorio-em-gestantes.pdf); chunks `ms_vsr_gestantes_2026:p6:c2:794d29752feb`, `ms_vsr_gestantes_2026:p6:c3:4812a2214f7b`.

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
