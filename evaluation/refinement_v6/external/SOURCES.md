# Teste externo congelado — Fase 18 (ADR-051)

Conjunto de alegações sobre vacinação humana com gabarito vindo de agências de
checagem, montado a partir de datasets públicos, **sem curadoria manual do
pesquisador** e **sem nenhuma inferência do ImmunoCheck** (pipeline, LLM ou
embeddings não foram executados sobre estes itens). Construído em 2026-10-16 por
`scripts/build_external_testset.py` (assistido por IA) e congelado em `freeze.json`.

## Artefatos

| Arquivo | Conteúdo | Versionado |
|---|---|---|
| `items.jsonl` | 54 itens completos, de fontes com licença MIT para os dados | sim |
| `supplement_manifest.jsonl` | 96 itens de fonte **sem licença de redistribuição**: URL da checagem, rótulo mapeado, tema, cobertura e `claim_sha256`, **sem o texto da alegação** | sim |
| `output/external_v6/items_supplement.jsonl` | os mesmos 96 itens com o texto, reconstruídos localmente | **não** (`output/` é ignorado) |
| `build_report.json` | contagens de candidatos, exclusões por motivo e distribuições | sim |
| `freeze.json` | commits das fontes, sha256 dos brutos, de `items.jsonl`, do manifesto, do script e do suplemento reconstruído | sim |

Reconstrução e conferência (baixa os brutos nos commits fixados para
`output/external_v6/raw/`, confere os sha256, refaz a seleção e compara com os
arquivos versionados e com o hash do suplemento):

```powershell
$env:PYTHONPATH = "src"; .\.venv\Scripts\python.exe scripts\build_external_testset.py
```

O conjunto completo para avaliação é `items.jsonl` + `items_supplement.jsonl`
(150 itens, IDs `ext6-*` e `ext6s-*`).

## Fontes investigadas

| Fonte | URL | Licença | Ano | Rótulos | Alegações sobre vacina* | Decisão |
|---|---|---|---|---|---|---|
| X-FACT (subconjunto `pt`: Lupa/piauí, Polígrafo, Aos Fatos) | https://github.com/utahnlp/x-fact (commit `c58b1ea`) | MIT (repositório e dados) | 2021 (checagens 2015–2020) | true, mostly true, partly true/misleading, mostly false, false, complicated, other | 95 | **usada, versionada** |
| FACTCK.BR (Aos Fatos, Lupa, Truco; ClaimReview) | https://github.com/jghm-f/FACTCK.BR (commit `57e25d7`) | MIT | 2019 (checagens 2016–2019) | rótulos textuais das agências (`alternativeName`) | 8 | **usada, versionada** |
| FACTCK.BR-extended (`datasets/FACTCKBR_updated.tsv`; Lupa, Pública, Aos Fatos, Observador, AFP, Estadão, UOL, Comprova…) | https://github.com/Residencia-em-IA-Grupo-6/FACTCK.BR-extended (commit `b19074e`) | código MIT; README: "os dados originais de checagem pertencem e são creditados às respectivas agências" | 2026 (checagens 2016–2026) | rótulos textuais das agências, às vezes frase completa | 417 | **usada só como referência + reconstrução** |
| FACTCK.BR-extended `saude_consolidado_unificado.tsv` | mesmo repositório | idem | 2026 | só `is_fake` booleano | 1 123 | descartada: rótulo binário não distingue MISLEADING e inclui notícias da EBC como "verdadeiras" |
| Central de Fatos / FactCenter (Couto et al., SBBD 2021; JIDM 2022) | https://hdl.handle.net/1843/74096 | não informada | 2021 | não documentado | — | descartada: dados não disponíveis para download ("Download data is not yet available") |
| FakeCovid (Shahi & Nandini, 2020) | https://zenodo.org/records/3965871 | conflitante (CC BY 4.0 vs CC0 em espelhos) | 2020 (jan–jul/2020) | rótulos de 92 agências | não contado | descartada: período anterior às vacinas de COVID-19, licença não confirmada na fonte primária |
| portuguese-fact-checking (HF; MuMiN-PT, COVID19.BR, Fake.br) | https://huggingface.co/datasets/ju-resplande/portuguese-fact-checking | MIT | 2023 | true/fake | não contado | descartada: posts de redes sociais e mensagens de WhatsApp de pessoas reais (restrição de dados de usuários) e notícias completas, não alegações curtas; só binário |
| Fake.br, FakeRecogna | (artigos PROPOR 2018/2022/2024) | variada | 2018–2024 | fake/true | — | descartadas: notícias completas, não alegações; rótulo binário |
| FakenewsBR (AKCIT) | https://github.com/AKCIT-FN/fakenews-data | MIT (repositório) | 2025 | fake/true | — | descartada: agrega os corpora acima, sem campo de alegação |

