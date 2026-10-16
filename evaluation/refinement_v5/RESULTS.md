# Resultados da linha exploratória v5 (15/10/2026)

Execução única de cada condição, com código congelado (`freeze.json`, commit `1e7644c`),
sobre os 96 itens v4 em três formas (original, coloquial, formal = 288 entradas). Temperatura 0,
seed 42 (raciocínio: temperatura 0,6). A v3 de referência é `results/dev/v3_all_run1.jsonl`.
Artefatos: `results/final/*_all_run1.jsonl`, `results/final/v5_multiquery_all_run2.jsonl` (pendente) e
`results/final/analysis.json`. **Resultado exploratório, não confirmatório** (ver ameaças).

## Desempenho nas alegações originais (96)

| Condição | Macro-F1 | Δ vs v3 (IC 95% por família) | 3 classes | Recall S / R / M / I | Precisão das conclusões | Precisão / recall de abstenção | Falhas | P95 |
|---|---|---|---|---|---|---|---|---|
| v3 (padrão) | 0,490 | — | 0,660 | 1,00 / 0,79 / 0,08 / 0,33 | 0,529 | 0,73 / 0,33 | 2 | 18,3 s |
| v5_base | 0,600 | +0,110 (−0,007 a +0,218) | 0,689 | 0,83 / 0,71 / 0,25 / 0,71 | 0,652 | 0,57 / 0,71 | 0 | 14,0 s |
| **v5_multiquery** | **0,653** | **+0,162 (+0,037 a +0,275)** | 0,733 | 0,88 / 0,83 / 0,29 / 0,71 | 0,706 | 0,61 / 0,71 | 0 | 14,8 s |
| v5_multiquery_reranker | 0,650 | +0,159 (+0,068 a +0,240) | 0,724 | 0,88 / 0,83 / 0,33 / 0,62 | 0,681 | 0,62 / 0,62 | 0 | 26,5 s |
| v5_multiquery_think | 0,648 | +0,157 (+0,019 a +0,287) | 0,780 | 0,83 / 0,75 / 0,21 / 0,96 | 0,717 | 0,64 / 0,96 | 3 | 77,0 s |

## Robustez a paráfrase (todas as formas)

| Condição | Consistência (mesmo veredito nas 3 formas) | Macro-F1 original / coloquial / formal | Macro-F1 agrupado |
|---|---|---|---|
| v3 | 0,635 | 0,490 / 0,648 / 0,569 | 0,573 |
| v5_base | **0,719** | 0,600 / 0,683 / 0,696 | 0,661 |
| v5_multiquery | 0,656 | 0,653 / 0,682 / 0,746 | **0,695** |
| v5_multiquery_reranker | 0,646 | 0,650 / 0,718 / 0,674 | 0,682 |
| v5_multiquery_think | 0,625 | 0,648 / 0,675 / 0,713 | 0,680 |

Estabilidade entre execuções (mesma entrada, duas execuções): v3 0,948 (contra os registros v4);
v5_multiquery **pendente** (run1 contra run2; repetição em andamento). Na primeira tentativa da
run2, os 18 primeiros casos estouraram o tempo limite do cliente (2 × 120 s, `OllamaError`) porque o
Ollama ainda processava uma requisição longa da condição com raciocínio. Esses registros de falha de
infraestrutura foram descartados e a repetição foi retomada; a métrica é descritiva e sem gate.

## Efeito nos padrões de erro que motivaram a v5 (alegações originais)

| Padrão | v3 | v5_multiquery |
|---|---|---|
| `MISLEADING` classificado como `REFUTED`/`SUPPORTED` | 21 de 24 | 12 de 24 |
| Abstenção fora do corpus classificada com veredito conclusivo | 11 de 14 | 7 de 14 |
| Evento individual não reconhecido | 5 de 10 | 0 de 10 |

## Regra de decisão (PROTOCOL.md)

| Critério | v5_base | v5_multiquery | +reranker | +think |
|---|---|---|---|---|
| 1. Δ ≥ +0,05 e IC inferior > 0 | ✗ | ✓ | ✓ | ✓ |
| 2. Consistência ≥ v3 | ✓ | ✓ | ✓ | ✗ |
| 3. Queda de recall S/R ≤ 0,10 | ✗ (S −0,17) | ✗ (S −0,12) | ✗ (S −0,12) | ✗ (S −0,17) |
| 4. Precisão de abstenção ≥ 0,50 | ✓ | ✓ | ✓ | ✓ |
| 5. Falhas ≤ 2 | ✓ | ✓ | ✓ | ✗ (3) |
| 6. P95 ≤ 45 s | ✓ | ✓ | ✓ | ✗ |

**Nenhuma condição satisfaz a regra. A v3 permanece padrão do bot; a v5 fica opt-in
(`PIPELINE_VERSION=v5`, multiconsulta sem reranker nem raciocínio).** O critério 3 não foi
flexibilizado após a observação dos dados.

## Leitura

- A decomposição com agregação determinística melhora o macro-F1 em todas as formas e condições
  (+0,11 a +0,16 nas originais; IC acima de zero em três das quatro condições), eleva a precisão
  das conclusões (0,53 → 0,71), elimina falhas técnicas e reduz a latência.
- O ganho vem dos três padrões diagnosticados: eventos individuais passam a ser reconhecidos
  (5 → 0 erros), `MISLEADING` é confundido menos (21 → 12) e há menos conclusões sem base
  fora do corpus (11 → 7).
- O custo é conservadorismo: o recall de `SUPPORTED` cai de 1,00 para 0,88 (3 de 24 viram
  abstenção). Dois desses três casos foram rebaixados pelas verificações determinísticas
  (trecho literal não encontrado e número ausente da evidência), isto é, o sistema prefere se
  abster quando não consegue ancorar a conclusão. A regra pré-registrada trata essa perda como
  impeditiva; ela é a principal razão da não promoção.
- Multiconsulta foi a variante mais útil (+0,05 sobre a consulta única nas originais).
  O reranker não trouxe ganho e quase dobrou a latência, o que confirma que o retrieval não é o
  gargalo. O modo de raciocínio aumentou o recall de abstenção (0,96) e o macro-F1 em 3 classes,
  mas teve 10 falhas de tempo/limite do Ollama nas 288 entradas e P95 de 77 s, contra 40 s na
  medição de calibração.
- A consistência sob paráfrase melhora pouco com a multiconsulta (0,656 contra 0,635); a
  consulta única é a mais consistente (0,719). O ganho de calibração (+0,238; consistência 0,729)
  encolheu na avaliação completa, o que é esperado após três iterações nos mesmos 48 itens.

## Ameaças à validade

Holdout v4 já revelado antes do desenho (inclusive na análise de erros que motivou a v5);
metade dos 96 itens foi usada nas iterações; conjunto sintético; curadoria sem revisor externo;
paráfrases redigidas com apoio de IA e ainda sem conferência do pesquisador; uma execução por
condição; não determinismo do Ollama; 24 famílias (IC largos).
