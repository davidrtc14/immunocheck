# Lote experimental 009 — Rotavírus, varicela e febre amarela

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
| 0097 | A revisão global de 2025 encontrou variação entre países no desempenho das vacinas contra gastroenterite grave por rotavírus. | Sustentada | Desfecho grave e variação geográfica, não toda diarreia. |
| 0098 | A metanálise de varicela de 2025 encontrou maior efetividade agregada com duas doses do que com uma dose. | Sustentada | Comparação agregada, com heterogeneidade e duração limitadas. |
| 0099 | Na revisão de febre amarela de 2022, a soroproteção após uma dose permaneceu alta em adultos saudáveis por cinco a dez anos. | Sustentada | Marcador de grupo e intervalo relatado, não garantia clínica individual. |
| 0100 | A revisão de 2022 descreveu queda de soroproteção em crianças vacinadas contra febre amarela antes dos dois anos. | Sustentada | Preservar marcador, grupo e tempo; não redefinir calendário individual. |
| 0101 | A revisão global de rotavírus de 2025 apresentou uma estimativa idêntica de eficácia para todos os países. | Refutada | As estimativas modeladas variam entre países e regiões. |
| 0102 | Na metanálise de varicela de 2025, uma dose teve maior efetividade agregada que duas doses. | Refutada | O resultado agregado favorece duas doses. |
| 0103 | A revisão de febre amarela de 2022 encontrou soroproteção baixa em todos os adultos saudáveis já aos três meses da primeira dose. | Refutada | O resumo descreve níveis altos, próximos de 100% inicialmente. |
| 0104 | A revisão de febre amarela de 2022 encontrou soroproteção de 100% em todas as crianças vacinadas antes dos dois anos ao longo de cinco anos. | Refutada | A estimativa agregada do subgrupo não foi de 100%. |
| 0105 | Há estimativas mais baixas de desempenho em algumas regiões, portanto a revisão prova que a vacina contra rotavírus é inútil nesses lugares. | Enganosa | Desempenho inferior real não equivale a inutilidade; incerteza e contexto precisam ser preservados. |
| 0106 | Duas doses tiveram maior efetividade agregada, então ficou garantida proteção total e permanente contra varicela. | Enganosa | Vantagem real é ampliada a proteção absoluta sem limite temporal. |
| 0107 | A soroproteção permaneceu alta em adultos saudáveis por vários anos, então uma dose garante o mesmo resultado em qualquer idade e condição imune. | Enganosa | Resultado de adultos saudáveis é extrapolado a grupos distintos. |
| 0108 | Houve queda de soroproteção em crianças vacinadas cedo, então nenhuma dessas crianças conserva qualquer proteção contra febre amarela. | Enganosa | Queda real em proporção agregada é transformada em ausência universal. |
| 0109 | A vacina contra rotavírus usada na região foi responsável pela queda das internações neste semestre. | Evidência insuficiente | Cenário fictício sem região, vacinação, internações ou comparação temporal adequada. |
| 0110 | A dose de varicela aplicada à turma foi ineficaz porque alguns alunos adoeceram. | Evidência insuficiente | Cenário fictício sem diagnóstico, esquemas, intervalos ou grupo comparador. |
| 0111 | A pessoa vacinada há dez anos ainda mantém o mesmo nível de anticorpos contra febre amarela. | Evidência insuficiente | Cenário fictício sem exame, histórico ou condição imune; níveis individuais não são inferidos da média. |
| 0112 | A criança vacinada antes dos dois anos perdeu a proteção contra febre amarela. | Evidência insuficiente | Cenário fictício sem avaliação individual; idade de aplicação não determina sozinha ausência de proteção. |

## Fontes e localização

- Família `rotavirus_geographic_performance`: [eclinm_rotavirus_global_2025](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11925534/fullTextXML); chunks `eclinm_rotavirus_global_2025:p1:c1:7d798e22b00a`, `eclinm_rotavirus_global_2025:p1:c2:4d8fec8bc6a9`, `eclinm_rotavirus_global_2025:p1:c3:1ae9c1f1f25b`.
- Família `varicella_dose_effectiveness`: [jkms_varicella_effectiveness_meta_2025](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12624214/fullTextXML); chunks `jkms_varicella_effectiveness_meta_2025:p1:c2:06e96d0b4cb0`, `jkms_varicella_effectiveness_meta_2025:p1:c3:ad2f28f58354`.
- Família `yellow_fever_adult_seroprotection`: [cid_yellow_fever_duration_meta_2022](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9761887/fullTextXML); chunks `cid_yellow_fever_duration_meta_2022:p1:c2:bee0ca8b1d39`.
- Família `yellow_fever_child_waning`: [cid_yellow_fever_duration_meta_2022](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9761887/fullTextXML); chunks `cid_yellow_fever_duration_meta_2022:p1:c2:bee0ca8b1d39`, `cid_yellow_fever_duration_meta_2022:p1:c3:45e6f0e1a5c9`.

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
