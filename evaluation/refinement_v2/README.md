# Refinamento de acurácia v2

Este diretório inicia uma linha experimental independente da avaliação definitiva da
v1. O teste antigo não pode ser usado para escolher alterações. O arquivo
`FROZEN_TEST_FAMILIES.txt` contém apenas os identificadores das 16 famílias do teste
v1, necessários para impedir reutilização; ele não contém alegações, rótulos ou
resultados.

## Estado atual

- 48 propostas de calibração, 12 por classe e 12 famílias novas;
- quatro propostas por família, uma para cada veredito;
- 24 chunks distintos de evidência em 12 documentos do corpus;
- as 48 propostas originais permanecem preservadas como `draft`;
- a primeira revisão assistida aprovou os 48 itens sem exceções e foi incorporada
  em um snapshot separado com `status=reviewed`;
- o retorno final declara conferência direta das fontes nas 12 famílias; essa
  declaração e o papel informado do revisor são preservados, mas não certificados
  pelo software;
- uma segunda anotação cega balanceada de 16 itens foi preparada, mas ainda não
  foi preenchida;
- nenhum holdout v2 foi criado ou aberto.

O desenho em matriz por família testa distinções difíceis dentro do mesmo assunto.
Ele não garante representatividade de notícias reais e pode conservar padrões de
redação sintética. As comparações deverão usar reamostragem por família, e não tratar
os 48 itens como observações independentes.

## Validação estrutural

```powershell
.\.venv\Scripts\python.exe scripts\validate_refinement_calibration.py
.\.venv\Scripts\python.exe scripts\validate_refinement_calibration.py `
  --dataset evaluation/refinement_v2/calibration/reviewed_items.jsonl `
  --status reviewed
```

Os comandos conferem referências no corpus local, equilíbrio entre classes, novidade
de famílias, rastreabilidade e o estágio declarado. Eles não certificam que o rótulo
ou a evidência estejam semanticamente corretos.

## Revisão humana

A revisão primária está preservada em `calibration/reviews/`, ligada por hash ao
snapshot `calibration/reviewed_items.jsonl`. O retorno declara consulta direta às 12
fontes, sem divergências; identidade e atividade declaradas não são certificadas pelo
software. A reconciliação técnica delimita duas expressões e separa os 36 rótulos
conclusivos dos 12 casos cuja insuficiência decorre da ausência de contexto
individual. Um segundo humano distinto deve receber **somente** a pasta
`calibration/independent_review/participant/`; o manifesto de seleção contém o mapa
de auditoria e não pode ser compartilhado antes da devolução.

O holdout de 32 itens só será construído depois que a candidata for escolhida e
congelada. Criá-lo agora permitiria que seu conteúdo influenciasse a implementação.
