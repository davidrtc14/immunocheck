# Protocolo v6: correção da v5 e confirmação em teste externo (ADR-051)

Registrado em 16/10/2026, **antes de qualquer inferência sobre o teste externo** e antes de
qualquer mudança no código da v5. A escolha da abordagem de avaliação foi aprovada pelo
pesquisador nesta data.

## Motivação

Na linha v5 (ADR-049), `v5_multiquery` obteve macro-F1 de 0,653 contra 0,490 da v3 nos 96 itens v4
(IC por família de +0,037 a +0,275). Ela foi reprovada só no critério de queda de recall de
`SUPPORTED` (1,00 → 0,88). Dois dos três `SUPPORTED` perdidos foram rebaixados pelas verificações
determinísticas: trecho literal não encontrado e número ausente da evidência. O conjunto v4 já foi
revelado, então nenhum ganho medido nele é confirmatório.

## Teste externo (`evaluation/refinement_v6/external/`)

São 150 alegações sobre vacinação humana com gabarito de agências de checagem (X-FACT, FACTCK.BR e
FACTCK.BR-extended), montadas por regra, sem curadoria do pesquisador e sem nenhuma inferência do
ImmunoCheck. O conjunto foi congelado em `external/freeze.json` (commit `5573f8d`). Os 96 itens sem
licença de redistribuição são reconstruídos localmente por `scripts/build_external_testset.py`, que
confere o sha256. A distribuição é de 12 `SUPPORTED`, 53 `MISLEADING` e 85 `REFUTED`, e nenhum
`INSUFFICIENT_EVIDENCE`. Detalhes em `external/SOURCES.md`.

**Problema de construto.** O gabarito é de mundo real. O ImmunoCheck responde só com o corpus e deve
se abster (`INSUFFICIENT_EVIDENCE`) quando a evidência não basta. Contar uma abstenção correta como
erro puniria o comportamento exigido pelo projeto. Além disso, a fronteira entre `MISLEADING` e
`REFUTED` depende do vocabulário de cada agência.

## Abordagem de avaliação (aprovada)

**Análise principal:** "sustentada × não sustentada", com a abstenção como terceira saída.
- Gabarito binário: `SUPPORTED` = sustentada; `REFUTED` e `MISLEADING` = não sustentada.
- Previsão: `SUPPORTED` = sustentada; `REFUTED` e `MISLEADING` = não sustentada;
  `INSUFFICIENT_EVIDENCE` = abstenção. Uma falha técnica conta como abstenção e entra também na
  contagem de falhas.
- Métricas:
  - **precisão das conclusões**: acertos entre as respostas conclusivas;
  - **erro grave**: fração dos itens não sustentados respondidos como `SUPPORTED`;
  - **cobertura**: fração de respostas conclusivas;
  - falhas técnicas e latência P95.
- Cada item tem família própria, então os IC 95% vêm de bootstrap pareado por item (10.000
  reamostras, semente 42).

**Análises secundárias, descritivas e sem gate:**
- macro-F1 em 3 classes (sustentada, não sustentada, abstenção como erro) no subconjunto
  `corpus_topic_coverage = covered`;
- estratificação por cobertura temática e por `external_flags` (`possible_individual_event`);
- recall de `SUPPORTED`, com só 12 itens e sem poder estatístico, declarado antes;
- matriz de confusão em 4 classes.

**O que o teste externo não avalia:** a distinção entre `MISLEADING` e `REFUTED` e o reconhecimento
de evento individual. Isso continua medido só no conjunto v4.

## Condições

| Condição | Descrição |
|---|---|
| `v3` | padrão atual do bot |
| `v5_multiquery` | v5 congelada no commit `1e7644c`, sem mudança; referência descritiva, porque já foi reprovada no critério 3 do v4 |
| `v5_fixed` | v5 com as correções da V2 (abaixo), em módulos ou opções novas; os hashes da v5 continuam reproduzíveis |
| `v5_fixed_qwen36` | `v5_fixed` com o `qwen3.6` como único LLM; entra só se o P95 medido na calibração v4 for ≤ 45 s, sem esgotar a memória |

## V2: correções da v5 (desenvolvimento só nos 48 itens `development` do v4)

1. **Verificação tolerante do trecho literal:** o trecho é aceito se pelo menos 90% dos seus tokens
   de conteúdo aparecerem, em ordem, numa janela do chunk citado, em vez de exigir substring exata.
   O mínimo de 20 caracteres continua.
2. **Normalização de números** na regra de número ausente: "70%" = "70 por cento" = "setenta por
   cento", vírgula ou ponto decimal, milhar com ponto, "mil" e "milhões".
3. Nenhuma outra mudança de prompt ou de regra de agregação. Mudanças adicionais exigem um adendo
   neste protocolo antes da fase final.

