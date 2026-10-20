# Registro de decisões arquiteturais

| ID | Decisão | Estado | Justificativa |
|---|---|---|---|
| ADR-001 | Telegram na v1 | Aceita | Gratuito, simples, long polling local e sem exigência de infraestrutura pública. |
| ADR-002 | WhatsApp fora da v1 | Aceita | Maior complexidade operacional; reavaliar somente após o protótipo funcional. |
| ADR-003 | Texto, imagem textual e link na v1 | Aceita; link alterado pela ADR-053 | São requisitos do problema e viáveis localmente; vídeo tem custo desproporcional. |
| ADR-004 | Vídeo como trabalho futuro | Aceita | Transcrição, quadros, direitos e custo computacional formariam uma subpesquisa. |
| ADR-005 | Sem cache conversacional | Aceita | Simplifica privacidade, avaliação e comportamento do protótipo. |
| ADR-006 | Execução e demonstração locais | Aceita | Evita dependência de hospedagem gratuita sem garantia. |
| ADR-007 | Qwen3-8B local como única LLM principal | Aceita | Reprodutibilidade, gratuidade e nenhuma transferência de conteúdo para terceiros. |
| ADR-008 | Gemini excluído da produção | Aceita | O tier gratuito tem implicações de uso de dados e criaria diferença entre avaliação e entrega. |
| ADR-009 | BGE-M3 + BM25 + RRF | Substituída pela ADR-020 | A conclusão do piloto de 12 consultas não se sustentou nas 72 consultas de desenvolvimento. |
| ADR-010 | Reranker condicionado ao experimento | Cumprida pela ADR-021 | O experimento formal mostrou ganho de relevância e custo local mensurável. |
| ADR-011 | PostgreSQL + pgvector | Aceita | Solução gratuita e madura para metadados, texto, vetores e rastreabilidade. |
| ADR-012 | Sem pesos editoriais manuais na primeira versão | Aceita | Evita viés e hiperparâmetros frágeis em conjunto pequeno. |
| ADR-013 | Produção sem persistência de interações | Aceita | Minimização por desenho e menor risco sob LGPD. |
| ADR-014 | Verificação pós-geração obrigatória | Mantida, calibração interna encerrada | A variante factual v3 piorou macro-F1 e zerou `MISLEADING`; o auditor v2 foi restaurado provisoriamente, sem promoção ao teste. |
| ADR-015 | Python 3.12 | Aceita | Base estável e reproduzível para o ecossistema de ML e OCR. |
| ADR-016 | Quatro classes com abstenção | Aceita | Evita binarização indevida e diferencia falta de evidência de falsidade. |
| ADR-017 | Fontes parciais em abstenções | Aceita | Fontes consultadas podem ser exibidas como não conclusivas, sem fingir que sustentam um veredito. |
| ADR-018 | Avaliação por famílias e teste selado | Aceita | Validação cruzada usa somente desenvolvimento e mantém famílias inteiras em um fold; o teste congelado só participa da execução definitiva. |
| ADR-019 | Baseline lexical obrigatório | Aceita | TF-IDF com regressão logística mede atalhos de redação no benchmark sintético e contextualiza o ganho real da pipeline RAG. |
| ADR-020 | BGE-M3 sem reranker; híbrido como entrada do reranker | Aceita | No desenvolvimento, o denso teve nDCG@10 0,461 contra 0,365 do híbrido; a diferença pareada ainda inclui empate, portanto o híbrido não demonstrou vantagem sem reranking. |
| ADR-021 | Híbrido + reranker como candidato fim a fim, não padrão | Encerrada pela ADR-024 | O ganho isolado de retrieval não se converteu em classificação fim a fim. |
| ADR-022 | Não promover a pipeline fim a fim v1 | Aceita | Macro-F1 máximo de 0,446, zero recall de `MISLEADING` nas condições auditadas e omissões materiais do extrator exigem uma iteração de desenvolvimento antes do teste. |
| ADR-023 | Guarda de integridade para alegações curtas | Aceita | A v2 eliminou três recusas indevidas e melhorou o denso sem auditor em +0,197 macro-F1 pareado (IC 95% +0,114 a +0,281). |
| ADR-024 | Reranker fora do caminho padrão | Aceita | Na v2, híbrido + reranker + auditor teve macro-F1 0,464, recall zero de `MISLEADING` e mediana de 19,3 s; fica apenas para ablação. |
| ADR-025 | BGE-M3 + auditor v2 como candidata de segurança | Não promovida | Embora eleve o recall de abstenção para 0,625, tem macro-F1 0,528 e recall `MISLEADING` 0,158; permanece no código somente como opção conservadora provisória. |
| ADR-026 | Auditor restrito à fidelidade factual | Descartada | A v3 obteve macro-F1 0,405, recall zero de `MISLEADING` e delta pareado negativo contra a v2; falhou os gates pré-registrados. |
| ADR-027 | BGE-M3 + auditor v2 como configuração definitiva da v1 | Aceita com limitação crítica | No teste único obteve macro-F1 0,416, recall de abstenção 0,750 e recall zero de `MISLEADING`; congela a prova de conceito, mas impede recomendação de implantação pública. |
| ADR-028 | Congelar a v1 e abrir linha experimental v2 com dados novos | Aceita | Evita ajuste pós-teste: os 64 itens finais e os 96 itens já calibrados permanecem históricos; a v2 exige nova calibração e novo holdout. |
| ADR-029 | Separar suficiência, classificação e fidelidade na v2 | Não promovida | Na calibração nova, a candidata teve macro-F1 0,373, delta de −0,057 contra a v1, recall zero de `MISLEADING` e 38/48 abstenções; falhou cinco dos sete gates. |
| ADR-030 | Testar BGE-M3 denso top 20 como única mudança da v2.1 | Não promovida | Macro-F1 subiu apenas 0,003 sobre top 6, ficou 0,054 abaixo da baseline, manteve recall zero de `MISLEADING` e causou quatro falhas de IDs; só um dos sete gates passou. |
| ADR-031 | Selecionar seis trechos do top 20 por MMR | Descartada na triagem | Hit@6 caiu de 21/36 para 12/36, sem nenhum ganho de cobertura e com nove perdas; só o gate de latência passou, portanto não houve inferência fim a fim. |
| ADR-032 | Testar decisão direta em quatro classes, denso top 6 e sem auditor | Não promovida | Macro-F1 subiu para 0,472 e houve ganho em classes conclusivas, mas apenas 1/12 abstenções foi reconhecida; quatro dos sete gates falharam. |
| ADR-033 | Triar gate de suficiência v2 com aliases curtos e regra explícita para extrapolações | Descartada na triagem | O gate marcou os 48 itens como suficientes: recuperou todos os conclusivos, mas nenhuma das 12 abstenções; quatro dos seis gates passaram. |
| ADR-034 | Encerrar o refinamento v2 sem promover candidata nem criar holdout | Aceita | Nenhuma condição passou todos os gates; novos ajustes nos mesmos 48 itens elevariam o risco de sobreajuste e o holdout não pode ser usado para selecionar arquitetura. |
| ADR-035 | Triar decisão relacional v3 com guarda de evento específico e denso top 15 | Não promovida | Recuperou `MISLEADING` e abstenção, mas zerou o recall de `REFUTED`; quatro dos sete gates passaram. |
| ADR-036 | Rotear alegações simples, compostas e eventos específicos para decisões especializadas | Não promovida por citação | Macro-F1 0,725 e seis de sete gates passaram; citação relevante ficou em 0,444, abaixo do mínimo de 0,60. |
| ADR-037 | Selecionar citações em estágio dedicado sem alterar o veredito roteado | Não promovida | Melhorou citação exata somente de 0,444 para 0,472 e elevou P95 para 16,47 s; o gate de 0,60 continuou falhando. |
| ADR-038 | Expandir passagens nos documentos selecionados antes da citação final | Confirmada pela ADR-041 | Elevou citação exata para 0,722 na calibração e para 0,833 na confirmação, preservando a decisão roteada. |
| ADR-039 | Congelar a candidata hierárquica v3 antes de construir dados confirmatórios | Aceita | Preserva código, prompts, modelo, corpus, índices e hashes após 7/7 gates, impedindo ajuste orientado pelo conjunto confirmatório. |
| ADR-040 | Usar gabarito documental com curadoria do pesquisador apoiada por IA na confirmação v3 | Aceita com limitação declarada | Elimina a dependência inviável de revisor externo no prazo do TCC; rótulos e evidências são congelados antes da execução, sem alegar validação clínica, independência ou concordância entre anotadores. |
| ADR-041 | Promover a candidata v3 para integração controlada ao protótipo | Aceita | Na confirmação nova, obteve macro-F1 0,846, ganho de 0,364 sobre a v1, recall `MISLEADING` 0,625, citação exata 0,833, falha zero e P95 19,35 s; passou 8/8 gates, sem abrir o teste histórico da v1. |
| ADR-042 | Integrar a v3 por seleção explícita de versão, preservando a v1 | Aceita | A integração reutiliza sem alteração os componentes congelados, adiciona uma camada de orquestração testável e mantém `PIPELINE_VERSION=v1` como reversão; a v3 só se torna padrão do bot após regressão e ensaio multimodal local. |
| ADR-043 | Tratar Docker/PostgreSQL como diagnóstico opcional no preflight do bot local | Aceita | O caminho online lê o corpus/índice local e não persiste interações; Docker e PostgreSQL continuam validados para ingestão/reprodução, mas sua indisponibilidade não bloqueia Telegram, CLI ou demonstração. |
| ADR-044 | Correções de segurança e robustez da Fase B do plano v4, sem alterar a v3 congelada | Aceita | Guarda de orientação individual, orçamento de contexto, âncoras de seção, limite de taxa e correções menores são defeitos, não ganhos de acurácia; entram como camadas e módulos novos, sem editar componentes congelados. |
| ADR-045 | Conjunto lacrado v4 (96 itens, 24 famílias) e instrumentação de ablação por documento | Aceita | Substitui o confirmatório de 32 itens por calibração e holdout maiores, com gate lexical e critério de promoção de retrieval pré-registrados; curadoria sem revisor externo declarada como limitação. |
| ADR-046 | Ancoragem verificável (D1) e abstenção calibrada (D2) na linha v4 opt-in | D1 não adotada pelo critério pré-registrado; D2 adotada com ressalva | Em 48 itens, D1 elevou macro-F1 de 0,450 para 0,542 (IC +0,026 a +0,171) mas falhou o limite de falhas técnicas (1/48 > 2%, falha herdada da v3). D2 atingiu +0,0301 aninhado, IC incluindo zero. `MISLEADING` ficou com recall zero em ambas. |
| ADR-047 | Caminho dedicado a MISLEADING (D4/D5) e emenda que leva D1 ao holdout | D4/D5 não adotadas pelo critério pré-registrado; emenda D1 aceita | `v4_d4` elevou o recall de MISLEADING de 0 para 0,67 e o macro-F1 para 0,593 (IC inclui zero), mas derrubou REFUTED (0,83→0,33) e SUPPORTED (0,92→0,58); precisão das conclusões 0,559 < piso 0,568. |
| ADR-048 | Não promover a candidata v4 (v3 + D1); a v3 permanece padrão | Aceita | No holdout v4 (48 itens, execução única) a candidata obteve macro-F1 0,487 contra 0,577 da v3 (Δ −0,089; IC −0,194 a +0,008) e falhou 4 de 8 gates pré-registrados. |
| ADR-049 | Linha exploratória v5: decomposição da alegação, NLI por proposição e agregação determinística | Não promovida; opt-in | Diagnóstico dos 42 erros da v3 no conjunto v4 aponta interpretação/decisão, não retrieval (doc_hit@15 0,94); `MISLEADING` passa a ser decidido por regra sobre proposições. Resultado (96 itens): macro-F1 0,653 vs 0,490 da v3 (IC +0,037 a +0,275), mas recall de `SUPPORTED` caiu 0,12 (> 0,10); nenhuma variante passou a regra. Exploratório. |
| ADR-050 | Camada de compreensão da entrada multimodal medida por benchmark sintético com gabarito automático | Avaliada; não promovida (v2 opt-in) | A extração de imagem, link e texto nunca teve a qualidade medida; alegações v4 embutidas em capturas, páginas e mensagens geradas permitem medir CER e concordância do veredito com o texto limpo sem curadoria humana. Modelos reservados e execução única congelada; regra em `evaluation/extraction_v1/PROTOCOL.md`. Concordância 0,630 → 0,731 (IC por família +0,074 a +0,129), mas falhas técnicas de 2,19% acima do limite fixo de 2%: `EXTRACTION_VERSION=v1` continua padrão. |
| ADR-051 | Correção pontual da v5 e confirmação em teste externo de agências de checagem | Avaliada; não promovida (v3 padrão) | 150 alegações externas congeladas sem inferência; avaliação "sustentada × não sustentada" com abstenção como terceira saída (precisão das conclusões, erro grave, cobertura), porque o gabarito é de mundo real e a abstenção fora do corpus é o comportamento exigido. Promoção exige os seis critérios v5 no v4 e não inferioridade no externo; regra em `evaluation/refinement_v6/PROTOCOL.md`. No externo, a v5 corta o erro grave pela metade (5,8% → 2,9%), mas a cobertura cai 0,147, acima do limite de 0,10. |
| ADR-052 | Nova base de avaliação do veredito: conjunto contrastivo gerado do corpus e teste externo 2 | Aceita (C7 e teste externo 2 congelados) | O v4 (96 itens, 24 `MISLEADING`) e o teste externo 1 já foram revelados e não permitem iterar a arquitetura. Alegações geradas de chunks do corpus têm rótulo por construção, conferido por portões automáticos e por revisão humana de uma amostra; o gerador (`mistral-small3.2`, Apache 2.0) é de outra família para evitar autopreferência do juiz. Métrica principal: macro-F1 de 4 classes; regra em `evaluation/refinement_v7/PROTOCOL.md`. C7 congelado em 18/10: 400 itens (207 de teste), revisão assistida por LLM declarada; relatório em `evaluation/refinement_v7/C7_REPORT.md`. |
| ADR-053 | Link como protótipo experimental; texto e imagem formam o escopo avaliado | Aceita | Com um mês até a entrega e o veredito como objetivo principal, o pesquisador definiu o escopo estritamente necessário: texto e imagem predominantemente textual. O processamento de link continua no bot, com as mesmas proteções de segurança, mas como protótipo experimental, sem critério de aceite próprio nem nova rodada de avaliação; as avaliações do veredito usam a entrada em texto. |
| ADR-054 | Veredito v7: seleção progressiva de candidatas no desenvolvimento do C7 e execução única no teste | Encerrada; substituída pela ADR-055 | Candidatas: relação `PARTIAL` para `MISLEADING`, contexto ampliado para o juiz, `qwen3.6` só no juiz, robustez da decomposição e voto por consistência. Cada uma entra se melhorar o macro-F1 do desenvolvimento em ≥ 0,02 sem piorar o erro grave e com P95 ≤ 45 s. A promoção contra a v3 exige ganho de macro-F1 ≥ 0,05 (IC > 0) no teste do C7 e os gates X1–X4 da Fase 18 no teste externo 2. Regra no Adendo 1 de `evaluation/refinement_v7/PROTOCOL.md`. |
| ADR-055 | Cascata v3 → `v5_fixed` com verificação de `SUPPORTED` e via de promoção por segurança | Aceita | Nenhuma candidata da ADR-054 passou na seleção. Combinando vereditos já obtidos no desenvolvimento do C7, a cascata (a `v5_fixed` só confere os `SUPPORTED` da v3) reduziu o erro grave de 10,4% para 2,1% com macro-F1 de 0,728 contra 0,703. Por decisão do pesquisador, entra como condição C6 da execução única, com uma via de promoção alternativa: não inferioridade do macro-F1 (IC ≥ −0,05) e redução clara do erro grave (Δ ≤ −0,03, IC < 0), além de X1–X4. Regra no Adendo 3 de `evaluation/refinement_v7/PROTOCOL.md`. Na execução única (20/10), a C6 passou em S1–S4 e X1–X4: macro-F1 0,720 contra 0,677 (IC +0,011 a +0,080), erro grave de 11,5% para 0,6% no C7 e de 2,3% para 0,3% no teste externo 2; não passou no P1 (+0,043 < +0,05). Substitui a v3 como padrão do veredito (`evaluation/refinement_v7/RESULTS.md`). |
| ADR-056 | Corpus v2: lote 009 para lacunas do plano de cobertura, avaliado com a C6 sem mudar a pipeline | Encerrada sem adoção | A C6 só concluiu em 35,2% das alegações reais do teste externo 2, sobretudo por falta de evidência no corpus. O lote 009 cobre lacunas já previstas no plano de cobertura de setembro (DNA, óbitos, sobrecarga, composição e eficácia das vacinas contra covid-19), só com domínio público ou Creative Commons e sem texto de agência de checagem, escolhido sem consultar os itens dos conjuntos. Execução única da C6 com o corpus v2 no teste do C7 e no teste externo 2, com reuso declarado dos conjuntos; o corpus v2 vira padrão se passar em E1–E3, K1–K2 e O1. Regra em `evaluation/corpus_v2/PROTOCOL.md`. Na execução única (20/10), o corpus v2 reprovou no E1: cobertura +0,010 (IC −0,013 a +0,033) no teste externo 2, com precisão, erro grave e C7 dentro das margens; o corpus v1 continua padrão (`evaluation/corpus_v2/RESULTS.md`). |

