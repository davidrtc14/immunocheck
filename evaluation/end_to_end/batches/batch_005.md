# Lote experimental 005 — Riscos e interpretações de estudos de covid-19

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
| 0049 | A revisão de 2023 detectou maior risco de mio/pericardite após vacinas de mRNA contra covid-19, embora os casos absolutos observados fossem poucos. | Sustentada | Preservar comparador sem infecção, janela e risco absoluto baixo. |
| 0050 | Na metanálise de 2024, a associação entre vacinação contra covid-19 e risco de Guillain-Barré diferiu conforme a plataforma vacinal. | Sustentada | Separar plataformas e comparadores; associação não prova mecanismo. |
| 0051 | A revisão de reprodução assistida de 2024 examinou tanto histórico de covid-19 quanto vacinação contra covid-19. | Sustentada | Escopo inclui infecção e vacinação; não confundir exposições. |
| 0052 | A revisão de mio/pericardite de 2023 não encontrou qualquer aumento relativo de risco entre vacinados e não vacinados sem infecção. | Refutada | O texto relata aumento relativo no comparador delimitado. |
| 0053 | A metanálise de Guillain-Barré de 2024 demonstrou o mesmo aumento de risco para vacinas de mRNA e de vetor adenoviral. | Refutada | Os resultados de plataforma não foram iguais. |
| 0054 | A revisão de reprodução assistida de 2024 analisou somente infecção e não incluiu vacinação. | Refutada | O objetivo e os resultados incluem comparação por vacinação. |
| 0055 | A revisão encontrou aumento relativo de mio/pericardite, então a maioria das pessoas que recebe vacina de mRNA desenvolverá a doença. | Enganosa | Aumento relativo real não implica ocorrência na maioria das pessoas. |
| 0056 | A análise encontrou aumento de risco com vetor adenoviral, então o resultado se aplica indistintamente a qualquer vacina contra covid-19. | Enganosa | Associação de plataforma específica é ampliada a todas. |
| 0057 | Centros de reprodução assistida fecharam durante a pandemia, então esse fechamento comprova que a vacinação causa infertilidade. | Enganosa | Fechamento real por risco de disseminação não prova infertilidade causada pela vacina. |
| 0058 | O caso de miocardite registrado ontem no hospital foi causado pela dose aplicada. | Evidência insuficiente | Cenário fictício sem vacina, data absoluta ou investigação; sequência temporal não prova causa. |
| 0059 | A síndrome de Guillain-Barré diagnosticada na cidade foi desencadeada pela vacinação. | Evidência insuficiente | Cenário fictício sem histórico, diagnósticos diferenciais ou investigação causal. |
| 0060 | A queda na taxa de gravidez da clínica deste ano foi causada pela vacinação de seus pacientes. | Evidência insuficiente | Cenário fictício sem população, comparação, protocolos ou fatores concorrentes. |

## Fontes e localização

- Família `mrna_myocarditis_risk`: [bmjopen_mrna_myocarditis_meta_2023](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10314577/fullTextXML); chunks `bmjopen_mrna_myocarditis_meta_2023:p1:c2:3c28c4cef001`, `bmjopen_mrna_myocarditis_meta_2023:p1:c3:0dd8040d879c`.
- Família `gbs_vaccine_platforms`: [jneurol_gbs_covid_vaccination_meta_2024](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10896967/fullTextXML); chunks `jneurol_gbs_covid_vaccination_meta_2024:p1:c2:46250b0fa2f1`, `jneurol_gbs_covid_vaccination_meta_2024:p1:c3:b84683dfdee9`.
- Família `art_fertility_scope`: [mdpi_covid_art_fertility_2024](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11431602/fullTextXML); chunks `mdpi_covid_art_fertility_2024:p1:c1:7b6dee18627c`, `mdpi_covid_art_fertility_2024:p1:c2:3be37682c018`.

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
