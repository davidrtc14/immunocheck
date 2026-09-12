# Lote documental 006 — decisão e publicação

Preparado e aprovado em 12/09/2026. O autor aprovou conjuntamente oito documentos
e manteve dois retidos. A decisão vale somente para os bytes identificados pelos
SHA-256 em `batch_006.csv`.

## Resultado executivo

- Dez candidatos foram examinados para comunicação, alegações causais, populações
  especiais, eficácia e epidemiologia.
- Nove XML JATS integrais foram coletados pelo serviço oficial Europe PMC. Eles
  somam 430.407 caracteres e 434 chunks potenciais, sem duplicatas exatas dentro
  do lote ou contra o corpus validado.
- **Foram aprovados oito documentos**, somando 400 chunks: seis têm
  licença Creative Commons e dois contêm concessão gratuita e expressa da Elsevier
  para reutilização em pesquisa enquanto o COVID-19 Resource Centre estiver ativo.
- **Foram retidos dois documentos:** um XML da Revista Panamericana não declara
  licença nos bytes coletados; o manuscrito sobre hospitalizações por rotavírus
  retornou HTTP 404 e não possui bytes auditáveis.

## Documentos aprovados

| Documento | Tema | Volume | Utilidade e cuidado obrigatório |
|---|---|---:|---|
| Intervenções contra desinformação vacinal | Comunicação e ética | 69 chunks | Nenhuma intervenção mediu adesão real; evidência majoritariamente dos EUA, heterogênea e com extração por um único revisor. |
| Vacinação e doenças autoimunes | Alegações causais | 33 chunks | O agrupamento de 144 estudos não pode negar eventos raros específicos nem ser extrapolado para vacinas ou doenças não estudadas. |
| Vacinas contra covid-19 e fertilidade | Alegações causais | 31 chunks | Evidência até junho de 2022; 93,1% dos estudos tinham qualidade pobre ou moderada e o seguimento máximo foi de nove meses. |
| Vacinação em adultos com doenças reumáticas autoimunes | Populações especiais | 103 chunks | Evidência clínica é escassa e muitos estudos não têm poder para segurança; distinguir doença, terapia, vacina e desfecho. |
| Idade da primeira dose contra sarampo | Eficácia e imunogenicidade | 55 chunks | Apenas 27% dos estudos epidemiológicos tinham baixo risco de viés; calendário depende do nível de transmissão e da norma vigente. |
| Surtos de sarampo na Etiópia | Epidemiologia | 28 chunks | Oito investigações, heterogeneidade alta e viés de publicação; taxas não são transferíveis ao Brasil. |
| Carga de coqueluche em países de renda baixa e média | Epidemiologia | 53 chunks | Dados escassos e concentrados em países de renda média alta, com diferenças de diagnóstico, vigilância e cobertura. |
| Carga global de rotavírus em menores de cinco anos | Epidemiologia | 28 chunks | Resultados do GBD são estimativas modeladas com intervalos de incerteza, não contagens individuais observadas. |

## Material retido

| Documento | Motivo |
|---|---|
| Epidemiologia da coqueluche na América Latina e Caribe — 1980–2015 | O XML foi coletado e é tecnicamente íntegro, mas não traz licença ou permissão explícita; gratuidade de leitura não autoriza reutilização integral. |
| Hospitalizações globais por rotavírus em 2019 | O registro é um manuscrito de autor e o endpoint oficial de XML integral retornou HTTP 404; não há recibo, extração ou licença auditável. |

## Auditoria técnica e jurídica

As oito fontes aprovadas foram obtidas como XML JATS integral pelo Europe PMC.
Quatro documentos declaram CC BY 4.0; um declara CC BY-NC 4.0; e o artigo da JAMA
declara CC BY sem explicitar a versão no XML. Os dois artigos da revista *Vaccine*
preservam nos próprios bytes a concessão gratuita da Elsevier para reutilização e
análise em pesquisa, por qualquer meio, com atribuição, enquanto o COVID-19
Resource Centre permanecer ativo. Essa condição temporal deve acompanhar a
proveniência e ser revalidada antes de eventual redistribuição externa.