## Histórico de alterações

- **01/09/2026 — ADR-009:** a hipótese híbrida foi promovida após a comparação piloto
  documentada em `RETRIEVAL_PHASE2.md`. O caminho online passou a carregar o índice BGE-M3 local,
  combinar top 60 lexical e denso por RRF 60 e entregar top 6 ao gerador. `RETRIEVAL_MODE=bm25`
  permanece somente para ablação e diagnóstico; o reranker continua desativado por padrão.
- **01/09/2026 — ADR-017:** o teste com alegação composta mostrou que descartar todas as referências
  após a auditoria reduzia a transparência. A resposta agora separa fontes conclusivas de fontes
  parciais consultadas; nenhuma interação passou a ser persistida.
- **16/09/2026 — ADR-018/019:** após o congelamento do benchmark, a Fase 6 passa a
  usar validação cruzada estratificada por `claim_family` exclusivamente no split de
  desenvolvimento. Um baseline lexical gratuito e local é obrigatório para revelar
  possível desempenho por moldes sintéticos. Métricas do teste não podem orientar
  alterações posteriores de prompt, modelo, retrieval, reranker ou limiares.
- **16/09/2026 — ADR-020/021:** o Experimento B substituiu a decisão provisória
  baseada no piloto. Em 72 consultas de desenvolvimento, o BGE-M3 isolado teve
  nDCG@10 0,461 e o híbrido RRF 0,365; o IC 95% do delta híbrido menos denso foi
  de -0,222 a +0,032. O reranking do conjunto híbrido alcançou nDCG@10 0,615,
  com delta de +0,153 sobre o denso (IC 95% +0,059 a +0,258), mas mediana de
  10,0 s somente para reranking em CPU. Por isso, o denso passa a ser a opção
  sem reranker e híbrido + reranker avança apenas como condição comparativa da
  avaliação fim a fim. Nenhum item do teste foi executado nessa alteração.
