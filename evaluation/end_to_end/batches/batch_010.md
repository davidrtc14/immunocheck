# Lote experimental 010 — Influenza, hepatite B e doença renal

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
| 0113 | A revisão de influenza de 2022 encontrou maior proteção com vacinação em duas temporadas consecutivas do que sem vacinação. | Sustentada | Preservar comparador e diferenças por temporada e subtipo. |
| 0114 | A revisão de hepatite B em crianças africanas de 2024 utilizou níveis de anti-HBs para estimar soroproteção. | Sustentada | Estimativa por marcador em estudos transversais, não incidência futura. |
| 0115 | A metanálise de vacinação em doença renal crônica de 2026 delimitou sua população a pacientes que não estavam em diálise. | Sustentada | Recorte explícito CKD-ND e diferentes vacinas. |
| 0116 | A revisão de pacientes renais de 2026 alertou que marcadores como soroconversão podem não refletir plenamente a efetividade clínica. | Sustentada | Conclusão distingue marcadores substitutos e desfechos clínicos. |
| 0117 | A revisão de influenza de 2022 concluiu que duas temporadas consecutivas de vacinação protegem menos que não receber vacina. | Refutada | O comparador sem vacinação é explicitamente desfavorável. |
| 0118 | A revisão de hepatite B de 2024 incluiu somente ensaios randomizados de infecção clínica, sem medir anticorpos. | Refutada | Método inclui estudos transversais e dosagem de anti-HBs. |
| 0119 | A população-alvo da metanálise de doença renal de 2026 foi composta exclusivamente por pacientes em diálise. | Refutada | O recorte é sem diálise, contradiz a exclusividade alegada. |
| 0120 | A revisão de pacientes renais de 2026 afirmou que soroconversão sempre equivale integralmente à proteção clínica. | Refutada | O alerta explícito contradiz equivalência universal. |
| 0121 | A revisão encontrou alguma atenuação da efetividade com vacinação repetida, portanto concluiu que abandonar a vacinação é melhor. | Enganosa | Atenuação frente a outro comparador é usada para recomendar abandono, conclusão não sustentada pela revisão. |
| 0122 | A revisão encontrou soroproteção variável por anti-HBs, então mediu diretamente quantas crianças desenvolverão hepatite B no futuro. | Enganosa | Marcador real é apresentado como medida direta de infecção futura. |
| 0123 | A revisão encontrou respostas vacinais em pacientes renais sem diálise, então seus resultados se aplicam sem ressalvas a qualquer paciente em diálise. | Enganosa | Resultados de população delimitada são extrapolados a outra condição. |
| 0124 | A revisão encontrou altas taxas de soroconversão, portanto eliminou a necessidade de estudos sobre infecções e mortalidade. | Enganosa | Resposta laboratorial real é usada para ignorar lacuna clínica declarada. |
| 0125 | A vacinação anual piorou a proteção contra gripe das pessoas deste município. | Evidência insuficiente | Cenário fictício sem temporadas, vacinação, subtipos ou estimativas comparativas. |
| 0126 | A vacinação contra hepatite B da cidade deixou mais da metade das crianças sem proteção. | Evidência insuficiente | Cenário fictício sem cidade, produto, exames, idades ou denominador. |
| 0127 | A resposta vacinal dos pacientes em diálise desta clínica foi igual à de pessoas sem doença renal. | Evidência insuficiente | Cenário fictício sem clínica, vacina, exames ou comparador; a revisão não responde a esse caso. |
| 0128 | A vacinação reduziu a mortalidade por infecção dos pacientes renais acompanhados neste serviço. | Evidência insuficiente | Cenário fictício sem serviço, vacina, seguimento ou comparação de mortalidade. |

## Fontes e localização

- Família `influenza_repeat_comparators`: [lancet_repeated_influenza_meta_2022](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9780123/fullTextXML); chunks `lancet_repeated_influenza_meta_2022:p1:c2:ec9e1d7a49b2`, `lancet_repeated_influenza_meta_2022:p1:c3:1376e8bbb7ca`.
- Família `hepb_serosurvey_measurement`: [bmc_hepb_children_africa_meta_2024](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10900737/fullTextXML); chunks `bmc_hepb_children_africa_meta_2024:p1:c2:e5bae33513c6`, `bmc_hepb_children_africa_meta_2024:p1:c3:577f7c98693b`.
- Família `ckd_nondialysis_population`: [ckj_ckd_vaccine_efficacy_meta_2026](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13133630/fullTextXML); chunks `ckj_ckd_vaccine_efficacy_meta_2026:p1:c1:ddbb9ed7fea9`, `ckj_ckd_vaccine_efficacy_meta_2026:p1:c2:e35ec322fb51`.
- Família `ckd_surrogates_clinical_endpoints`: [ckj_ckd_vaccine_efficacy_meta_2026](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13133630/fullTextXML); chunks `ckj_ckd_vaccine_efficacy_meta_2026:p1:c2:e35ec322fb51`, `ckj_ckd_vaccine_efficacy_meta_2026:p1:c3:40e25d3ccb7c`.

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
