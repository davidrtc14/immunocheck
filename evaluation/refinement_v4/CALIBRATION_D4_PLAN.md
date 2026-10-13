# Plano D4/D5 (registrado antes da execução)

Data do registro: 13/10/2026. Partição: calibração v4 (48 itens, 12 famílias). Holdout intocado.

## Emenda registrada à decisão D1

Por decisão do pesquisador (13/10/2026), a ancoragem D1 passa a compor a candidata v4 que será
levada ao holdout, **apesar** de ter reprovado o critério de falhas técnicas ≤ 2% da calibração D
(1/48 = 2,08%, falha herdada da v3). É um desvio declarado do critério pré-registrado em
`CALIBRATION_D_PLAN.md`; a promoção continua dependendo dos gates da Fase F. D2 (limiares) não
acompanha a candidata: sobre a base ancorada o ganho aninhado foi negativo (−0,016).

## Problema

Em v3 e v4 ancorada, `MISLEADING` teve recall 0/12 na calibração. Hipótese: sem o molde
explícito "premissa → conclusão", o roteador envia as alegações ao gerador direto, que escolhe
`SUPPORTED`/`REFUTED`.

## Mudanças testadas (condição `v4_d4`, tudo sobre `v4_grounded`)

1. **D4:** exemplos few-shot ilustrativos (tétano, inventados e alheios ao conjunto) no
   prompt do gerador relacional; o relacional recebe os mesmos 6 trechos do direto.
2. **D5:** em alegações roteadas como simples, o gerador direto decide e o relacional só pode
   converter uma conclusão em `MISLEADING` (nunca reverter abstenção). Em `PREMISE_CONCLUSION`
   e `UNANCHORED_SPECIFIC_EVENT` o comportamento da v3 é mantido.
3. **Robustez:** `ModelOutputError` vira abstenção técnica explícita (contada à parte), não
   exceção. A rota escolhida pelo roteador é registrada por item (diagnóstico de D5).

Nenhum prompt congelado foi editado: os acréscimos entram por clientes de composição.

## Critérios de adoção (fixados agora)

Adota-se `v4_d4` se, em relação a `v4_grounded`, todos valerem:
- recall de `MISLEADING` ≥ 4/12 (0,33);
- macro-F1 ≥ macro-F1 de `v4_grounded` + 0,03 (0,572);
- precisão das conclusões não inferior em mais que 0,05 (≥ 0,568);
- recall de abstenção ≥ 0,60 e nenhuma exceção não tratada;
- P95 ≤ 45 s.

Falha em qualquer critério mantém `v4_grounded` (sem D4/D5) e o resultado negativo é relatado.
Relata-se também a acurácia de rota por classe esperada (diagnóstico de D5, sem gate).

## Limitações

48 itens e 12 famílias; curadoria sem revisor externo; uma execução (temperatura 0, semente 42);
as decisões desta calibração usam os mesmos itens que motivaram o desenho (risco de otimismo).
