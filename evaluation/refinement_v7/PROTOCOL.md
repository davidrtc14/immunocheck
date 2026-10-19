# Protocolo v7: nova base de avaliação do veredito (ADR-052)

Registrado em 17/10/2026, antes de gerar qualquer alegação do conjunto novo e antes de qualquer
mudança na arquitetura do veredito. As escolhas abaixo foram aprovadas pelo pesquisador nesta data:
conjunto contrastivo com teste externo 2, revisão humana de uma amostra, macro-F1 de 4 classes como
métrica principal e P95 de 45 s como limite.

## Motivação

As Fases 16 a 18 mostraram onde o veredito perde precisão (diagnóstico nos registros finais da
Fase 18):
- **`MISLEADING` é o ponto cego.** Nos 24 itens `MISLEADING` do v4, a `v5_fixed` acertou 6 e a
  `v5_fixed_qwen36`, 11. Os erros vêm da agregação: o juiz marca as proposições como `ENTAILED` ou
  `CONTRADICTED`, e a distorção de escopo ou de inferência se perde na decomposição.
- **No teste externo, a abstenção vem do juiz.** Das 93 abstenções da `v5_fixed`, 55 tinham evidência
  recuperada e o juiz respondeu `NOT_ADDRESSED`; 31 não tinham evidência. Com o `qwen3.6`, 72 e 12.
- **Os conjuntos disponíveis não permitem iterar.** O v4 tem 96 itens (24 por classe) e já foi
  revelado; o teste externo da Fase 18 também. Medir de novo neles é exploratório.

A Fase 19 cria uma base de avaliação nova, maior e intocada, antes de qualquer mudança de
arquitetura (Fase 20).

## Conjunto contrastivo C7 (`evaluation/refinement_v7/`)

Alegações geradas a partir do corpus, com o rótulo definido pela construção e conferido por regras e
por revisão humana. As definições de rótulo são as de `evaluation/end_to_end/ANNOTATION_GUIDE.md`.

**Fontes:**
- `SUPPORTED`, `REFUTED` e `MISLEADING`: chunks dos 80 documentos do corpus, sorteados com semente
  fixa entre os que tratam de vacinação humana e trazem um fato verificável.
- `INSUFFICIENT_EVIDENCE`, dois tipos, metade cada:
  - **fato fora do corpus:** fatos dos documentos baixados mas não ingeridos (`status=downloaded` no
    `corpus/catalog.csv`), verdadeiros no mundo e ausentes do que o sistema consulta;
  - **evento individual:** relatos de caso particular sobre os temas do corpus, que nenhuma fonte
    geral permite sustentar ou contradizer (o mesmo tipo de abstenção do v4).

**Gerador:** `mistral-small3.2` local (Apache 2.0), de família diferente dos modelos avaliados
(`qwen3:8b` e `qwen3.6`), para evitar que um juiz avalie texto escrito por ele mesmo. Temperatura 0,
semente 42, prompt versionado, saída em JSON com schema. O gerador nunca é usado no bot.

**Construção a partir de um chunk** (uma chamada por chunk):
- `SUPPORTED`: reescrita fiel de um fato do chunk, em português, no registro de uma mensagem comum,
  sem copiar frases do texto;
- `REFUTED`: a mesma afirmação com a proposição central invertida (negação, número, direção ou
  população trocados) de modo que o chunk a contradiga diretamente;
- `MISLEADING`: mantém a parte sustentada e distorce escopo ou inferência, com o subtipo declarado
  (`overgeneralization`, `causal_leap`, `dropped_qualifier` ou `false_implication`) e os campos
  `sustained_part` e `distortion`, como exige o guia de anotação;
- trecho literal do chunk que sustenta o fato (`evidence_quote`).

O subtipo pedido para a versão `MISLEADING` segue um rodízio fixo pela ordem do sorteio, para
que os quatro apareçam em proporções parecidas. O prompt foi ajustado num piloto de 10 chunks.
Esses chunks podem reaparecer no sorteio do conjunto, o que não enviesa a avaliação: o piloto
ajustou só o gerador e nenhum sistema avaliado foi executado. Os exemplos do prompt usam uma vacina fictícia, não itens do v4.

Cada chunk fornece no máximo um item de cada rótulo, e um item por chunk entra no conjunto final, em
rodízio de rótulo, para que o mesmo fato não apareça em três versões.

