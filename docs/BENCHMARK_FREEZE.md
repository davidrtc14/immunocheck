# Congelamento do benchmark fim a fim — 16/09/2026

O benchmark foi congelado após autorização explícita do autor do projeto para
incorporar os 22 pareceres, aplicar a reestratificação aprovada, publicar os
registros humanos desidentificados e congelar o conjunto de teste.

## Identidades

- Snapshot primário preservado: `b3e587898c71c48995fa7c06a3e42c67a022e7bba54147ea78c694dc09401f73`.
- Dataset congelado: `5caabdab9347c13dd270e6a335599dc5e213f5ad814312f6bcdf45731a67a5bf`.
- Congelamento: `sha256:a352d9f93032b87652b38ffea2b855cef393bd822f04142dbfbd5830ad609666`.
- Corpus: `sha256:d6cb49e72edbe28e0958b1e8be440e655c93c972af78383121c04687f2d984a7`.

O arquivo `evaluation/end_to_end/freeze_manifest.json` contém os hashes de todos
os registros vinculados. `review_pool.jsonl` é o snapshot primário; `items.jsonl`
é o benchmark final. Manifestos anteriores com `test_frozen=false` são históricos.

## Composição final

- 160 itens revisados; 48 com segunda anotação e 22 decisões registradas.
- 96 itens de desenvolvimento e 64 de teste.
- Classes: 40 `SUPPORTED`, 49 `REFUTED`, 31 `MISLEADING` e 40
  `INSUFFICIENT_EVIDENCE`.
- Nenhuma família cruza os splits.
- Oito itens mudaram de split por uma troca de duas famílias completas, sem usar
  previsões ou métricas do ImmunoCheck.

## Regra após o congelamento

Desenvolvimento, seleção de modelo, prompts, retrieval, reranker e limiares devem
usar somente o split `development`. O split `test` pode ser executado apenas na
avaliação definitiva planejada; seus erros não podem alimentar ajustes posteriores.
Qualquer correção futura do benchmark deve gerar nova versão, justificativa, hashes
e declaração explícita de que o teste anterior deixou de ser comparável.

## Limitações preservadas

O benchmark é sintético e pode conter atalhos lexicais. A identidade, competência
e independência dos anotadores são autodeclaradas e não certificadas por software.
A triagem semântica assistida por IA foi aceita pelo autor, mas o parecer do
orientador sobre validade externa e evidências permanece necessário para o TCC.

## Reprodução

```powershell
.\.venv\Scripts\python.exe scripts\validate_end_to_end_dataset.py --ready
.\.venv\Scripts\python.exe -c "from pathlib import Path; from immunocheck.evaluation.benchmark_freeze import validate_freeze_manifest; print(validate_freeze_manifest(root=Path('evaluation/end_to_end'))['freeze_id'])"
```
