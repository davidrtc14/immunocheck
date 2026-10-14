# Revisão das paráfrases v5

Conferir apenas se cada paráfrase preserva o **mesmo fato-alvo** do original (sujeito,
população, números, negação, quantificadores, causalidade). O rótulo é herdado e não deve ser
reavaliado aqui. Marque `[x]` em `OK` ou anote a correção em `Ajuste`. Validação automática de
números/negação/quantificadores já aprovada (`tests/test_paraphrase_set.py`).

## ref4-0001 — INSUFFICIENT_EVIDENCE

- Original: Um menino de 3 anos ficou irritado por dois dias depois de receber três vacinas na mesma consulta, e a combinação foi forte demais para ele.
- Coloquial: gente, meu sobrinho de 3 anos tomou três vacinas na mesma consulta e ficou irritado dois dias, foi vacina demais junta pra ele
- Formal: Uma criança de 3 anos apresentou irritabilidade por dois dias após receber três vacinas em uma única consulta, o que indicaria que a combinação foi excessiva para ela.
- OK: [ ]  Ajuste:

## ref4-0002 — INSUFFICIENT_EVIDENCE

- Original: A Etiópia registrou zero casos de sarampo nos últimos cinco anos.
- Coloquial: vi que a Etiópia teve zero caso de sarampo nos últimos cinco anos
- Formal: Nos últimos cinco anos, a Etiópia não registrou nenhum caso de sarampo (zero casos).
- OK: [ ]  Ajuste:

## ref4-0003 — MISLEADING

- Original: A BCG é aplicada na rotina até 4 anos, 11 meses e 29 dias, inclusive em crianças de 6 anos com HIV que estejam assintomáticas e nunca tenham sido vacinadas.
- Coloquial: a BCG de rotina vai até 4 anos, 11 meses e 29 dias, e criança de 6 anos com HIV sem sintoma e que nunca tomou também pode tomar
- Formal: A BCG é administrada na rotina até 4 anos, 11 meses e 29 dias de idade, incluindo crianças de 6 anos vivendo com HIV, assintomáticas e nunca vacinadas.
- OK: [ ]  Ajuste:

## ref4-0004 — MISLEADING

- Original: Se o bebê perde a dose de hepatite B da maternidade, ainda é possível aplicá-la normalmente aos 3 meses de idade.
- Coloquial: se o bebê não tomou a hepatite B na maternidade, dá pra dar essa dose normal com 3 meses
- Formal: Caso a dose de hepatite B da maternidade não seja administrada, ela ainda pode ser aplicada normalmente aos 3 meses de idade.
- OK: [ ]  Ajuste:

## ref4-0005 — MISLEADING

- Original: Com cerca de 28 mil mortes evitadas em 2016, a vacina contra rotavírus já resolveu o problema da diarreia infantil e sua ampliação deixou de ser prioridade.
- Coloquial: a vacina do rotavírus evitou umas 28 mil mortes em 2016, então a diarreia infantil já tá resolvida e ampliar a vacina não é mais prioridade
- Formal: Tendo evitado cerca de 28 mil mortes em 2016, a vacina contra rotavírus teria resolvido o problema da diarreia infantil, de modo que sua ampliação deixou de ser prioritária.
- OK: [ ]  Ajuste:

## ref4-0006 — REFUTED

- Original: O SARS-CoV-2 foi o principal agente identificado entre os óbitos por Srag no período analisado.
- Coloquial: o principal vírus achado nas mortes por Srag no período foi o SARS-CoV-2
- Formal: No período analisado, o SARS-CoV-2 foi o agente mais identificado entre os óbitos por Srag.
- OK: [ ]  Ajuste:

## ref4-0007 — REFUTED

- Original: Na meta-análise etíope, estar vacinado contra o sarampo aumentou a chance de infecção durante os surtos.
- Coloquial: na meta-análise da Etiópia, quem era vacinado contra sarampo tinha mais chance de pegar a doença nos surtos
- Formal: Segundo a meta-análise etíope, a vacinação contra o sarampo esteve associada a maior chance de infecção durante os surtos.
- OK: [ ]  Ajuste:

## ref4-0008 — SUPPORTED

- Original: O DPNI definiu meta de 90% de cobertura para a vacinação contra a covid-19 tanto em gestantes quanto em pessoas com 60 anos ou mais.
- Coloquial: o DPNI botou meta de 90% de vacinação contra covid tanto pra gestante quanto pra quem tem 60 anos ou mais
- Formal: O DPNI estabeleceu a meta de 90% de cobertura vacinal contra a covid-19 para gestantes e para pessoas com 60 anos ou mais.
- OK: [ ]  Ajuste:

## ref4-0009 — SUPPORTED

- Original: Em adultos com doenças reumáticas autoimunes, os eventos adversos da vacinação foram em geral leves e comparáveis aos de pessoas saudáveis.
- Coloquial: adulto com doença reumática autoimune que se vacina tem efeito colateral leve no geral, parecido com o de gente saudável
- Formal: Em adultos com doenças reumáticas autoimunes, os eventos adversos pós-vacinação foram geralmente leves e comparáveis aos observados em pessoas saudáveis.
- OK: [ ]  Ajuste:

## ref4-0010 — SUPPORTED

- Original: O protocolo de vigilância de eventos adversos das vacinas covid-19 lista miocardite, pericardite e síndrome de Guillain-Barré entre os eventos adversos de especial interesse.
- Coloquial: o protocolo de vigilância das vacinas de covid coloca miocardite, pericardite e Guillain-Barré como eventos adversos de especial interesse
- Formal: Miocardite, pericardite e síndrome de Guillain-Barré constam entre os eventos adversos de especial interesse no protocolo de vigilância das vacinas covid-19.
- OK: [ ]  Ajuste:

## ref4-0011 — INSUFFICIENT_EVIDENCE

- Original: Uma jovem vacinada contra o HPV aos 12 anos desenvolveu verrugas genitais aos 20, o que mostra que a vacina não adianta.
- Coloquial: uma menina tomou a vacina do HPV com 12 anos e teve verruga genital aos 20, ou seja a vacina não adianta
- Formal: Uma jovem vacinada contra o HPV aos 12 anos apresentou verrugas genitais aos 20, fato que demonstraria que a vacina não adianta.
- OK: [ ]  Ajuste:

## ref4-0012 — INSUFFICIENT_EVIDENCE

- Original: A vacina contra o VSR aplicada em gestantes reduziu em 60% a mortalidade neonatal no Brasil.
- Coloquial: a vacina de VSR dada na gravidez diminuiu 60% a mortalidade dos recém-nascidos no Brasil
- Formal: No Brasil, a vacinação de gestantes contra o VSR reduziu em 60% a mortalidade neonatal.
- OK: [ ]  Ajuste:

## ref4-0013 — SUPPORTED

- Original: Crianças expostas ao HIV devem receber a BCG ao nascer ou o mais breve possível, até os 18 meses de idade.
- Coloquial: criança exposta ao HIV tem que tomar BCG ao nascer ou o quanto antes, até os 18 meses
- Formal: Crianças expostas ao HIV devem ser vacinadas com BCG ao nascimento ou o mais precocemente possível, até os 18 meses de idade.
- OK: [ ]  Ajuste:

## ref4-0014 — MISLEADING

- Original: A vacina contra a dengue da Takeda é indicada a adultos com base na eficácia demonstrada de 4 a 16 anos, sem restrição para gestantes.
- Coloquial: a vacina da dengue da Takeda tá indicada pra adulto por causa da eficácia mostrada de 4 a 16 anos, e grávida pode tomar sem restrição
- Formal: A vacina contra a dengue da Takeda é indicada para adultos com base na eficácia demonstrada na faixa de 4 a 16 anos, sem restrição para gestantes.
- OK: [ ]  Ajuste:

## ref4-0015 — SUPPORTED

- Original: Em novembro de 2024 o Brasil foi recertificado pela OPAS como país livre da circulação endêmica do vírus do sarampo.
- Coloquial: em novembro de 2024 a OPAS recertificou o Brasil como livre da circulação endêmica do sarampo
- Formal: O Brasil obteve, em novembro de 2024, a recertificação da OPAS como país livre da circulação endêmica do vírus do sarampo.
- OK: [ ]  Ajuste:

## ref4-0016 — MISLEADING

- Original: Mesmo durante uma doença febril aguda grave a vacina contra influenza pode ser aplicada, pois febre baixa não impede a vacinação.
- Coloquial: mesmo com doença febril aguda grave pode tomar a vacina da gripe, porque febre baixa não impede vacinar
- Formal: A vacina contra influenza pode ser administrada mesmo durante doença febril aguda grave, uma vez que febre baixa não impede a vacinação.
- OK: [ ]  Ajuste:

## ref4-0017 — SUPPORTED

- Original: Febre baixa ou moderada após uma dose anterior de vacina é uma falsa contraindicação e não impede a dose seguinte.
- Coloquial: se a pessoa teve febre baixa ou moderada depois de uma dose, isso é falsa contraindicação e não impede a próxima dose
- Formal: Febre baixa ou moderada após dose anterior de vacina constitui falsa contraindicação e não impede a administração da dose seguinte.
- OK: [ ]  Ajuste:

## ref4-0018 — SUPPORTED

- Original: A bula da vacina Comirnaty passou a incluir miocardite e pericardite na seção de advertências e precauções.
- Coloquial: a bula da Comirnaty agora tem miocardite e pericardite em advertências e precauções
- Formal: Miocardite e pericardite passaram a constar na seção de advertências e precauções da bula da vacina Comirnaty.
- OK: [ ]  Ajuste:

## ref4-0019 — INSUFFICIENT_EVIDENCE

- Original: A recertificação de 2024 exigiu que o Brasil mantivesse cobertura de tríplice viral acima de 98% por dez anos consecutivos.
- Coloquial: pra recertificar em 2024 o Brasil teve que manter a tríplice viral acima de 98% por dez anos seguidos
- Formal: A recertificação de 2024 teve como exigência a manutenção, pelo Brasil, de cobertura da tríplice viral acima de 98% durante dez anos consecutivos.
- OK: [ ]  Ajuste:

## ref4-0020 — SUPPORTED

- Original: Na meta-análise de surtos de sarampo na Etiópia, estar não vacinado esteve associado a maior chance de infecção (OR 5,96).
- Coloquial: na meta-análise dos surtos de sarampo na Etiópia, não ser vacinado tava ligado a mais chance de infecção (OR 5,96)
- Formal: Na meta-análise sobre surtos de sarampo na Etiópia, a condição de não vacinado associou-se a maior chance de infecção (OR 5,96).
- OK: [ ]  Ajuste:

## ref4-0021 — MISLEADING

- Original: A meta de 90% de cobertura da estratégia de influenza se aplica a todos os grupos prioritários, incluindo os atendidos apenas na estratégia especial.
- Coloquial: a meta de 90% da campanha da gripe vale pra todos os grupos prioritários, até os que só são atendidos na estratégia especial
- Formal: A meta de 90% de cobertura da estratégia de influenza abrange todos os grupos prioritários, inclusive aqueles atendidos apenas na estratégia especial.
- OK: [ ]  Ajuste:

## ref4-0022 — INSUFFICIENT_EVIDENCE

- Original: Pessoas com alergia a ovo têm maior risco de reação à vacina contra hepatite A.
- Coloquial: quem tem alergia a ovo tem mais risco de reação na vacina de hepatite A
- Formal: Pessoas alérgicas a ovo apresentam risco aumentado de reação à vacina contra hepatite A.
- OK: [ ]  Ajuste:

## ref4-0023 — REFUTED

- Original: A meta-análise concluiu que a coqueluche deixou de ser relevante em países de baixa e média renda graças à vacinação ampla.
- Coloquial: a meta-análise concluiu que a coqueluche deixou de ser relevante nos países de baixa e média renda por causa da vacinação ampla
- Formal: Segundo a conclusão da meta-análise, a coqueluche deixou de ser relevante em países de baixa e média renda em razão da ampla vacinação.
- OK: [ ]  Ajuste:

## ref4-0024 — INSUFFICIENT_EVIDENCE

