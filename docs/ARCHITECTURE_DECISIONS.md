# Registro de decisões arquiteturais

| ID | Decisão | Estado | Justificativa |
|---|---|---|---|
| ADR-001 | Telegram na v1 | Aceita | Gratuito, simples, long polling local e sem exigência de infraestrutura pública. |
| ADR-002 | WhatsApp fora da v1 | Aceita | Maior complexidade operacional; reavaliar somente após o protótipo funcional. |
| ADR-003 | Texto, imagem textual e link na v1 | Aceita | São requisitos do problema e viáveis localmente; vídeo tem custo desproporcional. |
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
| ADR-014 | Verificação pós-geração obrigatória | Aceita | Reduz citações inválidas e afirmações sem suporte; efeito será medido. |
| ADR-015 | Python 3.12 | Aceita | Base estável e reproduzível para o ecossistema de ML e OCR. |
| ADR-016 | Quatro classes com abstenção | Aceita | Evita binarização indevida e diferencia falta de evidência de falsidade. |
| ADR-017 | Fontes parciais em abstenções | Aceita | Fontes consultadas podem ser exibidas como não conclusivas, sem fingir que sustentam um veredito. |
| ADR-018 | Avaliação por famílias e teste selado | Aceita | Validação cruzada usa somente desenvolvimento e mantém famílias inteiras em um fold; o teste congelado só participa da execução definitiva. |
| ADR-019 | Baseline lexical obrigatório | Aceita | TF-IDF com regressão logística mede atalhos de redação no benchmark sintético e contextualiza o ganho real da pipeline RAG. |
| ADR-020 | BGE-M3 sem reranker; híbrido como entrada do reranker | Aceita | No desenvolvimento, o denso teve nDCG@10 0,461 contra 0,365 do híbrido; a diferença pareada ainda inclui empate, portanto o híbrido não demonstrou vantagem sem reranking. |
| ADR-021 | Híbrido + reranker como candidato fim a fim, não padrão | Aceita | O reranker chegou a nDCG@10 0,615 com ganho pareado positivo, mas acrescentou mediana de 10,0 s em CPU; a latência total ainda precisa ser validada. |
| ADR-022 | Não promover a pipeline fim a fim v1 | Aceita | Macro-F1 máximo de 0,446, zero recall de `MISLEADING` nas condições auditadas e omissões materiais do extrator exigem uma iteração de desenvolvimento antes do teste. |

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

## Política de alteração

Uma ADR aceita pode ser alterada quando houver evidência experimental, inviabilidade
técnica comprovada ou mudança de requisito. A alteração deve registrar data,
evidência, impacto metodológico e plano de migração; preferência tecnológica isolada
não é justificativa suficiente.
