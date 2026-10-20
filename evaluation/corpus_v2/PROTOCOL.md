# Protocolo da Fase 21 — Corpus v2 (ADR-056)

Registrado em 20/10/2026, antes de baixar qualquer documento novo e antes de qualquer execução com o
corpus ampliado. Prazo de corte: **27/10/2026**. Se a execução única não terminar até lá, o corpus v1
continua padrão, e a fase entra no TCC como trabalho em andamento.

## Pergunta

Na execução única da Fase 20, a cascata C6 só chegou a uma conclusão em 35,2% das 304 alegações reais
do teste externo 2. A maior parte das abstenções vem da falta de evidência no corpus. A pergunta desta
fase é se **ampliar o corpus, sem mudar nenhuma linha da pipeline**, aumenta a cobertura em alegações
reais sem perder a precisão das conclusões nem a segurança (erro grave).

## O que muda e o que não muda

- **Muda:** só o corpus. O corpus v2 é o corpus v1 (80 documentos, 7.585 trechos) mais o lote 009,
  processado com o mesmo construtor, os mesmos parâmetros de segmentação e o mesmo BGE-M3.
- **Não muda:** a pipeline v7 (cascata C6), o `qwen3:8b` (`500a1f067a9f`), os prompts, o top 15, o
  roteamento e todos os arquivos de `evaluation/refinement_v7/verdict_freeze.json`. O corpus v1 fica
  preservado para reversão.

## Regra de seleção do lote 009 (fixada antes da busca de documentos)

1. **Tema:** só lacunas já previstas no plano de cobertura de setembro (`corpus/coverage_plan.csv`),
   escrito antes de qualquer conjunto externo existir. A justificativa do tema
   `alegacoes_causais_recorrentes` cita "autismo, infertilidade, óbitos, DNA, sobrecarga e
   composição"; no corpus v1 faltavam fontes diretas sobre DNA, óbitos, sobrecarga imunológica e a
   composição das vacinas em geral. O tema `vacinas_especificas` cita covid-19, e o corpus v1 não tinha
   nenhuma fonte de eficácia ou efetividade das vacinas contra covid-19.
2. **Fonte:** instituição oficial de saúde ou artigo revisado por pares.
3. **Licença clara:** domínio público do governo dos EUA ou licença Creative Commons declarada. Os
   documentos retidos em setembro por licença conflitante continuam fora (decisão do pesquisador em
   20/10).
4. **Nenhum texto de agência de checagem**, conforme o AGENTS.md.
5. **Cegueira aos itens:** a seleção não consultou o texto de nenhuma alegação do teste do C7 nem do
   teste externo 2, nem resultados por item. O que já era conhecido: os agregados públicos do
   `external2/build_report.json` (anos de 2020 a 2024, agências e categorias de cobertura temática) e
   as métricas agregadas da Fase 20.

## Lote 009 (candidatos)

| `document_id` | Fonte | Lacuna | Licença |
|---|---|---|---|
| `fda_common_vaccine_ingredients` | FDA, Common Ingredients in FDA-Approved Vaccines | composição | domínio público (EUA) |
| `fda_thimerosal_vaccines` | FDA, Thimerosal and Vaccines | composição | domínio público (EUA) |
| `cdc_multiple_vaccines_2024` | CDC, Multiple Vaccines at Once | sobrecarga | domínio público (EUA) |
| `cdc_covid_vaccine_basics_2024` | CDC, COVID-19 Vaccine Basics | DNA e mecanismo | domínio público (EUA) |
| `cdc_covid_vaccine_safety_2025` | CDC, COVID-19 Vaccine Safety | óbitos e eventos adversos | domínio público (EUA) |
| `mmwr_covid_non_covid_mortality_2021` | MMWR 70(43), Xu et al. | óbitos | domínio público (EUA) |
| `lancetid_covid_first_year_impact_2022` | Lancet Infect Dis, Watson et al. (PMC9225255) | óbitos evitados | CC BY 4.0 |
| `fph_covid_effectiveness_meta_2022` | Front Public Health, Rahmani et al. (PMC9459165) | eficácia covid-19 | CC BY 4.0 |
| `bmj_coronavac_older_adults_2021` | BMJ, Ranzani et al. (PMC8377801) | eficácia covid-19 no Brasil | CC BY-NC 4.0 |

Cada documento passa pela mesma revisão técnica dos lotes anteriores (hash, extração, alertas,
duplicatas) e é registrado em `corpus/reviews/batch_009.*`. Um documento reprovado sai **sem
substituição**, para não abrir uma segunda rodada de escolha.

## Condições e execução única

- **Referência:** C6 com o corpus v1, os registros já gravados na execução única de 20/10
  (`output/v7_runs/final/C6_*_final.jsonl`). Não são reexecutados.
- **Candidata:** C6 com o corpus v2, uma única execução no teste do C7 (207 itens) e no teste externo
  2 (304 itens), com o código, os conjuntos e o corpus v2 congelados por hash antes (`freeze.json`).

**Reuso declarado dos conjuntos.** Os dois conjuntos já foram usados na Fase 20 e não há outro
conjunto externo disponível a tempo (o feed do externo 2 foi esgotado pelas regras de construção).
Por isso a seleção de documentos é cega aos itens, a regra abaixo é fixada agora, e o TCC apresenta
esta fase como avaliação secundária, com o reuso explícito.

## Regra de decisão

O corpus v2 vira padrão se passar em **todos** os critérios, contra a referência, com bootstrap
pareado (10.000 reamostras, semente 42; por item no externo 2 e por família no C7):

| Critério | Condição |
|---|---|
| E1 | Cobertura no externo 2: Δ ≥ +0,03 e limite inferior do IC 95% > 0 |
| E2 | Precisão das conclusões no externo 2: limite inferior do IC 95% do Δ ≥ −0,05 |
| E3 | Erro grave no externo 2: Δ ≤ +0,01 |
| K1 | Macro-F1 no teste do C7: limite inferior do IC 95% do Δ ≥ −0,05 |
| K2 | Erro grave no teste do C7: Δ ≤ +0,02 |
| O1 | P95 ≤ 45 s e falhas técnicas ≤ max(2%, taxa da referência), nos dois conjuntos |

Se reprovar em qualquer critério, o corpus v1 continua padrão, e o resultado entra no TCC como está.

## Diagnósticos (descritivos, fora da regra)

- Cobertura por categoria temática do externo 2 (`covered`, `generic_vaccination`, `partial`,
  `not_covered`).
- Proporção de evidências citadas que vêm do lote 009.
- No C7, as trocas de `INSUFFICIENT_EVIDENCE` para um veredito conclusivo, reportadas à parte (ver
  ameaças).

## Ameaças à validade (declaradas antes)

- **Reuso dos conjuntos:** o efeito medido é condicionado a conjuntos já vistos em agregado.
- **Gabarito do C7 derivado do corpus v1:** um item marcado `INSUFFICIENT_EVIDENCE` pode passar a ter
  evidência real no corpus v2, e o acerto vira "erro". Isso penaliza o corpus v2, por isso o K1 é de
  não inferioridade.
- **Ruído de execução:** cerca de 10 em 193 vereditos mudam entre repetições da mesma configuração;
  a referência não é reexecutada.
- **Idioma:** os documentos novos são em inglês, como boa parte do corpus v1; as alegações são em
  português.
- **Temporalidade:** páginas institucionais mudam; vale o conteúdo identificado pelo SHA-256 baixado.
