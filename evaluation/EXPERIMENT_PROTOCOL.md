# Protocolo experimental pré-registrado — Fase 6

Data: 16/09/2026. Este protocolo foi registrado antes da primeira execução do
baseline lexical da Fase 6.

## Identidade e separação

- Congelamento: `sha256:a352d9f93032b87652b38ffea2b855cef393bd822f04142dbfbd5830ad609666`.
- Dataset: `5caabdab9347c13dd270e6a335599dc5e213f5ad814312f6bcdf45731a67a5bf`.
- Desenvolvimento: 96 itens. Teste selado: 64 itens.
- `claim_family` é a unidade de agrupamento; uma família não pode aparecer em
  treino e validação no mesmo experimento.
- Nenhum resultado do teste pode alterar prompt, modelo, retrieval, reranker,
  limiar, regra ou redação do sistema.

## Questões de pesquisa

1. Um classificador puramente lexical já prevê os rótulos, indicando atalhos do
   benchmark sintético?
2. O retrieval híbrido melhora BM25 e dense isolados nas evidências dos itens de
   desenvolvimento?
3. O reranker melhora relevância o suficiente para justificar sua latência local?
4. A pipeline completa melhora qualidade e fidelidade em relação às ablações?
5. O protótipo é executável no Ryzen 5 7500F, RTX 4060 8 GB e 32 GB de RAM com
   latência compatível com demonstração interativa?

## Experimento A — baseline lexical

- Somente os 96 itens de desenvolvimento.
- TF-IDF de palavras em unigramas e bigramas, seguido de regressão logística com
  pesos balanceados.
- Validação cruzada estratificada em cinco folds, agrupada por `claim_family`,
  com semente `20260916`.
- Previsões out-of-fold; nenhuma métrica de treino será apresentada como resultado.
- Métricas primárias: macro-F1 e balanced accuracy. Secundárias: acurácia,
  weighted-F1, matriz de confusão e precisão/recall/F1 por classe.
- Intervalos de 95% por 2.000 reamostragens bootstrap de famílias inteiras.
- Coeficientes do ajuste sobre todo o desenvolvimento serão apenas diagnóstico de
  vocabulário; não constituem validação.

Interpretação prévia: desempenho alto do baseline não valida o ImmunoCheck; ele
indica que os moldes sintéticos facilitam o problema e deve limitar as conclusões.

## Experimento B — retrieval no desenvolvimento

- Consultas: alegações conclusivas do desenvolvimento com chunks de evidência
  humana; abstenções sem evidência conclusiva ficam fora dessas métricas.
- Condições: BM25, BGE-M3 dense, RRF híbrido e híbrido + reranker.
- Métricas: Recall@5, Recall@10, MRR, nDCG@10 e latência mediana/P95.
- Incerteza: bootstrap de famílias, 2.000 reamostragens, incluindo deltas pareados.
- Reranker só poderá ser promovido se o IC 95% do delta de nDCG@10 não incluir
  perda, Recall@5 não cair e o custo de latência for aceitável para a demonstração.

## Experimento C — fim a fim no desenvolvimento

Condições previstas:

1. BM25 + geração, sem auditor pós-geração — ablação exclusivamente offline.
2. Híbrido + geração, sem auditor — ablação exclusivamente offline.
3. Híbrido + geração + auditor de fidelidade — configuração candidata.
4. Híbrido + reranker + auditor, somente se o Experimento B aprovar o reranker.

Métricas: macro-F1, métricas por classe, precisão/recall da abstenção, validade das
citações, suporte das afirmações, taxa de aprovação do auditor, falhas técnicas e
latência. Erros serão categorizados sem alterar o teste.

## Execução definitiva no teste

O teste será executado uma única vez após fixar código, modelos, prompts e condições.
As condições comparativas pré-registradas poderão ser executadas no mesmo lote, mas
nenhuma observação do teste autoriza nova escolha. Mudança posterior exige declarar
uma nova versão e invalida a comparação confirmatória original.

## Limitações obrigatórias

- Benchmark inteiramente sintético e pequeno.
- Segunda revisão em 30%, não em 100%.
- Identidade, competência e independência não certificadas por software.
- Possíveis atalhos lexicais e validade externa limitada para notícias reais.
- O mesmo projeto participou da construção dos itens e da pipeline.

## Emenda após os Experimentos A e B, antes do Experimento C

Data: 16/09/2026. Esta emenda usa somente resultados de desenvolvimento e foi
registrada antes da primeira execução fim a fim da Fase 6. O teste continua
selado e não participou da decisão.

- O baseline lexical obteve macro-F1 0,610 (IC 95% 0,509–0,700). O resultado e
  termos como `entao`, `municipio` e `campanha` indicam risco material de atalhos
  de redação; conclusões sobre generalização para notícias reais serão limitadas.
- O híbrido melhorou BM25, mas não demonstrou vantagem sobre BGE-M3 isolado. O
  caminho sem reranker do Experimento C passa a usar BGE-M3.
