# Lote documental 009 — corpus v2 (ADR-056)

Preparado em 20/10/2026 pela regra de seleção de `evaluation/corpus_v2/PROTOCOL.md`, registrada antes
dos downloads. **Aprovado pelo autor em 20/10/2026 (os nove documentos).** A decisão vale somente para os bytes identificados pelos
SHA-256 em `batch_009.csv`.

## Resultado executivo

- Nove candidatos, todos para lacunas já previstas no plano de cobertura de setembro: composição (2),
  sobrecarga imunológica (1), DNA e mecanismo (1), óbitos (3) e eficácia das vacinas contra covid-19
  (2, um deles do Brasil).
- Os nove foram baixados, tiveram o hash conferido e passaram na extração: 256.378 caracteres e 260
  chunks potenciais, sem alerta técnico, sem caractere de substituição e sem duplicata no lote ou
  contra o corpus validado.
- **Os nove foram aprovados**, respeitando os limites abaixo. O corpus passa de 80 para 89
  documentos validados.

## Documentos

| Documento | Lacuna | Chunks | Licença/base | Limite principal |
|---|---|---:|---|---|
| FDA — Common Ingredients in FDA-Approved Vaccines | composição | 9 | domínio público (governo dos EUA) | Produtos e quantidades dos EUA. |
| FDA — Thimerosal and Vaccines | composição | 22 | domínio público (governo dos EUA) | Formulações dos EUA, mutáveis no tempo. |
| CDC — Multiple Vaccines at Once | sobrecarga | 6 | domínio público (governo dos EUA) | Calendário dos EUA, não do PNI. |
| CDC — COVID-19 Vaccine Basics | DNA e mecanismo | 10 | domínio público (governo dos EUA) | Recomendações dos EUA em revisão desde 2025. |
| CDC — COVID-19 Vaccine Safety | óbitos e eventos adversos | 45 | domínio público (governo dos EUA) | Relatos ao VAERS não provam causalidade; usar para segurança, não para indicação. |
| MMWR 70(43) — vacinação e mortalidade não covid | óbitos | 22 | domínio público (governo dos EUA) | Coorte observacional; possível viés de vacinado saudável. |
| Lancet Infect Dis — impacto global do 1º ano de vacinação | óbitos evitados | 42 | CC BY 4.0 (declarada no XML) | Estimativas modeladas, não contagens observadas. |
| Front Public Health — efetividade das vacinas covid-19 | eficácia covid-19 | 57 | CC BY 4.0 (declarada no XML) | Variantes anteriores à ômicron; heterogeneidade. |
| BMJ — CoronaVac em idosos no Brasil | eficácia covid-19 no Brasil | 47 | CC BY-NC 4.0 (declarada no XML) | Idosos de São Paulo sob a variante gama; há errata. |

## Coleta

- As páginas do CDC recusavam o user agent anterior do coletor (HTTP 403). O coletor passou a se
  identificar como `ImmunoCheck-TCC/0.1 (+https://github.com/davidrtc14/immunocheck)`, com URL de
  contato, sem se passar por navegador. A verificação TLS continua obrigatória; a falha de TLS do FDA
  foi transitória e não se repetiu.
- A URL catalogada da página "Multiple Vaccines at Once" estava desatualizada (404); foi corrigida
  para o endereço atual da mesma página.

## Independência, conflitos e triangulação

- O estudo de modelagem do Lancet declara financiamento do MRC, da OMS, da Gavi e da Fundação Gates.
  Os números de óbitos evitados devem ser apresentados como estimativas de modelo.
- O estudo da CoronaVac declara não ter financiamento externo; um dos autores é apoiado pela Fiocruz.
- Fontes dos EUA não substituem as recomendações do PNI; quando houver conflito, prevalecem as fontes
  brasileiras do corpus.
- Nenhum documento é de agência de checagem de fatos.

## Auditoria

Métricas e hashes em `batch_009.audit.json`; textos extraídos ficam só em `corpus/raw/reviews/`, fora
do Git.
