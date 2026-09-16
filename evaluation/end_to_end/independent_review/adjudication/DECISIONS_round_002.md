# Adjudicação e conferência documental — pacote único

Há 16 divergências de rótulo e seis casos adicionais de acesso limitado,
totalizando 22 itens para análise pontual. As duas anotações estão visíveis
porque esta etapa é de adjudicação, não de anotação cega.

O responsável deve ter familiaridade com vacinação, conforme o protocolo; apoio
do orientador é recomendado para as ambiguidades do manual. Registrar identificador
interno, data, decisão e fundamentação por item. Não inventar um terceiro revisor.
Não é necessário refazer os 48 itens: usar este pacote, mantendo aberta a auditoria
geral de evidências e famílias do benchmark sintético.

## Regras para resolver

- SUPPORTED exige sustentação direta; REFUTED exige contradição direta.
- MISLEADING exige parte factual relevante sustentada e distorção material identificada.
  Onze divergências são MISLEADING primário versus REFUTED secundário. Não escolher
  um deles automaticamente: explicar a aplicação consistente do manual.
- Informação geral não prova um caso local não identificado. Ausência de menção não refuta.
- Não manter rótulos apenas para alcançar cotas. Mudanças podem exigir nova estratificação,
  revisão de famílias ou substitutos antes do congelamento.
- O responsável pode manter o primeiro rótulo, aceitar o segundo, propor outro,
  excluir um caso mal definido ou deixá-lo pendente; sempre registrar fundamento.
- Uma mudança material na alegação exige nova anotação do item afetado, não a reutilização
  silenciosa dos rótulos da redação antiga.
- Há PDFs/XML já armazenados localmente em corpus/raw no PC do autor. Os caminhos
  relativos abaixo identificam os arquivos; pedir acesso ao snapshot quando a URL falhar.
  Não publicar esses bytes ou redistribuí-los sem verificar as condições de uso.
- Fontes do primeiro anotador são candidatas de evidência, não prova de que seu rótulo é correto.
  Os IDs de chunks ajudam a localizar contexto;
- Preservar ambos os retornos e as métricas calculadas antes desta discussão.
  PENDENTE não é um quinto veredito do sistema, apenas estado da revisão.

## Resumo do procedimento

O resumo final do formulário diz “catorze” insuficientes, lista 12 IDs e inclui o
item 033 como insuficiente, embora seu campo individual seja REFUTED. Foram usados
os campos individuais (11 insuficientes) no cálculo, sem corrigir a resposta original.
Conferir o item 033 e emitir correção separada das observações finais.

## annotation-001 — e2e-0018

A revisão de BCG de 2021 encontrou o mesmo resultado de proteção em todos os ensaios, independentemente do contexto epidemiológico.

- Motivo: conferência adicional de evidência.
- Primeiro rótulo original: REFUTED.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: bcg_effectiveness_context; split previsto: development.

Primeira justificativa: O texto descreve resultados distintos segundo contexto e tempo de seguimento. A conclusão de uniformidade é contradita; não inferir ineficácia geral da BCG.

Segunda justificativa: A revisão em questão (Trauer et al., Thorax 2021) tem como achado central exatamente o oposto: existe heterogeneidade considerável entre os ensaios de BCG, e essa variação é explicada pela intensidade/momento da exposição prévia a Mycobacterium tuberculosis (contexto epidemiológico de transmissão), com proteção sustentada mais evidente em cenários de transmissão em declínio. Ou seja, o resultado de proteção varia sistematicamente conforme o contexto, não é "o mesmo em todos os ensaios".

Fontes informadas pela revisora: Trauer JM, Kawai A, Coussens A, et al. "Timing of Mycobacterium tuberculosis exposure explains variation in BCG effectiveness: a systematic review and meta-analysis." Thorax 2021;76(11):1131-1141 (thorax_bcg_effectiveness_meta_2021). Resumo: "Review of 21 studies concludes variation in background intensity of Mycobacterium tuberculosis transmission explains the considerable heterogeneity in the results of trials of BCG vaccination, with sustained protection more evident in settings of declining transmission."

Dúvidas informadas: não tive acesso ao texto completo (XML) do PMC8526882 citado no SOURCES.md; a verificação baseou-se no resumo e em fontes secundárias (medRxiv/JCU) que reproduzem o objetivo e a conclusão do estudo, que são inequívocos quanto ao ponto central.

Pendência adicional: Acesso ao texto específico limitado; resumo e reprodução por outras fontes. Avaliar se a base documental é suficiente para esta proposição.

Chunks candidatos da primeira anotação: thorax_bcg_effectiveness_meta_2021:p1:c2:fb92535001d1, thorax_bcg_effectiveness_meta_2021:p1:c3:1c2ef8171bcc.

### Acesso às fontes do snapshot

- [Timing of Mycobacterium tuberculosis exposure explains variation in BCG effectiveness: a systematic review and meta-analysis](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8526882/fullTextXML) — thorax_bcg_effectiveness_meta_2021.
  Arquivo local: `corpus/raw/thorax_bcg_effectiveness_meta_2021.xml`; condição de uso: CC-BY-NC-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Proposição central: uniformidade de resultado entre ensaios, independentemente do contexto. O objetivo e a conclusão do estudo afirmam o oposto: heterogeneidade considerável entre ensaios, explicada pela intensidade/momento da exposição prévia a M. tuberculosis. Há contradição direta, logo REFUTED, e não MISLEADING: não existe parte factual relevante sustentada na alegação, apenas o tema verdadeiro (BCG), o que o manual proíbe usar como base para MISLEADING. Quanto à pendência de acesso: a alegação é sobre o achado central do estudo, e esse achado está enunciado no título e no resumo estruturado, que é a unidade documental adequada para essa alegação específica; resumo não é automaticamente insuficiente. O texto integral acrescentaria estratos e tamanhos de efeito, irrelevantes para decidir uniformidade versus heterogeneidade.
- Fontes, trechos/páginas e chunks conferidos: thorax_bcg_effectiveness_meta_2021 — título e resumo (Thorax 2021;76(11):1131-1141): a variação da intensidade de transmissão de fundo explica a heterogeneidade dos ensaios de BCG, com proteção sustentada mais evidente em cenários de transmissão em declínio. Chunks conferidos: thorax_bcg_effectiveness_meta_2021:p1:c2:fb92535001d1, thorax_bcg_effectiveness_meta_2021:p1:c3:1c2ef8171bcc (conferidos em nível de resumo pela URL do snapshot; o XML local corpus/raw/thorax_bcg_effectiveness_meta_2021.xml não foi aberto por mim).
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma. Sugiro apenas que, no congelamento, a linha de evidência registre explicitamente que a sustentação é de nível de resumo, para rastreabilidade.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-002 — e2e-0121

A revisão encontrou alguma atenuação da efetividade com vacinação repetida, portanto concluiu que abandonar a vacinação é melhor.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: MISLEADING.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: influenza_repeat_comparators; split previsto: test.

Primeira justificativa: Atenuação frente a outro comparador é usada para recomendar abandono, conclusão não sustentada pela revisão.

Segunda justificativa: A revisão sobre vacinação repetida contra influenza (Jones-Gray et al., Lancet Respiratory Medicine 2022) de fato encontrou atenuação da efetividade com vacinação repetida em temporadas consecutivas, mas a própria conclusão do estudo é que a vacinação em temporadas consecutivas "ainda proporcionou melhor proteção contra influenza do que não vacinar" (still provided better protection... than no vaccination). A inferência de que "abandonar a vacinação é melhor" contradiz diretamente essa conclusão — é um non sequitur.

Fontes informadas pela revisora: Jones-Gray E, Robinson EJ, Kucharski AJ, Fox A, Sullivan SG. "Does repeated influenza vaccination attenuate effectiveness? A systematic review and meta-analysis." Lancet Respir Med 2023;11(1):27-44 (lancet_repeated_influenza_meta_2022). Cobertura do Doherty Institute (15/12/2022): "They found that, when administered repeatedly in consecutive years, the effectiveness of the influenza vaccination might be reduced. However, vaccination in consecutive seasons still provided better protection against influenza than no vaccination."

Dúvidas informadas: nenhuma relevante quanto ao ponto lógico central.

Chunks candidatos da primeira anotação: lancet_repeated_influenza_meta_2022:p1:c2:ec9e1d7a49b2, lancet_repeated_influenza_meta_2022:p1:c3:1376e8bbb7ca.

### Acesso às fontes do snapshot

- [Does repeated influenza vaccination attenuate effectiveness? A systematic review and meta-analysis](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9780123/fullTextXML) — lancet_repeated_influenza_meta_2022.
  Arquivo local: `corpus/raw/lancet_repeated_influenza_meta_2022.xml`; condição de uso: CC-BY-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Critério aplicado uniformemente nas 11 divergências MISLEADING/REFUTED: REFUTED quando o documento-fonte afirma explicitamente o contrário da proposição central (a conclusão é contradita, não apenas não sustentada); MISLEADING quando a parte factual é sustentada e a conclusão é extrapolação material que a fonte não contradiz explicitamente, lembrando que ausência de menção não refuta. Aqui a alegação atribui à própria revisão uma conclusão ('abandonar a vacinação é melhor') que a revisão enuncia ao contrário: vacinação em temporadas consecutivas ainda protege mais do que não vacinar. A premissa (atenuação) é verdadeira, mas o núcleo da proposição é a conclusão atribuída à fonte, e essa conclusão é contradita de forma direta e explícita pelo documento. MISLEADING exigiria que a distorção não fosse explicitamente contradita; não é o caso.
- Fontes, trechos/páginas e chunks conferidos: lancet_repeated_influenza_meta_2022 — resumo/conclusão (Lancet Respir Med 2023;11(1):27-44): efetividade pode ser reduzida com administração repetida em anos consecutivos, porém a vacinação em temporadas consecutivas ainda conferiu melhor proteção do que a ausência de vacinação. Chunks conferidos: lancet_repeated_influenza_meta_2022:p1:c2:ec9e1d7a49b2, lancet_repeated_influenza_meta_2022:p1:c3:1376e8bbb7ca (nível de resumo).
- Ação sobre o item (manter, corrigir, excluir ou pendente): corrigir
- Correção textual sugerida, se necessária: Nenhuma alteração de texto da alegação. A correção é de rótulo (MISLEADING -> REFUTED); a alegação permanece idêntica e não exige nova anotação.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-008 — e2e-0021

A revisão de 2021 encontrou proteção da BCG na primeira infância, então esse efeito é permanente em qualquer contexto epidemiológico.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: MISLEADING.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: bcg_effectiveness_context; split previsto: development.

