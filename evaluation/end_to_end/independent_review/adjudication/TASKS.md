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
  Os IDs de chunks ajudam a localizar contexto; a verificação semântica é humana.
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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:

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

### Decisão humana a preencher

- Rótulo final proposto (ou PENDENTE):
- Fundamentação e aplicação do manual:
- Fontes, trechos/páginas e chunks conferidos:
- Ação sobre o item (manter, corrigir, excluir ou pendente):
- Correção textual sugerida, se necessária:
- Identificador interno do responsável:
- Data:
