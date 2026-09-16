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
