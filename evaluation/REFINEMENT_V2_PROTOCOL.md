# Protocolo de refinamento da acurácia v2

Data de registro: 22/09/2026.

## Objetivo e separação da v1

A avaliação definitiva da v1 permanece encerrada e imutável. Seus 64 itens de teste,
previsões e erros não poderão ser usados para selecionar prompt, modelo, retrieval,
auditor, limiar ou regra da v2. O resultado da v1 serve apenas para motivar uma nova
hipótese e permanece como evidência histórica do protótipo entregue.

A v2 será desenvolvida com dados novos. Nenhuma execução da v2 poderá carregar a
partição `test` do benchmark congelado em 16/09/2026.

## Hipótese principal

Separar três decisões hoje acopladas deve reduzir abstenções indevidas e preservar a
classe `MISLEADING`:

1. suficiência e pertinência da evidência recuperada;
2. classificação da relação entre alegação e evidência;
3. fidelidade factual da explicação e das citações.

O auditor não deve funcionar como segundo classificador nem converter discordância de
rótulo em abstenção. Ele deve bloquear somente afirmações factuais não sustentadas,
inconsistência estrutural, citação inválida ou orientação médica individual.

## Dados novos obrigatórios

- Conjunto de calibração: mínimo de 48 itens, 12 por classe e pelo menos 12 famílias
  inéditas em relação ao teste da v1.
- Holdout independente: mínimo de 32 itens, oito por classe e famílias ausentes da
  calibração e do teste da v1.
- Alegações sintéticas ou públicas, sem mensagens de usuários e sem dados pessoais.
- Evidências vinculadas a chunks do corpus por identificadores verificáveis.
- Revisão humana primária em 100% e segunda revisão em pelo menos 30%.
- Nenhum item do holdout pode ser aberto antes do congelamento da candidata.

## Diagnóstico permitido da v1

A auditoria automatizada pode usar somente as 96 saídas de desenvolvimento da v1 para
descrever gargalos agregados. Ela não autoriza uma quarta calibração nesses itens. Os
64 registros de teste não serão carregados pela ferramenta de diagnóstico.

## Condições da calibração v2

1. configuração congelada da v1 executada no novo conjunto, como baseline;
2. candidata com gate explícito de suficiência de evidência e classificador separado;
3. candidata anterior acrescida de auditor restrito à fidelidade, somente se a condição
   2 superar o baseline sem perda material de segurança.

Retrieval, top-k e modelo serão mantidos inicialmente. Cada alteração posterior deverá
mudar um componente por vez e produzir artefato separado.

## Métricas e gates de promoção

- Macro-F1 e balanced accuracy com bootstrap por família.
- Precisão, recall e F1 por classe, com destaque para `MISLEADING`.
- Precisão, recall e F1 da abstenção.
- Taxa de citação com interseção nas evidências anotadas.
- Regressões e recuperações provocadas pelo auditor.
- Falhas técnicas, mediana e P95 de latência.

Uma candidata só poderá avançar ao novo holdout se, na calibração:

- melhorar macro-F1 em pelo menos 0,08 sobre a v1 no mesmo conjunto novo;
- atingir recall de `MISLEADING` de pelo menos 0,40;
- atingir precisão de abstenção de pelo menos 0,45;
- atingir taxa de citação relevante de pelo menos 0,60;
- não reduzir o recall de nenhuma classe em mais de 0,05;
- manter falha técnica em no máximo 0,02 e P95 textual em até 20 segundos.

Os limites são gates de engenharia para este protótipo e não prova de eficácia clínica
ou validade externa.

## Execução confirmatória

Depois de fixar código, prompts, modelos, corpus e hashes, o holdout novo será executado
uma única vez. Qualquer melhoria posterior constituirá outra versão e exigirá novo
holdout. O teste da v1 continuará preservado e não será reexecutado.
