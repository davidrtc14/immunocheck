# Lote experimental 012 — Populações especiais e interpretação de indicadores

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
| 0145 | A metanálise de 2024 associou mRNA-1273 a maior probabilidade de soroconversão que BNT162b2 em adultos imunocomprometidos. | Sustentada | Desfecho imune e população delimitados; estudo financiado por fabricante requer triangulação. |
| 0146 | Na comparação de 2024, as diferenças de anticorpos neutralizantes e resposta celular não foram estatisticamente significativas. | Sustentada | Distinguir títulos totais, neutralização e resposta celular. |
| 0147 | A estratégia Multivacinação 2026 é apresentada como atualização da caderneta de crianças e adolescentes menores de quinze anos. | Sustentada | Público da estratégia, não universo de pessoas que podem se vacinar. |
| 0148 | O documento de 2026 calcula incremento percentual da cobertura pela diferença entre períodos dividida pelo valor do período anterior. | Sustentada | Percentual relativo, não diferença absoluta em pontos percentuais. |
| 0149 | A metanálise de 2024 encontrou menor probabilidade de soroconversão com mRNA-1273 que com BNT162b2. | Refutada | A direção agregada relatada é oposta. |
| 0150 | Na comparação de vacinas em imunocomprometidos de 2024, todas as diferenças de resposta celular e anticorpos neutralizantes foram significativas. | Refutada | O resumo ressalva ausência de significância para esses dois desfechos. |
| 0151 | O documento Multivacinação 2026 delimita seu público exclusivamente a pessoas com quinze anos ou mais. | Refutada | O público explícito é menor de quinze anos. |
| 0152 | O documento de 2026 define incremento percentual apenas como a diferença simples entre as duas coberturas, sem divisão pelo valor anterior. | Refutada | A nota metodológica inclui divisão e multiplicação por 100. |
| 0153 | A comparação encontrou maior soroconversão com mRNA-1273, portanto provou superioridade clínica para toda pessoa e situação. | Enganosa | Diferença imune real não prova superioridade clínica universal; considerar financiamento e heterogeneidade. |
| 0154 | Alguns desfechos imunes favoreceram mRNA-1273, então todos os desfechos comparados demonstraram vantagem estatística. | Enganosa | Diferenças reais em alguns marcadores são ampliadas aos demais. |
| 0155 | A estratégia atualiza cadernetas de menores de quinze anos, então quem é mais velho não precisa receber qualquer vacina. | Enganosa | Recorte real de uma campanha é convertido em dispensa universal fora dela. |
| 0156 | A figura relata incremento de cobertura de tríplice viral, portanto o valor de incremento pode ser interpretado diretamente como pontos percentuais. | Enganosa | Incremento real é apresentado com outra unidade; preservar base e recorte temporal. |
| 0157 | O produto usado na unidade protege melhor os pacientes imunocomprometidos que qualquer alternativa. | Evidência insuficiente | Cenário fictício sem produto, população, doses ou desfechos; não recomendar escolha individual. |
| 0158 | Os pacientes transplantados da clínica tiveram resposta celular superior com a vacina que receberam. | Evidência insuficiente | Cenário fictício sem produto, exames, tratamentos ou comparador local. |
| 0159 | Todas as cadernetas das crianças da cidade foram atualizadas durante a multivacinação. | Evidência insuficiente | Cenário fictício sem cidade, elegibilidade, registros ou denominador. |
| 0160 | A cobertura da vacina tríplice viral deste município aumentou trinta pontos percentuais no ano passado. | Evidência insuficiente | Cenário fictício sem município, coberturas inicial/final, dose ou períodos absolutos. |

## Fontes e localização

- Família `immunocompromised_mrna_seroconversion`: [idt_immunocompromised_mrna_meta_2024](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11219657/fullTextXML); chunks `idt_immunocompromised_mrna_meta_2024:p1:c2:385b830d37ae`.
- Família `immunocompromised_mrna_outcome_significance`: [idt_immunocompromised_mrna_meta_2024](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11219657/fullTextXML); chunks `idt_immunocompromised_mrna_meta_2024:p1:c2:385b830d37ae`.
- Família `multivaccination_target_age`: [ms_multivacinacao_2026](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/estrategia-para-atualizacao-da-cadernetas-de-vacinacao-das-criancas-e-dos-adolescentes-menores-de-15-anos-2013-multivacinacao-2026.pdf/@@download/file); chunks `ms_multivacinacao_2026:p1:c1:f01db00d520a`.
- Família `vaccination_coverage_relative_increment`: [ms_multivacinacao_2026](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/estrategia-para-atualizacao-da-cadernetas-de-vacinacao-das-criancas-e-dos-adolescentes-menores-de-15-anos-2013-multivacinacao-2026.pdf/@@download/file); chunks `ms_multivacinacao_2026:p7:c1:6c378fb74cf0`.

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
