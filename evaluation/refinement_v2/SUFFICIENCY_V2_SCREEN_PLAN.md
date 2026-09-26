# Plano congelado — triagem do gate de suficiência v2

Data de registro: 26/09/2026. O plano e o código devem ser versionados antes da
primeira inferência do novo gate.

## Hipótese e mudança isolada

O gate original foi suficiente em apenas 10/36 casos conclusivos e em 0/12 casos
`MISLEADING`, embora tenha abstido corretamente nos 12 casos insuficientes. A
decisão direta apresentou o extremo oposto e absteve corretamente em apenas 1/12.

O gate v2 mantém uma única decisão binária antes do classificador, mas:

- apresenta os seis chunks como aliases curtos `E1` a `E6`, sem IDs longos;
- explicita que escopo restrito, incerteza ou associação temporal podem bastar para
  avaliar uma extrapolação de universalidade, certeza ou causalidade;
- preserva as regras de não usar ausência de menção, não inferir caso individual e
  não usar conhecimento externo.

Extração, BGE-M3 top 6, chunks, Qwen3-8B, temperatura e semente permanecem
congelados. Nesta triagem não haverá chamada ao classificador nem ao auditor.

## Referência binária e gates

Os 36 rótulos conclusivos têm referência `sufficient=true`; os 12 itens
`INSUFFICIENT_EVIDENCE`, `sufficient=false`. Todos os gates devem passar:

1. recall de suficiência nos 36 conclusivos ≥ 0,70;
2. recall de insuficiência nos 12 abstentivos ≥ 0,67;
3. recall de suficiência em `MISLEADING` ≥ 0,67;
4. chunk anotado selecionado em pelo menos 60% dos 36 conclusivos;
5. taxa de falha técnica ≤ 0,02;
6. P95 do gate ≤ 8 segundos.

Falhar qualquer gate encerra a hipótese sem classificação fim a fim. Passar todos
apenas autoriza reutilizar o checkpoint do gate em um experimento posterior, que
exigirá plano e commit próprios. Teste v1 e holdout v2 não serão carregados.

## Comando e saídas

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\screen_refinement_sufficiency_v2.py
```

- `evaluation/results/refinement_v2/sufficiency_v2_screen.jsonl`;
- `evaluation/results/refinement_v2/sufficiency_v2_screen.json`.