Depois da iteração, código e prompts são congelados por hash em `evaluation/refinement_v6/freeze.json`.

## Execução final (única, em ordem)

1. Congelamento (`freeze.json`) e verificação do sha256 do suplemento reconstruído.
2. Nos 96 itens v4 (forma original), `v5_fixed` e, se houver, `v5_fixed_qwen36`. Isso é
   exploratório, porque o v4 já foi revelado, mas é necessário para checar o critério 3.
3. Nos 150 itens externos: as quatro condições, uma execução cada.

## Regra de decisão

Uma condição só substitui a v3 como padrão do bot se passar em **todos** os critérios abaixo.

**No v4 (96 itens):** os seis critérios de `evaluation/refinement_v5/PROTOCOL.md`, sem
flexibilizar: Δ macro-F1 ≥ +0,05 com limite inferior do IC > 0, consistência sob paráfrase ≥ a da
v3, queda de recall de `SUPPORTED` e de `REFUTED` ≤ 0,10, precisão de abstenção ≥ 0,50, falhas ≤ 2 e
P95 ≤ 45 s. A consistência sob paráfrase também exige as 192 paráfrases.

**No teste externo (150 itens), contra a v3:**

| Gate | Critério |
|---|---|
| X1 | Precisão das conclusões não inferior: Δ ≥ −0,02 e limite inferior do IC 95% ≥ −0,08 |
| X2 | Erro grave: taxa da candidata ≤ taxa da v3 + 0,02 |
| X3 | Cobertura: queda ≤ 0,10 |
| X4 | Falhas técnicas ≤ 2% e P95 ≤ 45 s |

**Desempate:** entre condições aprovadas, fica a de maior precisão das conclusões no teste
externo. Se a diferença for menor que 0,02, fica `v5_fixed`, que não depende do modelo de 23 GB.
Se nenhuma passar, a v3 continua padrão e o resultado entra no TCC como está.

## Ameaças à validade (declaradas antes)

- Gabarito externo sem revisão do projeto e mapeado por regra.
- `SUPPORTED` escasso.
- `MISLEADING` vem quase todo da fonte não redistribuível.
- Datas das checagens de 2017 a 2026, contra um corpus de 2026.
- Possível presença das checagens no pré-treino do Qwen.
- A análise binária esconde erros entre `MISLEADING` e `REFUTED`.
- O v4 continua exploratório.

## Adendo 1 (16/10/2026, antes de qualquer inferência e de qualquer código da V2)

**Fato observado** (releitura de resultados v5 já publicados, sem nova execução): as duas perdas de
`SUPPORTED` por verificação determinística que motivaram a V2 estão no holdout do v4. São elas
`ref4-0020` (número ausente) e `ref4-0049` (trecho não verificado). Na calibração há um único erro
de `SUPPORTED` (`ref4-0018`), e o próprio modelo o julgou `NOT_ADDRESSED`, sem rebaixamento. Por isso
a V2 não pode ser "desenvolvida na calibração" de forma informativa, e o critério 3 no v4 seria
circular para `v5_fixed`.

**Decisão aprovada pelo pesquisador:**

1. **As correções da V2 são definidas agora por princípio**, sem ajuste a dados:
   - **Trecho tolerante:** além da substring exata atual, o trecho é aceito se, com tokens
     alfanuméricos normalizados (`alnum_key` por palavra), a maior subsequência comum entre o trecho
     e o chunk citado cobrir pelo menos 90% dos tokens do trecho. O mínimo de 20 caracteres continua.
   - **Números equivalentes:** um número da proposição conta como presente se alguma forma
     equivalente estiver na evidência:
     - separador decimal com vírgula ou ponto;
     - separador de milhar com ponto ou espaço, ou sem separador;
     - "mil", "milhão" e "milhões" como multiplicadores;
     - "%", "por cento" e "porcento";
     - números por extenso de zero a vinte, dezenas até noventa e "cem".

   Os limiares (90%) e as listas acima ficam fixos; a calibração v4 só verifica que não há
   regressão (macro-F1 do `development` não menor que o da `v5_multiquery` e nenhuma falha nova).
2. **No v4, o critério 3 (queda de recall) fica descritivo** para `v5_fixed` e `v5_fixed_qwen36`,
   por circularidade. Os critérios 1, 2, 4, 5 e 6 continuam como gates nos 96 itens.
3. **A promoção passa a exigir** esses cinco critérios no v4 e os gates X1–X4 no teste externo, que
   é o único conjunto não visto. `v5_multiquery` continua sem possibilidade de promoção, porque já
   foi reprovada no critério 3 antes desta linha.
4. **Limitação declarada:** a perda de recall de `SUPPORTED` não pode ser confirmada em nenhum
   conjunto (12 itens no externo). O risco de conservadorismo fica coberto indiretamente pela
   cobertura (X3) e pela precisão das conclusões (X1).