- **17/09/2026 — ADR-022:** a primeira execução fim a fim em 96 itens de
  desenvolvimento não aprovou configuração para teste. Híbrido + reranker +
  auditor teve a maior estimativa de macro-F1 (0,446), porém os intervalos dos
  deltas entre condições incluíram zero, a mediana foi 18,6 s e o recall de
  `MISLEADING` foi zero. O extrator removeu marcadores materiais em diversos
  encadeamentos de premissa e conclusão, alterando a alegação antes do RAG.
  A execução foi preservada como diagnóstico v1; o teste permaneceu selado.
- **17/09/2026 — ADR-023/024/025:** a v2 alterou somente o extrator e foi
  registrada antes da execução. O BGE-M3 sem auditor subiu de macro-F1 0,381
  para 0,577; o delta pareado por família foi +0,197 (IC 95% +0,114 a +0,281),
  com 15 previsões corrigidas e nenhuma correta piorada entre as mudanças. A
  condição densa auditada subiu para 0,528, mas o auditor alterou 39 resultados:
  12 melhoraram, 19 pioraram e oito continuaram errados. Híbrido + reranker +
  auditor ficou em 0,464, sem reconhecer `MISLEADING`, e teve mediana de 19,3 s.
  O reranker deixa de ser candidato online. O denso auditado permanece como
  candidato de segurança porque eleva recall de abstenção, mas o teste continua
  fechado até avaliar/calibrar o auditor sem novo uso do teste.
