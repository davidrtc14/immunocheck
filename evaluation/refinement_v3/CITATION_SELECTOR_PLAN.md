# Plano pré-experimental — seletor de citações v3

Data de registro: 26/09/2026.

## Hipótese isolada

A candidata roteada passou seis de sete gates e falhou somente a taxa de citação
relevante. Um seletor dedicado, sem autoridade para mudar veredito ou explicação,
pode escolher evidências mais diretamente ligadas à decisão entre os 15 resultados
densos já recuperados.

## Condição

- todos os 48 vereditos e textos da candidata roteada serão preservados;
- somente decisões conclusivas acionam o seletor;
- entrada: alegação, decisão congelada e 15 trechos com aliases `E1`–`E15`;
- saída: de uma a três referências pertencentes à entrada;
- falha estrutural conserva as citações anteriores, mas conta como falha técnica;
- latência do seletor é somada à latência fim a fim já registrada;
- nenhuma chamada ao auditor factual será feita.

O top 15 contém evidência anotada em 25 dos 36 itens conclusivos, teto de citação
0,694. O gate exige pelo menos 22 acertos (0,611). A seleção não poderá consultar
IDs anotados nem rótulos esperados.

## Gates e interpretação

Aplicam-se novamente os sete gates. Como os vereditos estão congelados, macro-F1,
recall e abstenção devem permanecer idênticos; os riscos novos são falha técnica e
P95. Para promoção exploratória, todos os sete precisam passar e o relatório deve
confirmar zero mudanças de veredito.

Teste final e holdout não serão carregados. Mesmo que a calibração passe, a candidata
apenas se torna elegível para congelamento e avaliação em conjunto novo com revisão
humana; não autoriza implantação pública.
