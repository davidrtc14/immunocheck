# Refinamento de acurácia v3

## Estado

A candidata roteada com seleção hierárquica de citações passou os sete gates de
calibração, foi formalmente congelada e depois passou os oito gates da confirmação
documental em 26/09/2026. Ela está aprovada para integração controlada, mas ainda
permanece fora do bot até a Fase 9.

Resultado de calibração:

- macro-F1: 0,725, contra 0,430 da v1 no mesmo conjunto;
- delta: +0,295, IC percentil de 95% por família de +0,165 a +0,469;
- recall `MISLEADING`: 0,417;
- precisão de abstenção: 0,750;
- citação relevante por ID exato: 0,722;
- falha técnica: zero;
- P95: 18,72 s;
- gates aprovados: 7/7.

## Arquitetura candidata

```text
alegação + retrieval denso top 15
              ↓
       roteador estrutural
       ├─ simples → decisão direta top 6
       ├─ premissa-conclusão → decisão relacional top 15
       └─ evento específico sem âncora → abstenção
              ↓
       seleção inicial de documentos
              ↓
   expansão de chunks no mesmo documento
              ↓
       seleção final de até 3 citações
```

O resultado completo está em `HIERARCHICAL_CITATION_RESULTS.md`; a configuração e
os hashes imutáveis estão em `CANDIDATE_FREEZE.md`. Os experimentos intermediários
permanecem documentados para que a trajetória não seja confundida com uma única
tentativa bem-sucedida.

## Confirmação

Em 32 itens e oito famílias novas, a v3 obteve macro-F1 0,846 contra 0,482 da v1,
recall `MISLEADING` 0,625, precisão de abstenção 1,000, citação exata 0,833, falha
zero e P95 19,35 s. Todos os oito gates passaram. Consulte
`confirmatory/RESULTS.md` e os artefatos estruturados em
`evaluation/results/refinement_v3/`.

## Limite metodológico

O valor 0,725 não é resultado final nem estimativa de uso público. A arquitetura foi
desenvolvida observando erros dos 48 itens de calibração, cuja matriz sintética por
família também pode favorecer o roteamento. A confirmação usa 32 itens, oito por
classe, famílias ausentes da calibração e do teste v1 e execução única após o
congelamento. O gabarito foi curado pelo pesquisador com apoio de IA e evidências do
corpus; não possui validação clínica independente nem concordância entre anotadores.