- O híbrido + reranker foi aceito como condição comparativa: o IC 95% do ganho
  de nDCG@10 foi positivo contra híbrido e denso, e Recall@5 aumentou. Ele não
  foi promovido ao padrão porque acrescentou cerca de 10 s por consulta em CPU.

As quatro condições fim a fim ficam, portanto:

1. BM25 + geração, sem auditor — ablação offline.
2. BGE-M3 + geração, sem auditor — ablação offline.
3. BGE-M3 + geração + auditor — candidata simples.
4. Híbrido + reranker + auditor — candidata de maior qualidade de retrieval.

Esta alteração é adaptação transparente com dados de desenvolvimento, não uma
hipótese confirmatória nova. As condições e decisões ficam fixas antes do teste.

## Emenda diagnóstica v2 após a primeira execução fim a fim

Data: 17/09/2026. Registrada antes da primeira inferência da v2. A v1 usou os 96
itens de desenvolvimento e não carregou teste. O maior macro-F1 foi 0,446; os
ICs dos deltas entre candidatas incluíram zero e as condições auditadas tiveram
recall zero para `MISLEADING`.

A inspeção de erros encontrou alteração da alegação antes do retrieval. Em dez
dos 19 itens `MISLEADING`, o texto extraído ficou com menos de 80% do tamanho do
original e frequentemente perdeu `então`, `portanto`, universais ou a conclusão.
Três alegações verificáveis de política/logística vacinal foram recusadas como
fora do escopo. Esses números são diagnóstico de desenvolvimento, não validação
semântica independente.

A v2 altera **somente o extrator de alegações**:

1. políticas, logística, acesso e comunicação vacinal entram explicitamente no
   escopo já definido de vacinação humana;
2. o prompt exige preservar premissa e conclusão do mesmo fato-alvo;
3. uma guarda determinística preserva a entrada curta e de alegação única se a
   extração remover negação, quantificador, causalidade ou conector material.

Retrieval, top-k, corpus, embeddings, reranker, LLM, gerador, auditor, schemas,
temperatura e sementes permanecem fixos. A v2 usa novos artefatos e não
sobrescreve a v1.

Critérios definidos antes da execução:

- reduzir as três recusas indevidas de escopo;
- obter recall maior que zero para `MISLEADING` em ao menos uma condição
  auditada;
- relatar macro-F1, abstenção, citação, falhas e latência mesmo se piorarem;
- comparar v1/v2 por item e família, sem selecionar exemplos favoráveis;
- não promover configuração ao teste apenas por melhora pontual no
  desenvolvimento.

## Emenda de calibração do auditor v3

Data: 17/09/2026. Registrada antes da primeira inferência da v3. A análise da
v2 mostrou que o auditor aumentou o recall de abstenção de 0,125 para 0,625,
mas reduziu o recall de `MISLEADING` de 0,474 para 0,158. Entre as 39 mudanças
de rótulo, 19 pioraram previsões corretas. O teste continua selado e não
participou desta decisão.

A v3 altera **somente o objetivo do auditor pós-geração**. Ele deixa de atuar
como um segundo classificador e passa a avaliar apenas se as afirmações factuais
do rascunho — inclusive `correct_fact` e `omitted_or_distorted` — estão cobertas
pelos trechos citados. Discordância isolada entre `REFUTED` e `MISLEADING` não
reprova o rascunho; afirmação factual sem apoio, exagero causal, alteração do
sentido da fonte ou orientação médica individual continuam provocando abstenção.
Validação de IDs, campos obrigatórios e coerência estrutural permanece inalterada.

Para isolar o componente, a execução reutilizará as extrações, os seis chunks
densos e os rascunhos já registrados na v2, chamando novamente apenas o auditor.
Não haverá novo retrieval nem nova geração. O checkpoint v2 e seu hash serão
validados antes da execução; a v3 terá artefatos separados e não sobrescreverá
resultados anteriores.

Critérios definidos antes da execução, todos no desenvolvimento:

- macro-F1 pelo menos igual ao auditor v2 no ponto estimado (`0,528`);
- recall de `MISLEADING` de pelo menos `0,35` (sete dos 19 itens);
- recall de abstenção de pelo menos `0,50` (12 dos 24 itens);
- taxa de citação relevante de pelo menos `0,50`, falha técnica de no máximo
  `0,02` e P95 de latência total estimada de no máximo 12 segundos;
- promoção somente se todos os limites forem cumpridos e houver melhora em
  macro-F1 ou recall de `MISLEADING` sobre o auditor v2.

Serão relatados matriz de confusão, métricas por classe, precisão/F1 de
abstenção, mudanças item a item e bootstrap pareado por família com 2.000
reamostragens. Se os gates falharem, não haverá nova variante orientada pelos
mesmos 96 itens: o teste permanecerá fechado até uma decisão metodológica
explícita.