- Original: Uma criança exposta ao HIV desenvolveu cicatriz grande da BCG, o que indica que a vacina lhe fez mal.
- Coloquial: uma criança exposta ao HIV ficou com cicatriz grande da BCG, sinal de que a vacina fez mal pra ela
- Formal: Uma criança exposta ao HIV desenvolveu cicatriz extensa da BCG, o que indicaria que a vacina lhe causou dano.
- OK: [ ]  Ajuste:

## ref4-0025 — SUPPORTED

- Original: O estudo estima que a vacina contra rotavírus evitou cerca de 28 mil mortes em menores de 5 anos em 2016.
- Coloquial: o estudo diz que a vacina do rotavírus evitou umas 28 mil mortes de crianças menores de 5 anos em 2016
- Formal: O estudo estima que, em 2016, a vacina contra rotavírus evitou aproximadamente 28 mil mortes de menores de 5 anos.
- OK: [ ]  Ajuste:

## ref4-0026 — INSUFFICIENT_EVIDENCE

- Original: A vacinação contra a covid-19 em idosos reduziu em 35% as internações por Srag em 2025.
- Coloquial: vacinar idoso contra covid diminuiu 35% das internações por Srag em 2025
- Formal: Em 2025, a vacinação contra a covid-19 em idosos reduziu em 35% as hospitalizações por Srag.
- OK: [ ]  Ajuste:

## ref4-0027 — SUPPORTED

- Original: Na América Latina e no Caribe, 66% a 84% dos sorotipos que causam doença pneumocócica invasiva em menores de 5 anos estão incluídos na VPC13.
- Coloquial: na América Latina e Caribe, de 66% a 84% dos sorotipos que dão doença pneumocócica invasiva em menores de 5 anos tão na VPC13
- Formal: Na América Latina e no Caribe, a VPC13 inclui de 66% a 84% dos sorotipos causadores de doença pneumocócica invasiva em menores de 5 anos.
- OK: [ ]  Ajuste:

## ref4-0028 — REFUTED

- Original: A vacina contra o HPV oferecida pelo SUS protege contra todos os tipos de HPV.
- Coloquial: a vacina de HPV do SUS protege contra todos os tipos de HPV
- Formal: A vacina contra o HPV disponibilizada pelo SUS confere proteção contra todos os tipos de HPV.
- OK: [ ]  Ajuste:

## ref4-0029 — REFUTED

- Original: A revisão concluiu que a PCV10 reduz a soroinfecção mais do que a PCV13 em todos os sorotipos da PCV7.
- Coloquial: a revisão concluiu que a PCV10 reduz soroinfecção mais que a PCV13 em todos os sorotipos da PCV7
- Formal: De acordo com a revisão, a PCV10 reduz a soroinfecção em maior grau que a PCV13 em todos os sorotipos da PCV7.
- OK: [ ]  Ajuste:

## ref4-0030 — REFUTED

- Original: As bulas das vacinas contra a Covid-19 nunca foram alteradas depois do registro ou da autorização de uso.
- Coloquial: as bulas das vacinas de covid nunca foram mudadas depois do registro ou da autorização de uso
- Formal: As bulas das vacinas contra a Covid-19 jamais foram alteradas após o registro ou a autorização de uso.
- OK: [ ]  Ajuste:

## ref4-0031 — REFUTED

- Original: A estratégia de vacinação nas fronteiras é destinada exclusivamente a cidadãos brasileiros, e estrangeiros são excluídos.
- Coloquial: a vacinação nas fronteiras é só pra brasileiro, estrangeiro fica de fora
- Formal: A estratégia de vacinação nas fronteiras destina-se exclusivamente a cidadãos brasileiros, com exclusão de estrangeiros.
- OK: [ ]  Ajuste:

## ref4-0032 — REFUTED

- Original: Receber várias vacinas no mesmo dia sobrecarrega o sistema imunológico e aumenta os eventos adversos em comparação com aplicá-las separadamente.
- Coloquial: tomar várias vacinas no mesmo dia sobrecarrega a imunidade e dá mais efeito colateral do que tomar separado
- Formal: A administração de várias vacinas no mesmo dia sobrecarrega o sistema imunológico e eleva os eventos adversos em comparação com a aplicação em separado.
- OK: [ ]  Ajuste:

## ref4-0033 — REFUTED

- Original: O protocolo de vigilância das vacinas covid-19 não prevê monitorar eventos cardíacos nem neurológicos após a vacinação.
- Coloquial: o protocolo de vigilância das vacinas de covid não prevê monitorar evento cardíaco nem neurológico depois da vacina
- Formal: O protocolo de vigilância das vacinas covid-19 não contempla o monitoramento de eventos cardíacos ou neurológicos pós-vacinação.
- OK: [ ]  Ajuste:

## ref4-0034 — MISLEADING

- Original: A vacina garante proteção de 90,7% a toda criança de 5 a 11 anos vacinada, segundo a eficácia estimada no estudo avaliado pela Anvisa.
- Coloquial: a vacina garante 90,7% de proteção pra toda criança de 5 a 11 anos que tomar, segundo a eficácia do estudo que a Anvisa avaliou
- Formal: Segundo a eficácia estimada no estudo avaliado pela Anvisa, a vacina assegura proteção de 90,7% a toda criança vacinada de 5 a 11 anos.
- OK: [ ]  Ajuste:

## ref4-0035 — MISLEADING

- Original: As alterações de bula das vacinas contra a Covid-19 feitas pela Anvisa mostram que as vacinas são mais perigosas que a doença e deveriam ser retiradas.
- Coloquial: as mudanças nas bulas das vacinas de covid feitas pela Anvisa mostram que a vacina é mais perigosa que a doença e devia ser retirada
- Formal: As alterações de bula das vacinas contra a Covid-19 realizadas pela Anvisa demonstrariam que as vacinas são mais perigosas que a doença e deveriam ser retiradas do mercado.
- OK: [ ]  Ajuste:

## ref4-0036 — INSUFFICIENT_EVIDENCE

