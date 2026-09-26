# Plano pré-experimental — roteamento estrutural v3

Data de registro: 26/09/2026.

## Hipótese

Os experimentos anteriores revelaram especialistas complementares: a decisão direta
foi sensível a alegações sustentadas e refutadas; a decisão relacional reconheceu
conteúdo enganoso e preservou melhor a abstenção. Selecionar o especialista pela
forma da alegação deve evitar que a mesma instrução tente resolver relações distintas.

## Roteamento congelado

Uma chamada local, baseada somente no texto da alegação e sem acesso ao rótulo ou às
evidências anotadas, escolherá exatamente uma rota:

- `GENERAL_SIMPLE` → saída já registrada do decisor direto denso top 6;
- `PREMISE_CONCLUSION` → saída já registrada do decisor relacional denso top 15;
- `UNANCHORED_SPECIFIC_EVENT` → abstenção determinística sem fonte conclusiva.

O roteador classifica estrutura, não veracidade. Uma frase longa ou com quantificador
continua simples se possuir uma única proposição central. Premissa-conclusão exige
duas proposições separáveis e uma relação explícita de razão, prova ou resultado.
Evento específico exige atribuição a pessoa, campanha, unidade ou ocorrência sem
âncora documental pública.

## Execução, latência e gates

As saídas dos dois especialistas serão reutilizadas sem novas chamadas. A latência
do roteador será somada à latência previamente medida da rota selecionada; na
abstenção, será somada ao estágio compartilhado de extração e retrieval. Falha do
roteador produz abstenção e conta como falha técnica.

Aplicam-se os mesmos sete gates: delta de macro-F1 ≥ 0,08, recall `MISLEADING` ≥
0,40, precisão de abstenção ≥ 0,45, citação relevante ≥ 0,60, queda máxima de recall
por classe ≤ 0,05, falha técnica ≤ 0,02 e P95 ≤ 20 s. Teste final e holdout não serão
carregados.

Esta é uma exploração na calibração já observada. Passar os gates autoriza apenas
congelar a candidata e construir um conjunto confirmatório novo, com revisão humana;
não comprova validade externa nem autoriza implantação pública.