Primeira justificativa: Resultado sustentado de ensaios na infância extrapolado para duração e contextos sem respaldo. Trata-se de interpretação da revisão histórica, não orientação sobre revacinação. Revisar a classificação.

Segunda justificativa: Mesmo fundamento do item 001 — a própria revisão de 2021 (Trauer et al., Thorax) tem como conclusão central que a variação de efetividade da BCG é explicada pelo contexto epidemiológico de transmissão de M. tuberculosis, com proteção sustentada mais evidente especificamente em cenários de transmissão em declínio. Isso contradiz a ideia de um efeito "permanente em qualquer contexto epidemiológico".

Fontes informadas pela revisora: mesmo documento do item 001 (thorax_bcg_effectiveness_meta_2021).

Dúvidas informadas: nenhuma.

Chunks candidatos da primeira anotação: thorax_bcg_effectiveness_meta_2021:p1:c2:fb92535001d1, thorax_bcg_effectiveness_meta_2021:p1:c3:1c2ef8171bcc.

### Acesso às fontes do snapshot

- [Timing of Mycobacterium tuberculosis exposure explains variation in BCG effectiveness: a systematic review and meta-analysis](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8526882/fullTextXML) — thorax_bcg_effectiveness_meta_2021.
  Arquivo local: `corpus/raw/thorax_bcg_effectiveness_meta_2021.xml`; condição de uso: CC-BY-NC-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Critério aplicado uniformemente nas 11 divergências MISLEADING/REFUTED: REFUTED quando o documento-fonte afirma explicitamente o contrário da proposição central (a conclusão é contradita, não apenas não sustentada); MISLEADING quando a parte factual é sustentada e a conclusão é extrapolação material que a fonte não contradiz explicitamente, lembrando que ausência de menção não refuta. A premissa (proteção observada na primeira infância) é sustentada, mas a proposição central é a permanência do efeito 'em qualquer contexto epidemiológico', que é exatamente a tese que o estudo rejeita: a variação da efetividade é explicada pelo contexto de transmissão. Contradição direta com o achado central do documento, portanto REFUTED. Não se trata de orientação sobre revacinação, e sim de interpretação do que a revisão concluiu.
- Fontes, trechos/páginas e chunks conferidos: thorax_bcg_effectiveness_meta_2021 — título e resumo: a variação de efetividade é explicada pelo momento da exposição a M. tuberculosis e pela intensidade de transmissão de fundo. Chunks conferidos: thorax_bcg_effectiveness_meta_2021:p1:c2:fb92535001d1, thorax_bcg_effectiveness_meta_2021:p1:c3:1c2ef8171bcc (nível de resumo).
- Ação sobre o item (manter, corrigir, excluir ou pendente): corrigir
- Correção textual sugerida, se necessária: Nenhuma alteração textual; correção apenas de rótulo (MISLEADING -> REFUTED).
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-011 — e2e-0020

A revisão do BMJ relata reações locais após vacinas com alumínio, portanto demonstra que elas causam danos sistêmicos graves.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: MISLEADING.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: aluminum_local_reactions; split previsto: development.

Primeira justificativa: A observação local real não sustenta a conclusão sistêmica atribuída à revisão. Não minimizar reações adversas reais. Revisar fronteira MISLEADING/REFUTED.

Segunda justificativa: A revisão do BMJ de 2026 (mesma fonte do item 007) de fato relata reações locais (nódulos/granulomas persistentes) após vacinas contendo adjuvante de alumínio, mas classifica essas reações como localizadas, pouco frequentes, autolimitadas e de baixa a moderada certeza — e, adicionalmente, conclui que não há associação causal entre essas vacinas e desfechos sistêmicos graves ou de longo prazo. A inferência de "dano sistêmico grave" a partir de reações estritamente locais é um non sequitur e contradiz a própria conclusão do estudo citado.

Fontes informadas pela revisora: Doyon-Plourde P et al., BMJ 2026;393:e088921 (bmj_aluminium_adjuvants_2026): "Localised persistent nodules or granulomas were observed infrequently after diphtheria-tetanus-pertussis vaccines, consistent with delayed type hypersensitivity (<1%, self-limited; moderate to low certainty)"; e "Current evidence does not support causal associations between aluminium adjuvanted vaccines and serious or long term health outcomes."

Dúvidas informadas: nenhuma.

Chunks candidatos da primeira anotação: bmj_aluminium_adjuvants_2026:p1:c3:ee7613a8d44e, bmj_aluminium_adjuvants_2026:p1:c47:b15627b4c1d0.

### Acesso às fontes do snapshot

- [Aluminium adjuvants in vaccines and potential health effects - systematic review](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13147496/fullTextXML) — bmj_aluminium_adjuvants_2026.
  Arquivo local: `corpus/raw/bmj_aluminium_adjuvants_2026.xml`; condição de uso: CC-BY-NC-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Critério aplicado uniformemente nas 11 divergências MISLEADING/REFUTED: REFUTED quando o documento-fonte afirma explicitamente o contrário da proposição central (a conclusão é contradita, não apenas não sustentada); MISLEADING quando a parte factual é sustentada e a conclusão é extrapolação material que a fonte não contradiz explicitamente, lembrando que ausência de menção não refuta. A premissa é sustentada (a revisão relata nódulos/granulomas locais). A conclusão atribuída à revisão — demonstração de danos sistêmicos graves — é contradita explicitamente pelo mesmo documento, que conclui não haver associação entre vacinas com adjuvante de alumínio e desfechos graves ou de longo prazo, e que classifica as reações relatadas como localizadas, infrequentes e autolimitadas. Contradição direta, portanto REFUTED. Registro que isso não minimiza as reações locais, que são reais e permanecem descritas no item 014.
- Fontes, trechos/páginas e chunks conferidos: bmj_aluminium_adjuvants_2026 — resumo/resultados (BMJ 2026;393:e088921): nódulos ou granulomas localizados observados de forma infrequente após vacinas DTP, <1%, autolimitados, certeza moderada a baixa; e ausência de suporte a associações causais com desfechos graves ou de longo prazo. Chunks conferidos: bmj_aluminium_adjuvants_2026:p1:c3:ee7613a8d44e, bmj_aluminium_adjuvants_2026:p1:c47:b15627b4c1d0 (nível de resumo/seção de resultados publicada).
- Ação sobre o item (manter, corrigir, excluir ou pendente): corrigir
- Correção textual sugerida, se necessária: Nenhuma alteração textual; correção apenas de rótulo (MISLEADING -> REFUTED).
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-013 — e2e-0105

Há estimativas mais baixas de desempenho em algumas regiões, portanto a revisão prova que a vacina contra rotavírus é inútil nesses lugares.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: MISLEADING.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: rotavirus_geographic_performance; split previsto: test.

Primeira justificativa: Desempenho inferior real não equivale a inutilidade; incerteza e contexto precisam ser preservados.

Segunda justificativa: A revisão global de 2025 (Prunas/Asare/Pitzer et al., EClinicalMedicine) confirma que a eficácia/efetividade prevista da vacina varia entre regiões (de 18,6% a 94,3%), sendo menor nas regiões Africana, Sudeste Asiático e Mediterrâneo Oriental. Contudo, mesmo nas estimativas mais baixas, a vacina ainda confere proteção substancial (não nula/negativa); "inútil" é uma extrapolação não sustentada pelos próprios dados do estudo, que descrevem desempenho reduzido, não ausência de efeito.

Fontes informadas pela revisora: Prunas O et al. "Global estimates of rotavirus vaccine efficacy and effectiveness: a rapid review and meta-regression analysis." EClinicalMedicine 2025;81:103122 (eclinm_rotavirus_global_2025): "Predicted vaccine efficacy ranged from 69.6% to 94.3% across countries in the Americas, European, and Western Pacific Regions, with a decreased efficacy ranging from 18.6% to 85.3% in the African, South-East Asian, and Eastern Mediterranean regions."

Dúvidas informadas: nenhuma quanto ao dado numérico; a interpretação de "inútil" é a parte refutada.

Chunks candidatos da primeira anotação: eclinm_rotavirus_global_2025:p1:c1:7d798e22b00a, eclinm_rotavirus_global_2025:p1:c2:4d8fec8bc6a9, eclinm_rotavirus_global_2025:p1:c3:1ae9c1f1f25b.

### Acesso às fontes do snapshot

- [Global estimates of rotavirus vaccine efficacy and effectiveness - a rapid review and meta-regression analysis](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11925534/fullTextXML) — eclinm_rotavirus_global_2025.
  Arquivo local: `corpus/raw/eclinm_rotavirus_global_2025.xml`; condição de uso: CC-BY-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Critério aplicado uniformemente nas 11 divergências MISLEADING/REFUTED: REFUTED quando o documento-fonte afirma explicitamente o contrário da proposição central (a conclusão é contradita, não apenas não sustentada); MISLEADING quando a parte factual é sustentada e a conclusão é extrapolação material que a fonte não contradiz explicitamente, lembrando que ausência de menção não refuta. A premissa (estimativas mais baixas em algumas regiões) é sustentada. A conclusão de que a revisão 'prova que a vacina é inútil' nesses lugares é contradita pelos próprios números do documento: nas regiões de menor desempenho a eficácia prevista permanece positiva, de 18,6% a 85,3%. Eficácia positiva e inutilidade são incompatíveis, logo há contradição direta e não apenas extrapolação. Nota de calibração: não afirmo que o desempenho regional é adequado, apenas que o documento não sustenta inutilidade.
- Fontes, trechos/páginas e chunks conferidos: eclinm_rotavirus_global_2025 — resumo/resultados (EClinicalMedicine 2025;81:103122): eficácia prevista de 69,6% a 94,3% nas Américas, Europa e Pacífico Ocidental, e de 18,6% a 85,3% nas regiões Africana, Sudeste Asiático e Mediterrâneo Oriental. Chunks conferidos: eclinm_rotavirus_global_2025:p1:c1:7d798e22b00a, eclinm_rotavirus_global_2025:p1:c2:4d8fec8bc6a9, eclinm_rotavirus_global_2025:p1:c3:1ae9c1f1f25b.
- Ação sobre o item (manter, corrigir, excluir ou pendente): corrigir
- Correção textual sugerida, se necessária: Nenhuma alteração textual; correção apenas de rótulo (MISLEADING -> REFUTED).
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-015 — e2e-0027

Linhagens celulares são utilizadas como plataformas na produção de algumas vacinas virais.

- Motivo: conferência adicional de evidência.
- Primeiro rótulo original: SUPPORTED.
- Segundo rótulo da rodada revisada: SUPPORTED.
- Família: cell_lines_manufacturing; split previsto: development.

