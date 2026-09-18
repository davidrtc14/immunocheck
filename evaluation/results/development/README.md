# Resultados de desenvolvimento — Fase 6

Data das execuções: 16/09/2026. Estes resultados seguem o protocolo em
`evaluation/EXPERIMENT_PROTOCOL.md` e usam exclusivamente o split de
desenvolvimento do benchmark congelado. Nenhum dos 64 itens de teste foi
carregado nos modelos ou usado para decisão.

## Identidade

- Freeze: `sha256:a352d9f93032b87652b38ffea2b855cef393bd822f04142dbfbd5830ad609666`.
- Dataset congelado: `5caabdab9347c13dd270e6a335599dc5e213f5ad814312f6bcdf45731a67a5bf`.
- Classificação lexical: 96 itens, 33 famílias, cinco folds agrupados.
- Retrieval: 72 itens conclusivos; 24 abstenções sem evidência conclusiva foram
  corretamente excluídas das métricas de ranking.
- Incerteza: 2.000 reamostragens bootstrap de famílias inteiras, semente
  `20260916`.

## Baseline lexical

| Métrica | Estimativa | IC 95% por família |
|---|---:|---:|
| Macro-F1 | 0,610 | 0,509–0,700 |
| Balanced accuracy | 0,627 | 0,534–0,717 |
| Acurácia | 0,615 | 0,514–0,706 |

F1 por classe: `SUPPORTED` 0,533; `REFUTED` 0,510; `MISLEADING` 0,605;
`INSUFFICIENT_EVIDENCE` 0,792. Um modelo sem corpus nem RAG classificou bem
acima do acaso. Coeficientes diagnósticos destacaram termos associados ao molde,
como `entao` em `MISLEADING` e `municipio`/`campanha` em abstenções. Isso não
invalida o benchmark, mas impede tratá-lo como prova de generalização para
notícias reais.

## Retrieval

| Sistema | Recall@5 | Recall@10 | MRR | nDCG@10 | Mediana local |
|---|---:|---:|---:|---:|---:|
| BM25 | 0,350 | 0,384 | 0,283 | 0,294 | 53,5 ms |
| BGE-M3 | 0,528 | 0,625 | 0,459 | 0,461 | 132,8 ms |
| BM25 + BGE-M3 + RRF | 0,426 | 0,583 | 0,330 | 0,365 | 186,4 ms |
| Híbrido + BGE reranker v2-m3 | 0,667 | 0,722 | 0,654 | 0,615 | 10,2 s total |

O híbrido melhorou BM25 em nDCG@10 por +0,071 (IC 95% +0,004 a +0,144),
mas não superou o denso: delta -0,096 (IC 95% -0,222 a +0,032). O reranker
melhorou o híbrido por +0,250 (IC 95% +0,170 a +0,333) e o denso por +0,153
(IC 95% +0,059 a +0,258). Recall@5 também aumentou nos dois contrastes.

O reranker levou mediana de 10,0 s isoladamente e 10,2 s com retrieval; P95
total de 11,7 s. O pico do processo foi 3,97 GB de RAM. A medição ocorreu em
CPU no ambiente local, sem API ou modelo pago.

## Decisão antes do experimento fim a fim

1. BGE-M3 é a candidata simples sem reranker.
2. Híbrido + reranker avança como candidata comparativa de maior qualidade.
3. O reranker não vira padrão antes da latência fim a fim com geração e auditor.
4. O teste permanece selado até código, modelos, prompts e condições estarem
   definitivamente fixos.

## Experimento fim a fim v1

A primeira execução das quatro condições foi concluída em 17/09/2026. Nenhuma
configuração foi promovida: o melhor macro-F1 pontual foi 0,446 e as condições
auditadas tiveram recall zero para `MISLEADING`. A análise, as latências e a
taxonomia inicial de erros estão em `END_TO_END_V1.md`.

Os arquivos `end_to_end_records.jsonl` e `end_to_end.json` preservam as 96 saídas
e o resumo vinculado ao checkpoint. Eles são diagnósticos de desenvolvimento,
não resultados confirmatórios no teste.

## Experimento fim a fim v2

A v2 alterou somente o extrator, conforme emenda prévia ao protocolo. BGE-M3 sem
auditor obteve macro-F1 0,577 e BGE-M3 com auditor, 0,528. O reranker não converteu
o ganho de ranking em classificação e permaneceu com recall zero de `MISLEADING`.

O relatório completo está em `END_TO_END_V2.md`. Os artefatos brutos são
`end_to_end_v2_records.jsonl`, `end_to_end_v2.json` e
`end_to_end_v1_v2_comparison.json`. O teste continua selado.

## Calibração do auditor v3

A v3 reutilizou integralmente extração, retrieval e geração densos da v2 e
executou novamente somente o auditor com objetivo restrito à fidelidade factual.
Ela falhou os gates pré-registrados: macro-F1 0,405, recall zero de `MISLEADING`
e delta pareado negativo contra o auditor v2 (IC 95% -0,212 a -0,024). Recall de
abstenção 0,708, citação relevante 0,542, falha técnica 0,010 e P95 de 11,6 s
passaram seus limites isolados, mas não compensaram a perda de qualidade.

O relatório completo está em `END_TO_END_V3_AUDITOR.md`; os artefatos brutos são
`end_to_end_v3_records.jsonl` e `end_to_end_v3.json`. A variante foi descartada,
o auditor v2 foi restaurado provisoriamente e o teste continua selado.

## Reprodução

Com o ambiente do projeto e os modelos já disponíveis localmente:

```powershell
python scripts/evaluate_lexical_baseline.py
python scripts/evaluate_development_retrieval.py
python scripts/evaluate_development_reranker.py
python scripts/evaluate_development_auditor_v3.py
```

Os scripts recusam sobrescrever resultados existentes sem `--overwrite`. Os
artefatos JSON preservam métricas, previsões/rankings, intervalos, identidade do
freeze, versões de modelo, latências e ambiente necessário à auditoria.

## Limitações

- Dataset pequeno, sintético e produzido no mesmo projeto.
- Apenas 30% dos itens tiveram segunda revisão independente.
- A unidade bootstrap por família reduz, mas não elimina dependências temáticas.
- Os julgamentos de retrieval dependem dos chunks humanos anotados e não cobrem
  todas as evidências potencialmente relevantes do corpus.
- A análise lexical demonstra risco de artefatos de redação; resultados finais
  devem ser descritos como validade interna neste benchmark, não eficácia geral.
- Validade externa e adequação das evidências ainda requerem discussão com o
  orientador, conforme o gate acadêmico da Fase 5.
