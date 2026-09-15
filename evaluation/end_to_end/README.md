# Dataset fim a fim

Este diretório receberá `items.jsonl`, com uma alegação por linha no formato de
`item_template.json`. O template é estrutural e não constitui um item anotado.

## Regras de construção

1. Reescrever alegações públicas sem nomes, perfis ou identificadores.
2. Manter cada item atômico: uma proposição verificável por vez.
3. Não copiar a resposta de fact-checkers para o corpus de conhecimento.
4. Registrar origem apenas para rastreabilidade; a origem da alegação não é evidência.
5. Rótulos conclusivos exigem chunks que sustentem diretamente a anotação.
6. `INSUFFICIENT_EVIDENCE` não recebe `evidence_chunk_ids` conclusivos.
7. O anotador principal revisa 100%; um segundo anotador revisa ao menos 30%.
8. Divergências de rótulo exigem adjudicação registrada.
9. O split de teste será congelado antes do ajuste final e não poderá orientar prompts,
   limiares ou hiperparâmetros.
10. Preservar `primary_label` e `second_label` antes da adjudicação; `label` é final.
11. Não separar a mesma `claim_family` entre desenvolvimento e teste.

O procedimento e os critérios de rótulo estão em `ANNOTATION_GUIDE.md`.
O primeiro lote está em `batches/batch_001.md`: 12 propostas sintéticas de
desenvolvimento, ainda sem revisão humana. Ele não é `items.jsonl` definitivo.

Validação estrutural desse lote contra o corpus local:

```powershell
.\.venv\Scripts\python.exe scripts\validate_end_to_end_dataset.py evaluation\end_to_end\batches\batch_001.jsonl
```

`--ready` deve recusá-lo enquanto houver rascunhos. O aceite exige mínimo de 100
itens, pelo menos 25 por classe, split estratificado 60%/40%, famílias separadas,
rótulos originais preservados e segunda revisão em pelo menos 30%.

Validação durante a construção:

```powershell
python scripts/validate_end_to_end_dataset.py
```

Validação dos critérios mínimos antes de congelar o teste:

```powershell
python scripts/validate_end_to_end_dataset.py --ready
```

O validador rejeita IDs e alegações duplicados, chunks inexistentes, revisões
incompletas, conclusões sem evidência e divergências sem adjudicação.
Também rejeita o mesmo identificador nas duas revisões. Isso não certifica a
independência humana nem a pertinência semântica das evidências.