**Portões automáticos** (descartam o candidato; o motivo fica registrado):
1. `evidence_quote` precisa ser substring do chunk (normalização de acentos e espaços);
2. todo número da versão `SUPPORTED` precisa ter forma equivalente no chunk;
3. a versão gerada não pode copiar o chunk: sobreposição de 4-gramas de palavras ≤ 0,30;
4. as três versões precisam ser diferentes entre si;
5. duplicatas no conjunto inteiro (similaridade BGE-M3 ≥ 0,92) ficam só uma vez;
6. `INSUFFICIENT_EVIDENCE` de fato fora do corpus é descartado se algum chunk do corpus tiver
   similaridade BGE-M3 ≥ 0,85 com a alegação; os três chunks mais próximos vão para o revisor.
7. toda alegação precisa mencionar uma vacina ou a vacinação (acrescentado no piloto do gerador,
   antes da geração do conjunto).

**Tamanho e divisão:** alvo de 400 itens (100 por classe), com mínimo de 60 por classe. A família é o
documento de origem; documentos inteiros vão para desenvolvimento ou teste (50%/50%, estratificado
por tema), e nenhuma família atravessa os dois.
- *Ampliação por rendimento (18/10, antes da revisão e de qualquer inferência):* com 6 chunks por
  documento, 191 de 449 chunks do corpus não tinham fato utilizável e a montagem rendeu 81/81/80
  itens nas três classes do corpus. O limite subiu para 8 chunks por documento (578 chunks). O
  sorteio por documento mantém os 6 primeiros, então nada do que já tinha sido gerado mudou. O sorteio
  dos relatos individuais ficou preso ao limite original e os chunks deles saem do corpus, para que
  nenhum chunk gere dois itens.

**Revisão humana:** amostra estratificada de 80 itens (20 por classe, metade de cada split). O revisor
vê a alegação, o chunk de origem (ou os três mais próximos, no `INSUFFICIENT_EVIDENCE`), o rótulo
proposto e, no `MISLEADING`, a parte sustentada e a distorção. Ele marca correto, incorreto ou ambíguo,
sem ver nenhuma resposta do sistema.
- A taxa de erro de rótulo é reportada por classe, com IC.
- Se uma classe passar de 10% de erro, as regras de geração dessa classe são corrigidas e uma nova
  amostra dela é revisada, sempre antes do congelamento.
- Itens revisados como incorretos são corrigidos ou excluídos; ambíguos são excluídos.
- O pesquisador é um único revisor: isso é verificação de qualidade do rótulo por construção, não
  anotação independente, e é declarado como tal.
- *Emenda de 18/10 (revisão assistida por LLM):* a revisão das amostras foi preenchida pelo
  pesquisador com uma ferramenta de IA externa, e não item a item pela página de revisão. As taxas de
  erro abaixo são, portanto, de uma **revisão assistida por LLM sob responsabilidade do
  pesquisador**, não de uma revisão humana independente, e isso entra nas ameaças à validade. A
  ferramenta recebeu só alegações sintéticas e trechos de documentos públicos do corpus, sem nenhum
  dado de usuário.
- *Emenda de 18/10 (correção da regra de `INSUFFICIENT_EVIDENCE` fora do corpus):* na primeira
  revisão, SUPPORTED, REFUTED e MISLEADING tiveram 0 de 20 erros, e os relatos individuais 0 de 11.
  Já os fatos fora do corpus tiveram 7 de 9 erros: são fatos genéricos de páginas do MS e da OPAS que
  o corpus já cobre, e o portão 6 (similaridade BGE-M3 ≥ 0,85) não percebeu isso, porque os sete
  ficaram entre 0,69 e 0,76. A regra passa a ser esta, fixada antes de rodar:
  1. o portão 6 por similaridade continua valendo;
  2. novo portão 8, de cobertura julgada por LLM: o gerador (`mistral-small3.2`, temperatura 0,
     saída estruturada) recebe a alegação e os 5 chunks do corpus mais próximos por BGE-M3, e diz se
     algum deles sustenta, contradiz ou mostra que a alegação é exagerada ou parcial. Só ficam as
     alegações em que nenhum trecho resolve a questão. Antes de usar o portão, ele é conferido nos 9
     itens revisados: deve descartar a maioria dos 7 erros e manter os 2 acertos;
  3. para compensar as perdas, o sorteio dos documentos fora do corpus passa a usar todos os chunks
     candidatos, não mais 6 por documento;
  4. se sobrarem menos de 50 fatos fora do corpus, os relatos individuais completam os 100 itens da
     classe, com um sorteio extra de chunks que não geraram nenhum outro item. A proporção final
     entre as duas origens é reportada.

  *Resultado da conferência do portão 8 (registrado depois de rodar):* nos 9 itens revisados, ele
  descartou os 7 erros (5 `supports`, 2 `partial`) e também os 2 acertos (1 `supports`, 1
  `partial`). A segunda condição falhou, porque o portão é mais rigoroso que a revisão. Esse excesso
  custa itens, não validade do rótulo. A regra foi mantida como registrada, sem ajuste, e a falha é
  declarada. Nos 50 fatos da primeira geração, só 6 passaram (33 `supports`, 8 `partial`, 3
  `contradicts`).

  *Remontagem e escolha da rodada 2 (antes de sortear):* com o portão 8 e o sorteio ampliado,
  sobraram 20 fatos de fora do corpus (93 descartados pelo juiz: 69 `supports`, 19 `partial` e 5
  `contradicts`). Os relatos individuais completaram a classe com 80 itens. A rodada 1 casou com 67
  dos 80 itens revisados: os 9 fatos de fora revisados caíram no portão 8, e 4 itens saíram na
  remontagem. Uma amostra aleatória de 20 pegaria só uns 4 fatos de fora, justamente a origem
  corrigida, enquanto os relatos já tiveram 0 de 11 erros. Por isso a rodada 2 revisa **os 20 fatos de
  fora inteiros**. A taxa de erro da classe é estimada ponderando as duas origens pelo peso de cada
  uma no conjunto (0,2 e 0,8), e o limite de 10% vale para a origem corrigida e para a classe.

  O texto original desta emenda previa revisar uma amostra aleatória de 20 itens de
  `INSUFFICIENT_EVIDENCE`, com o mesmo limite de 10%, antes do congelamento. As correções da primeira revisão nas outras classes continuam
  valendo, e os itens são casados pelo chunk de origem e pela alegação, não pelo id.