Primeira justificativa: A fonte descreve plataformas de expressão e produção.

Segunda justificativa: É um fato técnico bem estabelecido e consensual na literatura de fabricação de vacinas (inclusive no documento do corpus sobre linhagens celulares como plataformas de expressão para vacinas virais pós-Covid-19): linhagens como Vero, MRC-5, WI-38 e outras são utilizadas rotineiramente como substrato de cultivo viral na produção de vacinas (ex.: poliomielite, febre amarela, rubéola, alguns processos de influenza).

Fontes informadas pela revisora: título e escopo do documento do corpus "Animal Cell Lines as Expression Platforms in Viral Vaccine Production: A Post Covid-19 Perspective" (acsomega_animal_cell_lines_vaccines_2024), cujo próprio tema é a revisão do uso de linhagens celulares animais como plataformas de produção de vacinas virais.

Dúvidas informadas: não obtive o texto completo do artigo (XML do PMC11025085) para citar trecho/página específicos; a afirmação, porém, corresponde exatamente ao escopo e título do documento, que por si só corrobora a proposição.

Pendência adicional: Acesso restrito ao título/escopo do artigo específico; completar a conferência documental.

Chunks candidatos da primeira anotação: acsomega_animal_cell_lines_vaccines_2024:p1:c2:bdd7985b4783.

### Acesso às fontes do snapshot

- [Animal Cell Lines as Expression Platforms in Viral Vaccine Production: A Post Covid-19 Perspective](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11025085/fullTextXML) — acsomega_animal_cell_lines_vaccines_2024.
  Arquivo local: `corpus/raw/acsomega_animal_cell_lines_vaccines_2024.xml`; condição de uso: CC-BY-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): SUPPORTED
- Fundamentação e aplicação do manual: A alegação é genérica e existencial: linhagens celulares são usadas como plataformas na produção de 'algumas' vacinas virais. O título e o escopo declarado do documento afirmam exatamente essa proposição (linhagens celulares animais como plataformas de expressão na produção de vacinas virais), o que constitui sustentação direta. Avaliação de suficiência, conforme exigido: para uma alegação existencial e de escopo amplo, o enunciado de escopo do documento é unidade suficiente; o texto integral seria necessário apenas para alegações quantitativas ou sobre linhagens específicas, que a proposição não faz. Mantive SUPPORTED sem usar conhecimento externo como prova.
- Fontes, trechos/páginas e chunks conferidos: acsomega_animal_cell_lines_vaccines_2024 — título e escopo declarado: 'Animal Cell Lines as Expression Platforms in Viral Vaccine Production: A Post Covid-19 Perspective'. Chunk conferido: acsomega_animal_cell_lines_vaccines_2024:p1:c2:bdd7985b4783, que descreve as linhagens celulares como plataformas de expressão usadas na produção de vacinas virais e resume os processos de produção baseados em cultura celular (localização informada no retorno de diligências de 16/09/2026; o XML local não foi aberto por mim, e a conferência do chunk se deu por esse registro).
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma. A conferência desejável foi atendida: o chunk p1:c2 cobre plataformas de expressão e processos baseados em cultura celular, o que basta para a alegação; não é mais necessário anexar exemplos de linhagens.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-018 — e2e-0054

A revisão de reprodução assistida de 2024 analisou somente infecção e não incluiu vacinação.

- Motivo: conferência adicional de evidência.
- Primeiro rótulo original: REFUTED.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: art_fertility_scope; split previsto: development.

Primeira justificativa: O objetivo e os resultados incluem comparação por vacinação.

Segunda justificativa: O documento do corpus sobre esse tema (Milostić-Srb et al., Diseases 2024) tem como título "The Effect of COVID-19 AND COVID-19 Vaccination on Assisted Human Reproduction Outcomes: A Systematic Review and Meta-Analysis" — ou seja, o próprio escopo declarado da revisão inclui explicitamente tanto o efeito da infecção por COVID-19 quanto da vacinação contra COVID-19 sobre desfechos de reprodução assistida, contradizendo a afirmação de que analisou "somente infecção".

Fontes informadas pela revisora: Milostić-Srb A et al. "The Effect of COVID-19 and COVID-19 Vaccination on Assisted Human Reproduction Outcomes: A Systematic Review and Meta-Analysis." Diseases 2024;12(9):201 (mdpi_covid_art_fertility_2024) — título e objeto do estudo.

Dúvidas informadas: não obtive o corpo completo do artigo (apenas título, afiliações e abertura do resumo) para citar um trecho metodológico específico, mas o título por si só é suficiente para refutar a proposição de que a revisão tratou "somente" de infecção.

Pendência adicional: Acesso restrito ao título e abertura do resumo; conferir o escopo efetivamente estudado.

Chunks candidatos da primeira anotação: mdpi_covid_art_fertility_2024:p1:c1:7b6dee18627c, mdpi_covid_art_fertility_2024:p1:c2:3be37682c018.

### Acesso às fontes do snapshot

- [The Effect of COVID-19 and COVID-19 Vaccination on Assisted Human Reproduction Outcomes - systematic review and meta-analysis](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11431602/fullTextXML) — mdpi_covid_art_fertility_2024.
  Arquivo local: `corpus/raw/mdpi_covid_art_fertility_2024.xml`; condição de uso: CC-BY-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: A alegação é sobre o escopo da revisão: teria analisado 'somente infecção', sem vacinação. O escopo declarado do documento inclui explicitamente as duas exposições, o que contradiz diretamente a proposição central. Suficiência: para uma alegação de escopo, o título e o objetivo declarados são a unidade documental pertinente; não é preciso o corpo do artigo para constatar que a vacinação integra o objeto do estudo. Não há parte factual relevante sustentada que justificasse MISLEADING.
- Fontes, trechos/páginas e chunks conferidos: mdpi_covid_art_fertility_2024 — título e objetivo (Diseases 2024;12(9):201): 'The Effect of COVID-19 and COVID-19 Vaccination on Assisted Human Reproduction Outcomes: A Systematic Review and Meta-Analysis'. Chunks conferidos: mdpi_covid_art_fertility_2024:p1:c1:7b6dee18627c, mdpi_covid_art_fertility_2024:p1:c2:3be37682c018 (nível de título/resumo).
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-019 — e2e-0019

A vacina quadrivalente inclui proteção contra os tipos 16 e 18, então protege contra qualquer tipo de HPV.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: MISLEADING.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: hpv_type_coverage; split previsto: development.

Primeira justificativa: Premissa factual sobre tipos incluídos seguida de extrapolação a todos os tipos. Revisar atomicidade e fronteira com REFUTED; não preservar classe por cota.

Segunda justificativa: A vacina quadrivalente cobre apenas os tipos 6, 11, 16 e 18 de um universo de mais de 200 tipos de HPV descritos. Cobrir os dois principais tipos oncogênicos (16 e 18) não equivale a proteger contra "qualquer tipo"; há evidência de proteção cruzada parcial para alguns tipos filogeneticamente próximos (ex. 31, 45), mas não para o espectro completo de genótipos, inclusive tipos circulantes relevantes no Brasil (ex. 52, 53, 58) não cobertos pela quadrivalente.

Fontes informadas pela revisora: mesma base do item 006; artigo sobre genótipos de HPV mais prevalentes em exames PCR no Brasil não cobertos pela vacina quadrivalente (HPV 52, 53, 54).

Dúvidas informadas: nenhuma.

Chunks candidatos da primeira anotação: ms_hpv:p1:c5:d2c96edbaf75.

### Acesso às fontes do snapshot

- [HPV - prevenção e vacinação](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/h/hpv) — ms_hpv.
  Arquivo local: `corpus/raw/ms_hpv.html`; condição de uso: CC-BY-ND-3.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Critério aplicado uniformemente nas 11 divergências MISLEADING/REFUTED: REFUTED quando o documento-fonte afirma explicitamente o contrário da proposição central (a conclusão é contradita, não apenas não sustentada); MISLEADING quando a parte factual é sustentada e a conclusão é extrapolação material que a fonte não contradiz explicitamente, lembrando que ausência de menção não refuta. A premissa (inclusão dos tipos 16 e 18) é verdadeira, mas a proposição central é a proteção contra qualquer tipo de HPV, contradita diretamente pela fonte do corpus, que descreve a vacina como quadrivalente, restrita aos tipos 6, 11, 16 e 18. Cobertura de quatro tipos e cobertura de qualquer tipo são mutuamente excludentes; por isso REFUTED e não MISLEADING. Sobre a observação de atomicidade da primeira anotação: a alegação é atômica o bastante, pois premissa e conclusão compartilham o mesmo objeto.
- Fontes, trechos/páginas e chunks conferidos: ms_hpv — página oficial 'HPV: prevenção e vacinação' (Ministério da Saúde), descrição da vacina quadrivalente como protetora contra os tipos 6, 11, 16 e 18. Chunk conferido: ms_hpv:p1:c5:d2c96edbaf75.
- Ação sobre o item (manter, corrigir, excluir ou pendente): corrigir
- Correção textual sugerida, se necessária: Nenhuma alteração textual; correção apenas de rótulo (MISLEADING -> REFUTED).
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-022 — e2e-0148

O documento de 2026 calcula incremento percentual da cobertura pela diferença entre períodos dividida pelo valor do período anterior.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: SUPPORTED.
- Segundo rótulo da rodada revisada: INSUFFICIENT_EVIDENCE.
- Família: vaccination_coverage_relative_increment; split previsto: test.

Primeira justificativa: Percentual relativo, não diferença absoluta em pontos percentuais.

Segunda justificativa: A fórmula descrita [(novo − antigo) / antigo] é de fato a definição matemática padrão e correta de "incremento percentual" (taxa de variação percentual), amplamente utilizada em relatórios epidemiológicos, incluindo os do Ministério da Saúde. No entanto, não localizei, dentro do corpus disponível em SOURCES.md, um documento de 2026 específico e identificável cujo texto eu pudesse cotejar diretamente para confirmar que é essa a fórmula empregada no documento referido pela proposição (que não nomeia o documento).

Fontes informadas pela revisora: busca no corpus por documentos de 2026 do PNI/MS (ex. ms_multivacinacao_2026, ms_calendario_2026, ms_influenza_2026) que apresentassem seção metodológica de cálculo de "incremento percentual" — não localizei uma seção explícita com essa fórmula no material recuperado.

Dúvidas informadas: alta — proposição não identifica de qual "documento de 2026" se trata; sem esse dado, a checagem pontual da fórmula efetivamente usada não é possível dentro do corpus, ainda que a fórmula descrita seja matematicamente padrão.

Pendência adicional: Documento de 2026 não identificado/localizado pela revisora; conferir a identificação e o escopo da proposição.

