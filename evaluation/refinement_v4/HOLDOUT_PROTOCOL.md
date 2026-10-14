# Protocolo do holdout v4 (Fase F) — registrado antes da execução

Data do registro: 13/10/2026.

## Candidata e linha de base

- **Candidata v4:** pipeline v3 com a ancoragem verificável D1 (`GroundedVerdictGenerator`), sem
  limiares D2 e sem D4/D5. A inclusão de D1, apesar da reprovação do critério de falhas técnicas
  na calibração D, foi decidida pelo pesquisador (emenda em `CALIBRATION_D4_PLAN.md`).
- **Linha de base:** v3 com prompts congelados, sem ancoragem.
- Mesmo modelo (`qwen3:8b`, digest em `holdout_freeze.json`), temperatura 0, semente 42, contexto
  8.192, corpus e índice versionados. Hashes e commit em `holdout_freeze.json`.

## Execução

Os 48 itens `split: test` do v4 são executados **uma única vez** por condição. Retomar após queda é
permitido (checkpoint por item); repetir ou reexecutar não é. Nenhuma alteração de código, prompt,
corpus, modelo, limiar ou item é permitida depois do congelamento. Falhas técnicas contam como
`INSUFFICIENT_EVIDENCE` e entram no gate de falhas.

## Gates (todos devem passar para promover a candidata a padrão)

1. Macro-F1 absoluto da candidata ≥ 0,45.
2. Ganho de macro-F1 sobre a v3 ≥ +0,05 (estimativa pontual); o IC 95% por família do ganho
   é reportado, sem exigência de exclusão do zero (n = 48).
3. Recall de `INSUFFICIENT_EVIDENCE` ≥ 0,50 **e** precisão de abstenção ≥ 0,50.
4. Precisão das conclusões da candidata ≥ a da v3.
5. Queda de recall de `SUPPORTED` e de `REFUTED` em relação à v3 ≤ 0,10 cada.
6. Falhas técnicas ≤ 2 de 48.
7. P95 de latência ≤ 45 s.
8. Citação relevante: entre os itens conclusivos esperados, a fração com conclusão e ao menos um
   `chunk_id` citado dentro da evidência anotada ≥ 0,50 e não inferior à da v3 em mais que 0,05.

Reportados sem gate: recall de `MISLEADING` (limitação conhecida: 0/12 na calibração), matriz de
confusão, métricas por classe, mediana de latência, IC por família, bootstrap pareado.

## Regra de decisão

Se os 8 gates passarem, a candidata é recomendada como padrão para a próxima integração (com
ensaio local e atualização do bot); caso contrário a v3 permanece e o resultado negativo entra no
TCC. Em ambos os casos relata-se a tabela completa de ablação (calibração + holdout), inclusive
os resultados negativos (D2, D4/D5, reranker, híbrido).

## Limitações

Curadoria do gabarito sem revisor externo nem segunda anotação; 48 itens e 12 famílias (intervalos
largos); conjunto sintético e documental, sem mensagens reais; uma execução por condição; a
calibração motivou o desenho (risco de otimismo na candidata).
