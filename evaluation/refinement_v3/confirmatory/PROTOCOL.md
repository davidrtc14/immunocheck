# Protocolo confirmatório pragmático da candidata v3

## Objetivo

Medir, uma única vez, a candidata v3 congelada em alegações e famílias ausentes da
calibração v2 e do teste final da v1. O teste histórico da v1 não será reaberto.

## Construção do gabarito

- 32 itens, oito por classe e oito famílias com um item de cada classe;
- alegações conclusivas derivadas de trechos identificados no corpus versionado;
- `INSUFFICIENT_EVIDENCE` reservado a casos específicos sem informação suficiente;
- rótulo, justificativa e IDs de evidência definidos antes de qualquer inferência;
- curadoria feita pelo pesquisador com apoio de IA e verificação documental;
- nenhuma revisão clínica, segunda anotação ou validação por especialista é alegada.

Essa simplificação é proporcional a um protótipo de TCC e será registrada como
limitação. O conjunto não deve ser descrito como benchmark clínico validado.

## Separação e imutabilidade

As famílias e as formulações são novas. O arquivo `items.jsonl`, este protocolo e o
manifesto devem ser commitados antes da execução. Depois disso, não se alteram
gabarito, candidata, corpus, modelo ou índices. Uma mudança invalida o caráter
confirmatório e passa a constituir nova iteração de desenvolvimento.

## Critérios mínimos pré-registrados

A candidata é satisfatória para o protótipo acadêmico se, simultaneamente:

- macro-F1 absoluto >= 0,60;
- ganho de macro-F1 sobre a v1 >= 0,08;
- recall de `MISLEADING` >= 0,40;
- precisão de `INSUFFICIENT_EVIDENCE` >= 0,45;
- citações exatas em itens conclusivos >= 0,60;
- queda máxima de recall por classe contra a v1 <= 0,05;
- falha técnica <= 0,02;
- P95 textual <= 20 segundos no computador-alvo.

O resultado deve apresentar matriz de confusão, métricas por classe, mediana, P95 e
intervalo bootstrap por família. Se algum gate falhar, a v3 não substitui a v1; os
erros podem orientar uma v4, mas o mesmo conjunto deixa de ser confirmatório.
