# Plano congelado — calibração v2.1, retrieval denso top 20

Data de registro: 26/09/2026. Este plano deve ser versionado antes da primeira
inferência da iteração v2.1.

## Hipótese e mudança isolada

O diagnóstico da fase A encontrou evidência anotada no top 6 denso para 58,3% dos
36 itens conclusivos e no top 20 para 72,2%. A hipótese é que disponibilizar os
20 trechos ao gate de suficiência reduza abstensões indevidas sem degradar as
demais classes.

A única mudança em relação a `v2_separated_no_auditor` será:

- BGE-M3 denso: `top_k=6` → `top_k=20`.

Permanecem congelados o snapshot adjudicado, as alegações já extraídas na fase A,
o modelo `qwen3:8b`, os prompts de suficiência e classificação conclusiva,
temperatura 0, semente 42 e a ausência de auditor pós-geração. A baseline v1 será
copiada sem alteração do checkpoint da fase A. Não haverá nova extração por LLM.

## Dados e isolamento

- snapshot: `calibration/adjudicated_items.jsonl`;
- SHA-256: `9cd26e96b7d5ee35ddb32ebf7a36914b3349db81c3e21d4f4476cf4cf66e09f8`;
- 48 itens, 12 por classe e 12 famílias exclusivas de calibração;
- checkpoint da fase A será usado somente para reutilizar a extração e a baseline;
- nenhum item do teste v1 ou do holdout v2 será carregado;
- o holdout v2 ainda não existe.

## Condições pareadas

1. `v1_dense_with_auditor`: saída congelada da baseline da fase A;
2. `v2_separated_dense_top20_no_auditor`: mesma candidata separada, agora com os
   20 primeiros trechos do BGE-M3 denso.

## Métricas e decisão

Serão reutilizados, sem alteração, os sete gates da fase A:

- delta de macro-F1 sobre a v1 ≥ 0,08;
- recall de `MISLEADING` ≥ 0,40;
- precisão de abstenção ≥ 0,45;
- taxa de citação relevante ≥ 0,60;
- queda de recall de qualquer classe ≤ 0,05;
- falha técnica ≤ 0,02;
- P95 textual ≤ 20 segundos.

Também serão reportados balanced accuracy, métricas por classe, matriz de confusão,
latência e bootstrap pareado por família com 2.000 reamostragens. O relatório
comparará descritivamente a candidata top 20 à candidata top 6, mas a promoção
continua condicionada aos sete gates contra a baseline congelada.

Para evitar repetir a chamada de extração, a latência fim a fim usará como proxy o
tempo compartilhado da fase A (extração + retrieval top 6) somado às novas chamadas
do gate e do classificador. O retrieval top 20 será medido também em campo separado,
mas não será somado ao proxy, pois ele substitui — em vez de complementar — o
retrieval top 6 já incluído. Essa aproximação e sua limitação serão preservadas no
relatório.

Falhar qualquer gate impede a execução do auditor factual e a promoção. Como esta
hipótese nasceu do diagnóstico dos mesmos 48 itens, um resultado positivo ainda
exigirá confirmação posterior no holdout v2 antes de qualquer substituição da v1.

## Comando

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\evaluate_refinement_top20.py
```

Saídas previstas: `evaluation/results/refinement_v2/calibration_top20.jsonl` e
`evaluation/results/refinement_v2/calibration_top20.json`.
