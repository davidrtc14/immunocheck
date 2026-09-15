# Lote experimental 008 — Acesso e organização da vacinação

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
| 0085 | O microplanejamento da vacinação considera características geográficas, sociais e demográficas do território. | Sustentada | Planejamento local inclui população e território. |
| 0086 | A estratégia de vacinação nas escolas de 2025 prevê definir o processo de autorização dos pais ou responsáveis. | Sustentada | Registrar o processo previsto, sem inferir regra jurídica geral de consentimento. |
| 0087 | A Operação Gota busca ampliar o acesso à vacinação em regiões remotas da Amazônia Legal. | Sustentada | A fonte delimita objetivo e território. |
| 0088 | O manual de microplanejamento prescreve um processo fixo, sem adaptação aos desafios locais. | Refutada | O trecho exige processo adaptável e dinâmico. |
| 0089 | O documento de vacinação nas escolas de 2025 não prevê qualquer coleta ou registro de autorização dos responsáveis. | Refutada | O documento prevê coleta e registro de autorizações. |
| 0090 | A estratégia Operação Gota é descrita como ação exclusiva do Ministério da Saúde, sem articulação intersetorial. | Refutada | A descrição inclui Defesa, FAB e diferentes esferas de saúde. |
| 0091 | O microplanejamento adapta ações ao território, então dispensa monitoramento e avaliação das coberturas vacinais. | Enganosa | Adaptação real não elimina etapas de monitoramento e avaliação. |
| 0092 | A estratégia leva vacinação às escolas, então a escola pode ignorar o processo de autorização previsto no próprio documento. | Enganosa | Local acessível real não revoga o procedimento descrito. |
| 0093 | A Operação Gota usa logística aérea para ampliar acesso, então sua existência prova cobertura completa de todas as comunidades remotas. | Enganosa | Estratégia real de acesso não prova alcance integral ou cobertura universal. |
| 0094 | O microplanejamento executado neste município alcançou as metas de todas as vacinas. | Evidência insuficiente | Cenário fictício sem município, período, indicadores ou denominadores. |
| 0095 | Todos os responsáveis autorizaram a vacinação realizada na escola nesta semana. | Evidência insuficiente | Cenário fictício sem escola, termos ou registros; não inferir consentimento pela realização da ação. |
| 0096 | A missão da Operação Gota deste ano vacinou todas as pessoas da comunidade. | Evidência insuficiente | Cenário fictício sem missão, registros, elegibilidade ou denominador. |

## Fontes e localização

- Família `microplanning_local_context`: [ms_microplanejamento_2025](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/manual-de-microplanejamento.pdf/view); chunks `ms_microplanejamento_2025:p9:c2:e4022a1a66df`, `ms_microplanejamento_2025:p16:c1:7b56ae3dfd97`.
- Família `school_vaccination_consent`: [ms_escolas_2025](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/estrategia-de-vacinacao-nas-escolas-2025.pdf/@@download/file); chunks `ms_escolas_2025:p13:c2:566ba4feb6bc`.
- Família `operation_gota_remote_access`: [ms_operacao_gota_2026](https://www.gov.br/saude/pt-br/composicao/svsa/pni/operacao-gota/publicacoes/estrategia-de-vacinacao-operacao-gota-2026); chunks `ms_operacao_gota_2026:p6:c1:184dc7629b8c`, `ms_operacao_gota_2026:p6:c2:bac1eab9d490`.

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
