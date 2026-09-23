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
- todos os itens ainda são `draft` e não representam decisão humana;
- nenhum holdout v2 foi criado ou aberto.

O desenho em matriz por família testa distinções difíceis dentro do mesmo assunto.
Ele não garante representatividade de notícias reais e pode conservar padrões de
redação sintética. As comparações deverão usar reamostragem por família, e não tratar
os 48 itens como observações independentes.

## Validação estrutural

```powershell
.\.venv\Scripts\python.exe scripts\validate_refinement_calibration.py
```

O comando confere referências no corpus local, equilíbrio entre classes, novidade de
famílias, rastreabilidade e permanência em rascunho. Ele não certifica que o rótulo ou
a evidência estejam semanticamente corretos.

## Revisão humana

O autor deve revisar os 48 itens pelo pacote `calibration/PRIMARY_REVIEW.md`, podendo
aprovar famílias inteiras e listar exceções. Somente depois disso será gerado um
snapshot com `status=reviewed`, `primary_label`, justificativa, responsável e data.
Um segundo humano distinto deverá receber uma seleção cega de ao menos 15 itens
(30% arredondados para cima), sem propostas, justificativas ou resultados do sistema.

O holdout de 32 itens só será construído depois que a candidata for escolhida e
congelada. Criá-lo agora permitiria que seu conteúdo influenciasse a implementação.
