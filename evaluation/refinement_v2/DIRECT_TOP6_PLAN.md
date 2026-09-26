# Plano congelado — decisão direta densa top 6

Data de registro: 26/09/2026. Este plano deve ser versionado antes da primeira nova
inferência da iteração.

## Hipótese

Na candidata separada top 20, a evidência anotada estava presente no retrieval de
9/12 casos `MISLEADING`, mas nenhum chunk anotado foi preservado pelo gate. Dez
casos foram abstidos e dois classificados como `REFUTED`. A hipótese é que o gate
de suficiência, e não apenas o retrieval, esteja bloqueando a fronteira semântica.

A candidata usa o gerador direto já existente, capaz de escolher entre as quatro
classes, sem gate anterior e sem auditor posterior. Permanecem congelados:

- extração da fase A;
- BGE-M3 denso top 6 e exatamente os mesmos IDs recuperados na fase A;
- `qwen3:8b`, temperatura 0 e semente 42;
- prompt e schema do `LLMVerdictGenerator` existente;
- snapshot adjudicado e baseline v1 auditada.

Não há prompt novo nem ajuste orientado por item. A mudança lógica em relação à
baseline é retirar o auditor; em relação à v2 separada, é substituir gate +
classificador conclusivo pelo gerador direto de quatro classes.

## Condições e isolamento

1. `v1_dense_with_auditor`: saída congelada do checkpoint da fase A;
2. `v2_direct_dense_top6_no_auditor`: extração e retrieval reutilizados, com uma
   nova chamada apenas ao gerador direto.

Nenhum item do teste v1 ou do holdout v2 será carregado. O holdout v2 continua
inexistente. O checkpoint será incremental.

## Gates

São os mesmos sete gates das iterações anteriores:

- delta de macro-F1 sobre a v1 ≥ 0,08;
- recall de `MISLEADING` ≥ 0,40;
- precisão de abstenção ≥ 0,45;
- taxa de citação relevante ≥ 0,60;
- queda de recall de qualquer classe ≤ 0,05;
- falha técnica ≤ 0,02;
- P95 textual ≤ 20 segundos.

O auditor factual não integra esta candidata. Falhar qualquer gate impede sua
promoção e a criação do holdout. Passar todos os gates apenas autoriza congelar a
candidata e construir um holdout novo; não constitui confirmação externa.

## Comando e saídas

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\evaluate_refinement_direct_top6.py
```

- `evaluation/results/refinement_v2/calibration_direct_top6.jsonl`;
- `evaluation/results/refinement_v2/calibration_direct_top6.json`.
