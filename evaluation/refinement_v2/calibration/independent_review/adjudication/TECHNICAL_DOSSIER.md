# Dossiê técnico pré-adjudicação

Estado: **adjudicação humana concluída em 26/09/2026**.

Este documento analisa os três desacordos remanescentes da devolução de `rv0067`.
A correção da tarefa 010 preservou o texto original e passou a concordar com o
rótulo primário (`INSUFFICIENT_EVIDENCE`), portanto ela não exige adjudicação. O
resultado pré-adjudicação final é 13/16 (81,25%), com kappa de Cohen 0,75.

## Critério de classes aplicado

- `REFUTED`: a proposição central é diretamente contradita pela evidência, sem parte
  factual relevante que precise ser preservada.
- `MISLEADING`: existe uma parte factual relevante sustentada, mas contexto, alcance
  ou inferência foram materialmente distorcidos.
- `INSUFFICIENT_EVIDENCE`: faltam informações para sustentar ou contradizer com
  segurança o caso específico; não equivale a falso.

## ref2-annotation-003 / ref2-cal-0007

**Alegação:** O registro de uma convulsão após a vacina mpox confirmou que a vacina
foi a causa do evento.

- Rótulo primário: `MISLEADING`.
- Rótulo secundário: `REFUTED`.
- Evidência decisiva: `ms_mpox_seguranca_2025:p2:c3:0adbf3f2c967`.
- Achado sustentado: a convulsão ocorreu 48 horas após a vacina.
- Limite causal: o caso foi classificado como B2/indeterminado, com diagnósticos
  diferenciais não investigados e descartados.
- Recomendação técnica: **`MISLEADING`**. A alegação preserva um evento e uma relação
  temporal reais, mas converte causalidade indeterminada em confirmação. Rotulá-la
  apenas como refutada apagaria a parte factual sustentada.

## ref2-annotation-011 / ref2-cal-0003

**Alegação:** Como aumentaram as notificações de hipersensibilidade após a vacina
contra dengue, ficou provado que toda reação notificada foi causada pelo imunizante.

- Rótulo primário: `MISLEADING`.
- Rótulo secundário: `REFUTED`.
- Evidências decisivas: `ms_dengue_seguranca_2025:p2:c1:e817446a7a7a` e
  `ms_dengue_seguranca_2025:p2:c3:f0d46e38fe04`.
- Achado sustentado: houve aumento das notificações de hipersensibilidade e anafilaxia.
- Limite causal: Esavi é ocorrência temporalmente associada e não possui
  necessariamente relação causal; uma notificação pode gerar múltiplos pares.
- Recomendação técnica: **`MISLEADING`**. A premissa sobre o sinal de notificação é
  verdadeira, enquanto “toda reação” e causalidade comprovada são generalizações
  indevidas.

## ref2-annotation-012 / ref2-cal-0048

**Alegação:** A coqueluche de um adolescente vacinado ocorreu porque a dose de
reforço aplicada nele não produziu imunidade.

- Rótulo primário: `INSUFFICIENT_EVIDENCE`.
- Rótulo secundário: `MISLEADING`.
- Evidência conclusiva associada: nenhuma; o item é um cenário sintético individual.
- Informação ausente: confirmação diagnóstica, histórico vacinal, intervalo desde a
  dose, resposta imune e investigação de causas alternativas.
- Recomendação técnica: **`INSUFFICIENT_EVIDENCE`**. O estudo populacional sobre
  queda de efetividade não prova nem contradiz o mecanismo causal deste indivíduo.
  Classificar como enganoso presumiria como verdadeira uma parte factual do caso que
  não foi documentada.

## Decisão humana registrada

O autor do projeto aprovou expressamente as três recomendações em lote. As decisões
e justificativas estão preservadas em `DECISIONS_2026-09-26.md`, com o código interno
`project_author`. O formulário original vazio permanece histórico. Resultado:

- decisões finais: 3;
- respostas secundárias arquivadas: 16;
- itens incorporados ao snapshot adjudicado: 16;
- rótulos finais alterados em relação ao primário: 0;
- inferências da pipeline na calibração: 0.