- Original: Um menino de 6 anos vacinado teve covid duas semanas depois, e a vacina não funciona em crianças.
- Coloquial: um menino de 6 anos vacinado pegou covid duas semanas depois, a vacina não funciona em criança
- Formal: Uma criança de 6 anos vacinada contraiu covid duas semanas depois, o que mostraria que a vacina não funciona em crianças.
- OK: [ ]  Ajuste:

## ref4-0037 — SUPPORTED

- Original: A anafilaxia ao ovo, mesmo grave, não contraindica a vacina tríplice viral.
- Coloquial: anafilaxia ao ovo, mesmo grave, não contraindica a tríplice viral
- Formal: Mesmo a anafilaxia grave ao ovo não constitui contraindicação à vacina tríplice viral.
- OK: [ ]  Ajuste:

## ref4-0038 — MISLEADING

- Original: Com taxa de ataque de 34,51 por 10.000 habitantes nos surtos etíopes, o sarampo é raro e a vacinação é dispensável.
- Coloquial: nos surtos da Etiópia a taxa de ataque foi 34,51 por 10.000 habitantes, então sarampo é raro e vacinar é dispensável
- Formal: Considerando a taxa de ataque de 34,51 por 10.000 habitantes nos surtos etíopes, o sarampo seria raro e a vacinação, dispensável.
- OK: [ ]  Ajuste:

## ref4-0039 — REFUTED

- Original: O DPNI definiu meta de cobertura de apenas 50% para idosos na vacinação contra a covid-19.
- Coloquial: o DPNI botou meta de só 50% de cobertura de covid pros idosos
- Formal: O DPNI fixou meta de cobertura de apenas 50% para idosos na vacinação contra a covid-19.
- OK: [ ]  Ajuste:

## ref4-0040 — MISLEADING

- Original: O Brasil foi recertificado como livre do sarampo endêmico em 2024 e, por isso, não corre mais risco de reintrodução do vírus.
- Coloquial: o Brasil foi recertificado livre do sarampo endêmico em 2024, então não tem mais risco do vírus voltar
- Formal: Tendo sido recertificado como livre do sarampo endêmico em 2024, o Brasil não corre mais risco de reintrodução do vírus.
- OK: [ ]  Ajuste:

## ref4-0041 — INSUFFICIENT_EVIDENCE

- Original: Um homem vacinado durante a ação de fronteira em Foz do Iguaçu teve febre, o que mostra que a estratégia é perigosa.
- Coloquial: um homem vacinado na ação de fronteira em Foz do Iguaçu teve febre, isso mostra que a estratégia é perigosa
- Formal: Um homem vacinado durante a ação de fronteira em Foz do Iguaçu apresentou febre, o que demonstraria que a estratégia é perigosa.
- OK: [ ]  Ajuste:

## ref4-0042 — INSUFFICIENT_EVIDENCE

- Original: A vacina pneumocócica conjugada reduziu em 80% a mortalidade por pneumonia em crianças indígenas da Bolívia.
- Coloquial: a vacina pneumocócica conjugada diminuiu 80% a mortalidade por pneumonia em criança indígena da Bolívia
- Formal: Em crianças indígenas da Bolívia, a vacina pneumocócica conjugada reduziu em 80% a mortalidade por pneumonia.
- OK: [ ]  Ajuste:

## ref4-0043 — MISLEADING

- Original: Está provado que vacinar pacientes com doenças reumáticas autoimunes não traz nenhum risco de piora, pois os estudos não observaram aumento da atividade da doença.
- Coloquial: tá provado que vacinar paciente com doença reumática autoimune não tem nenhum risco de piorar, porque os estudos não viram aumento da atividade da doença
- Formal: Está comprovado que a vacinação de pacientes com doenças reumáticas autoimunes não acarreta nenhum risco de piora, visto que os estudos não observaram aumento da atividade da doença.
- OK: [ ]  Ajuste:

## ref4-0044 — SUPPORTED

- Original: A estratégia de vacinação nas fronteiras contempla pessoas de todas as idades, residentes ou estrangeiras, em municípios da faixa de fronteira que não tenham sido vacinadas ou não tenham comprovação vacinal.
- Coloquial: a vacinação nas fronteiras atende gente de todas as idades, morador ou estrangeiro, nos municípios da faixa de fronteira que não foi vacinado ou não tem comprovante
- Formal: A estratégia de vacinação nas fronteiras abrange pessoas de todas as idades, residentes ou estrangeiras, em municípios da faixa de fronteira, que não tenham sido vacinadas ou não possuam comprovação vacinal.
- OK: [ ]  Ajuste:

## ref4-0045 — SUPPORTED

- Original: Não há evidência científica de que o sistema imune se sobrecarregue quando uma pessoa recebe várias vacinas na mesma ocasião.
- Coloquial: não existe evidência científica de que a imunidade fica sobrecarregada quando a pessoa toma várias vacinas juntas
- Formal: Não há evidência científica de sobrecarga do sistema imune quando uma pessoa recebe múltiplas vacinas na mesma ocasião.
- OK: [ ]  Ajuste:

## ref4-0046 — REFUTED

- Original: A vacinação em pacientes com doenças reumáticas autoimunes aumentou claramente a atividade da doença de base.
- Coloquial: vacinar paciente com doença reumática autoimune aumentou claramente a atividade da doença
- Formal: A vacinação de pacientes com doenças reumáticas autoimunes aumentou de forma clara a atividade da doença de base.
- OK: [ ]  Ajuste:

## ref4-0047 — MISLEADING

- Original: A PCV13 mostrou menor risco de soroinfecção que a PCV10 em vários sorotipos, o que vale para todos os sorotipos comparados.
- Coloquial: a PCV13 teve menos risco de soroinfecção que a PCV10 em vários sorotipos, então vale pra todos os sorotipos comparados
- Formal: A PCV13 apresentou menor risco de soroinfecção que a PCV10 em vários sorotipos, resultado que se estenderia a todos os sorotipos comparados.
- OK: [ ]  Ajuste:

## ref4-0048 — INSUFFICIENT_EVIDENCE

