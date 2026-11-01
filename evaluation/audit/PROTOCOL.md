# Protocolo: auditoria humana das respostas conclusivas da v7

Registrado em 01/11/2026, antes do sorteio e da avaliação, a pedido do orientador: verificar com
avaliadores humanos se as explicações da v7 estão corretas e se as fontes exibidas as sustentam,
o que as "fontes rastreáveis" do título hoje só garantem por construção.

## Amostra

- **45 respostas conclusivas** (sustentada, refutada ou enganosa) da v7, sorteadas com semente 42
  entre os itens com veredito conclusivo na execução única de 20/10:
  - **30 do teste do C7**, 10 por veredito (sustentada, refutada e enganosa);
  - **15 do teste externo 2**, proporcionais aos vereditos conclusivos: 13 refutadas e 2 enganosas.
- Os registros de 20/10 não guardam o texto da explicação. Por isso, a v7 (configuração padrão do
  bot) gera de novo a resposta de cada item sorteado, com o mesmo modelo, temperatura e semente. Se a
  resposta nova não for conclusiva, o item é trocado pelo próximo da ordem sorteada no mesmo estrato.
  A auditoria avalia essas respostas, que são as que o bot entrega; não altera nenhuma métrica.

## Avaliação

Dois autores avaliam a mesma planilha **de forma independente**, sem conversar sobre os itens e sem
ver as respostas do outro antes de terminar. Para cada item, a planilha mostra a alegação, o veredito,
a explicação, o fato correto ou a distorção apontada, as fontes exibidas e o texto dos trechos citados.

| Pergunta | Opções | Critério |
|---|---|---|
| A explicação está correta? | Sim / Parcial / Não | Sim: tudo o que ela afirma é correto e coerente com o veredito. Parcial: há imprecisão menor que não muda o veredito. Não: há erro factual ou a explicação contradiz o veredito. |
| As fontes sustentam a explicação? | Sim / Parcial / Não | Sim: os trechos citados afirmam o que a explicação diz. Parcial: sustentam só parte. Não: não tratam do que foi dito ou o contradizem. |
| Comentário | livre | Opcional; obrigatório quando a resposta for Não. |

O gabarito do conjunto não é mostrado: o que se avalia é a resposta, e não o acerto do veredito, já
medido pelas métricas.

## Análise

`scripts/analyze_audit.py` calcula, para cada pergunta: a proporção de Sim, Parcial e Não de cada
avaliador; a concordância observada; e o **kappa de Cohen** (três categorias, sem pesos), com a
leitura usual de Landis e Koch (1977). Os itens em que os avaliadores discordarem são listados para
consenso, registrado à parte, sem alterar as avaliações independentes usadas no kappa.

## Arquivos

- `scripts/build_audit_sample.py`: sorteio, geração das respostas e planilha (`output/audit/`, fora
  do Git, porque contém trechos do corpus e alegações das agências).
- `output/audit/avaliador_A.csv` e `avaliador_B.csv`: preenchidas por cada avaliador.
- `evaluation/audit/results.json`: só agregados, versionado.