Chunks candidatos da primeira anotação: ms_multivacinacao_2026:p7:c1:6c378fb74cf0.

### Acesso às fontes do snapshot

- [Multivacinação 2026 - estratégia para atualização da caderneta de menores de 15 anos](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/estrategia-para-atualizacao-da-cadernetas-de-vacinacao-das-criancas-e-dos-adolescentes-menores-de-15-anos-2013-multivacinacao-2026.pdf/@@download/file) — ms_multivacinacao_2026.
  Arquivo local: `corpus/raw/ms_multivacinacao_2026.pdf`; condição de uso: CC-BY-NC-SA-4.0.
- [Instrução Normativa do Calendário Nacional de Vacinação 2026](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/instrucao-normativa-que-instrui-o-calendario-nacional-de-vacinacao-2026.pdf/@@download/file) — ms_calendario_2026.
  Arquivo local: `corpus/raw/ms_calendario_2026.pdf`; condição de uso: official-act-BR-L9610-art8-IV.
- [Estratégia de vacinação contra a influenza nas regiões Nordeste Centro-Oeste Sul e Sudeste - 2026](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/guias-e-manuais/2026/estrategia-de-vacinacao-contra-a-influenza-nas-regioes-nordeste-centro-oeste-sul-e-sudeste-2026.pdf/@@download/file) — ms_influenza_2026.
  Arquivo local: `corpus/raw/ms_influenza_2026.pdf`; condição de uso: CC-BY-NC-SA-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): SUPPORTED
- Fundamentação e aplicação do manual: Diligência atendida: conferi diretamente a nota metodológica da Figura 2, na página 7 do arquivo digital (página impressa 6) de ms_multivacinacao_2026, que define o incremento percentual como a diferença entre o valor do período atual e o do período anterior, dividida pelo valor do período anterior, multiplicada por 100. A alegação descreve exatamente essa operação; a multiplicação por 100 apenas expressa o quociente em pontos percentuais e não altera a fórmula, de modo que há sustentação direta e o rótulo é SUPPORTED. Registro a fundamentação anterior, que agora fica superada: eu havia proposto PENDENTE porque não decido por INSUFFICIENT_EVIDENCE quando a insuficiência não é do corpus, e sim do meu acesso: o documento está identificado no manifesto e existe no snapshot local, e a primeira anotação aponta a nota metodológica em ms_multivacinacao_2026:p7. INSUFFICIENT_EVIDENCE significaria que o corpus não permite decidir, o que seria uma afirmação falsa sobre o corpus. Busca realizada: tentativa de recuperação do PDF de Multivacinação 2026 e das publicações de 2026 do PNI (calendário 2026, influenza 2026) pela URL pública; não obtive o texto da seção metodológica que define incremento percentual. Informação faltante à época: o enunciado literal da fórmula na p.7 do documento. Com a diligência, a condição que eu mesma havia enunciado (SUPPORTED se a fórmula fosse (atual - anterior)/anterior x 100) foi verificada de forma literal, e o rótulo se resolveu por ela.
- Fontes, trechos/páginas e chunks conferidos: ms_multivacinacao_2026, p.7 do arquivo digital (p. impressa 6), nota da Figura 2 'Incremento de coberturas vacinais (%) das vacinas para menores de 2 anos. Brasil, 2022-2025': o incremento percentual foi calculado pela diferença entre o valor observado no período atual e no período anterior, dividida pelo valor do período anterior, multiplicada por 100. Chunk conferido: ms_multivacinacao_2026:p7:c1:6c378fb74cf0. Integridade do arquivo conferida por mim: SHA-256 3f1edcd8a0481374f77ad46e6966b81e45a23b8187c9c1abfadef085b1b302df, 935.928 bytes, coincidente com o document_sha256 do chunk.
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma. Retiro a sugestão anterior de nomear o documento na redação: a diligência mostrou que o chunk versionado ancora a alegação sem ambiguidade, e a mudança seria material, exigindo nova anotação sem ganho de verificabilidade.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-023 — e2e-0152

O documento de 2026 define incremento percentual apenas como a diferença simples entre as duas coberturas, sem divisão pelo valor anterior.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: REFUTED.
- Segundo rótulo da rodada revisada: INSUFFICIENT_EVIDENCE.
- Família: vaccination_coverage_relative_increment; split previsto: test.

Primeira justificativa: A nota metodológica inclui divisão e multiplicação por 100.

Segunda justificativa: Assim como no item 022, não foi possível localizar, no corpus disponível, o documento de 2026 específico mencionado na proposição para confirmar ou refutar diretamente qual fórmula ele emprega. Do ponto de vista conceitual, a diferença simples entre duas coberturas (em pontos percentuais) é estatisticamente distinta de "incremento percentual" (variação relativa), mas isso por si só não permite concluir o que um documento não identificado efetivamente define, sem acesso ao texto.

Fontes informadas pela revisora: mesma busca do item 022, sem resultado conclusivo.

Dúvidas informadas: alta — mesma limitação do item 022: documento-fonte não identificado nominalmente na proposição nem localizado no corpus com essa definição metodológica específica.

Pendência adicional: Mesma pendência de identificação documental do item 022.

Chunks candidatos da primeira anotação: ms_multivacinacao_2026:p7:c1:6c378fb74cf0.

### Acesso às fontes do snapshot

- [Multivacinação 2026 - estratégia para atualização da caderneta de menores de 15 anos](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/estrategia-para-atualizacao-da-cadernetas-de-vacinacao-das-criancas-e-dos-adolescentes-menores-de-15-anos-2013-multivacinacao-2026.pdf/@@download/file) — ms_multivacinacao_2026.
  Arquivo local: `corpus/raw/ms_multivacinacao_2026.pdf`; condição de uso: CC-BY-NC-SA-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Diligência atendida na mesma conferência do item 022, como eu havia proposto, para evitar rótulos mutuamente incompatíveis. A nota metodológica da p.7 enuncia divisão pelo valor do período anterior e multiplicação por 100, o que contradiz diretamente a proposição de que o documento definiria incremento percentual 'apenas como a diferença simples entre as duas coberturas, sem divisão pelo valor anterior'. Contradição direta e literal, logo REFUTED, e não MISLEADING: não há parte factual relevante sustentada, apenas a menção correta ao tema do indicador.
- Fontes, trechos/páginas e chunks conferidos: ms_multivacinacao_2026, p.7 do arquivo digital (p. impressa 6), nota da Figura 2, com a fórmula transcrita no item 022. Chunk conferido: ms_multivacinacao_2026:p7:c1:6c378fb74cf0. Integridade do arquivo conferida por mim (SHA-256 3f1edcd8a0481374f77ad46e6966b81e45a23b8187c9c1abfadef085b1b302df).
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma; retiro também aqui a sugestão de nomear o documento, pelas razões do item 022. Com 022 em SUPPORTED e 023 em REFUTED, a família vaccination_coverage_relative_increment mantém duas classes distintas no split test, sem necessidade de substitutos.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-024 — e2e-0051

A revisão de reprodução assistida de 2024 examinou tanto histórico de covid-19 quanto vacinação contra covid-19.

- Motivo: conferência adicional de evidência.
- Primeiro rótulo original: SUPPORTED.
- Segundo rótulo da rodada revisada: SUPPORTED.
- Família: art_fertility_scope; split previsto: development.

Primeira justificativa: Escopo inclui infecção e vacinação; não confundir exposições.

Segunda justificativa: O título do documento do corpus (Milostić-Srb et al., Diseases 2024) já declara esse duplo escopo: "The Effect of COVID-19 AND COVID-19 Vaccination on Assisted Human Reproduction Outcomes: A Systematic Review and Meta-Analysis" — confirmando que a revisão examinou tanto a infecção por COVID-19 quanto a vacinação.

Fontes informadas pela revisora: mesma fonte do item 018 (mdpi_covid_art_fertility_2024) — título do artigo.

Dúvidas informadas: nenhuma quanto ao escopo declarado no título; não tive acesso ao corpo completo do artigo para detalhar como cada variável foi tratada estatisticamente.

Pendência adicional: Mesmo limite de acesso do item 018; conferir inclusão das duas exposições.

Chunks candidatos da primeira anotação: mdpi_covid_art_fertility_2024:p1:c1:7b6dee18627c, mdpi_covid_art_fertility_2024:p1:c2:3be37682c018.

### Acesso às fontes do snapshot

- [The Effect of COVID-19 and COVID-19 Vaccination on Assisted Human Reproduction Outcomes - systematic review and meta-analysis](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11431602/fullTextXML) — mdpi_covid_art_fertility_2024.
  Arquivo local: `corpus/raw/mdpi_covid_art_fertility_2024.xml`; condição de uso: CC-BY-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): SUPPORTED
- Fundamentação e aplicação do manual: A alegação afirma que a revisão examinou as duas exposições, infecção prévia e vacinação. O escopo declarado do documento sustenta diretamente essa proposição. Suficiência: alegação de escopo é decidível pelo título e objetivo declarados. Registro o limite: a alegação não afirma nada sobre resultados, estratificação ou significância, de modo que a ausência do corpo do artigo não afeta o rótulo. Item coerente, por construção, com o 018, que é sua negação e foi rotulado REFUTED.
- Fontes, trechos/páginas e chunks conferidos: mdpi_covid_art_fertility_2024 — título e objetivo (Diseases 2024;12(9):201). Chunks conferidos: mdpi_covid_art_fertility_2024:p1:c1:7b6dee18627c, mdpi_covid_art_fertility_2024:p1:c2:3be37682c018 (nível de título/resumo).
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-026 — e2e-0089

O documento de vacinação nas escolas de 2025 não prevê qualquer coleta ou registro de autorização dos responsáveis.

- Motivo: conferência adicional de evidência.
- Primeiro rótulo original: REFUTED.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: school_vaccination_consent; split previsto: development.

Primeira justificativa: O documento prevê coleta e registro de autorizações.

Segunda justificativa: A Estratégia de Vacinação nas Escolas 2025 do Ministério da Saúde é consistentemente descrita, em comunicações oficiais e orientações técnicas associadas (incluindo a Portaria MS nº 6.715/2025, que rege a estratégia), como condicionada ao consentimento dos pais/responsáveis: os alunos "serão vacinados... sempre com o consentimento dos familiares e/ou responsáveis", com uso de "termos de consentimento" assinados pelos responsáveis antes da vacinação em ambiente escolar. Isso contradiz diretamente a afirmação de que não há qualquer previsão de coleta/registro de autorização.

