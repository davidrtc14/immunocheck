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

Esta implementação ainda não foi executada sobre os 48 itens candidatos. Os rótulos
continuam sendo propostas do agente, pendentes de revisão humana. Não há alegação de
ganho de acurácia e a v1 não foi promovida, substituída ou reavaliada.

O novo gate acrescenta uma chamada à LLM e pode elevar a latência. Qualidade,
abstenção, regressões e custo só serão medidos depois da revisão do conjunto de
calibração, sob os gates pré-registrados. O auditor factual já falhou quando testado
isoladamente na v1; sua presença aqui é uma hipótese condicionada à separação dos
estágios, não evidência de melhoria.
