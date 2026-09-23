# Revisão primária — calibração v2

Estado: **rascunho assistido**. Nenhum item abaixo conta como anotação humana até o
autor registrar sua decisão. As propostas foram escritas a partir do corpus local;
não vieram de mensagens de usuários nem de resultados do sistema.

## Como revisar

Para cada família, confira a fonte e avalie: alegação atômica, rótulo, evidência e
justificativa. É permitido aprovar uma família inteira e listar apenas exceções. Uma
resposta conjunta deve declarar que os 48 itens foram examinados; aprovação por
silêncio não será registrada.

Formato sugerido:

```text
Revisor: autor_do_projeto
Data: AAAA-MM-DD
Decisão: aprovo as famílias 01–12, exceto:
- ref2-cal-XXXX: trocar ...
```

Esta é a primeira revisão. Ela não substitui a segunda anotação cega por pessoa
distinta em ao menos 15 itens.

## 01 — Sinal pós-comercialização da vacina contra dengue

Fonte: [Ministério da Saúde — Segurança da vacina contra dengue após um ano de implementação no Brasil](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/boletins/epidemiologicos/edicoes/2025/boletim-epidemiologico-volume-56-no-18.pdf/@@download/file).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0001 | A farmacovigilância após a introdução da vacina contra dengue pode revelar eventos raros que não apareceram nos ensaios iniciais. | `SUPPORTED` | A fonte descreve essa função do monitoramento pós-implantação. |
| ref2-cal-0002 | Depois da aprovação, a vacina contra dengue deixa de ser acompanhada quanto a eventos adversos. | `REFUTED` | A fonte documenta acompanhamento contínuo. |
| ref2-cal-0003 | Como aumentaram as notificações de hipersensibilidade após a vacina contra dengue, ficou provado que toda reação notificada foi causada pelo imunizante. | `MISLEADING` | Há sinal de notificação, mas Esavi não implica causalidade automática. |
| ref2-cal-0004 | A urticária apresentada por uma adolescente de uma unidade não identificada foi causada pela dose de vacina contra dengue recebida na semana anterior. | `INSUFFICIENT_EVIDENCE` | O caso fictício não contém investigação causal. |

## 02 — Gravidade das notificações após vacina mpox