Fontes informadas pela revisora: comunicação oficial do Ministério da Saúde/MEC sobre a Campanha "Vacinação nas Escolas – Ciência e Defesa da Vida" 2025: "Os alunos... serão vacinados... sempre com o consentimento dos familiares e/ou responsáveis"; relato de execução municipal (Divinópolis-MG) descrevendo o fluxo de "termos de consentimento" assinados pelos pais antes da vacinação escolar, em conformidade com a Lei Federal nº 14.886/2024 (Programa Nacional de Vacinação na Escola).

Dúvidas informadas: não tive acesso ao texto integral do documento específico "Estratégia de Vacinação nas Escolas – 2025" (ms_escolas_2025) listado no SOURCES.md para citar o dispositivo exato de autorização; a conclusão apoia-se em múltiplas fontes oficiais convergentes sobre a mesma estratégia, que mencionam consistentemente a exigência de consentimento.

Pendência adicional: Documento específico de escolas 2025 não acessado integralmente; usadas comunicações relacionadas.

Chunks candidatos da primeira anotação: ms_escolas_2025:p13:c2:566ba4feb6bc.

### Acesso às fontes do snapshot

- [Estratégia de vacinação nas escolas 2025](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/estrategia-de-vacinacao-nas-escolas-2025.pdf/@@download/file) — ms_escolas_2025.
  Arquivo local: `corpus/raw/ms_escolas_2025.pdf`; condição de uso: CC-BY-NC-SA-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Diligência atendida: li a passagem no próprio documento invocado pela alegação. O Quadro 3 traz o bloco 'Obtenção de Autorização dos Pais', com a ação de definir processo para obter consentimento dos pais e/ou responsáveis, sob responsabilidade da Coordenação de Educação, e prevê criar formulários com termo de recusa em formato físico e digital, definir meios para a coleta e o registro das autorizações com prazos claros e monitorar a taxa de respostas. A alegação nega que exista qualquer previsão de coleta ou registro de autorização; o documento a prevê de forma expressa, inclusive com o verbo 'registro'. Contradição direta, logo REFUTED. Não é MISLEADING porque a alegação não tem parte factual sustentada: é uma negativa integralmente contradita. Convergi, agora com base documental própria, com o rótulo das duas rodadas, sem que a concordância tenha sido o critério.
- Fontes, trechos/páginas e chunks conferidos: ms_escolas_2025, p.13 do arquivo digital (p. impressa 12), Quadro 3, bloco 'Obtenção de Autorização dos Pais': definir processo para obter consentimento dos pais e/ou responsáveis; criar formulários com termo de recusa (modelo do Anexo A) em formato físico e digital; definir meios para a coleta e registro das autorizações, com prazos bem claros; monitorar a taxa de respostas. Complementos conferidos no mesmo documento: Quadro 4, p.14 do arquivo digital, que manda oferecer o termo de recusa para assinatura quando os responsáveis recusarem a vacina, e o Anexo 'Modelo de Termo de Recusa da Vacina'. Chunk conferido: ms_escolas_2025:p13:c2:566ba4feb6bc. Integridade do arquivo conferida por mim: SHA-256 9afcf8cb3dd03ea04c94bf1c19e9b11c7db94d0e08dd0f0f980d8e4b9c52d885, 4.550.864 bytes, coincidente com o document_sha256 do chunk. Fontes correlatas antes consultadas (comunicação MS/MEC, Portaria 6.715/2025, relato municipal) deixam de ser necessárias e não foram usadas como prova.
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma alteração de alegação. Como o rótulo final coincide com os das duas rodadas, não há correção a registrar e o item deixa de precisar de adjudication_basis=evidence_audit. Registro, porém, um achado da leitura, relevante para a auditoria do benchmark e não para este rótulo: o instrumento previsto é um termo de recusa, de lógica opt-out, e não um termo de autorização assinado; minha justificativa da segunda rodada descrevia 'termos de consentimento assinados', o que é impreciso quanto ao mecanismo. A resposta original fica preservada e a correção está no documento avulso.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-030 — e2e-0155

A estratégia atualiza cadernetas de menores de quinze anos, então quem é mais velho não precisa receber qualquer vacina.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: MISLEADING.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: multivaccination_target_age; split previsto: test.

Primeira justificativa: Recorte real de uma campanha é convertido em dispensa universal fora dela.

Segunda justificativa: A estratégia "Multivacinação 2026" (ms_multivacinacao_2026) tem como público-alvo declarado crianças e adolescentes menores de 15 anos — isso é um recorte operacional de uma ação específica, não uma declaração sobre as necessidades vacinais de outras faixas etárias. O Calendário Nacional de Vacinação prevê esquemas próprios para adultos e idosos (ex. dT, influenza, febre amarela, entre outras), de modo que o fato de uma estratégia pontual focar em menores de 15 anos não implica ausência de necessidade vacinal para pessoas mais velhas. É um non sequitur.

Fontes informadas pela revisora: título e escopo da publicação "Multivacinação 2026: estratégia para a atualização da caderneta de vacinação das crianças e dos adolescentes menores de 15 anos" (ms_multivacinacao_2026); Calendário Nacional de Vacinação do MS, que mantém esquemas específicos para adultos e idosos independentemente dessa estratégia.

Dúvidas informadas: nenhuma quanto ao raciocínio lógico.

Chunks candidatos da primeira anotação: ms_multivacinacao_2026:p1:c1:f01db00d520a.

### Acesso às fontes do snapshot

- [Multivacinação 2026 - estratégia para atualização da caderneta de menores de 15 anos](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/estrategia-para-atualizacao-da-cadernetas-de-vacinacao-das-criancas-e-dos-adolescentes-menores-de-15-anos-2013-multivacinacao-2026.pdf/@@download/file) — ms_multivacinacao_2026.
  Arquivo local: `corpus/raw/ms_multivacinacao_2026.pdf`; condição de uso: CC-BY-NC-SA-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Critério aplicado uniformemente nas 11 divergências MISLEADING/REFUTED: REFUTED quando o documento-fonte afirma explicitamente o contrário da proposição central (a conclusão é contradita, não apenas não sustentada); MISLEADING quando a parte factual é sustentada e a conclusão é extrapolação material que a fonte não contradiz explicitamente, lembrando que ausência de menção não refuta. A premissa (recorte etário da estratégia) é verdadeira. A conclusão — dispensa universal de vacinas para quem tem quinze anos ou mais — é contradita diretamente por documento do próprio corpus, o Calendário Nacional de Vacinação, que mantém esquemas para adolescentes mais velhos, adultos, gestantes e idosos, e pela estratégia de influenza 2026, cujos grupos prioritários incluem idosos. O recorte operacional de uma ação não é enunciado de dispensa, e o corpus enuncia o oposto da conclusão.
- Fontes, trechos/páginas e chunks conferidos: ms_multivacinacao_2026 — público-alvo declarado no item 2.5, crianças e adolescentes menores de 15 anos (até 14 anos, 11 meses e 29 dias); chunk conferido ms_multivacinacao_2026:p1:c1:f01db00d520a. Evidência direta de indicação vacinal acima dessa faixa, conferida por mim no mesmo documento, Anexo 'Vacinas ofertadas durante a Multivacinação 2026': a linha dT prevê, para pessoas a partir de 7 anos, esquema básico de três doses e reforço a cada 10 anos, sem limite superior de idade; a linha influenza inclui grupos especiais independentemente da idade. Conferência desejável indicada no retorno de diligências: ms_calendario_2026:p25:c1:e18d32a958d1 (influenza para idosos a partir de 60 anos) e ms_calendario_2026:p25:c2:809af2820757 (uma dose anual por temporada para idosos), registrados aqui como localizados no snapshot, não abertos por mim.
- Ação sobre o item (manter, corrigir, excluir ou pendente): corrigir
- Correção textual sugerida, se necessária: Nenhuma alteração textual; correção apenas de rótulo (MISLEADING -> REFUTED).
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-031 — e2e-0141

A baixa cobertura vacinal foi a única causa do surto de sarampo observado neste bairro.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: INSUFFICIENT_EVIDENCE.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: measles_manaus_historical_outbreak; split previsto: test.

Primeira justificativa: Cenário fictício sem bairro, dados de casos, cobertura ou investigação de fatores concorrentes.

Segunda justificativa: O estudo do corpus sobre o surto de sarampo na Amazônia brasileira (Manaus, 2018–2019) mostra que, embora a baixa cobertura vacinal seja um fator central (cerca de 95% dos casos ocorreram em pessoas não vacinadas na última década), o próprio estudo identifica fatores socioeconômicos como determinantes adicionais da disseminação da doença — áreas com maior densidade de casos tendiam a ter menor padrão de vida. Isso corrobora a natureza multifatorial de surtos de sarampo (cobertura vacinal, fatores socioeconômicos, mobilidade populacional, etc.), contradizendo a afirmação de causa única. Além disso, a proposição refere-se a "este bairro" (não identificado), o que também é um dado local não verificável isoladamente.

Fontes informadas pela revisora: Martins FM et al. "Temporal and spatial analysis of over 7,000 measles cases outbreak from 2018 to 2019 in the Brazilian Amazon." Einstein (São Paulo) 2024;22:eAO0931 (einstein_measles_amazon_spatiotemporal_2024). Destaques: "Approximately 95% of the measles cases reported occurred in unvaccinated individuals... Our findings revealed that socioeconomic factors influence the spread of the disease"; e no resumo: "spatial analysis revealed that areas with the highest case densities tended to have the lowest standard of living."

Dúvidas informadas: o estudo consultado é sobre Manaus, não sobre "este bairro" não identificado; a conclusão sobre multicausalidade é generalizável ao padrão epidemiológico de surtos de sarampo, mas o evento específico do bairro citado não é, por si, verificável.

Chunks candidatos da primeira anotação: nenhum conclusivo.

### Acesso às fontes do snapshot

- [Temporal and spatial analysis of over 7,000 measles cases outbreak from 2018 to 2019 in the Brazilian Amazon](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11081026/fullTextXML) — einstein_measles_amazon_spatiotemporal_2024.
  Arquivo local: `corpus/raw/einstein_measles_amazon_spatiotemporal_2024.xml`; condição de uso: CC-BY-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): INSUFFICIENT_EVIDENCE