**Congelamento:** o split de teste é congelado por hash (itens, corpus, gerador, prompt e portões)
antes de qualquer execução do veredito sobre o C7. O desenvolvimento pode ser usado livremente na
Fase 20.

## Teste externo 2 (`evaluation/refinement_v7/external2/`)

Alegações sobre vacinação humana checadas por agências e publicadas em português, que não estejam no
teste externo 1, no v4 nem no C7, montadas por regra e congeladas antes de qualquer inferência. A
fonte preferida é o feed público de marcação ClaimReview; a licença é verificada antes do uso, e itens
sem licença de redistribuição são versionados só por URL e hash, como no teste externo 1. Os rótulos
das agências são mapeados para três classes, e a análise segue a da Fase 18 (sustentada × não
sustentada, com a abstenção à parte). O resultado é descritivo se o conjunto tiver menos de 60 itens.

**Composição observada (17/10/2026, antes de qualquer inferência):** o feed do Data Commons rendeu
304 itens pelas regras do teste externo 1 (283 `REFUTED`, 20 `MISLEADING`, 1 `SUPPORTED`; detalhes em
`external2/SOURCES.md`). Como quase todos são alegações não sustentadas, as métricas do externo 2 são
o erro grave, a precisão das conclusões e a cobertura; o recall de `SUPPORTED` não é calculável.

## Métricas

- **Principal:** macro-F1 de 4 classes no teste do C7, com IC 95% por bootstrap pareado por família.
- **Travas:** erro grave (alegação não sustentada respondida como `SUPPORTED`) ≤ ao da referência
  + 0,02; P95 ≤ 45 s; falhas técnicas ≤ max(2%, taxa da referência). O limite de falhas passa a ser
  relativo, lição da Fase 17.
- **Diagnósticas:** recall por classe; recuperação do chunk de origem entre as evidências (separa erro
  de busca de erro do juiz); taxa de `NOT_ADDRESSED` com evidência recuperada; acerto por subtipo de
  `MISLEADING`.
- **Teste externo 2:** precisão das conclusões, erro grave e cobertura, descritivos ou com os gates da
  Fase 18 se houver itens suficientes.

## O que fica para a Fase 20

As mudanças de arquitetura candidatas (contexto ampliado para o juiz, etapa de enquadramento para
`MISLEADING`, `qwen3.6` só no juiz, saída estruturada em todas as chamadas, voto por consistência) e a
regra de decisão são registradas num adendo a este protocolo, depois de o C7 existir e antes de
qualquer contato com o teste. As linhas de base são a v3 (padrão) e a `v5_fixed`.

## Adendo 1 — Fase 20: candidatas e regra de decisão (18/10/2026)

Registrado depois do congelamento do C7 (`freeze.json`, 18/10) e antes de qualquer execução do
veredito sobre o C7 ou sobre o teste externo 2. Até aqui, nenhum sistema foi rodado sobre esses
conjuntos.

### Ponto de partida