- **17/09/2026 — ADR-026:** a calibração v3 foi registrada no commit `4b9fc0d`
  antes das inferências e reutilizou extração, retrieval e geração da v2. Restringir
  o auditor à fidelidade factual reduziu macro-F1 de 0,528 para 0,405 e o recall de
  `MISLEADING` de 0,158 para zero; o IC 95% do delta pareado por família foi
  -0,212 a -0,024. A variante foi descartada e o prompt v2 restaurado. Conforme o
  protocolo, não haverá nova calibração orientada pelos mesmos 96 itens. O teste
  permanece fechado até validação externa ou decisão metodológica com o orientador.
- **18/09/2026 — ADR-027:** após confirmação do gate, os 64 itens de teste foram
  executados uma única vez no commit `52ab0bd`. A configuração teve macro-F1 0,416
  (IC 95% 0,308–0,507), recall de abstenção 0,750 e recall zero de `MISLEADING`.
  A mediana foi 9,43 s, o P95 12,42 s e não houve falha técnica. A versão fica
  congelada como protótipo acadêmico demonstrável; nenhum ajuste pós-teste é
  permitido e os resultados não sustentam serviço público de verificação em saúde.
- **22/09/2026 — ADR-028/029:** iniciou-se uma linha experimental independente para
  refinar acurácia sem reutilizar o teste final ou recalibrar nos 96 itens antigos.
  A auditoria diagnóstica desses 96 registros atribuiu 19 regressões e 12 recuperações
  ao auditor, encontrou taxa de erro de 84,2% em `MISLEADING` e seis riscos de
  integridade na extração. Esses números motivam, mas não calibram, a hipótese de
  separar suficiência da evidência, classificação e fidelidade. O protocolo exige
  pelo menos 48 itens novos de calibração e 32 de holdout, com famílias separadas.
  Nenhum registro do teste final foi carregado nessa auditoria.
- **22/09/2026 — implementação da ADR-029:** a candidata opt-in passou a ter gate de
  suficiência, classificador restrito a `SUPPORTED`, `REFUTED` e `MISLEADING`, e
  auditor limitado à fidelidade factual. O gate filtra as evidências entregues ao
  classificador e falha de forma segura diante de IDs inválidos. Os builders da v1
  permanecem inalterados. A decisão continua em validação porque não houve execução
  sobre o novo conjunto nem demonstração de ganho.
- **26/09/2026 — resultado da ADR-029:** após revisão primária, segunda anotação
  independente e adjudicação, as condições foram executadas nos 48 itens novos. A
  v1 obteve macro-F1 0,430 e a candidata separada sem auditor, 0,373. O delta
  pareado foi −0,057 (IC percentil por família de −0,157 a +0,053); a candidata
  teve recall zero de `MISLEADING`, recall 0,083 de `REFUTED` e 38 abstenções.
  Somente falha técnica e P95 passaram. A fase B com auditor factual não foi
  executada e a candidata não será promovida.
- **26/09/2026 — diagnóstico e ADR-030:** a atribuição exclusiva encontrou 14
  misses de retrieval, cinco riscos de extração, oito rejeições do gate apesar de
  evidência anotada e duas seleções inadequadas do gate. Aumentar a profundidade
  densa para 20 eleva a cobertura anotada de 58,3% para 72,2%; BM25 e híbrido RRF
  foram inferiores. A próxima iteração muda somente top-k, sem auditor ou ajuste de
  prompt, e permanece sujeita aos mesmos sete gates.
- **26/09/2026 — resultado da ADR-030:** ampliar o denso de top 6 para top 20
  elevou o recall de `REFUTED` de 0,083 para 0,417, mas não reconheceu corretamente
  nenhum `MISLEADING`, reduziu a taxa de citação relevante para 0,139 e provocou
  quatro saídas com IDs inválidos, rejeitadas pelo guardrail. O macro-F1 foi 0,376,
  apenas +0,003 sobre top 6 e −0,054 contra a baseline (IC percentil por família de
  −0,184 a +0,079). Só o gate de P95 passou; a candidata não foi promovida e o
  auditor factual não foi executado. O próximo estudo deve separar recuperação
  ampla da seleção compacta de contexto, em vez de enviar mais trechos diretamente
  à LLM.
- **26/09/2026 — triagem da ADR-031:** MMR com peso de relevância 0,70 selecionou
  seis trechos entre os 20 densos em menos de 0,5 ms no P95, mas reduziu Hit@6 de
  21/36 para 12/36 e a cobertura de `MISLEADING` de 6/12 para 3/12. Não ganhou
  nenhum hit e perdeu nove; um de cinco gates passou. A hipótese foi encerrada sem
  chamada de LLM, sem teste e sem holdout. O incidente pré-experimental de uma
  execução sem persistência foi registrado no próprio plano e limita a triagem a
  diagnóstico de desenvolvimento.
- **26/09/2026 — ADR-032:** no top 20, nove dos 12 casos `MISLEADING` continham ao
  menos um chunk anotado, mas o gate separado preservou zero; dez foram convertidos
  em abstenção e dois em `REFUTED`. Como o gerador direto denso sem auditor já teve
  o melhor ponto estimado no desenvolvimento histórico, a próxima iteração remove
  somente gate e auditor, reutiliza o top 6 da fase A e permanece submetida aos
  mesmos sete gates contra a baseline v1 auditada.
- **26/09/2026 — resultado da ADR-032:** a decisão direta alcançou macro-F1 0,472,
  recall 0,917 de `SUPPORTED`, 0,833 de `REFUTED` e 0,250 de `MISLEADING`, com P95
  de 10,12 s e nenhuma falha técnica. Entretanto, reconheceu somente 1/12 casos de
  evidência insuficiente e o delta de macro-F1 foi +0,042 (IC percentil por família
  de −0,090 a +0,190), abaixo do gate. Três de sete gates passaram. A candidata não
  foi promovida: o experimento delimita um extremo excessivamente conclusivo, em
  contraste com o gate separado excessivamente conservador.
- **26/09/2026 — resultado da ADR-033:** aliases `E1`–`E6` eliminaram falhas de ID
  e a regra explícita recuperou suficiência nos 36/36 casos conclusivos, inclusive
  12/12 `MISLEADING`. Porém o gate também declarou suficientes os 12/12 casos que
  exigiam abstenção e manteve a seleção de chunks anotados em 50%. Quatro de seis
  gates passaram; conforme o plano, classificador e auditor não foram executados.
  Novas alterações de prompt nos mesmos 48 itens ficam suspensas para evitar
  sobreajuste da calibração.
- **26/09/2026 — ADR-034:** a linha experimental foi encerrada sem promoção. Entre
  as condições fim a fim, a melhor estimativa foi a decisão direta top 6, com
  macro-F1 0,472, mas o delta de +0,042 ficou abaixo do gate, o intervalo por
  família incluiu regressão e 11/12 casos insuficientes receberam conclusão. MMR e
  o gate de suficiência v2 também falharam suas triagens. Como nenhuma candidata se
  tornou elegível, o holdout v2 não foi criado. A v1 segue congelada como protótipo
  acadêmico limitado, e o próximo marco é consolidar a entrega do TCC.
- **26/09/2026 — ADR-035:** a continuidade experimental abre uma v3 opt-in sem
  alterar o protótipo. A candidata usa aliases, explicita evento específico versus
  afirmação geral e preserva `MISLEADING` quando uma premissa sustentada leva a
  extrapolação material. Serão enviados 15 dos 20 resultados densos, profundidade
  fixada antes da execução e com cobertura anotada máxima de 25/36. A calibração
  reutilizada serve apenas para triagem; eventual promoção exige dados novos.
- **26/09/2026 — resultado da ADR-035:** a candidata relacional obteve macro-F1
  0,469, recall 0,833 de `MISLEADING` e precisão de abstenção 0,692, mas classificou
  incorretamente todos os 12 casos `REFUTED`. O delta sobre a baseline foi +0,039
  (IC por família de −0,081 a +0,175), a citação ficou em 0,556 e quatro de sete
  gates passaram. A condição não foi promovida. A complementaridade observada
  autoriza estudar roteamento por forma da alegação, ainda apenas como exploração.
- **26/09/2026 — ADR-036:** um roteador local baseado somente na forma textual da
  alegação escolherá entre decisão direta para proposição simples, decisão relacional
  para premissa-conclusão e abstenção para evento específico sem âncora. As saídas
  dos especialistas serão reutilizadas e a latência do roteador será contabilizada.
  Os sete gates permanecem inalterados e qualquer sucesso exige confirmação nova.
- **26/09/2026 — resultado da ADR-036:** a candidata roteada alcançou macro-F1
  0,725, delta +0,295 com IC por família de +0,165 a +0,469, recall 0,417 de
  `MISLEADING` e precisão de abstenção 0,750. Não houve regressão de recall, falha
  técnica ou estouro de latência. A citação relevante foi 0,444; por isso seis de
  sete gates passaram e a candidata não foi promovida. A próxima alteração fica
  restrita à seleção de citações, sem mudar os vereditos registrados.
- **26/09/2026 — ADR-037:** decisões conclusivas da candidata roteada receberão uma
  chamada dedicada que escolhe até três evidências do top 15. O estágio não pode
  mudar veredito ou explicação; falhas mantêm as referências anteriores, são
  contabilizadas e precisam respeitar os mesmos gates de erro e latência. O teto
  anotado é 25/36 e o mínimo operacional permanece 22/36.
- **26/09/2026 — resultado da ADR-037:** o seletor preservou todos os vereditos e
  não teve falhas, mas elevou citação exata apenas de 16/36 para 17/36 e o P95 para
  16,47 s. Uma auditoria diagnóstica encontrou o mesmo documento anotado em 30/36,
  sem converter essa proximidade em acerto. A hipótese seguinte passa a expandir
  candidatos dentro dos documentos selecionados, mantendo o limite de três fontes.
- **26/09/2026 — ADR-038:** a seleção hierárquica manterá cada semente, incluirá os
  quatro primeiros chunks do documento e vizinhos imediatos da mesma página, com
  deduplicação e máximo de 20 candidatos. O segundo seletor não poderá alterar a
  decisão e terá sua latência somada ao caminho anterior. O gate continua sendo ID
  exato; correspondência documental não será contada como sucesso.
- **26/09/2026 — resultado da ADR-038:** a expansão elevou citação exata de 17/36
  para 26/36 e preservou os 48 vereditos. A candidata manteve macro-F1 0,725, delta
  +0,295 (IC por família +0,165 a +0,469), recall `MISLEADING` 0,417, precisão de
  abstenção 0,750, falha zero e P95 18,72 s. Todos os sete gates passaram. A
  aprovação é somente de calibração exploratória; código e artefatos devem ser
  congelados antes de criar o conjunto confirmatório independente.
- **26/09/2026 — ADR-039:** a candidata do commit `38e8da9` foi congelada com
  hashes de código, corpus, índice e digest do Qwen3-8B. Ela permanece opt-in e fora
  do bot. A partir deste marco, qualquer alteração nesses componentes invalida sua
  elegibilidade para o conjunto confirmatório v3 e exige nova versão.
- **26/09/2026 — ADR-040:** a exigência operacional de revisão humana externa do
  conjunto confirmatório foi substituída por curadoria documental do pesquisador
  com apoio de IA. Os 32 itens mantêm famílias inéditas, equilíbrio entre classes,
  justificativa e IDs exatos de evidência definidos antes da execução. A opção reduz
  atraso e é proporcional ao protótipo de graduação, mas deverá constar como
  limitação: o conjunto não possui validação clínica independente nem medida de
  concordância entre anotadores.
- **26/09/2026 — ADR-041:** a execução única usou 32 itens e oito famílias novas,
  congelados antes da inferência. A v3 atingiu macro-F1 0,846 contra 0,482 da v1,
  com intervalo bootstrap do ganho de +0,192 a +0,540, recall `MISLEADING` 0,625,
  precisão de abstenção 1,000, citação exata 0,833, falha zero e P95 19,35 s. Os
  oito gates passaram. A configuração torna-se a referência para integração ao
  bot, mas a v1 em execução não é alterada por esta decisão e o resultado não
  sustenta implantação pública ou validação clínica.
- **26/09/2026 — ADR-042:** a integração da candidata confirmada será feita por uma
  nova camada de orquestração, sem editar os componentes e prompts congelados. O
  caminho terá seleção explícita `v1`/`v3`, falha fechada para IDs de fonte inválidos
  e referências sempre construídas a partir do corpus local. A v3 somente será
  adotada como padrão do bot e da CLI depois de testes das quatro classes, controles
  de privacidade e ensaio real de texto, imagem e link; a v1 continuará disponível
  como reversão e comparação histórica.
- **26/09/2026 — resultado da ADR-042:** a suíte geral aprovou 404 testes, e o
  ensaio controlado aprovou texto, imagem, link e rejeição de vídeo. A v3 passa a ser
  o padrão do bot e da CLI; a seleção explícita da v1 permanece disponível. As 32
  consultas confirmatórias reproduziram exatamente o ranking top 15 registrado. A
  divergência de serialização dos arquivos locais ignorados do índice está declarada
  em `docs/V3_INTEGRATION.md` e impede alegação de identidade byte a byte, mas não
  alterou os rankings observados nem motivou recalibração.
- **26/09/2026 — ADR-043:** o preflight passa a distinguir dependências do caminho
  online de infraestrutura auxiliar. Python, corpus/índice, modelo Ollama, Tesseract,
  artefatos e testes continuam obrigatórios. Docker, Compose e PostgreSQL são
  diagnósticos opcionais porque não participam da análise online nem armazenam
  interações; sua ausência deve ser reportada, mas não rebaixa a prontidão técnica
  do bot local. A integração PostgreSQL permanece coberta por teste dedicado quando
  `IMMUNOCHECK_TEST_DATABASE_URL` for fornecida.
- **13/10/2026 — ADR-044:** a Fase B do plano v4 adiciona (i) `advice_guard`, filtro
  determinístico que reaproveita `PERSONAL_MEDICAL_ADVICE` e converte saídas com
  orientação individual em `INSUFFICIENT_EVIDENCE` sem fontes; (ii) `ContextBudgetClient`,
  que estima tokens e trunca cada trecho de evidência (nunca o prompt de sistema) antes
  do Ollama, além de limitar a 6.000 caracteres o texto de link/OCR enviado ao extrator;
  (iii) campo opcional `section` (título + parágrafo) para HTML/XML; (iv) limite de taxa e
  allowlist opcional por chat, somente em memória; (v) correções do BM25, da CLI e do
  extrator XML. Nenhum prompt, modelo, top-k, corpus ou índice da v3 foi alterado e
  nenhum experimento foi executado; a reingestão do corpus para gravar `section` está
  pendente de decisão porque mudaria os hashes congelados.
- **13/10/2026 — ADR-045:** a Fase A do plano v4 adicionou métricas por documento, o harness
  de ablação com bootstrap pareado por família e o conjunto v4 (48 itens de calibração e 48 de
  holdout lacrado). O baseline lexical reprovou na primeira redação (macro-F1 0,558 > 0,45) e foi
  corrigido por reescrita de 47 alegações (0,328); ambas as execuções foram preservadas. A ablação
  na calibração não demonstrou ganho de reranker nem de híbrido sobre o denso. A segunda anotação
  (50%) está preparada e pendente de revisor humano; nenhuma inferência do sistema foi feita
  sobre o holdout.
- **13/10/2026 — ADR-046:** o plano D1/D2 foi registrado antes das inferências. Na calibração v4 a v3
  obteve macro-F1 0,450 (0,846 no confirmatório de 32 itens), com recall zero de `MISLEADING`.
  D1 (ancoragem) obteve 0,542; falhou apenas o critério de falhas técnicas (a mesma falha ocorre
  na v3). D2 deu ganho aninhado de +0,0301 (IC com zero). A v4 opt-in usa a v3 + limiares D2;
  levar D1 ao holdout exige emenda explícita do pesquisador. Detalhes em
  `evaluation/refinement_v4/CALIBRATION_D_RESULTS.md`.
- **13/10/2026 — ADR-047:** por decisão do pesquisador, a ancoragem D1 integra a candidata v4 que será
  levada ao holdout, em desvio declarado do critério de falhas da calibração D. O plano D4/D5 foi
  registrado antes da execução; `v4_d4` falhou um de seis critérios por 0,009 e mostrou conversão
  excessiva para `MISLEADING`. Permanece opt-in (`d4=True`) e fora da candidata. Detalhes em
  `evaluation/refinement_v4/CALIBRATION_D4_RESULTS.md`.