O aviso `all rights reserved` do artigo sobre fertilidade não foi ignorado: a
aprovação limita-se à concessão de pesquisa que aparece conjuntamente no
documento e ao uso local, acadêmico e não comercial. Arquivos brutos, textos e
chunks continuam ignorados pelo Git; a licença MIT do código não relicencia as
fontes.

## Guardrails metodológicos

- Ausência de associação agrupada não demonstra risco zero e não elimina eventos
  adversos raros já reconhecidos para combinações específicas de vacina e desfecho.
- Resultados sobre autoimunidade devem preservar vacina, doença, janela temporal,
  idade, desenho do estudo e risco de viés.
- `Não houve diferença estatisticamente significativa` não equivale a comprovar
  equivalência ou a excluir efeitos de longo prazo sobre fertilidade.
- Imunogenicidade, eficácia, efetividade, cobertura e carga de doença são desfechos
  diferentes; não serão apresentados como sinônimos.
- Recomendações sobre idade da vacina contra sarampo dependem da transmissão local
  e não substituem o calendário brasileiro vigente.
- Estimativas de surtos da Etiópia e de países de renda baixa e média não serão
  convertidas em taxas brasileiras.
- Números do GBD são saídas de modelos e devem manter intervalos de incerteza,
  premissas e ano de referência.
- Estratégias de comunicação serão usadas para transparência e autonomia, não para
  manipular, constranger ou censurar usuários; efeitos contraproducentes precisam
  ser reconhecidos.
- Nenhuma mensagem real de usuário foi armazenada ou usada como dado de pesquisa,
  e nenhuma alegação do conjunto de teste foi criada neste lote.

## Reprodução

```powershell
.\.venv\Scripts\python.exe scripts\audit_corpus_batch.py --batch 006
```

O comando registra falha enquanto o manuscrito de rotavírus permanecer sem recibo.
Isso representa a retenção segura da fonte, não falha dos nove documentos auditados.
O JSON público contém apenas metadados, hashes e métricas; os textos integrais ficam
locais e ignorados pelo Git.

## Decisão humana

O autor aprovou conjuntamente os oito documentos recomendados e confirmou a
retenção dos outros dois. `batch_006.csv` registra `project_author`, a data da
decisão e uma justificativa explícita por candidato. Somente as oito fontes
aprovadas foram promovidas a `validated`; as duas retidas continuam `candidate`.

## Publicação e validação

A publicação gerou a versão
`sha256:253c380014fb96f32be9dd3f47629ee055d1218bff85c594c757f8891d6754cb`,
com **58 documentos, 6.479 chunks e 6.479 embeddings**. O BGE-M3 reutilizou os
6.079 vetores anteriores e calculou 400 novos em CPU, offline, em 264,25 segundos.

Os embeddings foram importados antes da ativação transacional no PostgreSQL. A
conferência direta confirmou 58 documentos, 6.479 chunks e 6.479 embeddings na
versão ativa. Uma busca exata por cosseno, usando um chunk da revisão sobre vacinas
e doenças autoimunes como consulta, devolveu o próprio chunk em primeiro lugar com
similaridade 1,000000.

Oito consultas temáticas dirigidas recuperaram cada documento novo em primeiro
lugar no ranking híbrido BM25 + BGE-M3 + RRF. Esse ensaio confirma a acessibilidade
das fontes e não substitui a avaliação de retrieval com consultas e julgamentos
humanos congelados.

A regressão final aprovou 182 testes na suíte geral e um teste adicional em banco
PostgreSQL exclusivo e descartável; um teste de integração aparece como ignorado na
suíte geral quando a URL exclusiva não é fornecida. O Ruff foi executado sem
apontamentos. A base temporária foi removida após o ensaio.
