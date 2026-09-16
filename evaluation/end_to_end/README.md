# Dataset fim a fim

Estado em 16/09/2026: benchmark **congelado** após autorização explícita do autor.
`items.jsonl` contém 160 itens revisados, 48 segundas revisões incorporadas, 22
decisões finais e zero exclusões. São 96 itens de desenvolvimento e 64 de teste;
as classes finais têm 40 `SUPPORTED`, 49 `REFUTED`, 31 `MISLEADING` e 40
`INSUFFICIENT_EVIDENCE`. O manifesto autoritativo é `freeze_manifest.json`.

`review_pool.jsonl` preserva o snapshot primário anterior à segunda revisão;
`items.jsonl` é agora o benchmark adjudicado. Os manifestos antigos continuam com
`test_frozen=false` porque descrevem etapas históricas, e não devem ser reescritos.
Os pareceres desidentificados estão em `independent_review/adjudication/`.

## Histórico do segundo humano

**Atualização:** o segundo humano já devolveu as 48 respostas. Não pedir nova revisão
integral. Consulte [retornos e limitações](independent_review/returns/README.md) e
o [pacote de adjudicação](independent_review/adjudication/TASKS.md). Há 16 divergências
e seis conferências adicionais, com ambos os julgamentos visíveis nesta etapa.
`independent_review/review_receipt.json` registra o recebimento e hashes, sem declarar
teste congelado. O texto abaixo descreve o procedimento usado para preparar a seleção.

Há 48 tarefas selecionadas de forma reproduzível: 12 por classe, sete de
desenvolvimento e cinco de teste por classe. Consulte
[independent_review/participant/README.md](independent_review/participant/README.md).

Entregar **somente a pasta participant** ao segundo anotador. O mapa de auditoria
`independent_review/selection_manifest.json`, este índice e o repositório público
contêm rótulos e não devem ser consultados por ele durante a anotação. Registrar
exposição prévia; o pacote sem respostas não certifica cegamento. O autor não
pode assumir as duas revisões.

O participante pode preencher `ANNOTATIONS.md` (mais simples) ou `tasks.jsonl`.
A seleção não cria respostas. Após o retorno, preservar rótulos originais,
calcular concordância/Cohen's kappa antes da adjudicação e resolver divergências.
Respostas discordantes ainda não adjudicadas devem permanecer separadas do dataset.

## Regras e validação

Reproduzir a concordância pré-adjudicação (somente leitura, sem LLM ou banco):

```powershell
.\.venv\Scripts\python.exe scripts\report_annotation_agreement.py
.\.venv\Scripts\python.exe scripts\report_annotation_agreement.py evaluation\end_to_end\independent_review\returns\round_001.jsonl
```

O primeiro comando usa a rodada revisada; o segundo reproduz a inicial. Ambos
usam `primary_label`, não decisões finais. Não interpretar kappa como acurácia
do sistema nem esconder a primeira rodada após o pedido de conferência documental.

Procedimento: [ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md).
Limitações: [REVIEW_INDEX.md](REVIEW_INDEX.md). O benchmark é inteiramente sintético,
correlacionado por famílias e precisa de auditoria com o orientador. Aprovação
assistida não comprova leitura independente de cada fonte ou especialização.
Quantidade não demonstra generalização para notícias reais nem desempenho de OCR.

```powershell
.\.venv\Scripts\python.exe scripts\validate_end_to_end_dataset.py
.\.venv\Scripts\python.exe scripts\validate_end_to_end_dataset.py --ready
```

O primeiro comando valida estrutura e referências ao corpus local. O segundo deve
aceitar o conjunto congelado. O aceite exige mínimo de 100 itens, 25 por classe,
split 60%/40%, famílias separadas, rótulos
originais preservados e segundo anotador em pelo menos 30%. O validador não
certifica identidade, cegamento ou pertinência semântica das evidências.

Não coletar mensagens reais do Telegram. Não incluir respostas de fact-checkers
no corpus quando originarem alegações de avaliação. Não usar erros do teste
congelado para ajustar prompts, modelos, limiares, retrieval ou reranker.