- **13/10/2026 — ADR-048:** a candidata v4 (v3 + ancoragem D1) foi congelada por hashes e executada uma única vez no holdout v4, com os gates registrados antes. Resultado negativo: macro-F1 0,487 contra 0,577 da v3; falharam os gates de ganho, precisão das conclusões, queda de recall de `REFUTED` e citação. A v3 permanece o padrão do bot e da CLI; `PIPELINE_VERSION=v4` fica documentada como opt-in experimental. Resultados em `evaluation/refinement_v4/HOLDOUT_RESULTS.md`.

- **14/10/2026 — ADR-049:** aberta a linha exploratória v5 (`PIPELINE_VERSION=v5`, opt-in). A
  extração passa a produzir alegação canônica, tipo (geral/evento individual) e 1–3 proposições com
  papel e tipo; cada proposição é julgada por NLI com verificação determinística de escopo e de trecho
  literal; o veredito é agregado por regra explícita. Multiconsulta, reranker e modo de raciocínio do
  Qwen são ablações. Como não há conjunto novo e o holdout v4 foi revelado, a avaliação usa os 96 itens
  v4 e paráfrases com rótulo herdado e não tem valor confirmatório. Protocolo e regra de decisão em
  `evaluation/refinement_v5/PROTOCOL.md`, registrados antes de qualquer inferência.
- **15/10/2026 — ADR-049 (resultado):** a v3 deu o mesmo veredito nas três redações em 63,5% dos
  itens. Na execução final, `v5_multiquery` obteve macro-F1 0,653 contra 0,490 (IC por família
  +0,037 a +0,275), consistência 0,656, zero falhas e P95 14,8 s; reranker e raciocínio não
  acrescentaram ganho (o raciocínio teve P95 77 s e 10 falhas de tempo). Todas as variantes
  reprovaram no critério de queda de recall de `SUPPORTED` (1,00 → 0,88). A v3 permanece padrão; a
  v5 fica opt-in com multiconsulta. Desvio declarado: remoção da pós-regra de escopo na calibração
  (Adendo 2). Detalhes em `evaluation/refinement_v5/RESULTS.md`.
- **16/10/2026 — ADR-050:** aberta a Fase 17 (extração multimodal). Um benchmark sintético
  (`src/immunocheck/evaluation/extraction_benchmark.py`) embute as 96 alegações v4 em capturas de
  WhatsApp e de redes sociais, fotos de tela, memes, páginas HTML e PDF e mensagens com link ou ruído
  de encaminhamento. O gabarito é o próprio texto da alegação, e a referência do veredito é a alegação
  limpa enviada ao mesmo pipeline. Mudanças de extração entram em módulos novos, sem editar
  `text_components.py` nem `document_expansion.py`. Os arquivos congelados da v5 (`bootstrap.py`,
  `ollama.py`) podem receber ligações novas; a reprodução da v5 usa o commit `1e7644c`. O ensaio V0
  mostrou o `qwen3.6` viável como alternativa de OCR por visão (cerca de 3 s por imagem com o modelo
  carregado, mas a RAM fica no limite). Protocolo em `evaluation/extraction_v1/PROTOCOL.md`.
- **17/10/2026 — ADR-050, resultado:** execução final única nos 48 itens `test` (912 casos por
  condição). A camada nova (`improved`) elevou a concordância com o veredito do texto limpo de 0,630
  para 0,731 (Δ +0,101, IC por família +0,074 a +0,129) e, nos modelos reservados, de 0,586 para
  0,654; a variante com visão (`improved_vision`) chegou a 0,740, com CER das imagens de 0,016 e
  nenhuma rejeição, mas com 41 a 52 s nos pedidos em que a visão foi acionada. As duas passaram em
  G1–G5 e reprovaram em G6: 2,19% e 2,40% de falhas técnicas, contra o limite fixo de 2% (a linha de
  base teve 3,85%). As falhas são `ModelOutputError` do extrator de alegação da v3, fora da camada
  avaliada, mas a regra não é reinterpretada. `EXTRACTION_VERSION=v1` continua padrão; a v2 fica
  opt-in. Achado: a mensagem com link concorda só 0,23 porque o extrator de alegação se confunde com
  o comentário à frente do conteúdo. Detalhes em `evaluation/extraction_v1/RESULTS.md`.
- **16/10/2026 — ADR-051:** aberta a Fase 18. O teste externo (`evaluation/refinement_v6/external/`,
  150 alegações de X-FACT, FACTCK.BR e FACTCK.BR-extended; 12 `SUPPORTED`, 53 `MISLEADING`, 85
  `REFUTED`) foi montado por regra e congelado sem nenhuma inferência. Os 96 itens sem licença de
  redistribuição são versionados só por URL e hash. Como o gabarito é de mundo real e o sistema deve
  se abster fora do corpus, a análise principal é binária com a abstenção à parte. O recall de
  `SUPPORTED` fica descritivo por falta de poder estatístico. As correções da v5 (trecho tolerante e
  normalização de números) são desenvolvidas só na calibração v4. Protocolo em
  `evaluation/refinement_v6/PROTOCOL.md`.
- **17/10/2026 — ADR-051, resultado:** execução final única (congelamento em `c42d783`). A
  `v5_fixed` passou nos cinco critérios do v4 (macro-F1 0,637, Δ +0,146 com IC por família +0,020
  a +0,256), mas reprovou no teste externo: precisão das conclusões 0,877 contra 0,861 da v3 (IC da
  diferença −0,083 a +0,116, abaixo do limite de −0,08 em X1) e cobertura 0,380 contra 0,527 (X3). O
  erro grave caiu de 5,8% para 2,9%. A `v5_fixed_qwen36` teve o melhor veredito do projeto (macro-F1
  0,716 e consistência 0,760 no v4; precisão 0,898 e erro grave 2,2% no externo), mas reprovou em X3
  e no critério 5. A v3 continua padrão. Depois da execução, ao investigar as falhas, foi encontrado
  um defeito na regra tolerante de números (quebra de linha aceita como separador de milhar, o que
  gerava `ValueError` em tabelas da evidência; 5 e 7 entradas no v4, nenhuma no externo). As
  execuções não foram repetidas e a decisão não depende do defeito; a correção entrou em seguida,
  com teste. Detalhes em `evaluation/refinement_v6/RESULTS.md`.