- Original: Bebês que recebem a dose de hepatite B nas primeiras 12 horas têm 40% menos mortalidade neonatal por qualquer causa.
- Coloquial: bebê que toma a hepatite B nas primeiras 12 horas tem 40% menos mortalidade neonatal por qualquer causa
- Formal: Recém-nascidos vacinados contra hepatite B nas primeiras 12 horas apresentam mortalidade neonatal por qualquer causa 40% menor.
- OK: [ ]  Ajuste:

## ref4-0049 — SUPPORTED

- Original: A meta da estratégia contra a influenza em 2026 é vacinar pelo menos 90% de cada grupo prioritário de rotina: crianças, gestantes e idosos com 60 anos ou mais.
- Coloquial: a meta da campanha da gripe em 2026 é vacinar pelo menos 90% de cada grupo prioritário de rotina: criança, gestante e idoso de 60 anos ou mais
- Formal: A estratégia contra a influenza de 2026 tem como meta vacinar no mínimo 90% de cada grupo prioritário de rotina: crianças, gestantes e idosos com 60 anos ou mais.
- OK: [ ]  Ajuste:

## ref4-0050 — REFUTED

- Original: Todas as vacinas conferem memória imunológica completa em uma única dose, e as doses adicionais não têm função biológica.
- Coloquial: todas as vacinas dão memória imunológica completa com uma dose só, e as doses extras não servem pra nada
- Formal: Todas as vacinas conferem memória imunológica completa com dose única, de modo que as doses adicionais não possuem função biológica.
- OK: [ ]  Ajuste:

## ref4-0051 — INSUFFICIENT_EVIDENCE

- Original: A OMS exigiu que a fase III dos ensaios de vacinas durasse no mínimo seis meses.
- Coloquial: a OMS exigiu que a fase III dos testes de vacina durasse no mínimo seis meses
- Formal: A OMS estabeleceu a exigência de que a fase III dos ensaios de vacinas tivesse duração mínima de seis meses.
- OK: [ ]  Ajuste:

## ref4-0052 — SUPPORTED

- Original: No estudo com crianças de 5 a 11 anos avaliado pela Anvisa, a estimativa pontual de eficácia contra covid-19 sintomática foi de 90,7% em relação ao placebo.
- Coloquial: no estudo com crianças de 5 a 11 anos que a Anvisa avaliou, a eficácia estimada contra covid sintomática foi 90,7% em relação ao placebo
- Formal: No estudo em crianças de 5 a 11 anos avaliado pela Anvisa, a estimativa pontual de eficácia contra covid-19 sintomática foi de 90,7% em comparação ao placebo.
- OK: [ ]  Ajuste:

## ref4-0053 — SUPPORTED

- Original: Na análise final do estudo MATISSE, a prematuridade foi mais frequente em gestantes vacinadas contra o VSR entre 28 e 32 semanas (6,8%) do que no grupo placebo (4,8%).
- Coloquial: na análise final do MATISSE, teve mais prematuro nas gestantes vacinadas contra VSR entre 28 e 32 semanas (6,8%) do que no placebo (4,8%)
- Formal: Na análise final do estudo MATISSE, a prematuridade foi mais frequente entre gestantes vacinadas contra o VSR entre 28 e 32 semanas (6,8%) do que no grupo placebo (4,8%).
- OK: [ ]  Ajuste:

## ref4-0054 — INSUFFICIENT_EVIDENCE

- Original: A Anvisa publicou comunicado de risco sobre lotes contaminados de vacinas contra a Covid-19.
- Coloquial: a Anvisa soltou comunicado de risco sobre lote contaminado de vacina de covid
- Formal: A Anvisa emitiu comunicado de risco referente a lotes contaminados de vacinas contra a Covid-19.
- OK: [ ]  Ajuste:

## ref4-0055 — REFUTED

- Original: O Brasil nunca recebeu da OPAS a certificação de eliminação da circulação endêmica do sarampo.
- Coloquial: o Brasil nunca recebeu da OPAS a certificação de eliminação do sarampo endêmico
- Formal: O Brasil jamais recebeu da OPAS a certificação de eliminação da circulação endêmica do sarampo.
- OK: [ ]  Ajuste:

## ref4-0056 — INSUFFICIENT_EVIDENCE

- Original: A coqueluche mata mais prematuros extremos do que recém-nascidos a termo no Nordeste do Brasil.
- Coloquial: no Nordeste a coqueluche mata mais prematuro extremo do que bebê que nasceu no tempo certo
- Formal: No Nordeste do Brasil, a coqueluche causa mais óbitos entre prematuros extremos do que entre recém-nascidos a termo.
- OK: [ ]  Ajuste:

## ref4-0057 — MISLEADING

- Original: A estratégia nas fronteiras oferta as vacinas do Calendário Nacional brasileiro, e os países vizinhos aplicam essas mesmas vacinas em suas ações.
- Coloquial: a estratégia nas fronteiras oferece as vacinas do Calendário Nacional brasileiro, e os países vizinhos aplicam essas mesmas vacinas nas ações deles
- Formal: A estratégia nas fronteiras oferta as vacinas do Calendário Nacional brasileiro, as quais também são aplicadas pelos países vizinhos em suas ações.
- OK: [ ]  Ajuste:

## ref4-0058 — REFUTED

- Original: Depois da introdução das vacinas pneumocócicas conjugadas na região, os sorotipos vacinais aumentaram na doença invasiva.
- Coloquial: depois que entraram as vacinas pneumocócicas conjugadas na região, os sorotipos vacinais aumentaram na doença invasiva
- Formal: Após a introdução das vacinas pneumocócicas conjugadas na região, houve aumento dos sorotipos vacinais na doença invasiva.
- OK: [ ]  Ajuste:

## ref4-0059 — MISLEADING

- Original: Depois da introdução das vacinas conjugadas os sorotipos vacinais diminuíram na América Latina, e a doença pneumocócica invasiva foi eliminada na região.
- Coloquial: depois das vacinas conjugadas os sorotipos vacinais caíram na América Latina, e a doença pneumocócica invasiva foi eliminada da região
- Formal: Com a introdução das vacinas conjugadas, os sorotipos vacinais diminuíram na América Latina e a doença pneumocócica invasiva foi eliminada da região.
- OK: [ ]  Ajuste:

## ref4-0060 — REFUTED

- Original: Uma criança que teve febre moderada depois da primeira dose de uma vacina deve ser impedida de receber as doses seguintes.
- Coloquial: criança que teve febre moderada depois da primeira dose tem que ser impedida de tomar as próximas
- Formal: Uma criança que apresentou febre moderada após a primeira dose de uma vacina deve ser impedida de receber as doses subsequentes.
- OK: [ ]  Ajuste:

## ref4-0061 — INSUFFICIENT_EVIDENCE

- Original: Uma lactente teve diarreia na semana seguinte à vacina de rotavírus, e a vacina não funciona.
- Coloquial: uma bebê teve diarreia na semana depois da vacina de rotavírus, e a vacina não funciona
- Formal: Uma lactente apresentou diarreia na semana seguinte à vacinação contra rotavírus, o que mostraria que a vacina não funciona.
- OK: [ ]  Ajuste:

## ref4-0062 — SUPPORTED

- Original: Em países de baixa e média renda, a mortalidade por coqueluche foi estimada em 0,8% e a letalidade em 6,5%, com a maioria das mortes em lactentes menores de 6 meses.
- Coloquial: nos países de baixa e média renda, a mortalidade da coqueluche foi estimada em 0,8% e a letalidade em 6,5%, e a maioria das mortes foi em bebê menor de 6 meses
- Formal: Em países de baixa e média renda, estimou-se mortalidade por coqueluche de 0,8% e letalidade de 6,5%, concentrando-se a maioria dos óbitos em lactentes menores de 6 meses.
- OK: [ ]  Ajuste:

## ref4-0063 — MISLEADING

- Original: Uma vacina aprovada foi testada somente em 20 a 50 pessoas, número usado na fase I para avaliar a segurança.
- Coloquial: uma vacina aprovada foi testada só em 20 a 50 pessoas, que é o número da fase I pra ver segurança
- Formal: Uma vacina aprovada teria sido testada somente em 20 a 50 pessoas, número empregado na fase I para avaliação de segurança.
- OK: [ ]  Ajuste:

## ref4-0064 — MISLEADING

- Original: A letalidade da coqueluche é de 6,5%: de cada cem crianças que contraem a doença em qualquer país do mundo, mais de seis morrem.
- Coloquial: a letalidade da coqueluche é 6,5%: de cada cem crianças que pegam a doença em qualquer país do mundo, mais de seis morrem
- Formal: A letalidade da coqueluche é de 6,5%, ou seja, em qualquer país do mundo, mais de seis em cada cem crianças que contraem a doença morrem.
- OK: [ ]  Ajuste:

## ref4-0065 — INSUFFICIENT_EVIDENCE

- Original: A OMS revisou em 2023 os eventos adversos de especial interesse das vacinas covid-19 e reduziu a lista de eventos monitorados.
- Coloquial: a OMS revisou em 2023 os eventos adversos de especial interesse das vacinas de covid e diminuiu a lista do que é monitorado
- Formal: Em 2023, a OMS revisou os eventos adversos de especial interesse das vacinas covid-19 e reduziu a lista de eventos monitorados.
- OK: [ ]  Ajuste:

## ref4-0066 — INSUFFICIENT_EVIDENCE

- Original: O Ministério da Saúde considera falsa contraindicação o uso de corticoide inalatório por crianças asmáticas.
- Coloquial: o Ministério da Saúde considera falsa contraindicação criança asmática usar corticoide inalatório
- Formal: Para o Ministério da Saúde, o uso de corticoide inalatório por crianças asmáticas constitui falsa contraindicação.
- OK: [ ]  Ajuste:

## ref4-0067 — INSUFFICIENT_EVIDENCE

- Original: Em comparação com a PCV13, a PCV20 mostrou menor risco de soroinfecção em todos os sorotipos compartilhados.
- Coloquial: comparada com a PCV13, a PCV20 teve menos risco de soroinfecção em todos os sorotipos em comum
- Formal: Em relação à PCV13, a PCV20 apresentou menor risco de soroinfecção em todos os sorotipos compartilhados.
- OK: [ ]  Ajuste:

## ref4-0068 — REFUTED

- Original: Vacinas de vírus vivos atenuados podem ser aplicadas rotineiramente em gestantes, pois o vírus vacinal não tem como alcançar o feto.
- Coloquial: vacina de vírus vivo atenuado pode ser dada de rotina pra grávida, porque o vírus da vacina não tem como chegar no feto
- Formal: Vacinas de vírus vivos atenuados podem ser administradas rotineiramente a gestantes, uma vez que o vírus vacinal não tem como alcançar o feto.
- OK: [ ]  Ajuste:

## ref4-0069 — REFUTED

- Original: Quem já teve reação alérgica ao ovo está proibido de receber a vacina tríplice viral.
- Coloquial: quem já teve reação alérgica a ovo é proibido de tomar a tríplice viral
- Formal: Pessoas com histórico de reação alérgica ao ovo estão proibidas de receber a vacina tríplice viral.
- OK: [ ]  Ajuste:

## ref4-0070 — INSUFFICIENT_EVIDENCE

- Original: Uma gestante recebeu vacina viva sem saber e o bebê nasceu com malformação, o que prova que a vacina foi a causa.
- Coloquial: uma grávida tomou vacina viva sem saber e o bebê nasceu com malformação, prova que foi a vacina
- Formal: Uma gestante recebeu uma vacina viva sem saber e o bebê nasceu com malformação, o que provaria que a vacina foi a causa.
- OK: [ ]  Ajuste:

## ref4-0071 — MISLEADING

- Original: A maioria das infecções por HPV se resolve sozinha em cerca de 24 meses; vacinar-se contra o HPV é desnecessário.
- Coloquial: a maioria das infecções por HPV some sozinha em uns 24 meses, então tomar vacina de HPV é desnecessário
- Formal: A maioria das infecções por HPV se resolve espontaneamente em cerca de 24 meses; por isso, a vacinação contra o HPV seria desnecessária.
- OK: [ ]  Ajuste:

## ref4-0072 — REFUTED

