# Plano pré-experimental — candidata relacional v3, denso top 15

Data de registro: 26/09/2026.

## Hipótese

Uma decisão estruturada que diferencie (a) alegações sobre eventos individuais não
investigados e (b) premissas verdadeiras usadas para conclusões exageradas deve
melhorar simultaneamente a abstenção e o recall de `MISLEADING`. Aliases curtos devem
evitar os erros de cópia de IDs observados no top 20.

## Condição e isolamento

- baseline: v1 densa top 6 com auditor, já registrada na fase A;
- candidata: Qwen3-8B local, uma decisão relacional estruturada, sem auditor;
- recuperação: primeiros 15 resultados do checkpoint denso top 20 já registrado;
- extração, corpus, temperatura e semente: inalterados;
- teste final v1 e holdout: não serão carregados;
- saída: checkpoint incremental, sem sobrescrever artefatos anteriores.

O top 15 foi fixado antes da inferência. Ele contém evidência anotada em 25/36 casos
conclusivos (69,4%), permitindo superar o gate de citação de 60% sem enviar os 20
trechos que elevaram erros estruturais. Esse número é diagnóstico de retrieval, não
resultado de classificação.

## Regra de decisão

O modelo rotula o escopo e a relação evidencial. O código aplica duas invariantes:

1. evento específico sem investigação daquele evento resulta em
   `INSUFFICIENT_EVIDENCE`;
2. premissa sustentada com extrapolação material resulta em `MISLEADING`, e não em
   refutação total.

Nos demais casos, a relação estruturada mapeia para as quatro classes. Conclusões
exigem ao menos uma referência válida, limitada a três aliases fornecidos.

## Gates e limite de interpretação

Serão mantidos exatamente os sete gates do protocolo v2: delta de macro-F1 ≥ 0,08,
recall `MISLEADING` ≥ 0,40, precisão de abstenção ≥ 0,45, citação relevante ≥ 0,60,
queda máxima de recall por classe ≤ 0,05, falha técnica ≤ 0,02 e P95 ≤ 20 s.

Esta execução reutiliza a calibração já observada e, portanto, é exploratória. Mesmo
que passe todos os gates, não constitui confirmação independente nem autoriza uso
público. Ela apenas permite congelar uma candidata e preparar dados novos para uma
avaliação confirmatória com revisão humana.
