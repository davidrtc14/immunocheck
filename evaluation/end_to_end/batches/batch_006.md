# Lote experimental 006 — Produtos e evidências de vacinas contra dengue

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
| 0061 | A metanálise de TAK-003 de 2024 distinguiu resultados em pessoas com e sem infecção prévia por dengue. | Sustentada | A fonte separa soronegativos e soropositivos. |
| 0062 | A revisão de TAK-003 de 2024 apontou incertezas sobre uso de dose única em países não endêmicos. | Sustentada | Preservar recorte de uma dose e contexto não endêmico. |
| 0063 | O guia de 2026 descreve Butantan-DV como vacina de dose única com vírus atenuados dos quatro sorotipos da dengue. | Sustentada | Composição e esquema são do produto específico. |
| 0064 | A metanálise de TAK-003 de 2024 demonstrou proteção clínica contra todos os sorotipos em menores inicialmente soronegativos. | Refutada | Nos menores soronegativos, a proteção relatada foi delimitada a DENV-1 e DENV-2. |
| 0065 | O estudo de TAK-003 de 2024 foi um único ensaio, sem combinar conjuntos de dados. | Refutada | O estudo é metanálise e combina 19 conjuntos de dados. |
| 0066 | O guia de Butantan-DV descreve Qdenga e Butantan-DV como produtos com o mesmo número de doses. | Refutada | O guia distingue uma dose de Butantan-DV e duas de Qdenga. |
| 0067 | A TAK-003 gerou resposta imune aos quatro sorotipos, então ficou demonstrada proteção clínica igual contra todos eles em qualquer população. | Enganosa | Imunogenicidade real não equivale a proteção clínica uniforme. |
| 0068 | A revisão detectou resposta imune após uma dose de TAK-003, portanto resolveu todas as incertezas de uso de dose única em países não endêmicos. | Enganosa | Resposta imune observada não elimina as incertezas declaradas. |
| 0069 | Butantan-DV é de dose única, então qualquer vacina contra dengue também deve ser aplicada em dose única. | Enganosa | Esquema real de um produto é extrapolado a outros. |
| 0070 | A pessoa vacinada que teve dengue na cidade recebeu uma dose sem eficácia. | Evidência insuficiente | Cenário fictício sem sorotipo, dose, intervalo, exposição ou laudo do produto; doença não prova inutilidade da dose. |
| 0071 | O esquema de uma dose usado na campanha internacional foi suficiente para proteger todos os viajantes. | Evidência insuficiente | Cenário fictício sem produto, destino, população ou desfechos da campanha. |
| 0072 | O frasco de vacina contra dengue disponibilizado na unidade é o produto do Instituto Butantan. | Evidência insuficiente | Cenário fictício sem identificação do frasco, lote, fabricante ou registro. |

## Fontes e localização

- Família `tak003_serostatus`: [mdpi_dengue_tak003_meta_2024](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11281463/fullTextXML); chunks `mdpi_dengue_tak003_meta_2024:p1:c1:fae44a46869d`, `mdpi_dengue_tak003_meta_2024:p1:c2:4f8df631090e`.
- Família `tak003_single_dose_uncertainty`: [mdpi_dengue_tak003_meta_2024](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11281463/fullTextXML); chunks `mdpi_dengue_tak003_meta_2024:p1:c1:fae44a46869d`, `mdpi_dengue_tak003_meta_2024:p1:c2:4f8df631090e`.
- Família `butantan_dengue_product`: [ms_guia_dengue_butantan_2026](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/guias-e-manuais/2026/guia-tecnico-operacional-da-vacina-dengue-atenuada-do-instituto-butantan.pdf); chunks `ms_guia_dengue_butantan_2026:p5:c2:538cac9d7668`, `ms_guia_dengue_butantan_2026:p7:c1:7f0cb5ffec9b`.

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