- Original: O estudo MATISSE não encontrou nenhuma diferença na prematuridade entre gestantes vacinadas contra o VSR e o grupo placebo.
- Coloquial: o estudo MATISSE não achou nenhuma diferença de prematuridade entre grávida vacinada contra VSR e o placebo
- Formal: O estudo MATISSE não identificou nenhuma diferença na prematuridade entre gestantes vacinadas contra o VSR e o grupo placebo.
- OK: [ ]  Ajuste:

## ref4-0073 — REFUTED

- Original: Antes de ser aprovada, uma vacina é testada apenas em animais de laboratório e em algumas dezenas de voluntários humanos.
- Coloquial: antes de aprovar, a vacina é testada só em bicho de laboratório e em umas poucas dezenas de voluntários
- Formal: Antes da aprovação, uma vacina é testada apenas em animais de laboratório e em algumas dezenas de voluntários humanos.
- OK: [ ]  Ajuste:

## ref4-0074 — SUPPORTED

- Original: Gestantes não devem receber vacinas de vírus vivos atenuados.
- Coloquial: grávida não deve tomar vacina de vírus vivo atenuado
- Formal: Vacinas de vírus vivos atenuados não devem ser administradas a gestantes.
- OK: [ ]  Ajuste:

## ref4-0075 — INSUFFICIENT_EVIDENCE

- Original: Uma idosa recebeu a mesma vacina três vezes e continuou doente, o que prova que doses repetidas não funcionam.
- Coloquial: uma senhora tomou a mesma vacina três vezes e continuou doente, prova que dose repetida não funciona
- Formal: Uma idosa recebeu a mesma vacina três vezes e permaneceu doente, o que provaria que doses repetidas não funcionam.
- OK: [ ]  Ajuste:

## ref4-0076 — REFUTED

- Original: A dose de hepatite B ao nascer pode ser aplicada em qualquer momento da infância, sem prazo máximo.
- Coloquial: a dose de hepatite B do nascimento pode ser dada em qualquer momento da infância, sem prazo máximo
- Formal: A dose de hepatite B ao nascer pode ser administrada em qualquer momento da infância, sem prazo máximo.
- OK: [ ]  Ajuste:

## ref4-0077 — INSUFFICIENT_EVIDENCE

- Original: Uma mulher com lúpus piorou duas semanas depois da vacina da gripe, e a vacina causou a crise.
- Coloquial: uma mulher com lúpus piorou duas semanas depois da vacina da gripe, foi a vacina que causou a crise
- Formal: Uma mulher com lúpus apresentou piora duas semanas após a vacina contra a gripe, e a vacina teria causado a crise.
- OK: [ ]  Ajuste:

## ref4-0078 — SUPPORTED

- Original: Entre os sorotipos da PCV7, o risco de soroinfecção foi menor com a PCV13 do que com a PCV10 para os sorotipos 4, 6B, 9V, 18C e 23F.
- Coloquial: nos sorotipos da PCV7, o risco de soroinfecção foi menor com PCV13 do que com PCV10 pros sorotipos 4, 6B, 9V, 18C e 23F
- Formal: Entre os sorotipos da PCV7, a PCV13 apresentou menor risco de soroinfecção que a PCV10 para os sorotipos 4, 6B, 9V, 18C e 23F.
- OK: [ ]  Ajuste:

## ref4-0079 — SUPPORTED

- Original: Algumas vacinas exigem várias doses porque isso ajuda a produzir anticorpos de longa duração e a formar células de memória.
- Coloquial: algumas vacinas precisam de várias doses porque isso ajuda a fazer anticorpo que dura bastante e célula de memória
- Formal: Algumas vacinas requerem múltiplas doses porque isso contribui para a produção de anticorpos de longa duração e para a formação de células de memória.
- OK: [ ]  Ajuste:

## ref4-0080 — MISLEADING

- Original: Para reduzir o número de picadas, o vacinador pode misturar na mesma seringa as vacinas que serão aplicadas na mesma visita.
- Coloquial: pra dar menos picada, o vacinador pode misturar na mesma seringa as vacinas da mesma visita
- Formal: Com o objetivo de reduzir o número de injeções, o vacinador pode misturar na mesma seringa as vacinas a serem aplicadas na mesma visita.
- OK: [ ]  Ajuste:

## ref4-0081 — REFUTED

- Original: Crianças expostas verticalmente ao HIV nunca podem receber a vacina BCG.
- Coloquial: criança exposta ao HIV na gestação nunca pode tomar BCG
- Formal: Crianças com exposição vertical ao HIV jamais podem receber a vacina BCG.
- OK: [ ]  Ajuste:

## ref4-0082 — INSUFFICIENT_EVIDENCE

- Original: Um idoso vacinado contra a gripe em abril teve influenza em junho, e a vacina não protege idosos.
- Coloquial: um idoso tomou a vacina da gripe em abril e pegou influenza em junho, a vacina não protege idoso
- Formal: Um idoso vacinado contra a gripe em abril contraiu influenza em junho, o que mostraria que a vacina não protege idosos.
- OK: [ ]  Ajuste:

## ref4-0083 — MISLEADING

- Original: Por serem capazes de proteger contra patógenos muito semelhantes, os anticorpos gerados por uma vacina valem contra qualquer outro vírus.
- Coloquial: como os anticorpos da vacina protegem contra patógeno muito parecido, eles valem contra qualquer outro vírus
- Formal: Uma vez que protegem contra patógenos muito semelhantes, os anticorpos gerados por uma vacina seriam eficazes contra qualquer outro vírus.
- OK: [ ]  Ajuste:

## ref4-0084 — MISLEADING

- Original: Pessoas com anafilaxia ao ovo podem tomar a vacina contra influenza em qualquer posto, sem nenhum cuidado adicional, porque alergia a ovo não impede essa vacina.
- Coloquial: quem tem anafilaxia a ovo pode tomar a vacina da gripe em qualquer posto, sem nenhum cuidado a mais, porque alergia a ovo não impede essa vacina
- Formal: Pessoas com anafilaxia ao ovo podem receber a vacina contra influenza em qualquer posto, sem nenhum cuidado adicional, porque a alergia a ovo não impede essa vacinação.
- OK: [ ]  Ajuste:

