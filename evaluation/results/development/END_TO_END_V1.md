# Experimento fim a fim v1 — desenvolvimento

Execução concluída em 17/09/2026 com o código congelado no commit `ecd9e4c`.
Foram processados os 96 itens de desenvolvimento, distribuídos em 33 famílias.
O relatório declara `test_items_loaded: 0`; o teste de 64 itens permaneceu
selado. O checkpoint tem SHA-256
`555e115ae4e6aa86c31888cf1e182ea5b12bbf986b8e0289cd46159d83c66d1d`.

## Resultados

| Condição | Macro-F1 | IC 95% por família | Acurácia | Citação relevante | Mediana | P95 |
|---|---:|---:|---:|---:|---:|---:|
| BM25, sem auditor | 0,401 | 0,322–0,482 | 0,458 | 0,375 | 7,5 s | 9,7 s |
| BGE-M3, sem auditor | 0,381 | 0,304–0,460 | 0,479 | 0,431 | 7,3 s | 10,6 s |
| BGE-M3 + auditor | 0,418 | 0,346–0,483 | 0,500 | 0,431 | 8,5 s | 12,6 s |
| Híbrido + reranker + auditor | 0,446 | 0,373–0,519 | 0,531 | 0,583 | 18,6 s | 23,3 s |

Os ICs 95% dos deltas pareados de macro-F1 incluíram zero:

- auditor menos denso sem auditor: mediana +0,039; IC -0,044 a +0,118;
- rerankeado menos denso auditado: mediana +0,031; IC -0,050 a +0,104;
- rerankeado menos denso sem auditor: mediana +0,070; IC -0,038 a +0,161.

Logo, o ponto estimado favorece híbrido + reranker + auditor, mas o conjunto de
desenvolvimento não demonstra superioridade conclusiva em classificação. O ganho
de retrieval aparece com mais clareza na taxa de ao menos uma citação humana
relevante: 58,3% contra 43,1% no denso.

## Abstenção e auditor

| Condição | Precisão da abstenção | Recall da abstenção | F1 da abstenção |
|---|---:|---:|---:|
| BM25, sem auditor | 0,300 | 0,125 | 0,176 |
| BGE-M3, sem auditor | 0,286 | 0,083 | 0,129 |
| BGE-M3 + auditor | 0,395 | 0,625 | 0,484 |
| Híbrido + reranker + auditor | 0,375 | 0,625 | 0,469 |

O auditor alterou 31 dos 96 rascunhos densos: 13 mudanças corrigiram o rótulo,
11 transformaram um rótulo correto em incorreto e sete continuaram incorretas.
Comparado ao denso auditado, o caminho rerankeado mudou 26 resultados: 12
melhoraram, nove pioraram e cinco continuaram errados. Portanto, nem auditor nem
reranker podem ser descritos como monotonicamente seguros.

## Falhas por classe

- O recall de `MISLEADING` foi 0 nas duas condições auditadas. BM25 sem auditor
  chegou a 0,211 e BGE-M3 sem auditor a 0,105.
- A melhor condição obteve F1 0,615 em `SUPPORTED`, 0,702 em `REFUTED`, 0 em
  `MISLEADING` e 0,469 em `INSUFFICIENT_EVIDENCE`.
- Doze itens tiveram o mesmo rótulo errado nas quatro condições; sete deles eram
  `MISLEADING`.
- Cada condição teve duas falhas estruturadas em 96 itens (2,1%), causadas por
  campos semanticamente incompatíveis na saída do gerador. A falha segura
  converteu esses casos em abstenção.

## Causa dominante: alteração da alegação

O extrator marcou 93/96 entradas como pertencentes ao escopo e não apresentou
falha técnica, mas três alegações verificáveis foram recusadas como fora do
escopo. Em dez dos 19 itens `MISLEADING`, o texto extraído ficou com menos de 80%
do comprimento do original. Essa razão é apenas triagem diagnóstica, não métrica
semântica, mas a inspeção confirmou omissões materiais.

Exemplo: “a maioria das vacinas fica entre 2–8 °C, então a faixa serve para
qualquer vacina” virou apenas “a maioria das vacinas deve ser armazenada entre
2–8 °C”. A extrapolação falsa desapareceu e todas as condições responderam
`SUPPORTED`. Padrões semelhantes removeram `então`, `portanto`, `qualquer`,
`necessariamente` ou a conclusão universal de encadeamentos premissa–conclusão.

O prompt também tratou alegações sobre microplanejamento e logística de vacinação
como fora do escopo, embora façam parte da política de imunização humana coberta
pelo projeto.

## Outras categorias de erro

- **Causalidade individual:** associação geral foi usada para confirmar causa em
  um caso fictício (“o caroço foi causado pelo alumínio”), quando o rótulo humano
  exigia abstenção.
- **Fronteira `MISLEADING`/`REFUTED`:** extrapolações universais foram frequentemente
  tratadas como falsidade integral, perdendo a premissa verdadeira.
- **Autoverificação dependente:** gerador e auditor usam o mesmo Qwen3-8B; a taxa
  de aprovação do auditor foi 63,7% no denso e 62,2% no rerankeado. Isso não é
  validação independente.
- **Validade externa:** o baseline lexical obteve macro-F1 0,610, acima de todas
  as condições RAG, reforçando o risco de moldes sintéticos.

## Decisão

Esta v1 **não está aprovada para o teste congelado nem para alegação de versão
estável**. O próximo ensaio de desenvolvimento será uma v2 separada, limitada a:

1. preservar marcadores materiais e o encadeamento de alegações curtas;
2. incluir políticas, logística, acesso e comunicação vacinal no escopo;
3. manter retrieval, reranker, gerador, auditor e parâmetros inalterados, para
   atribuir diferenças à correção do extrator.

O teste continuará selado. Qualquer melhoria na v2 será relatada como ajuste com
dados de desenvolvimento, não como confirmação externa.