- Fundamentação e aplicação do manual: Corrijo meu próprio rótulo da segunda rodada. A proposição é causal e local, sobre um surto observado 'neste bairro', sem identificação de bairro, período, número de casos, cobertura local ou investigação. O manual é explícito: informação geral não prova, e tampouco refuta, um caso local não identificado. O estudo de Manaus 2018-2019 descreve outro evento, em outra unidade territorial, e serve para mostrar que surtos de sarampo costumam ser multifatoriais, o que é enunciado geral, não contradição direta do caso alegado. Aplico o mesmo critério nos itens 037 e 046, também locais e não identificados. Registro que INSUFFICIENT_EVIDENCE não significa que a alegação seja verdadeira.
- Fontes, trechos/páginas e chunks conferidos: Busca: einstein_measles_amazon_spatiotemporal_2024 (surto de Manaus, 2018-2019) e documentos do PNI sobre sarampo. Nenhum documento do corpus trata do bairro, do período ou do surto alegados. Nenhum chunk conferido como evidência conclusiva, conforme a regra para INSUFFICIENT_EVIDENCE. Informação faltante: identificação do território, série de casos, cobertura vacinal local e investigação de fatores concorrentes.
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma. Se o projeto quiser um item conclusivo sobre multicausalidade, ele deve ser uma alegação nova referida explicitamente ao surto de Manaus, com nova anotação, e não a reescrita silenciosa deste.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-033 — e2e-0123

A revisão encontrou respostas vacinais em pacientes renais sem diálise, então seus resultados se aplicam sem ressalvas a qualquer paciente em diálise.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: MISLEADING.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: ckd_nondialysis_population; split previsto: test.

Primeira justificativa: Resultados de população delimitada são extrapolados a outra condição.

Segunda justificativa: A literatura de imunogenicidade vacinal em doença renal crônica documenta de forma consistente que pacientes em diálise apresentam respostas imunes distintas (frequentemente mais reduzidas) das de pacientes com DRC não dialíticos, a ponto de exigirem protocolos vacinais próprios — por exemplo, diretrizes clínicas recomendam esquema de dose dobrada de vacina contra hepatite B especificamente para pacientes em diálise, com ausência de recomendação equivalente para pacientes com DRC pré-diálise, refletindo diferenças de resposta imunológica entre os dois grupos. Isso contraria a ideia de que resultados obtidos em não dialíticos se aplicariam "sem ressalvas" a pacientes em diálise.

Fontes informadas pela revisora: revisão sistemática (Cochrane) sobre vacinação de dose dobrada de hepatite B versus dose padrão em pacientes com DRC, distinguindo subgrupos "em diálise" e "não em diálise" precisamente porque a resposta imune difere entre eles; metanálises sobre vacina COVID-19 em pacientes com DRC/diálise mostrando desfechos e taxas de soropositividade distintos dos observados em não dialíticos.

Dúvidas informadas: não tive acesso direto ao texto completo do artigo específico do corpus "ckj_ckd_vaccine_efficacy_meta_2026" (PMC13133630), publicado em 2026; a conclusão apoia-se em literatura consolidada e convergente sobre a distinção clínica entre os subgrupos, mas recomendo confirmação contra o texto exato desse artigo de 2026 quando disponível.

Pendência adicional: Texto específico não acessado; observações finais o incluem entre insuficientes, mas campo individual marca REFUTED. Confirmar intenção.

Chunks candidatos da primeira anotação: ckj_ckd_vaccine_efficacy_meta_2026:p1:c1:ddbb9ed7fea9, ckj_ckd_vaccine_efficacy_meta_2026:p1:c2:e35ec322fb51.

### Acesso às fontes do snapshot

- [Vaccine efficacy in CKD patients not on dialysis: a systematic review and meta-analysis](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13133630/fullTextXML) — ckj_ckd_vaccine_efficacy_meta_2026.
  Arquivo local: `corpus/raw/ckj_ckd_vaccine_efficacy_meta_2026.xml`; condição de uso: CC-BY-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): MISLEADING
- Fundamentação e aplicação do manual: Critério aplicado uniformemente nas 11 divergências MISLEADING/REFUTED: REFUTED quando o documento-fonte afirma explicitamente o contrário da proposição central (a conclusão é contradita, não apenas não sustentada); MISLEADING quando a parte factual é sustentada e a conclusão é extrapolação material que a fonte não contradiz explicitamente, lembrando que ausência de menção não refuta. Aqui a parte factual relevante é sustentada pelo próprio escopo do documento: a revisão avalia resposta vacinal em pacientes com DRC não dialíticos. A distorção material é de população: a conclusão estende 'sem ressalvas' os resultados a pacientes em diálise, justamente o grupo que a revisão exclui por desenho. Essa extrapolação não é contradita explicitamente pelo documento, que nada afirma sobre dialíticos; e ausência de menção não refuta. Por isso MISLEADING, e não REFUTED. Corrijo meu rótulo da segunda rodada, que se apoiou em literatura externa ao corpus, Cochrane de hepatite B e metanálises de COVID-19 em diálise, uso que o manual não admite como fonte conclusiva para esta alegação. A distorção é identificável apenas pelo escopo declarado, o que basta para MISLEADING sem depender do texto integral.
- Fontes, trechos/páginas e chunks conferidos: ckj_ckd_vaccine_efficacy_meta_2026 — título e escopo declarado: eficácia vacinal em pacientes com DRC não dialíticos. Chunks conferidos em nível de título/escopo: ckj_ckd_vaccine_efficacy_meta_2026:p1:c1:ddbb9ed7fea9, ckj_ckd_vaccine_efficacy_meta_2026:p1:c2:e35ec322fb51. Não abri corpus/raw/ckj_ckd_vaccine_efficacy_meta_2026.xml; a decisão não depende do corpo do artigo, apenas da população incluída.
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma alteração de alegação. Sobre a inconsistência apontada no resumo do procedimento: o campo individual da segunda rodada trazia REFUTED e as observações finais listavam este item entre os insuficientes, além de escreverem 'catorze' para 12 IDs listados. A resposta original fica preservada; a correção é registrada aqui e no documento avulso CORRECOES_E_AUDITORIA.md, que acompanha esta cópia. O cálculo feito pelos campos individuais, com 11 insuficientes, permanece o cálculo válido daquela rodada.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-034 — e2e-0057

Centros de reprodução assistida fecharam durante a pandemia, então esse fechamento comprova que a vacinação causa infertilidade.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: MISLEADING.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: art_fertility_scope; split previsto: development.

Primeira justificativa: Fechamento real por risco de disseminação não prova infertilidade causada pela vacina.

Segunda justificativa: Non sequitur claro — o fechamento de centros de reprodução assistida durante a pandemia foi motivado por medidas de distanciamento social e restrições sanitárias gerais (para reduzir a circulação do vírus SARS-CoV-2), sem qualquer relação lógica com a hipótese de que a vacinação causaria infertilidade. Além disso, essa hipótese específica já foi examinada e não sustentada pela literatura consultada no corpus, que não encontrou associação entre vacinação contra COVID-19 e piora de desfechos de reprodução assistida.

Fontes informadas pela revisora: literatura sobre fechamento de clínicas de reprodução assistida por medidas de biossegurança no início da pandemia (não relacionada à vacinação, que só passou a estar disponível posteriormente); mesma base dos itens 018/024 (mdpi_covid_art_fertility_2024) e literatura correlata (vaccine_covid_fertility_meta_2022) sobre ausência de associação entre vacinação e infertilidade.

Dúvidas informadas: nenhuma quanto à falácia lógica central.

Chunks candidatos da primeira anotação: mdpi_covid_art_fertility_2024:p1:c1:7b6dee18627c, mdpi_covid_art_fertility_2024:p1:c2:3be37682c018.

### Acesso às fontes do snapshot

- [The Effect of COVID-19 and COVID-19 Vaccination on Assisted Human Reproduction Outcomes - systematic review and meta-analysis](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11431602/fullTextXML) — mdpi_covid_art_fertility_2024.
  Arquivo local: `corpus/raw/mdpi_covid_art_fertility_2024.xml`; condição de uso: CC-BY-4.0.
- [The impact of COVID-19 vaccines on fertility - A systematic review and meta-analysis](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9464596/fullTextXML) — vaccine_covid_fertility_meta_2022.
  Arquivo local: `corpus/raw/vaccine_covid_fertility_meta_2022.xml`; condição de uso: Elsevier-COVID-resource-free-research-reuse.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Critério aplicado uniformemente nas 11 divergências MISLEADING/REFUTED: REFUTED quando o documento-fonte afirma explicitamente o contrário da proposição central (a conclusão é contradita, não apenas não sustentada); MISLEADING quando a parte factual é sustentada e a conclusão é extrapolação material que a fonte não contradiz explicitamente, lembrando que ausência de menção não refuta. A premissa sobre fechamento de centros durante a pandemia não é, ela própria, sustentada por documento do corpus, e o tema verdadeiro não basta para MISLEADING. Além disso, a proposição central, de que a vacinação causa infertilidade e de que o fechamento o comprovaria, é contradita diretamente por documento do corpus dedicado ao tema, que não encontra impacto da vacinação sobre fertilidade. Há, portanto, contradição direta somada à inversão cronológica evidente, já que os fechamentos antecederam a disponibilidade das vacinas.
- Fontes, trechos/páginas e chunks conferidos: vaccine_covid_fertility_meta_2022 — revisão sistemática e metanálise sobre impacto das vacinas de COVID-19 na fertilidade, sem associação deletéria; mdpi_covid_art_fertility_2024 — desfechos de reprodução assistida por infecção e por vacinação. Chunks conferidos em nível de título/resumo: mdpi_covid_art_fertility_2024:p1:c1:7b6dee18627c, mdpi_covid_art_fertility_2024:p1:c2:3be37682c018.
- Ação sobre o item (manter, corrigir, excluir ou pendente): corrigir
- Correção textual sugerida, se necessária: Nenhuma alteração textual; correção apenas de rótulo (MISLEADING -> REFUTED).
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-037 — e2e-0111

A pessoa vacinada há dez anos ainda mantém o mesmo nível de anticorpos contra febre amarela.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: INSUFFICIENT_EVIDENCE.
- Segundo rótulo da rodada revisada: MISLEADING.
- Família: yellow_fever_adult_seroprotection; split previsto: test.

Primeira justificativa: Cenário fictício sem exame, histórico ou condição imune; níveis individuais não são inferidos da média.

Segunda justificativa: A mesma revisão de 2022 mede "soroproteção" como uma variável categórica (título de anticorpos neutralizantes ≥ 1:10), não o nível absoluto/quantitativo de anticorpos. A literatura de cinética pós-vacinal indica declínio gradual dos títulos de anticorpos ao longo do tempo, mesmo quando a pessoa permanece soroprotegida (acima do limiar). Assim, "permanecer soroprotegido" não equivale a "manter o mesmo nível" de anticorpos — a proposição mistura um dado parcialmente correto (proteção pode persistir por 5–10 anos ou mais em adultos saudáveis) com uma inferência mais forte (nível constante de anticorpos) não sustentada pela evidência. Além disso, é uma afirmação sobre um indivíduo específico não identificado, portanto não verificável isoladamente.

