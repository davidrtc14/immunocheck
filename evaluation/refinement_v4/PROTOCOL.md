# Protocolo do conjunto v4 (Fase A do plano de melhorias v4)

## Objetivo

Fornecer um conjunto novo, maior e menos sujeito a atalhos de redação do que o confirmatório
v3 (32 itens, 8 famílias), para calibrar e depois confirmar uma eventual pipeline v4. O
teste histórico da v1 e o confirmatório v3 não são reutilizados.

## Estrutura

- 96 itens, 24 famílias; cada família tem exatamente um item por classe
  (`SUPPORTED`, `REFUTED`, `MISLEADING`, `INSUFFICIENT_EVIDENCE`), logo 24 por classe.
- Calibração (`split: development`): 12 famílias, 48 itens. Pode orientar escolhas de
  retrieval e de abstenção (Fases C e D).
- Holdout (`split: test`): 12 famílias, 48 itens. **Lacrado**: não é consultado por nenhum
  experimento até a Fase F, que o executa uma única vez com configuração congelada.
- Famílias e alegações são novas: o validador rejeita nomes de família e textos já presentes
  em qualquer `.jsonl` de `evaluation/`.
- `MISLEADING` é construído como parte sustentada + extrapolação, omissão de condição ou
  generalização que a fonte desmente; não segue um único molde (há alegações com e sem
  conectivos causais).
- `INSUFFICIENT_EVIDENCE` tem dois subtipos (`origin_type`): `abstention_out_of_corpus`
  (14 itens: afirmação específica ausente das fontes) e `abstention_individual_event`
  (10 itens: relato individual sem identificação).
- Oito itens (`origin_type: public_pattern_rewritten`) reescrevem padrões genéricos de
  desinformação sobre vacinas, de autoria do pesquisador. Nenhum texto de verificadores de
  fatos foi consultado ou copiado.
- Cada item conclusivo cita `chunk_id` exatos do corpus versionado
  (`corpus/processed/chunks.jsonl`); o validador confere a existência dos IDs.
- Itens `REFUTED`/`MISLEADING` derivados de `anvisa_influenza_componentes_2026` e
  `ms_vacinas_autismo_faq` (páginas "contra fake news") foram evitados de propósito.

## Curadoria e limites de validade

Gabarito de rótulo, justificativa e evidência definido pelo pesquisador com apoio de IA antes
de qualquer inferência (mesma política da ADR-040). **Não há revisor externo nem validação
clínica.** A segunda anotação independente (≥ 50%) está preparada em
`second_annotation/participant/` (48 itens, 12 famílias, cego), mas **foi dispensada por decisão do pesquisador em 13/10/2026** (prazo do TCC), sem concordância reportada;
só poderia ser descrita como realizada depois que um revisor humano devolver o formulário e a
concordância for calculada com `annotation_agreement.py`.

A busca de evidências usou BM25 e expressões regulares sobre o corpus; nenhuma busca densa foi
usada na anotação, mas a escolha dos trechos pode favorecer sistemas lexicais. Métricas de
retrieval no conjunto devem ser lidas com essa ressalva.

## Gate de atalhos lexicais (A4)

Pré-registrado antes de executar: o baseline TF-IDF + regressão logística (validação cruzada
agrupada por família, 5 folds, somente calibração) deve ter macro-F1 ≤ 0,45 (acaso = 0,25).

Histórico (nenhuma execução do sistema ImmunoCheck foi feita em nenhuma iteração):

| Iteração | Macro-F1 do baseline | IC 95% (família) | Gate |
|---|---|---|---|
| 1 (redação inicial) | 0,558 | 0,459–0,646 | reprovado |
| 2 (redação revisada) | 0,328 | 0,204–0,429 | aprovado |

A iteração 1 expôs atalhos: quase todo `MISLEADING` usava "então/portanto", as abstenções
usavam anos futuros ou primeira pessoa, e `REFUTED` usava "nunca/nenhuma". Reescreveram-se 47
alegações para diversificar estrutura e tempo verbal e conferiram-se, por regex, as afirmações
de abstenção contra o corpus. O resultado da iteração 1 foi preservado em
`results/lexical_baseline_calibration_iter1.json`. Como a segunda iteração foi ajustada contra o
próprio baseline, o gate comprova apenas ausência de atalho lexical *forte* na calibração, e o
holdout deve ser verificado uma única vez, no momento da Fase F (treino na calibração, teste no
holdout), sem reescrita posterior.

## Critério de promoção de retrieval (Fase C)

Antes de qualquer experimento da Fase C: uma técnica só é promovida se melhorar
Doc-Recall@15 e/ou nDCG@10 sobre `dense_top15` com IC 95% percentil pareado por família
estritamente acima de zero na calibração (`results/retrieval_ablation_calibration.json`) e se a
latência P95 de texto/link ficar ≤ 45 s. Resultados negativos serão relatados.

## Imutabilidade

`items.jsonl` e este protocolo são registrados em `manifest.json` com SHA-256. Alterar itens
da calibração ou do holdout depois do manifesto cria uma nova versão do conjunto e invalida
qualquer resultado anterior sobre ele.

## Resultado da ablação de retrieval na calibração (A2, 13/10/2026)

36 consultas conclusivas, 12 famílias, alegação crua como consulta
(`results/retrieval_ablation_calibration.json`). Nenhuma condição superou `dense_top15`
pelo critério pré-registrado: BM25 e híbrido RRF ficaram abaixo em nDCG@10 (IC do delta
abaixo de zero); `dense30_rerank15` teve Doc-Recall@15 +0,042 (IC +0,000 a +0,125) e nDCG@10
−0,031 (IC −0,182 a +0,137), logo inconclusivo, com mediana de 14,1 s por consulta. Há efeito
de teto: o denso já cobre 93% dos documentos anotados em 15 chunks. Conclusão: na calibração v4
não há ganho demonstrado de reranker nem de híbrido; C1 não é promovido por este critério.
