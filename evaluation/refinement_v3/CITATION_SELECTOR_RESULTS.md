# Resultado — seletor de citações v3

Execução concluída em 26/09/2026 no plano congelado pelo commit `27987e6`. O
seletor processou apenas decisões conclusivas, preservou os 48 vereditos e não
carregou teste final ou holdout.

## Resultado

| Métrica | Roteada | Roteada + seletor |
|---|---:|---:|
| Macro-F1 | 0,725 | 0,725 |
| Citação relevante por ID exato | 0,444 | 0,472 |
| Falha técnica | 0,000 | 0,000 |
| P95 | 13,26 s | 16,47 s |

O seletor elevou os acertos de citação de 16/36 para 17/36, abaixo dos 22/36
necessários. Seis de sete gates continuaram aprovados; o gate de citação falhou.

Uma auditoria diagnóstica, sem efeito sobre o gate, encontrou correspondência com o
mesmo documento anotado em 30/36 itens e com a mesma página ou página vizinha em
29/36. Isso sugere que parte da diferença decorre de granularidade: o seletor escolhe
passagens materialmente próximas, mas não o `chunk_id` único registrado. Documento
igual não prova sustentação e não substitui revisão semântica.

## Rastreabilidade

- plano: `f53a4118b39e05d5cc69c8e3291a67d157f7747dea8ce603d180a754c11050f4`;
- checkpoint: `480b3bfa8c1c896004eb257b854e121edcef8a75d03be40bb7b55e97b43c226d`;
- relatório: `3d75d1d5ad8ff881b05a338734fd5941fba2ca1aff739b29068657dd46526694`;
- mudanças de veredito: zero;
- inferências do teste final e do holdout: zero.

O próximo experimento deve testar recuperação hierárquica dentro dos documentos já
selecionados: passagens iniciais representativas e vizinhas do trecho recuperado,
sem consultar anotações. Essa hipótese ataca chunking e proveniência; não autoriza
reinterpretar retrospectivamente documentos iguais como citações corretas.
