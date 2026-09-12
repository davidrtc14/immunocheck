# Lote documental 006 — parecer para aprovação

Preparado em 12/09/2026. Nenhum documento deste lote foi promovido ao corpus:
as decisões abaixo são propostas e dependem de aprovação conjunta do autor. A
aprovação valerá somente para os bytes identificados pelos SHA-256 em
`batch_006.csv`.

## Resultado executivo

- Dez candidatos foram examinados para comunicação, alegações causais, populações
  especiais, eficácia e epidemiologia.
- Nove XML JATS integrais foram coletados pelo serviço oficial Europe PMC. Eles
  somam 430.407 caracteres e 434 chunks potenciais, sem duplicatas exatas dentro
  do lote ou contra o corpus validado.
- **Propõe-se aprovar oito documentos**, somando 400 chunks potenciais: seis têm
  licença Creative Commons e dois contêm concessão gratuita e expressa da Elsevier
  para reutilização em pesquisa enquanto o COVID-19 Resource Centre estiver ativo.
- **Propõe-se reter dois documentos:** um XML da Revista Panamericana não declara
  licença nos bytes coletados; o manuscrito sobre hospitalizações por rotavírus
  retornou HTTP 404 e não possui bytes auditáveis.

## Documentos propostos para aprovação

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

## Material proposto para retenção

| Documento | Motivo |
|---|---|
| Epidemiologia da coqueluche na América Latina e Caribe — 1980–2015 | O XML foi coletado e é tecnicamente íntegro, mas não traz licença ou permissão explícita; gratuidade de leitura não autoriza reutilização integral. |
| Hospitalizações globais por rotavírus em 2019 | O registro é um manuscrito de autor e o endpoint oficial de XML integral retornou HTTP 404; não há recibo, extração ou licença auditável. |

## Auditoria técnica e jurídica

As oito aprovações propostas foram obtidas como XML JATS integral pelo Europe PMC.
Quatro documentos declaram CC BY 4.0; um declara CC BY-NC 4.0; e o artigo da JAMA
declara CC BY sem explicitar a versão no XML. Os dois artigos da revista *Vaccine*
preservam nos próprios bytes a concessão gratuita da Elsevier para reutilização e
análise em pesquisa, por qualquer meio, com atribuição, enquanto o COVID-19
Resource Centre permanecer ativo. Essa condição temporal deve acompanhar a
proveniência e ser revalidada antes de eventual redistribuição externa.

O aviso `all rights reserved` do artigo sobre fertilidade não foi ignorado: a
aprovação proposta limita-se à concessão de pesquisa que aparece conjuntamente no
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

## Estado

**Aguardando aprovação humana conjunta.** Se as decisões propostas forem aprovadas,
somente os oito documentos marcados `approve` serão promovidos, versionados,
indexados e testados. Os outros dois continuarão candidatos e retidos.