- **Linhas de base:**
  - **v3**, a padrão do bot (pipeline roteado);
  - **`v5_fixed`**, a v5 com a verificação tolerante e a correção de números da Fase 18 (`99d4999`).
    É a melhor alternativa medida até agora.
- **Problemas observados nos registros da Fase 18:**
  - `MISLEADING` se perde na agregação;
  - quando a decomposição resulta em uma única proposição, a agregação nunca produz `MISLEADING`;
  - o juiz só conhece três relações (`ENTAILED`, `CONTRADICTED`, `NOT_ADDRESSED`), sem um meio-termo
    para "sustentado em parte, mas exagerado";
  - a maioria das abstenções vem do juiz dizer `NOT_ADDRESSED` mesmo com evidência recuperada.

### Candidatas

Cada candidata é uma opção injetada, desligada por padrão, implementada em módulos novos. Nenhum
arquivo congelado da v3, da v5 ou da v6 é editado, para que os resultados anteriores continuem
reprodutíveis.

| Id | Candidata | Hipótese | Custo esperado |
|---|---|---|---|
| C1 | **Relação de enquadramento:** o juiz ganha uma quarta relação, `PARTIAL` (o trecho sustenta o núcleo, mas a proposição exagera o alcance, omite uma ressalva ou salta para causa). Exige trecho literal, como as outras. Na agregação, `PARTIAL` em proposição central ou conclusão, sem contradição central, vira `MISLEADING`, inclusive quando há uma proposição só. | Recupera o recall de `MISLEADING` sem custo de latência. | Nenhum |
| C2 | **Contexto ampliado para o juiz:** cada evidência recuperada vai com os chunks vizinhos do mesmo documento (anterior e seguinte), dentro de um teto de caracteres. | Reduz `NOT_ADDRESSED` quando a frase decisiva está no chunk ao lado. | Prompt maior, mais latência |
| C3 | **`qwen3.6` só no juiz:** a decomposição continua com o `qwen3:8b`. | Melhor juiz da Fase 18 (macro-F1 de 0,716 no v4), com menos latência que o `qwen3.6` no pipeline todo. | P95 de ~25 s na Fase 18 |
| C4 | **Robustez da decomposição:** uma nova tentativa com instrução de reparo quando o extrator devolve `ModelOutputError`; se falhar de novo, cai na v3 em vez de abster. | Reduz falhas técnicas. | Só nos casos de falha |
| C5 | **Voto por consistência no juiz:** 3 julgamentos com sementes diferentes (temperatura 0,3) e maioria por proposição; empate vira `NOT_ADDRESSED`. | Estabiliza julgamentos na fronteira. | 3× o custo do juiz; só entra se o P95 couber |

A "saída estruturada em todas as chamadas", listada no protocolo, já está em vigor: todas as
chamadas da v5 usam `format: schema`. Por isso ela não é candidata.

### Desenvolvimento (só o split de desenvolvimento do C7, 193 itens)

1. **Linhas de base:** a v3 e a `v5_fixed` são rodadas uma vez no desenvolvimento e servem de
   referência para todo o desenvolvimento.
2. **Seleção progressiva:** começa pela `v5_fixed` e cada candidata é testada na ordem C1, C4, C2,
   C3, C5. Ela fica se, contra a configuração acumulada:
   - melhorar o macro-F1 de 4 classes no desenvolvimento em pelo menos 0,02;
   - não aumentar o erro grave em mais de 0,02;
   - mantiver o P95 em até 45 s.

   A C4 é exceção: fica se reduzir as falhas técnicas sem piorar o macro-F1 em mais de 0,01.
3. **Ajustes dentro de cada candidata:** prompts e limiares podem ser iterados livremente no
   desenvolvimento, mas cada versão testada é registrada (data, mudança, métricas) em
   `evaluation/refinement_v7/DEVELOPMENT_LOG.md`. A versão escolhida é a última registrada, e não a
   melhor entre muitas sorteadas ao acaso.
4. **Prazo:** o desenvolvimento termina até 31/10/2026. Se uma candidata não estiver pronta, ela fica
   de fora, e isso é registrado.
5. **Congelamento:** a configuração final recebe o nome **v7**. Os hashes do código, dos prompts e dos
   modelos vão para `evaluation/refinement_v7/verdict_freeze.json` antes da execução no teste.

### Execução final (única)

- **Teste do C7 (207 itens) e teste externo 2 (304 itens),** com quatro condições: v3, `v5_fixed`, v7
  e **v7 sem `qwen3.6`** (só se a C3 entrar). Esta última é a variante rápida, que não depende do
  modelo de 23 GB.
