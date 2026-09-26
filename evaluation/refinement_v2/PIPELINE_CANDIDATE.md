# Candidata de pipeline separada

Data de implementação estrutural: 22/09/2026.

## Fluxo experimental

```text
entrada → extração → retrieval denso
                    ↓
              gate de suficiência
              ├─ insuficiente → abstenção + fontes parciais válidas
              └─ suficiente → subconjunto de evidências pertinentes
                                   ↓
                         classificador conclusivo
                   SUPPORTED | REFUTED | MISLEADING
                                   ↓
                         auditor de fidelidade
                                   ↓
                               resposta
```

O gate decide apenas se há cobertura documental suficiente. Uma contradição direta
também é suficiente; portanto, `sufficient=true` não significa que a alegação seja
verdadeira. O classificador não pode devolver `INSUFFICIENT_EVIDENCE`, pois a
abstenção pertence exclusivamente ao estágio anterior. O auditor verifica fatos,
citações e orientação médica individual, sem atuar como segundo classificador.

## Invariantes implementadas

- A candidata é opt-in por `build_refinement_text_pipeline` ou
  `build_refinement_multimodal_pipeline`; os builders usados pelo bot continuam na v1.
- IDs selecionados pelo gate precisam pertencer ao conjunto recuperado.
- Somente evidências selecionadas como pertinentes chegam ao classificador.
- Gate insuficiente interrompe o fluxo antes da classificação.
- Gate suficiente sem fonte, fonte inventada ou citação inválida falha de forma segura.
- Fontes parciais válidas podem acompanhar a abstenção sem serem apresentadas como
  sustentação de um veredito conclusivo.
- O auditor factual pode bloquear conteúdo não sustentado, mas não escolhe outro rótulo.

## Estado experimental

Esta implementação foi executada nos 48 itens adjudicados em 26/09/2026. A candidata
sem auditor obteve macro-F1 0,373 contra 0,430 da v1, recall zero de `MISLEADING` e
38 abstenções. Cinco dos sete gates falharam; por isso o auditor factual não foi
executado e a candidata não foi promovida.

O novo gate acrescentou uma chamada à LLM e elevou o P95 para 14,74 s, ainda dentro
do limite de 20 s. Seu problema dominante foi semântico, não operacional: tratou
como insuficientes 38 dos 48 itens e reduziu o recall de `REFUTED` em 0,50. Os
artefatos completos estão em `evaluation/results/refinement_v2/`.
