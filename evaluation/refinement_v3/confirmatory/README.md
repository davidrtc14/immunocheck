# Conjunto confirmatório v3

Este diretório contém um teste novo e fechado da candidata descrita em
`../CANDIDATE_FREEZE.md`.

- `items.jsonl`: 32 alegações com gabarito documental pré-execução;
- `PROTOCOL.md`: regras, limitações e gates registrados antes da inferência;
- `manifest.json`: hashes preenchidos e congelados antes da execução;
- `RESULTS.md`: criado somente depois da avaliação única;
- resultados estruturados ficam em `evaluation/results/refinement_v3/confirmatory.*`.

O campo `reviewer` informa `project_researcher_ai_assisted` para não confundir a
curadoria documental com revisão independente ou parecer de especialista.