- **Integridade:** antes de rodar, o script confere os hashes do C7 e do teste externo 2 contra os
  congelamentos. Cada condição roda uma vez, com checkpoint retomável, e não se repete.

### Regra de promoção

A v7 (ou a variante sem `qwen3.6`) substitui a v3 como padrão do bot se passar em todos os critérios
abaixo, sempre contra a v3. Os ICs são de bootstrap pareado, 10.000 reamostras, semente 42.

**No teste do C7:**

| Critério | Condição |
|---|---|
| P1 | Macro-F1 de 4 classes: Δ ≥ +0,05 e limite inferior do IC 95% (pareado por família) > 0 |
| P2 | Erro grave (item não `SUPPORTED` respondido como `SUPPORTED`): taxa ≤ taxa da v3 + 0,02 |
| P3 | Recall de `MISLEADING` ≥ ao da v3 |
| P4 | P95 ≤ 45 s; falhas técnicas ≤ max(2%, taxa da v3) |

**No teste externo 2,** com as mesmas métricas e os mesmos limites da Fase 18 (pareado por item):

| Critério | Condição |
|---|---|
| X1 | Precisão das conclusões: Δ ≥ −0,02 e limite inferior do IC 95% ≥ −0,08 |
| X2 | Erro grave ≤ taxa da v3 + 0,02 |
| X3 | Queda de cobertura ≤ 0,10 |
| X4 | P95 ≤ 45 s; falhas técnicas ≤ max(2%, taxa da v3) |

Os limites dos critérios X são os da Fase 18, mantidos sem alteração mesmo depois de a v5 ter
reprovado em X3. Mudá-los depois de ver aquele resultado seria ajuste ao dado.

- **Desempate:** se as duas variantes da v7 passarem, fica a de maior macro-F1 no teste do C7. Se a
  diferença for menor que 0,02, fica a variante sem `qwen3.6`.
- **`v5_fixed`:** é rodada só como comparação e não pode ser promovida nesta fase. Ela já foi
  avaliada na Fase 18.
- **Se nenhuma passar:** a v3 continua padrão, e os resultados entram no TCC como estão.

**Diagnósticas (sem gate):**
- recall por classe;
- acerto por subtipo de `MISLEADING` e por origem do `INSUFFICIENT_EVIDENCE` (relato ou fato de fora);
- recuperação do chunk de origem entre as evidências;
- `NOT_ADDRESSED` com evidência recuperada;
- concordância entre as condições.

## Adendo 2 — C3 substituída pela C3b (19/10/2026, antes de qualquer contato com o teste)

**O que mudou na premissa.** A C3 previa o `qwen3.6` só no juiz, com menos latência que o modelo no
pipeline todo. Medido no desenvolvimento, aconteceu o contrário: o `qwen3.6` (23 GB, 76% em CPU) não
cabe na GPU de 8 GB junto com o `qwen3:8b`, e o Ollama descarrega um modelo para carregar o outro a cada
item. Os cinco primeiros itens levaram de 33,9 s a 49,3 s (dois acima de 45 s), o que inviabiliza o
critério de P95 ≤ 45 s. A execução foi interrompida nesses cinco itens e registrada no
`DEVELOPMENT_LOG.md`.

**C3b.** O `qwen3.6` passa a ser usado no pipeline inteiro (decomposição, juiz e explicação), sem troca
de modelo. É a condição `v5_fixed_qwen36` da Fase 18, que teve P95 de 25,3 s a 27,2 s e o melhor
macro-F1 de veredito do projeto no v4 (0,716). A hipótese da candidata não muda (um juiz mais capaz);
só a forma de usá-lo.

**O que não muda.** A C3b é testada no mesmo lugar da ordem (depois da C2, antes da C5), com o mesmo
critério de seleção, inclusive P95 ≤ 45 s. Na execução final, a "v7 sem `qwen3.6`" continua sendo a
variante rápida, rodada só se a C3b entrar, e o desempate continua favorecendo a variante sem
`qwen3.6` quando a diferença de macro-F1 for menor que 0,02.

## Ameaças à validade (declaradas antes)

- As alegações são sintéticas: o estilo e a distribuição diferem das mensagens reais, e o teste
  externo 2 serve de checagem em alegações reais.
- O rótulo por construção pode errar; a revisão de uma amostra mede esse erro, mas não o elimina.
- O `SUPPORTED` derivado de um chunk pode ser mais fácil de recuperar que uma alegação real; o portão
  de cópia reduz, mas não elimina, esse efeito.
- Um gerador de outra família reduz, mas não elimina, o viés de estilo.
- Os documentos fora do corpus podem repetir fatos de documentos ingeridos; o portão 6 e a revisão
  reduzem esse risco.