Fontes informadas pela revisora: mesma fonte do item 036 (cid_yellow_fever_duration_meta_2022), que define o desfecho como proporção de "seropositive" (≥1:10), não como magnitude de título; literatura geral sobre declínio de títulos de anticorpos pós-vacinais ao longo do tempo.

Dúvidas informadas: nenhuma quanto à distinção conceitual entre soroproteção (limiar) e nível de anticorpos (magnitude); o caso individual em si permanece não verificável.

Chunks candidatos da primeira anotação: nenhum conclusivo.

### Acesso às fontes do snapshot

- [Duration of Protection After Vaccination Against Yellow Fever: A Systematic Review and Meta-Analysis](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9761887/fullTextXML) — cid_yellow_fever_duration_meta_2022.
  Arquivo local: `corpus/raw/cid_yellow_fever_duration_meta_2022.xml`; condição de uso: CC-BY-NC-ND-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): INSUFFICIENT_EVIDENCE
- Fundamentação e aplicação do manual: Corrijo meu rótulo da segunda rodada. A proposição é sobre uma pessoa não identificada, sem exame, sem data de vacinação verificável e sem condição imunológica conhecida. Níveis individuais de anticorpos não se deduzem de proporções agregadas de soroproteção, e a revisão de 2022 mede soropositividade por limiar, não magnitude de título; mas essa distinção metodológica, embora correta, é informação geral e não decide um caso individual não identificado, como o manual determina. Mantenho a coerência com os itens 031 e 046. Observo que meu rótulo anterior, MISLEADING, exigiria uma parte factual sustentada sobre essa pessoa, que não existe.
- Fontes, trechos/páginas e chunks conferidos: Busca: cid_yellow_fever_duration_meta_2022, que reporta soroproteção agregada e não permite inferência individual. Nenhum chunk usado como evidência conclusiva. Informação faltante: identificação do indivíduo, data e tipo de vacinação, resultado de titulação de anticorpos neutralizantes e estado imunológico.
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma. Se o projeto desejar um item conclusivo sobre a distinção entre limiar de soroproteção e nível de anticorpos, isso deve ser uma alegação nova, com nova anotação.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-038 — e2e-0008

A existência de proteção coletiva significa que quem não pode se vacinar está totalmente protegido.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: MISLEADING.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: herd_protection; split previsto: development.

Primeira justificativa: A proteção indireta é um mecanismo real, mas a fonte não a apresenta como proteção total; a conclusão remove essa limitação.

Segunda justificativa: Por definição epidemiológica, a imunidade coletiva (herd immunity) reduz a probabilidade de circulação do patógeno em uma população com alta cobertura vacinal, diminuindo o risco de exposição de indivíduos não vacinados, mas não elimina esse risco. Pessoas não vacinadas continuam suscetíveis à infecção caso entrem em contato com o agente (ex. viajantes, bolsões de baixa cobertura, casos importados); "totalmente protegido" é uma afirmação absoluta que o próprio conceito não sustenta.

Fontes informadas pela revisora: definição epidemiológica padrão de imunidade coletiva (conceito consolidado em manuais de vigilância epidemiológica e imunologia, incluindo referências indiretas nos próprios documentos do PNI que tratam de surtos em bolsões de suscetíveis mesmo em cenários de cobertura nacional elevada, como os casos de sarampo importado descritos na Operação Gota 2026).

Dúvidas informadas: nenhuma quanto à definição conceitual.

Chunks candidatos da primeira anotação: who_como_vacinas_funcionam:p1:c5:d6ebab3149f2, who_como_vacinas_funcionam:p1:c6:a5cdd716d308.

### Acesso às fontes do snapshot

- [Como as vacinas funcionam](https://www.who.int/pt/news-room/feature-stories/detail/how-do-vaccines-work) — who_como_vacinas_funcionam.
  Arquivo local: `corpus/raw/who_como_vacinas_funcionam.html`; condição de uso: WHO-website-research-private-study.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Critério aplicado uniformemente nas 11 divergências MISLEADING/REFUTED: REFUTED quando o documento-fonte afirma explicitamente o contrário da proposição central; MISLEADING quando a parte factual é sustentada e a conclusão é extrapolação material que a fonte não contradiz explicitamente, lembrando que ausência de menção não refuta. Eu havia proposto MISLEADING supondo que a limitação estivesse apenas ausente do texto da OMS, e registrei expressamente que, se a fonte enunciasse que a proteção não é completa, o rótulo migraria para REFUTED. A diligência localizou o enunciado literal: a página afirma que nenhuma vacina confere 100% de proteção e que a imunidade de grupo não confere proteção total às pessoas que não podem ser vacinadas com segurança. Não se trata mais de ausência de menção, e sim de contradição direta da proposição central, exatamente o caso que meu critério classifica como REFUTED, como nos itens 002, 011 e 013. Aplico a mudança que eu mesma condicionei, e não porque ela aproxima o rótulo do da segunda rodada.
- Fontes, trechos/páginas e chunks conferidos: who_como_vacinas_funcionam — passagem da página arquivada segundo a qual nenhuma vacina confere 100% de proteção e a imunidade de grupo não confere proteção total às pessoas que não podem ser vacinadas com segurança. Chunks conferidos: who_como_vacinas_funcionam:p1:c5:d6ebab3149f2, who_como_vacinas_funcionam:p1:c6:a5cdd716d308. Transparência quanto ao meio de conferência: a passagem me foi apresentada no retorno de diligências de 16/09/2026 como transcrita da página arquivada no snapshot; não abri corpus/raw/who_como_vacinas_funcionam.html. Antes do congelamento, sugiro que o responsável pelo snapshot valide a transcrição no arquivo, já que ela é o fundamento único da mudança de rótulo.
- Ação sobre o item (manter, corrigir, excluir ou pendente): corrigir
- Correção textual sugerida, se necessária: Nenhuma alteração de alegação; a correção é de rótulo (MISLEADING -> REFUTED), motivada por evidência documental nova e não por convergência.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-039 — e2e-0063

O guia de 2026 descreve Butantan-DV como vacina de dose única com vírus atenuados dos quatro sorotipos da dengue.

- Motivo: conferência adicional de evidência.
- Primeiro rótulo original: SUPPORTED.
- Segundo rótulo da rodada revisada: SUPPORTED.
- Família: butantan_dengue_product; split previsto: development.

Primeira justificativa: Composição e esquema são do produto específico.

Segunda justificativa: A Butantan-DV é confirmada, por múltiplas fontes de 2025–2026 (Anvisa, Ministério da Saúde, Instituto Butantan e cobertura jornalística especializada), como o primeiro imunizante contra dengue em dose única, produzido com tecnologia de vírus vivo atenuado, tetravalente (protege contra os quatro sorotipos — DENV-1, DENV-2, DENV-3 e DENV-4), aprovado pela Anvisa em novembro/dezembro de 2025 e incorporado ao Calendário Nacional de Vacinação do SUS a partir de 2026.

Fontes informadas pela revisora: Anvisa/Agência Brasil (08/12/2025): "Imunizante é o primeiro em dose única no mundo e protege contra os quatro tipos da doença... A Butantan-DV é o primeiro imunizante contra a dengue em dose única do mundo... utiliza a tecnologia de vírus vivo atenuado"; bula da Butantan-DV (butantan.gov.br, 2026): "vacina dengue 1, 2, 3 e 4 (atenuada)".

Dúvidas informadas: não tive acesso ao texto integral do "Guia técnico-operacional da vacina dengue atenuada do Instituto Butantan" (ms_guia_dengue_butantan_2026) especificamente, mas as características técnicas descritas na proposição (dose única, vírus atenuados, quatro sorotipos) são amplamente confirmadas por fontes oficiais e correspondem exatamente ao produto que esse guia documenta.

Pendência adicional: Guia específico de 2026 não acessado integralmente; características confirmadas por outras fontes.

Chunks candidatos da primeira anotação: ms_guia_dengue_butantan_2026:p5:c2:538cac9d7668, ms_guia_dengue_butantan_2026:p7:c1:7f0cb5ffec9b.

### Acesso às fontes do snapshot

- [Guia técnico-operacional da vacina dengue atenuada do Instituto Butantan](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/guias-e-manuais/2026/guia-tecnico-operacional-da-vacina-dengue-atenuada-do-instituto-butantan.pdf) — ms_guia_dengue_butantan_2026.
  Arquivo local: `corpus/raw/ms_guia_dengue_butantan_2026.pdf`; condição de uso: CC-BY-NC-SA-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): SUPPORTED
- Fundamentação e aplicação do manual: A alegação descreve atributos de produto, esquema de dose única, vírus atenuados e cobertura dos quatro sorotipos, atribuindo essa descrição ao guia técnico-operacional do próprio produto. Suficiência: a bula oficial do imunizante e o ato regulatório da Anvisa estabelecem esses atributos de forma inequívoca, e o guia é documento operacional derivado desse mesmo produto, de modo que a descrição alegada corresponde ao objeto documentado. Diferencio deliberadamente este caso do item 026: ali a alegação é uma negativa sobre procedimento interno de um documento, que só o documento pode decidir; aqui a alegação recai sobre atributos do produto, verificáveis em fonte regulatória primária.
- Fontes, trechos/páginas e chunks conferidos: Bula da vacina dengue 1, 2, 3 e 4 (atenuada) do Instituto Butantan e aprovação da Anvisa de dezembro de 2025, dose única, vírus vivo atenuado, tetravalente; ms_guia_dengue_butantan_2026 como documento do corpus. Chunks conferidos: ms_guia_dengue_butantan_2026:p5:c2:538cac9d7668, que descreve as vacinas tetravalentes de vírus vivos atenuados e identifica a Butantan-DV como de dose única, do Instituto Butantan; e ms_guia_dengue_butantan_2026:p7:c1:7f0cb5ffec9b, segundo o qual a vacina dengue (atenuada) contém vírus atenuados dos sorotipos 1, 2, 3 e 4, para os quatro sorotipos DENV-1 a DENV-4. Os três atributos da alegação, dose única, vírus atenuados e quatro sorotipos, estão cobertos pelo próprio guia, o que torna a decisão conclusiva sem depender das fontes regulatórias. Transparência quanto ao meio de conferência: as passagens me foram apresentadas no retorno de diligências de 16/09/2026 como transcritas do guia no snapshot; não abri corpus/raw/ms_guia_dengue_butantan_2026.pdf.
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma. A exigência de citar páginas do próprio guia está atendida com as p.5 e p.7 agora registradas como conferidas, o que remove a incompletude apontada no retorno de diligências.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-044 — e2e-0092

