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
