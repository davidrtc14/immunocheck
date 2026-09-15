# Lote experimental 003 — Componentes e fabricação

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
| 0025 | O tiomersal é usado como conservante em alguns frascos multidose de vacinas. | Sustentada | Uso em alguns frascos, não presença universal. |
| 0026 | Excipientes de algumas vacinas podem participar de reações anafiláticas. | Sustentada | Possibilidade descrita, com anafilaxia rara; não universalizar. |
| 0027 | Linhagens celulares são utilizadas como plataformas na produção de algumas vacinas virais. | Sustentada | A fonte descreve plataformas de expressão e produção. |
| 0028 | A OMS descreve o mercúrio do tiomersal como metilmercúrio, o mesmo tipo que pode se acumular em peixes. | Refutada | A fonte distingue etilmercúrio e metilmercúrio. |
| 0029 | Segundo a revisão sobre aditivos de 2022, apenas o princípio ativo pode desencadear anafilaxia relacionada a vacinas. | Refutada | A fonte inclui excipientes e resíduos como potenciais desencadeantes. |
| 0030 | A revisão de linhagens celulares de 2024 exclui parâmetros regulatórios da seleção de plataformas de produção vacinal. | Refutada | A descrição inclui regulamentos atuais e eficiência do bioprocesso. |
| 0031 | O tiomersal contém mercúrio, então sua presença tem o mesmo significado toxicológico que o metilmercúrio de peixes. | Enganosa | A presença química real é usada para apagar a distinção toxicológica. Não avaliar toxicidade apenas pelo nome. |
| 0032 | Há excipientes com potencial alergênico, portanto qualquer pessoa terá anafilaxia ao receber uma vacina. | Enganosa | Possibilidade real é transformada em ocorrência universal. |
| 0033 | Linhagens celulares participam da fabricação de algumas vacinas, então o produto final é necessariamente uma injeção de tecido animal intacto. | Enganosa | Processo de produção real não determina presença de tecido intacto no produto final. A fonte não é ensaio analítico de um lote. |
| 0034 | O frasco multidose utilizado na unidade nesta semana estava sem conservante. | Evidência insuficiente | Cenário fictício sem produto, bula ou identificação do frasco. |
| 0035 | A reação alérgica observada na campanha foi provocada por um resíduo de antibiótico da vacina. | Evidência insuficiente | Cenário fictício sem composição, avaliação clínica ou investigação específica. |
| 0036 | O fabricante mudou a linhagem celular da vacina distribuída neste mês. | Evidência insuficiente | Cenário fictício sem produto, fabricante, documentação ou data absoluta. |

## Fontes e localização

- Família `thiomersal_preservation`: [who_vaccine_safety_qa_2025](https://www.who.int/news-room/questions-and-answers/item/vaccines-and-immunization-vaccine-safety); chunks `who_vaccine_safety_qa_2025:p1:c10:96465f274856`.
- Família `allergy_excipients`: [allergo_vaccine_additives_anaphylaxis_2022](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9194891/fullTextXML); chunks `allergo_vaccine_additives_anaphylaxis_2022:p1:c1:38a1b380c43b`, `allergo_vaccine_additives_anaphylaxis_2022:p1:c2:a1fa2fa1da9a`.
- Família `cell_lines_manufacturing`: [acsomega_animal_cell_lines_vaccines_2024](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11025085/fullTextXML); chunks `acsomega_animal_cell_lines_vaccines_2024:p1:c2:bdd7985b4783`.

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