\* Contagem pelo filtro de palavras-chave (`vacin`, `imuniza…`), antes das demais regras.

## Filtros (ordem de aplicação)

1. **Vacinação humana**: alegação contém `vacin*` ou `imuniza(ção|nte|r…)` e não
   menciona animais (cães, gado, aftosa, veterinária…). Alegações em inglês ficam de fora
   porque `vaccine` não casa com `vacin`.
2. **Forma**: 25–280 caracteres; sem pergunta final; sem truncamento da fonte
   (`......`); no máximo um fragmento `(...)`/`[...]`; sem texto do veredito embutido
   ("É falso que…", "Confira…").
3. **Artefato de mídia**: descarta alegações cujo sujeito é vídeo, foto, áudio, post,
   notícia, artigo ou "circula nas redes sociais" — o veredito depende da autenticidade da
   mídia, não de conhecimento sobre vacinas.
4. **Ator político**: descarta alegações que citam políticos, partidos, STF/CPI ou
   eleições, e checagens cuja URL indica discurso/campanha (lula, bolsonaro, cpi, debate,
   candidatos, eleições) — o gabarito depende de fatos políticos.
5. **Rótulo mapeável** (tabela abaixo); sem mapeamento → descarte.
6. **Duplicata de avaliação existente**: comparada com as 641 alegações distintas de todos
   os JSON/JSONL de `evaluation/` (inclui `refinement_v4/items.jsonl`,
   `refinement_v5/paraphrases.jsonl`, `end_to_end/` e resultados). Critério: Jaccard de
   tokens de conteúdo ≥ 0,6 **ou** razão do `difflib` ≥ 0,8. Nenhum candidato foi
   descartado por isso (as alegações do projeto foram escritas pelo pesquisador).
7. **Quase-duplicatas internas**: Jaccard ≥ 0,7 ou `difflib` ≥ 0,85; mantém-se o
   primeiro pela prioridade FACTCK.BR → X-FACT → FACTCK.BR-extended; grupos com rótulos
   divergentes são descartados inteiros.
8. **Revisão por amostragem (IA)**: duas exclusões pontuais, listadas com motivo em
   `MANUAL_EXCLUSIONS` no script — um fragmento de fala sem sujeito e uma linha da fonte
   em que a alegação vacinal está associada a uma checagem sobre uma rodovia.
9. **Teto de tamanho (150)**: todos os itens versionáveis entram; do suplemento, todo
   SUPPORTED entra e o espaço restante é dividido igualmente entre MISLEADING e REFUTED,
   escolhidos pela ordem do sha256 da referência de origem (sem olhar o texto).

| Motivo | Itens |
|---|---:|
| ator político | 46 |
| longa demais | 25 |
| quase-duplicata interna | 19 |
| truncada pela fonte | 15 |
| artefato de mídia | 9 |
| rótulo sem mapeamento | 8 |
| grupo de duplicatas com rótulos divergentes | 4 |
| pergunta | 4 |
| fragmentada | 2 |
| revisão por amostragem | 2 |
| fora da amostra pelo teto de 150 | 236 |

## Mapeamento de rótulos

| Rótulo da fonte | Veredito ImmunoCheck |
|---|---|
| X-FACT `true`, `mostly true`; agências "Verdadeiro", "Verdadeiro, mas" | `SUPPORTED` |
| X-FACT `false`, `mostly false`; agências "Falso", "Errado", "Fake", frases "FALSO: …", "É FALSO…", "São FALSAS…" | `REFUTED` |
| X-FACT `partly true/misleading`; agências "Enganoso", "Enganador", "Exagerado", "Distorcido", "Sem contexto", "Fora de contexto", "Subestimado", "Impreciso", "Não é bem assim", frases "ENGANOSO: …", "É ENGANOSO…" | `MISLEADING` |
| X-FACT `complicated/hard to categorise`, `other`; "Insustentável", "Impossível provar", "Discutível", "Ainda é cedo para dizer", "De olho", "Contextualizando", frases que não começam pelo veredito | descartado |

