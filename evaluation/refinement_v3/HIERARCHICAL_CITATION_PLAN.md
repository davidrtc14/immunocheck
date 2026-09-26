# Plano pré-experimental — citações hierárquicas v3

Data de registro: 26/09/2026.

## Hipótese

O primeiro seletor encontrou o documento anotado em 30/36 itens, mas o `chunk_id`
exato em apenas 17/36. Expandir passagens dentro desses documentos pode recuperar
trechos representativos afetados pela segmentação sem ampliar a busca para fontes
tematicamente diferentes.

## Expansão congelada

Para cada uma das até três citações selecionadas na etapa anterior, o conjunto da
segunda seleção conterá:

- o próprio trecho-semente;
- os quatro primeiros chunks do mesmo documento;
- chunks imediatamente anterior e posterior na mesma página;
- deduplicação e limite global de 20 candidatos.

O seletor recebe alegação e decisão congelada e devolve no máximo três aliases. Não
vê evidências anotadas, não altera veredito ou explicação e não usa fonte externa.
Falhas preservam as citações anteriores, mas contam como falha técnica.

## Gates

Os sete gates permanecem inalterados. A citação exata precisa atingir pelo menos
22/36; os outros seis já aprovados precisam permanecer aprovados. A latência desta
segunda seleção será somada ao caminho completo anterior e deve manter P95 ≤ 20 s.

O diagnóstico indica teto de 30/36 para o conjunto expandido, mas não garante que o
seletor escolha os chunks anotados. Teste final e holdout continuam fechados. Um
eventual sucesso é somente de calibração exploratória e exige confirmação humana em
dados novos.