A estratégia leva vacinação às escolas, então a escola pode ignorar o processo de autorização previsto no próprio documento.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: MISLEADING.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: school_vaccination_consent; split previsto: development.

Primeira justificativa: Local acessível real não revoga o procedimento descrito.

Segunda justificativa: Autocontraditório em si (se o próprio documento prevê um processo de autorização dos responsáveis, como confirmado no item 026, não é logicamente possível que a mesma estratégia autorize a escola a ignorar esse processo). Além disso, fontes oficiais sobre a execução da Estratégia de Vacinação nas Escolas reforçam consistentemente que a vacinação depende do consentimento prévio dos pais/responsáveis, sem exceção descrita para a própria escola dispensar essa etapa.

Fontes informadas pela revisora: mesma base do item 026.

Dúvidas informadas: nenhuma quanto à autocontradição lógica.

Chunks candidatos da primeira anotação: ms_escolas_2025:p13:c2:566ba4feb6bc.

### Acesso às fontes do snapshot

- [Estratégia de vacinação nas escolas 2025](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/estrategia-de-vacinacao-nas-escolas-2025.pdf/@@download/file) — ms_escolas_2025.
  Arquivo local: `corpus/raw/ms_escolas_2025.pdf`; condição de uso: CC-BY-NC-SA-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): REFUTED
- Fundamentação e aplicação do manual: Diligência atendida na mesma leitura do item 026. O documento prescreve o processo de obtenção de autorização como ação do microplanejamento municipal, com responsável designado, instrumentos, prazos e monitoramento da taxa de respostas, e no Quadro 4 determina oferecer o termo de recusa para assinatura quando os responsáveis recusarem a vacina. Não há, em nenhum ponto, faculdade de a escola dispensar essa etapa; ao contrário, a escola e a Coordenação de Educação são justamente as instâncias encarregadas dela. A conclusão da alegação contradiz diretamente o procedimento previsto no documento que ela própria invoca, e a alegação ainda é internamente incoerente, pois pressupõe o procedimento para em seguida dispensá-lo. Por isso REFUTED, e não MISLEADING: a premissa de que a estratégia leva vacinação às escolas é verdadeira, mas a proposição central é contradita de forma direta.
- Fontes, trechos/páginas e chunks conferidos: ms_escolas_2025, p.13 do arquivo digital (p. impressa 12), Quadro 3, bloco 'Obtenção de Autorização dos Pais', com a atribuição de responsabilidade à Coordenação de Educação e a definição de meios para coleta e registro das autorizações, com prazos bem claros; e p.14 do arquivo digital, Quadro 4, com a determinação de oferecer o termo de recusa para assinatura em caso de recusa dos responsáveis. Chunk conferido: ms_escolas_2025:p13:c2:566ba4feb6bc. Integridade do arquivo conferida por mim (SHA-256 9afcf8cb3dd03ea04c94bf1c19e9b11c7db94d0e08dd0f0f980d8e4b9c52d885, 4.550.864 bytes).
- Ação sobre o item (manter, corrigir, excluir ou pendente): corrigir
- Correção textual sugerida, se necessária: Nenhuma alteração de alegação; a correção é de rótulo, de MISLEADING, na primeira rodada, para REFUTED.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-046 — e2e-0125

A vacinação anual piorou a proteção contra gripe das pessoas deste município.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: INSUFFICIENT_EVIDENCE.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: influenza_repeat_comparators; split previsto: test.

Primeira justificativa: Cenário fictício sem temporadas, vacinação, subtipos ou estimativas comparativas.

Segunda justificativa: Contradiz o padrão estabelecido pela literatura consultada (itens 002/029/035): a vacinação repetida/anual contra influenza, mesmo com alguma atenuação pontual de efetividade em certos subtipos, mantém-se superior à ausência de vacinação — nunca "piora" a proteção em relação a não vacinar. Além disso, é uma afirmação causal local (município não identificado) não verificável isoladamente.

Fontes informadas pela revisora: mesma base dos itens 002/029/035 (lancet_repeated_influenza_meta_2022).

Dúvidas informadas: nenhuma quanto ao padrão geral da literatura; o evento local específico não é verificável em si.

Chunks candidatos da primeira anotação: nenhum conclusivo.

### Acesso às fontes do snapshot

- [Does repeated influenza vaccination attenuate effectiveness? A systematic review and meta-analysis](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9780123/fullTextXML) — lancet_repeated_influenza_meta_2022.
  Arquivo local: `corpus/raw/lancet_repeated_influenza_meta_2022.xml`; condição de uso: CC-BY-4.0.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): INSUFFICIENT_EVIDENCE
- Fundamentação e aplicação do manual: Corrijo meu rótulo da segunda rodada, que aplicou literatura geral a um caso local não identificado, contrariando o manual. A proposição afirma piora de proteção em 'pessoas deste município', sem município, temporadas, subtipos, coorte ou estimativas comparativas. A revisão de vacinação repetida não mede esse caso e não pode confirmá-lo nem contradizê-lo; ela refuta a alegação genérica correspondente, que é objeto de outros itens da mesma família, como 002 e 035. Mantenho aqui o mesmo critério dos itens 031 e 037. Ressalvo que INSUFFICIENT_EVIDENCE não é endosso da alegação.
- Fontes, trechos/páginas e chunks conferidos: Busca: lancet_repeated_influenza_meta_2022 e demais documentos da família influenza no corpus; nenhum trata do município alegado. Nenhum chunk usado como evidência conclusiva. Informação faltante: identificação do município, temporadas comparadas, status vacinal da população, desfechos e estimativas de efetividade local.
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma. Observo que 046 e 002 pertencem à mesma família, influenza_repeat_comparators, e ao split test; a manutenção de 046 como INSUFFICIENT_EVIDENCE preserva a diversidade de classes dessa família sem que isso tenha sido motivo da decisão.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16

## annotation-048 — e2e-0139

O informe registra milhares de notificações suspeitas, então esse total representa falhas comprovadas de vacinas contra meningite.

- Motivo: divergência de rótulo.
- Primeiro rótulo original: MISLEADING.
- Segundo rótulo da rodada revisada: REFUTED.
- Família: meningitis_notifications_confirmation; split previsto: test.

Primeira justificativa: Notificações reais não estabelecem etiologia, histórico vacinal nem falha de produto.

Segunda justificativa: O Informe Epidemiológico de Meningite do Ministério da Saúde (2ª edição, dados de 2010 a 1º semestre de 2025) de fato registra milhares de notificações suspeitas (11.937 casos suspeitos notificados entre 1º/1/2025 e 30/6/2025), das quais apenas 51,7% (6.169) foram confirmadas como casos de meningite. Esses números medem a ocorrência da doença meningite (por diferentes etiologias — bacteriana, viral, etc.), não eventos adversos pós-vacinação nem falhas vacinais; a maior parte das notificações sequer é confirmada como meningite, e nenhuma delas, por si só, estabelece nexo causal com falha de vacina. É um non sequitur clássico de farmacovigilância/vigilância epidemiológica: confundir volume de notificações de uma doença de notificação compulsória com "falhas comprovadas" de um produto vacinal específico.

Fontes informadas pela revisora: Ministério da Saúde. "Informe epidemiológico de meningite: 2010 ao primeiro semestre de 2025" — 2ª edição (ms_meningite_2025): "11.937 Casos suspeitos notificados de 1º/1/2025 até 30/6/2025... 6.169 (51,7%) [confirmados]."

Dúvidas informadas: nenhuma quanto ao non sequitur; o dado numérico confirma que o informe existe e trata de notificações de casos da doença, não de falhas vacinais.

Pendência adicional: Justificativa informa 51,7% confirmados e depois diz que a maior parte não foi confirmada. Corrigir a inconsistência sem modificar o retorno original.

Chunks candidatos da primeira anotação: ms_meningite_2025:p1:c1:3f3eaaf07fe2, ms_meningite_2025:p1:c2:19783c2f6e51.

### Acesso às fontes do snapshot

- [Informe epidemiológico de meningite - 2010 ao primeiro semestre de 2025](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/m/meningite/situacao-epidemiologica/boletim-epidemiologico/informe-meningite-2a-edicao.pdf/@@download/file) — ms_meningite_2025.
  Arquivo local: `corpus/raw/ms_meningite_2025.pdf`; condição de uso: MS-reproduction-permitted-attribution-noncommercial.

### Decisão a preencher

- Rótulo final proposto (ou PENDENTE): MISLEADING
- Fundamentação e aplicação do manual: Critério aplicado uniformemente nas 11 divergências MISLEADING/REFUTED: REFUTED quando o documento-fonte afirma explicitamente o contrário da proposição central (a conclusão é contradita, não apenas não sustentada); MISLEADING quando a parte factual é sustentada e a conclusão é extrapolação material que a fonte não contradiz explicitamente, lembrando que ausência de menção não refuta. A parte factual relevante é sustentada: o informe registra, de fato, milhares de notificações suspeitas no período. A distorção material está na inferência, que converte volume de notificações de uma doença de notificação compulsória em falhas comprovadas de produto vacinal, ignorando etiologia, confirmação laboratorial, status vacinal e nexo causal. O informe não enuncia nada sobre falha vacinal, logo não há contradição direta e sim distorção de alcance e inferência, o que o manual classifica como MISLEADING. Corrijo aqui meu rótulo da segunda rodada e também a inconsistência aritmética da minha justificativa anterior: dos 11.937 casos suspeitos notificados entre 1º/1/2025 e 30/6/2025, 6.169, ou 51,7%, foram confirmados, ou seja, a maioria foi confirmada como meningite, e cerca de 48% não; onde escrevi que 'a maior parte das notificações sequer é confirmada' há erro, sem efeito sobre o argumento central, que é a ausência de vínculo entre notificação de doença e falha de vacina. A resposta original fica preservada e a correção é registrada aqui e no documento avulso CORRECOES_E_AUDITORIA.md.
- Fontes, trechos/páginas e chunks conferidos: ms_meningite_2025 — Informe epidemiológico de meningite, 2ª edição, dados de 1º/1/2025 a 30/6/2025: 11.937 casos suspeitos notificados, 6.169 confirmados, 51,7%. Chunks conferidos: ms_meningite_2025:p1:c1:3f3eaaf07fe2, ms_meningite_2025:p1:c2:19783c2f6e51.
- Ação sobre o item (manter, corrigir, excluir ou pendente): manter
- Correção textual sugerida, se necessária: Nenhuma alteração de alegação. Correção registrada apenas na justificativa, conforme pedido, sem modificar o retorno original da segunda rodada.
- Identificador interno do responsável: usr_002-independente
- Data: 2026-09-16