`mostly true`/"Verdadeiro, mas" foi mapeado para SUPPORTED (imprecisão menor, sem
distorção material, conforme o guia de anotação); `mostly false` para REFUTED (o guia
manda preferir REFUTED quando não há parte factual relevante sustentada). Nenhum rótulo
externo foi mapeado para `INSUFFICIENT_EVIDENCE`, porque essa classe é relativa ao corpus
do ImmunoCheck, não ao mundo.

## Contagens finais

| | SUPPORTED | MISLEADING | REFUTED | Total |
|---|---:|---:|---:|---:|
| `items.jsonl` (X-FACT 48 + FACTCK.BR 6) | 11 | 6 | 37 | 54 |
| suplemento (FACTCK.BR-extended) | 1 | 47 | 48 | 96 |
| **total** | **12** | **53** | **85** | **150** |

- Cobertura temática heurística pelo corpus (`corpus_topic_coverage`): 103 `covered`,
  41 `generic_vaccination`, 2 `partial`, 4 `not_covered` (hantavírus, zika, vacina terapêutica contra câncer, HIV).
- Datas das checagens: 2017–2026, concentradas em 2020 (45), 2021 (19) e 2023 (17).
- 9 itens marcados `possible_individual_event` em `external_flags`.

## Esquema

Mesmo esquema de `evaluation/refinement_v4/items.jsonl` (carregável por
`load_end_to_end_items`), com `split = "test"` em todos os itens e `claim_family`
própria por item (`external_<item_id>`), sem colisão com famílias de desenvolvimento.
Diferenças deliberadas:

- `status = "draft"`, `rationale`/`reviewer`/`primary_label` nulos e `atomic = false`:
  o validador exige `evidence_chunk_ids` para itens `reviewed` conclusivos, e aqui não há
  evidência do corpus nem revisão humana do projeto; a atomicidade não foi avaliada.
  Consequência: carregadores que usam `require_reviewed=True` recusarão este arquivo; o
  executor da Fase 18 precisa carregá-lo com `require_reviewed=False` e não pode usar
  métricas de citação baseadas em `evidence_chunk_ids`.
- Campos extras (ignorados pelo carregador): `external_source`, `external_agency`,
  `external_source_label`, `external_claim_date`, `external_review_url`,
  `corpus_topic_coverage` e `external_flags`.

## Restrição do corpus (AGENTS.md)

`corpus/catalog.csv` (114 documentos) e o manifesto local
`corpus/processed/manifest.json` (80 documentos) não têm nenhuma URL de agência de
checagem (lista em `FACT_CHECKER_DOMAINS`; verificado também pelo teste). Uma busca
textual em `corpus/processed/chunks.jsonl` (7 585 chunks) por nomes de agências encontrou
apenas a expressão "ater-se aos fatos" no manual do MS, que não se refere à Aos Fatos. O
corpus contém notas da Anvisa e do MS que desmentem boatos (ex.:
`anvisa_influenza_componentes_2026`, `anvisa_vacinas_nao_experimentais_2026`,
`ms_vacinas_autismo_faq`); são fontes oficiais, não agências de checagem, mas podem
tratar dos mesmos boatos — registrar isso na análise.

## Limitações

- **SUPPORTED é escasso (12 itens, 8%)**: agências checam sobretudo boatos falsos; o
  recall de SUPPORTED terá intervalo de confiança largo. **MISLEADING** vem quase todo da
  fonte não redistribuível (47 de 53).
- O gabarito é de **mundo real**, na data da checagem; o ImmunoCheck responde com o
  corpus de 2026. Alegações temporais de 2020 (estado de desenvolvimento de vacinas,
  coberturas) podem ter mudado de verdade; eventos individuais (mortes atribuídas a
  vacinas) tendem a gerar `INSUFFICIENT_EVIDENCE` no sistema, o que conta como erro
  contra um gabarito REFUTED. Recomenda-se relatar também o resultado estratificado por
  `corpus_topic_coverage` e `external_flags`.
- Mapeamento por regra, sem revisão humana do projeto; X-FACT já traz rótulos
  normalizados pelos autores. Filtros e temas são heurísticos (regex).
- Possível contaminação: checagens públicas de 2015–2024 podem estar no pré-treino do
  Qwen3-8B.
- A fonte FACTCK.BR-extended continua sendo atualizada; a reconstrução depende do commit
  `b19074e` continuar acessível no GitHub (os sha256 dos brutos detectam alteração).
- Atribuição: X-FACT (Gupta & Srikumar, ACL 2021), FACTCK.BR (Moreno & Bressan, WebMedia
  2019) e FACTCK.BR-extended; as checagens pertencem às respectivas agências.