## ref4-0085 — SUPPORTED

- Original: Entre os casos de Srag com vírus identificado, o VSR foi o agente mais frequente (32,4%), enquanto a influenza A respondeu pela maior parcela dos óbitos (44,0%).
- Coloquial: nos casos de Srag com vírus identificado, o VSR foi o mais frequente (32,4%), mas a influenza A teve a maior parte das mortes (44,0%)
- Formal: Entre os casos de Srag com vírus identificado, o VSR foi o agente mais frequente (32,4%), ao passo que a influenza A respondeu pela maior parcela dos óbitos (44,0%).
- OK: [ ]  Ajuste:

## ref4-0086 — MISLEADING

- Original: Gestantes de qualquer idade, inclusive menores de 12 anos, podem usar qualquer uma das três vacinas covid-19 disponíveis.
- Coloquial: grávida de qualquer idade, até menor de 12 anos, pode usar qualquer uma das três vacinas de covid disponíveis
- Formal: Gestantes de qualquer idade, inclusive com menos de 12 anos, podem receber qualquer uma das três vacinas covid-19 disponíveis.
- OK: [ ]  Ajuste:

## ref4-0087 — INSUFFICIENT_EVIDENCE

- Original: O rinovírus causou mais óbitos por Srag do que a influenza A entre crianças menores de 2 anos.
- Coloquial: entre as crianças menores de 2 anos, o rinovírus matou mais por Srag do que a influenza A
- Formal: Entre crianças menores de 2 anos, o rinovírus causou mais óbitos por Srag do que a influenza A.
- OK: [ ]  Ajuste:

## ref4-0088 — REFUTED

- Original: O estudo apresentado à Anvisa não encontrou nenhuma proteção contra covid-19 sintomática em crianças de 5 a 11 anos.
- Coloquial: o estudo que foi pra Anvisa não achou nenhuma proteção contra covid sintomática em criança de 5 a 11 anos
- Formal: O estudo apresentado à Anvisa não identificou nenhuma proteção contra covid-19 sintomática em crianças de 5 a 11 anos.
- OK: [ ]  Ajuste:

## ref4-0089 — SUPPORTED

- Original: A primeira dose da vacina contra hepatite B deve ser aplicada logo após o nascimento, na sala de parto ou nas primeiras 12 horas, ainda na maternidade.
- Coloquial: a primeira dose da hepatite B tem que ser logo depois do nascimento, na sala de parto ou nas primeiras 12 horas, ainda na maternidade
- Formal: A primeira dose da vacina contra hepatite B deve ser administrada logo após o nascimento, na sala de parto ou nas primeiras 12 horas, ainda na maternidade.
- OK: [ ]  Ajuste:

## ref4-0090 — SUPPORTED

- Original: Crianças e adolescentes de 9 a 14 anos recebem dose única da vacina contra o HPV no SUS.
- Coloquial: no SUS, criança e adolescente de 9 a 14 anos toma dose única da vacina de HPV
- Formal: No SUS, crianças e adolescentes de 9 a 14 anos recebem dose única da vacina contra o HPV.
- OK: [ ]  Ajuste:

## ref4-0091 — REFUTED

- Original: A vacina contra rotavírus não evitou nenhuma morte infantil por diarreia em 2016.
- Coloquial: a vacina do rotavírus não evitou nenhuma morte de criança por diarreia em 2016
- Formal: Em 2016, a vacina contra rotavírus não evitou nenhuma morte infantil por diarreia.
- OK: [ ]  Ajuste:

## ref4-0092 — MISLEADING

- Original: O protocolo cita a exacerbação da doença pela vacina como evento potencial de interesse, o que prova que as vacinas covid-19 pioram a infecção subsequente.
- Coloquial: o protocolo cita a doença agravada pela vacina como evento potencial de interesse, prova que as vacinas de covid pioram a infecção depois
- Formal: O protocolo menciona a exacerbação da doença associada à vacina como evento potencial de interesse, o que provaria que as vacinas covid-19 agravam a infecção subsequente.
- OK: [ ]  Ajuste:

## ref4-0093 — REFUTED

- Original: No Calendário Nacional, a vacina influenza trivalente é indicada somente para pessoas com 60 anos ou mais.
- Coloquial: no Calendário Nacional, a vacina da gripe trivalente é só pra quem tem 60 anos ou mais
- Formal: No Calendário Nacional, a vacina influenza trivalente é indicada exclusivamente para pessoas com 60 anos ou mais.
- OK: [ ]  Ajuste:

## ref4-0094 — SUPPORTED

- Original: Os ensaios clínicos de vacinas ocorrem em três fases principais, e na fase III a vacina costuma ser aplicada a milhares de pessoas.
- Coloquial: os testes de vacina têm três fases principais, e na fase III a vacina costuma ser dada pra milhares de pessoas
- Formal: Os ensaios clínicos de vacinas compreendem três fases principais, e na fase III a vacina é geralmente administrada a milhares de pessoas.
- OK: [ ]  Ajuste:

## ref4-0095 — MISLEADING

- Original: A vacina contra o VSR reduziu em 70% o risco de infecção grave de vias aéreas inferiores e mantém essa proteção contra hospitalizações durante todo o primeiro ano.
- Coloquial: a vacina do VSR diminuiu 70% o risco de infecção grave das vias aéreas inferiores e mantém essa proteção contra internação o primeiro ano todo
- Formal: A vacina contra o VSR reduziu em 70% o risco de infecção grave do trato respiratório inferior e mantém essa proteção contra hospitalizações ao longo de todo o primeiro ano.
- OK: [ ]  Ajuste:

## ref4-0096 — MISLEADING

- Original: O VSR foi o vírus mais detectado entre os casos de Srag e também foi o que mais causou mortes.
- Coloquial: o VSR foi o vírus mais achado nos casos de Srag e também o que mais matou
- Formal: O VSR foi o vírus mais detectado entre os casos de Srag e também o principal responsável pelos óbitos.
- OK: [ ]  Ajuste:
