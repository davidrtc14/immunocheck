# Plano de calibração D1 + D2 (registrado antes da execução)

Data do registro: 13/10/2026. Conjunto: calibração v4 (`split: development`, 48 itens, 12
famílias). O holdout não é tocado.

## Condições

| Id | Descrição |
|---|---|
| `v3_plain` | Pipeline v3 (prompts congelados) com gravação de sinais; sem ancoragem e sem limiares. |
| `v4_grounded` | v3 + D1: os geradores direto e relacional pedem `support_spans`; conclusão sem trecho literal verificado (por campo exigido) ou com número ausente das fontes citadas é rebaixada para `INSUFFICIENT_EVIDENCE`. |
| `v3_plain+thr` / `v4_grounded+thr` | As anteriores com limiares D2 aplicados **offline** sobre os sinais gravados (confiança da extração, score top-1 e margem top-1/top-2). |

Os limiares são escolhidos por busca em grade (`calibrate_thresholds`: maximiza macro-F1;
desempate por menos sinais ativos e menos abstenções; no máximo 25% das conclusões corretas
podem ser sacrificadas). Como a escolha é feita nos mesmos 48 itens, relata-se também a
estimativa honesta por **validação cruzada deixando uma família de fora** (nested).

## Hipóteses e critérios de decisão (fixados agora)

- **H-D1:** a ancoragem reduz conclusões incorretas sem destruir as corretas. D1 é adotada se
  (i) macro-F1 de `v4_grounded` ≥ macro-F1 de `v3_plain` − 0,03, **e** (ii) a precisão das
  conclusões (acertos entre previsões não-abstenção) de `v4_grounded` ≥ a de `v3_plain` + 0,05
  ou o macro-F1 é maior, **e** (iii) falhas técnicas ≤ 2% e P95 ≤ 45 s.
- **H-D2:** limiares calibrados melhoram a abstenção. D2 é adotada se o macro-F1 da validação
  cruzada por família superar o macro-F1 sem limiares em ≥ 0,03.
- Se um critério falhar, o componente não entra na v4 e o resultado negativo é relatado. O
  tamanho da amostra (48 itens, 12 famílias) limita a potência: intervalos por família serão
  reportados e conclusões serão tratadas como indicativas, não confirmatórias.

## Limitações

Curadoria sem revisor externo (ver `PROTOCOL.md`). A calibração usa uma única execução por
condição (temperatura 0, semente 42). Os limiares congelados em `thresholds.json` só serão
avaliados no holdout na Fase F.