Fonte: [Ministério da Saúde — Monitoramento da segurança da vacina mpox](https://www.gov.br/saude/pt-br/vacinacao/esavi/monitoramento-dos-eventos/2025/informe-monitoramento-da-seguranca-da-vacina-mpox-se-6-de-2023-a-se-1-de-2025.pdf/@@download/file).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0005 | No informe brasileiro da vacina mpox, a maioria dos eventos adversos notificados foi classificada como não grave. | `SUPPORTED` | O informe registra 49 de 51 Esavi como não graves. |
| ref2-cal-0006 | Todos os eventos adversos notificados após a vacina mpox no informe brasileiro foram graves. | `REFUTED` | Contradiz a distribuição de gravidade. |
| ref2-cal-0007 | O registro de uma convulsão após a vacina mpox confirmou que a vacina foi a causa do evento. | `MISLEADING` | O evento existe, mas a causalidade foi indeterminada. |
| ref2-cal-0008 | A febre de um trabalhador de laboratório no dia seguinte à vacina mpox foi provocada pelo imunizante. | `INSUFFICIENT_EVIDENCE` | Faltam dados clínicos e causas alternativas. |

## 03 — Idade na primeira dose contra o sarampo

Fonte: [BMC Infectious Diseases — Effect of age at vaccination on measles vaccine effectiveness and immunogenicity](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7104533/fullTextXML).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0009 | Aplicar a primeira dose contra o sarampo mais cedo pode reduzir a imunogenicidade e a proteção obtidas após essa dose. | `SUPPORTED` | A revisão relata menor resposta após primeira dose precoce. |
| ref2-cal-0010 | A idade em que a primeira dose da vacina contra o sarampo é aplicada não influencia sua resposta imunológica. | `REFUTED` | Contradiz a associação observada. |
| ref2-cal-0011 | Como a vacinação precoce contra o sarampo pode gerar menor resposta após a primeira dose, uma criança vacinada cedo jamais se beneficia da segunda dose. | `MISLEADING` | Extrapola a primeira dose e ignora a alta soropositividade após a segunda. |
| ref2-cal-0012 | A falha vacinal de uma criança específica ocorreu porque ela recebeu a primeira dose contra o sarampo cedo demais. | `INSUFFICIENT_EVIDENCE` | Faltam histórico, confirmação e investigação individual. |

## 04 — Escopo da evidência para uma dose contra HPV

Fonte: [Vaccine X — Efficacy and immunogenicity of a single dose of HPV vaccine](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11169951/fullTextXML).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0013 | Uma revisão encontrou baixa ocorrência de infecção por HPV 16 ou 18 entre jovens vacinadas, sem diferença detectável entre os grupos de uma, duas ou três doses nos estudos avaliados. | `SUPPORTED` | Mantém população e desfechos da revisão. |
| ref2-cal-0014 | A revisão concluiu que uma dose de vacina contra HPV foi ineficaz em jovens saudáveis do sexo feminino. | `REFUTED` | É oposto à conclusão para essa população. |
| ref2-cal-0015 | Os resultados favoráveis de uma dose de vacina contra HPV em jovens saudáveis provam a mesma proteção duradoura para meninos, mulheres mais velhas e pessoas com HIV. | `MISLEADING` | Extrapola a grupos para os quais a revisão pede ensaios. |
| ref2-cal-0016 | Uma pessoa não identificada está protegida por toda a vida contra todos os tipos de HPV porque recebeu uma dose na adolescência. | `INSUFFICIENT_EVIDENCE` | Faltam produto, tipos virais e seguimento; a conclusão é universal. |

## 05 — Impacto das vacinas meningocócicas conjugadas

Fonte: [Revista Panamericana de Salud Pública — Impact and effectiveness of meningococcal vaccines](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6660876/fullTextXML).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0017 | Na revisão, vacinas meningocócicas conjugadas apresentaram proteção mais duradoura e maior impacto que vacinas polissacarídicas. | `SUPPORTED` | Reproduz a comparação da revisão. |
| ref2-cal-0018 | A revisão não encontrou impacto nem efetividade para vacinas meningocócicas conjugadas. | `REFUTED` | Contradiz as estimativas e conclusões. |
| ref2-cal-0019 | Como alguns estudos relataram efetividade de até 100% para vacina meningocócica conjugada, qualquer vacinado fica completamente protegido contra toda meningite. | `MISLEADING` | Universaliza estimativas por grupo e sorogrupo. |
| ref2-cal-0020 | Um caso de meningite em uma pessoa vacinada ocorreu porque a vacina meningocócica aplicada estava defeituosa. | `INSUFFICIENT_EVIDENCE` | Faltam agente, sorogrupo, produto e investigação. |

## 06 — Desfechos pneumocócicos por tipo vacinal em adultos

Fonte: [Pathogens — Efficacy and effectiveness of pneumococcal vaccines in adults](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10222197/fullTextXML).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0021 | A revisão em adultos sugere que PCV13 e PPSV23 protegem contra doença pneumocócica causada pelos sorotipos incluídos nas respectivas vacinas. | `SUPPORTED` | Preserva população e desfecho por tipo vacinal. |
| ref2-cal-0022 | PCV13 e PPSV23 não ofereceram proteção contra doença pneumocócica por sorotipos vacinais em adultos. | `REFUTED` | Contradiz a síntese da revisão. |
| ref2-cal-0023 | Os resultados contra sorotipos vacinais demonstram que PCV13 e PPSV23 previnem qualquer pneumonia em adultos, independentemente do agente ou sorotipo. | `MISLEADING` | Amplia resultados específicos para toda pneumonia. |
| ref2-cal-0024 | A pneumonia de um adulto vacinado ocorreu porque a vacina pneumocócica aplicada perdeu a eficácia. | `INSUFFICIENT_EVIDENCE` | Faltam etiologia, sorotipo e histórico clínico. |

## 07 — Certeza sobre vacinas aprimoradas de influenza

Fonte: [Reviews in Medical Virology — Relative efficacy, effectiveness and safety of enhanced influenza vaccines](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11850296/fullTextXML).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0025 | A revisão de vacinas de influenza aprimoradas não detectou aumento de eventos adversos graves, mas considerou limitada a evidência de efetividade relativa. | `SUPPORTED` | Mantém segurança e incerteza comparativa. |
| ref2-cal-0026 | A revisão detectou aumento de eventos adversos graves em todas as formulações aprimoradas de vacina contra influenza. | `REFUTED` | É oposto ao achado relatado. |
| ref2-cal-0027 | Uma estimativa de efetividade relativa de 88% prova que toda vacina de influenza aprimorada é sempre 88% superior à padrão em qualquer adulto e temporada. | `MISLEADING` | Seleciona um extremo e ignora heterogeneidade e certeza baixa. |
| ref2-cal-0028 | A gripe de um idoso vacinado confirma que a formulação aprimorada recebida por ele não funcionou. | `INSUFFICIENT_EVIDENCE` | Faltam confirmação, produto, temporada e contrafactual. |

## 08 — Associação agrupada entre vacinação e autoimunidade

Fonte: [Vaccines — Can Vaccination Trigger Autoimmune Disorders?](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8402438/fullTextXML).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0029 | Uma meta-análise encontrou ocorrência global semelhante de doenças autoimunes entre pessoas vacinadas e não vacinadas. | `SUPPORTED` | Reflete a associação agrupada de 0,99. |
| ref2-cal-0030 | A meta-análise confirmou que pessoas vacinadas desenvolvem doenças autoimunes com frequência maior que pessoas não vacinadas. | `REFUTED` | Contradiz a ocorrência equivalente estimada. |
| ref2-cal-0031 | Como não houve aumento global de doenças autoimunes, nenhuma manifestação autoimune individual pode ocorrer temporalmente após qualquer vacina. | `MISLEADING` | Confunde ausência de associação populacional com impossibilidade individual. |
| ref2-cal-0032 | A doença autoimune diagnosticada em uma pessoa meses após a vacinação foi desencadeada pela vacina. | `INSUFFICIENT_EVIDENCE` | Temporalidade isolada não determina causa. |

## 09 — Certeza da evidência de covid-19 na gestação

Fonte: [Drug Safety — Safety and effectiveness of COVID-19 vaccines during pregnancy](https://link.springer.com/content/pdf/10.1007/s40264-024-01458-w.pdf).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0033 | Uma revisão viva encontrou evidências, embora de baixa a muito baixa certeza, favoráveis à segurança e à efetividade das vacinas de covid-19 durante a gestação. | `SUPPORTED` | Mantém achados e certeza da evidência. |
| ref2-cal-0034 | A revisão concluiu que a vacinação contra covid-19 piorou todos os desfechos maternos e neonatais avaliados. | `REFUTED` | Contradiz segurança e reduções relatadas. |
| ref2-cal-0035 | A redução de infecção observada com vacinas de mRNA em gestantes prova proteção idêntica e total para qualquer plataforma, variante e momento da gestação. | `MISLEADING` | Elimina diferenças entre plataformas, variantes e incerteza. |
| ref2-cal-0036 | Uma complicação ocorrida na gestação foi causada pela vacina contra covid-19 recebida pela paciente. | `INSUFFICIENT_EVIDENCE` | Caso sem desfecho, cronologia ou avaliação causal. |

## 10 — Táticas de medo contra desinformação vacinal

Fonte: [Vaccine — Communication interventions for countering vaccine misinformation](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9829031/fullTextXML).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0037 | Uma revisão de intervenções de comunicação encontrou que táticas de medo podem ser ineficazes e até aumentar a adesão à desinformação sobre vacinas. | `SUPPORTED` | Preserva o caráter probabilístico da conclusão. |
| ref2-cal-0038 | A revisão mostrou que apresentar riscos vacinais com certeza absoluta sempre reduz a desinformação. | `REFUTED` | A revisão relata possível efeito contrário. |
| ref2-cal-0039 | Como humor e avisos prévios foram estratégias promissoras, está provado que qualquer mensagem bem-humorada aumenta a vacinação da população. | `MISLEADING` | Troca resultado promissor por garantia de adesão real. |
| ref2-cal-0040 | Uma campanha local perdeu cobertura vacinal porque usou uma imagem assustadora em um cartaz. | `INSUFFICIENT_EVIDENCE` | Não há desenho causal nem dados da campanha fictícia. |

## 11 — Mecanismos de adjuvantes

Fonte: [Signal Transduction and Targeted Therapy — Vaccine adjuvants: mechanisms and platforms](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10356842/fullTextXML).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0041 | Adjuvantes podem atuar como imunoestimulantes ou sistemas de entrega para ampliar a resposta adaptativa ao antígeno vacinal. | `SUPPORTED` | Resume as categorias funcionais da revisão. |
| ref2-cal-0042 | Adjuvantes impedem a apresentação de antígenos e enfraquecem deliberadamente a resposta imune da vacina. | `REFUTED` | Contradiz os mecanismos descritos. |
| ref2-cal-0043 | Como adjuvantes podem intensificar a resposta imune, aumentar sua quantidade sempre torna qualquer vacina mais eficaz e igualmente segura. | `MISLEADING` | Inventa relação universal de dose, eficácia e segurança. |
| ref2-cal-0044 | A reação local de uma pessoa foi causada especificamente pelo adjuvante da vacina que ela recebeu. | `INSUFFICIENT_EVIDENCE` | Faltam produto, composição e avaliação clínica. |

## 12 — Queda de proteção das vacinas acelulares contra coqueluche

Fonte: [PLoS ONE — Acellular pertussis vaccines effectiveness over time](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6005504/fullTextXML).

| ID | Alegação | Proposta | Critério a conferir |
|---|---|---|---|
| ref2-cal-0045 | A proteção das vacinas acelulares contra coqueluche é inicialmente alta, mas diminui com o passar do tempo. | `SUPPORTED` | Reproduz a interpretação principal da revisão. |
| ref2-cal-0046 | A efetividade da vacina acelular contra coqueluche permanece inalterada por muitos anos após a vacinação. | `REFUTED` | Contradiz o declínio estimado. |
| ref2-cal-0047 | Como a proteção contra coqueluche diminui com o tempo, a dose de reforço na adolescência não oferece proteção adicional alguma. | `MISLEADING` | Usa o waning para negar a proteção adicional do reforço. |
| ref2-cal-0048 | A coqueluche de um adolescente vacinado ocorreu porque a dose de reforço aplicada nele não produziu imunidade. | `INSUFFICIENT_EVIDENCE` | Faltam confirmação diagnóstica e histórico individual. |

## Declaração de decisão

- [ ] Examinei as 12 fontes e as 48 propostas.
- [ ] Registrei abaixo todas as correções necessárias, ou declarei não haver exceções.
- [ ] Entendo que esta aprovação será registrada como primeira revisão assistida.
- [ ] Entendo que os itens continuarão fora da pipeline até a incorporação auditável.

Decisão e exceções: **pendentes**.
