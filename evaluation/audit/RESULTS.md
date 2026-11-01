# Resultados: auditoria humana das respostas conclusivas da v7

Conforme `PROTOCOL.md`: 45 respostas conclusivas da v7 (30 do teste do C7 e 15 do teste externo 2),
avaliadas de forma independente por dois autores em 01/11/2026. Agregados em `results.json`; as
planilhas preenchidas ficam em `output/audit/`, fora do Git.

**Amostra gerada:** ao gerar de novo as respostas, 3 itens sorteados deram "evidência insuficiente"
e foram trocados pelos seguintes do estrato, como previsto. Um item mudou de enganosa para refutada
e foi mantido por continuar conclusivo. A composição final ficou em 11 refutadas, 10 sustentadas e
9 enganosas no C7, e em 13 refutadas e 2 enganosas no teste externo 2.

**Ressalva de preenchimento:** um comentário de cada avaliador parece ter sido colado na linha
errada (A11 do avaliador A trata do tema do A12; A24 do avaliador B repete o comentário do A22). As
classificações foram usadas como entregues, sem correção posterior.

## Concordância

| Pergunta | Avaliador A (Sim / Parcial / Não) | Avaliador B (Sim / Parcial / Não) | Concordância observada | Kappa de Cohen |
|---|---|---|---|---|
| A explicação está correta? | 26 / 11 / 8 | 27 / 15 / 3 | 62,2% | 0,325 |
| As fontes sustentam a explicação? | 17 / 20 / 8 | 22 / 20 / 3 | 57,8% | 0,303 |

Pela leitura de Landis e Koch (1977), os dois kappas indicam concordância **razoável** (0,21 a 0,40).
O avaliador A foi mais rigoroso: marcou "Não" em 8 itens em cada pergunta, contra 3 do avaliador B.
Quase todas as discordâncias são entre categorias vizinhas (Sim × Parcial ou Parcial × Não); só 1
item teve Sim × Não na explicação, e 3 nas fontes.

### Análise complementar (posterior ao protocolo)

O kappa é deprimido quando uma categoria domina as respostas (paradoxo do kappa; Feinstein e
Cicchetti, 1990), o que acontece aqui: a maioria dos itens foi julgada aceitável pelos dois. Por
isso, depois de ver os resultados, foram calculados o AC1 de Gwet (2008), menos sensível a esse
efeito, e a concordância agrupando Sim e Parcial como "aceitável". Essas medidas não substituem o
kappa registrado no protocolo.

| Pergunta | AC1 (3 categorias) | Aceitável × Não: concordância | Kappa | AC1 |
|---|---|---|---|---|
| Explicação correta | 0,477 | 88,9% | 0,497 | 0,859 |
| Fontes sustentam | 0,397 | 80,0% | 0,094 | 0,745 |

Nas fontes, 80% de concordância convivem com kappa de 0,09, o caso típico do paradoxo. A maior parte
da discordância está na fronteira entre "Parcial" e "Não", e não na direção do julgamento.

## O que os avaliadores encontraram

- **Explicação aceitável (Sim ou Parcial):** 37 de 45 para o avaliador A e 42 de 45 para o B.
- **Explicação errada para os dois (3 itens, todos do C7):** dois são o erro inverso já visto nas
  métricas, alegações verdadeiras dadas como refutadas, um deles com a explicação repetindo a
  própria alegação como se a refutasse. No terceiro, a explicação usa um número de casos da doença
  como se fosse de vacinação fora da faixa etária.
- **Fontes que sustentam por inteiro:** só 17 (A) e 22 (B) de 45. O problema mais comum, apontado
  nos comentários dos dois, é a explicação ir além do trecho citado: trocar a vacina ou a população
  do estudo (PCV10 por PCV13, vacina de VSR por vacina covid), generalizar a partir de um manual
  genérico ou afirmar "não há aumento" onde a fonte só traz evidência de baixa certeza.
- **Teste externo 2:** nenhuma explicação foi julgada errada pelos dois, mas as fontes sustentaram
  por inteiro só 2 (A) e 6 (B) de 15. Nessas alegações a v7 costuma refutar apontando que os trechos
  não tratam do tema, o que os avaliadores leram como sustentação parcial.

## Leitura

As fontes são reais e rastreáveis por construção, mas a auditoria mostra que isso não garante que
cada frase da explicação esteja no trecho citado: a sustentação completa ocorreu em cerca de 40% a
50% das respostas. A concordância apenas razoável entre os avaliadores indica que os critérios
"parcial" e "não" deixaram margem de interpretação; uma rubrica mais detalhada e avaliadores da
área da saúde são o passo seguinte.