- **17/10/2026 — ADR-052:** aberta a Fase 19 (nova base de avaliação). O diagnóstico dos registros da
  Fase 18 mostrou que `MISLEADING` se perde na agregação por proposição (6 de 24 acertos na
  `v5_fixed`) e que, no teste externo, a maioria das abstenções vem do juiz com evidência recuperada
  (55 de 93). Como o v4 e o teste externo 1 já foram revelados, a Fase 19 constrói um conjunto
  contrastivo gerado do corpus, com rótulo por construção, portões automáticos e revisão humana de
  80 itens, e um teste externo 2 com checagens recentes. O teste é congelado antes de qualquer
  mudança de arquitetura (Fase 20). O pesquisador aprovou a métrica principal (macro-F1 de 4
  classes), o limite de 45 s e o download do `mistral-small3.2`, usado só na geração. Protocolo em
  `evaluation/refinement_v7/PROTOCOL.md`.
- **18/10/2026 — ADR-052:** o C7 foi gerado, revisado e congelado (400 itens, 100 por classe; 207
  no teste e 193 no desenvolvimento, divididos por documento). O primeiro sorteio rendeu 81/81/80 nas
  classes do corpus, e o limite subiu de 6 para 8 chunks por documento. A revisão das amostras foi
  preenchida pelo pesquisador com uma ferramenta de IA, e não item a item: a emenda a declara como
  **revisão assistida por LLM**. Na rodada 1, só os fatos de fora do corpus erraram (7 de 9), porque
  eram fatos genéricos já cobertos pelo corpus. A regra corrigida acrescenta um juiz de cobertura
  (portão 8) e completa a classe com relatos individuais. Na conferência, o portão descartou os 7
  erros e também os 2 acertos, falha declarada. Na rodada 2, os 20 fatos de fora restantes tiveram 0
  erros. Limitação principal: `INSUFFICIENT_EVIDENCE` ficou com 80% de relatos de casos particulares.
  Detalhes em `evaluation/refinement_v7/C7_REPORT.md`.
- **18/10/2026 — ADR-053 (altera a ADR-003):** a pedido do pesquisador, o escopo avaliado do TCC
  passa a ser texto e imagem predominantemente textual. O link permanece no bot como protótipo
  experimental, com as proteções de segurança (bloqueio de IP privado, esquemas inseguros,
  redirecionamentos e tamanho), mas sem critério de aceite nem avaliação próprios a partir da Fase
  19. Impacto metodológico: nenhum resultado anterior muda; a ADR-050 (extração) já tratava o link
  separadamente. Migração: o manuscrito e o `PROJECT_BRIEF.md` passam a descrever o link como
  experimental.
- **18/10/2026 — ADR-054:** aberta a Fase 20. O Adendo 1 do protocolo da v7 registra cinco
  candidatas, a seleção progressiva no desenvolvimento do C7 (193 itens), o prazo de 31/10 para o
  desenvolvimento e a regra de promoção contra a v3 (critérios P1–P4 no teste do C7 e X1–X4 no teste
  externo 2, com os limites da Fase 18 sem alteração). Nada foi executado sobre os conjuntos antes do
  registro.
- **19/10/2026 — ADR-054 e ADR-055:** a seleção no desenvolvimento terminou sem candidata aprovada
  (C1 em cinco versões, C2, C3b, C4 e C5; a C3 foi trocada pela C3b no Adendo 2 por latência). A
  análise exploratória da combinação v3 + `v5_fixed` levou ao Adendo 3: a cascata C6 entra na execução
  única ao lado da v3 e da `v5_fixed`, com uma via de promoção por segurança decidida pelo pesquisador
  antes de qualquer contato com o teste.
- **20/10/2026 — ADR-055 aceita:** execução única das condições v3, `v5_fixed` e C6 no teste do C7
  (207 itens) e no teste externo 2 (304 itens), com o congelamento conferido antes e depois. A C6
  passou pela via de segurança: macro-F1 +0,043 (IC +0,011 a +0,080), erro grave −0,109 (IC −0,157 a
  −0,066) no C7, e precisão das conclusões de 0,940 para 0,991 no teste externo 2, com queda de
  cobertura de 0,030. Não passou no P1 da regra original. A `v5_fixed` isolada reprovaria em P1, P3
  e X3. Limitações: recall de `SUPPORTED` de 0,76 para 0,63, P95 de 26,5 s e regra desenhada no
  desenvolvimento.
- **20/10/2026 — ADR-055 integrada:** a C6 virou `PIPELINE_VERSION=v7`, padrão do bot e da CLI,
  montada em `bootstrap_bot.py` sem editar os módulos congelados. Com imagem ou link, a v3 e a
  `v5_fixed` compartilham uma única normalização, descartada ao fim da requisição. A v3 e a v1
  continuam selecionáveis para reversão. Passada de fumaça: texto verdadeiro confirmado pela
  verificação (31 s), texto falso refutado (17 s), imagem com um único OCR (20 s) e o fluxo do
  Telegram com cliente simulado.
- **20/10/2026 — ADR-056 proposta:** Fase 21, corpus v2. O prazo de entrega passou a 06/11, com a
  pesquisa pronta até 31/10. Antes de qualquer download, ficaram registrados a regra de seleção do
  lote 009 (lacunas do plano de cobertura de setembro, licença clara, nenhum texto de agência de
  checagem, cegueira aos itens dos conjuntos), os nove candidatos, a execução única da C6 com o
  corpus v2 e a regra de decisão (E1–E3 no teste externo 2, K1–K2 no teste do C7, O1).
- **20/10/2026 — ADR-056 encerrada sem adoção:** lote 009 aprovado pelo autor e corpus v2 congelado
  (89 documentos, 7.845 trechos; texto e vetores do v1 idênticos). Na execução única, a cobertura no
  teste externo 2 subiu só de 35,2% para 36,2% (IC do Δ −0,013 a +0,033), abaixo do E1; precisão, erro
  grave, macro-F1 do C7 (−0,010, IC −0,033 a +0,010) e operação ficaram dentro das margens. O corpus v1
  continua padrão. As abstenções em alegações reais não decorrem principalmente de lacunas temáticas.

## Política de alteração

Uma ADR aceita pode ser alterada quando houver evidência experimental, inviabilidade
técnica comprovada ou mudança de requisito. A alteração deve registrar data,
evidência, impacto metodológico e plano de migração; preferência tecnológica isolada
não é justificativa suficiente.
