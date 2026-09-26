# Plano congelado — calibração v2, fase A

Data de registro: 26/09/2026. Este plano deve ser versionado antes da primeira
inferência nos 48 itens adjudicados.

## Dados e isolamento

- snapshot: `calibration/adjudicated_items.jsonl`;
- SHA-256: `9cd26e96b7d5ee35ddb32ebf7a36914b3349db81c3e21d4f4476cf4cf66e09f8`;
- 48 itens, 12 por classe e 12 famílias exclusivas de calibração;
- nenhum item do teste v1 ou do holdout v2 será carregado;
- o holdout v2 ainda não existe.

## Condições pareadas

1. `v1_dense_with_auditor`: gerador de quatro classes e auditor v2 da configuração
   definitiva da v1, com BGE-M3 denso top 6;
2. `v2_separated_no_auditor`: gate de suficiência seguido do classificador restrito
   a `SUPPORTED`, `REFUTED` e `MISLEADING`, com o mesmo BGE-M3 denso top 6 e sem
   auditor pós-geração.

Para cada item, extração e retrieval serão executados uma vez e compartilhados entre
as condições. O modelo será `qwen3:8b` local, temperatura 0 e semente 42. O checkpoint
é incremental e validado como prefixo ordenado do snapshot.

## Métricas e decisão

Serão reportados macro-F1, balanced accuracy, precisão/recall/F1 por classe,
abstenção, interseção de citações, falhas técnicas, mediana/P95 e bootstrap pareado
por família com 2.000 reamostragens.

O auditor factual da fase B só poderá ser executado se **todos** os gates abaixo
forem satisfeitos pela condição 2:

- delta de macro-F1 sobre a v1 ≥ 0,08;
- recall de `MISLEADING` ≥ 0,40;
- precisão de abstenção ≥ 0,45;
- taxa de citação relevante ≥ 0,60;
- queda de recall de qualquer classe ≤ 0,05;
- falha técnica ≤ 0,02;
- P95 textual ≤ 20 segundos.

Falhar qualquer gate encerra a hipótese desta candidata sem executar a fase B. Não
serão feitos ajustes orientados por estes 48 resultados; uma nova hipótese exigirá
novo registro e separação metodológica explícita.

## Comando

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\evaluate_refinement_calibration.py
```

Saídas previstas: `evaluation/results/refinement_v2/calibration_phase_a.jsonl` e
`evaluation/results/refinement_v2/calibration_phase_a.json`.

