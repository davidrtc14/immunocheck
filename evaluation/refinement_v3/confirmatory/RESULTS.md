# Resultado confirmatório da candidata v3

Data da execução única: 26/09/2026.

## Decisão

**Aprovada para integração controlada ao protótipo acadêmico.** A candidata roteada
com citações hierárquicas passou os oito gates pré-registrados em 32 itens de oito
famílias novas. Isso encerra a Fase 8, mas não equivale a validação clínica nem
autoriza implantação pública.

O conjunto e o protocolo foram congelados no commit `43838ec`; o executor foi
versionado no commit `c9065a8`. O teste final histórico da v1 não foi carregado.

## Resultado principal

| Métrica | v1 | v3 | Resultado v3 |
|---|---:|---:|---:|
| Acurácia | 0,531 | 0,844 | 27/32 |
| Macro-F1 | 0,482 | 0,846 | +0,364 |
| Recall `SUPPORTED` | 0,875 | 1,000 | 8/8 |
| Recall `REFUTED` | 0,500 | 0,875 | 7/8 |
| Recall `MISLEADING` | 0,000 | 0,625 | 5/8 |
| Recall `INSUFFICIENT_EVIDENCE` | 0,750 | 0,875 | 7/8 |
| Precisão de abstenção | 0,333 | 1,000 | 7/7 abstenções corretas |
| Citação por ID exato nos conclusivos | 0,667 | 0,833 | 20/24 |
| Falha técnica | 0,000 | 0,000 | 0/32 |
| Latência mediana | 9,95 s | 13,78 s | — |
| Latência P95 | 12,09 s | 19,35 s | — |

O intervalo percentil de 95% do ganho pareado de macro-F1, com reamostragem por
família, foi de **+0,192 a +0,540**. A matriz de confusão da v3, nas linhas
`SUPPORTED`, `REFUTED`, `MISLEADING` e `INSUFFICIENT_EVIDENCE`, foi:

```text
[[8, 0, 0, 0],
 [0, 7, 1, 0],
 [0, 3, 5, 0],
 [0, 1, 0, 7]]
```

## Gates

| Gate | Limite | Observado | Estado |
|---|---:|---:|---|
| Macro-F1 absoluto | >= 0,60 | 0,846 | passou |
| Ganho de macro-F1 sobre v1 | >= 0,08 | +0,364 | passou |
| Recall `MISLEADING` | >= 0,40 | 0,625 | passou |
| Precisão de abstenção | >= 0,45 | 1,000 | passou |
| Citação exata | >= 0,60 | 0,833 | passou |
| Queda máxima de recall por classe | <= 0,05 | nenhuma queda | passou |
| Falha técnica | <= 0,02 | 0,000 | passou |
| P95 textual | <= 20 s | 19,35 s | passou |

## Auditoria dos cinco erros

| Item | Esperado | Previsto | Diagnóstico |
|---|---|---|---|
| `0016` | `REFUTED` | `MISLEADING` | o conector “portanto” induziu rota relacional apesar de ambas as partes serem refutadas |
| `0017` | `MISLEADING` | `REFUTED` | a premissa sobre resíduos não foi preservada pelo roteador direto |
| `0020` | `MISLEADING` | `REFUTED` | confundiu exagero de risco absoluto com falsidade integral |
| `0023` | `MISLEADING` | `REFUTED` | perdeu a validade contextual da premissa sobre BCG |
| `0031` | `INSUFFICIENT_EVIDENCE` | `REFUTED` | não reconheceu o adolescente com tuberculose como evento individual sem âncora |

Não haverá correção orientada por esses cinco itens na candidata confirmada. Eles
podem motivar uma versão posterior somente com outro conjunto de desenvolvimento.

## Auditoria de citações

Houve acerto de ID exato em 20 dos 24 itens conclusivos. Em 23/24 havia ao menos
um trecho do mesmo documento anotado. Três dos quatro misses exatos apontaram para
outros chunks do mesmo documento ou para documentos diretamente pertinentes; a
métrica oficial permanece a conservadora por ID exato e não foi recalculada.

## Limitações

- o conjunto tem apenas 32 alegações sintéticas e balanceadas;
- o gabarito foi construído pelo pesquisador com apoio de IA e evidência do corpus;
- não houve especialista externo, segunda anotação ou concordância entre avaliadores;
- as famílias são novas, mas a estrutura das quatro classes ainda pode favorecer o
  roteamento;
- a margem do P95 para o gate de 20 segundos é pequena;
- o resultado sustenta um protótipo de TCC, não um serviço clínico ou público.

Artefatos estruturados:

- `evaluation/results/refinement_v3/confirmatory.json`;
- `evaluation/results/refinement_v3/confirmatory.jsonl`.
