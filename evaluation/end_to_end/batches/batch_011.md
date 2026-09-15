# Lote experimental 011 — Epidemiologia e vigilância

Preparado em 15/09/2026. **16 propostas; todas pendentes de revisão humana.**
Split previsto: **teste**. O teste ainda não está congelado.
Corpus de referência:
`sha256:d6cb49e72edbe28e0958b1e8be440e655c93c972af78383121c04687f2d984a7`.

As formulações são sintéticas: 12 baseadas em fatos de fontes e 4 cenários
fictícios indeterminados. Não são amostra de notícias reais, mensagens do Telegram
ou previsões do sistema. Datas e resultados de artigos se referem ao documento
citado, não a aconselhamento médico atual. O equilíbrio de rótulos é proposto,
nunca uma obrigação da revisão humana.

## Alegações e rótulos propostos

| ID | Alegação | Rótulo | Justificativa proposta / informação ausente |
| --- | --- | --- | --- |
| 0129 | O estudo de Manaus analisou dados de casos de sarampo ocorridos em 2018 e 2019 e sua distribuição geográfica e temporal. | Sustentada | Separar data de publicação e período observado. |
| 0130 | A revisão de coqueluche de 2020 encontrou prevalências diferentes conforme o método de confirmação laboratorial. | Sustentada | Preservar estudos comparados e método. |
| 0131 | O informe de meningites distingue casos suspeitos notificados de casos confirmados no primeiro semestre de 2025. | Sustentada | Recorte de janeiro a junho e distinção de denominadores. |
| 0132 | O informe de poliomielite de 2025 alerta para risco de reintrodução enquanto houver circulação de poliovírus no mundo. | Sustentada | Eliminação local e circulação externa são conceitos distintos. |
| 0133 | O estudo de Manaus investigou apenas casos de sarampo ocorridos em 2024, ano de sua publicação. | Refutada | O método delimita 2018 e 2019. |
| 0134 | Na revisão de coqueluche de 2020, cultura e PCR produziram sempre estimativas idênticas de prevalência. | Refutada | O texto relata subestimação por cultura frente a PCR. |
| 0135 | O informe de meningites apresenta todos os casos suspeitos notificados como casos confirmados. | Refutada | Os totais de suspeitos e confirmados são diferentes. |
| 0136 | O informe de 2025 afirma que a eliminação da poliomielite no Brasil dispensa vigilância e vacinação. | Refutada | O documento exige vigilância ativa e vacinação. |
| 0137 | O estudo encontrou maior densidade de casos em áreas com menor padrão de vida, então prova que pobreza determina a infecção de qualquer pessoa. | Enganosa | Associação territorial histórica real é convertida em determinação causal individual. |
| 0138 | A revisão encontrou menor detecção por cultura em comparação com PCR, então todo resultado negativo de cultura é necessariamente um caso de coqueluche. | Enganosa | Diferença real de sensibilidade é transformada em diagnóstico individual universal. |
| 0139 | O informe registra milhares de notificações suspeitas, então esse total representa falhas comprovadas de vacinas contra meningite. | Enganosa | Notificações reais não estabelecem etiologia, histórico vacinal nem falha de produto. |
| 0140 | O Brasil passou décadas sem casos registrados de poliomielite, então a doença foi erradicada mundialmente e a vacinação perdeu sua finalidade. | Enganosa | Histórico local real é ampliado à erradicação global, conclusão contrariada pelo informe. |
| 0141 | A baixa cobertura vacinal foi a única causa do surto de sarampo observado neste bairro. | Evidência insuficiente | Cenário fictício sem bairro, dados de casos, cobertura ou investigação de fatores concorrentes. |
| 0142 | O aumento de coqueluche registrado na cidade decorreu apenas da troca do método diagnóstico. | Evidência insuficiente | Cenário fictício sem série, métodos, casos ou cobertura; revisão geral não determina a causa local. |
| 0143 | As vacinas contra meningite falharam no município, segundo as notificações desta semana. | Evidência insuficiente | Cenário fictício sem município, confirmação, agente, vacinação ou comparação. |
| 0144 | A criança com paralisia notificada na unidade contraiu poliomielite apesar de vacinada. | Evidência insuficiente | Cenário fictício sem confirmação etiológica, histórico ou investigação; PFA não confirma por si só poliomielite. |

## Fontes e localização

- Família `measles_manaus_historical_outbreak`: [einstein_measles_amazon_spatiotemporal_2024](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11081026/fullTextXML); chunks `einstein_measles_amazon_spatiotemporal_2024:p1:c2:54cfb9604cd3`, `einstein_measles_amazon_spatiotemporal_2024:p1:c3:15cc2d05ce95`.
- Família `pertussis_diagnostic_methods`: [bmc_pertussis_lmic_burden_meta_2020](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7453720/fullTextXML); chunks `bmc_pertussis_lmic_burden_meta_2020:p1:c2:8a49957561f6`, `bmc_pertussis_lmic_burden_meta_2020:p1:c3:6a783eb9bc82`.
- Família `meningitis_notifications_confirmation`: [ms_meningite_2025](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/m/meningite/situacao-epidemiologica/boletim-epidemiologico/informe-meningite-2a-edicao.pdf/@@download/file); chunks `ms_meningite_2025:p1:c1:3f3eaaf07fe2`, `ms_meningite_2025:p1:c2:19783c2f6e51`.
- Família `polio_surveillance_reintroduction`: [ms_pfa_2025](https://www.gov.br/saude/pt-br/vacinacao/informes/informe-poliomielite-pfa.pdf/@@download/file); chunks `ms_pfa_2025:p1:c1:888fdb097e9c`, `ms_pfa_2025:p1:c2:50aa9c056720`.

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
