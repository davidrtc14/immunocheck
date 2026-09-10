# Lote documental 004 — aprovação e publicação

Preparado e aprovado pelo autor em 09/09/2026; publicado em 10/09/2026. A
aprovação vale somente para os bytes identificados pelos SHA-256 em
`batch_004.csv`.

## Resultado executivo

- 12 candidatos foram examinados, com prioridade para eficácia, alegações causais,
  populações especiais e vacinas específicas.
- Dez documentos foram coletados e extraídos; duas páginas do CDC recusaram a
  coleta automatizada com HTTP 403.
- **Oito documentos foram aprovados:** quatro artigos científicos integrais,
  uma revisão sobre vacinação na gestação, dois relatórios da Conitec e a revisão
  final da OMS sobre vacinas, tiomersal e autismo.
- Os oito somam 319 páginas/unidades documentais, 959.669 caracteres e 1.061 chunks
  potenciais. Quatro unidades são artigos XML JATS; 315 são páginas físicas de PDF.
- **Quatro itens permaneceram retidos:** AHRQ pela restrição da rota de
  distribuição automatizada, HPV pela ausência de licença aberta explícita e duas
  páginas do CDC por falta de bytes auditáveis.
- Não há duplicatas exatas dentro do lote nem contra o corpus validado.

## Documentos aprovados

| Documento | Tema | Volume | Utilidade e cuidado obrigatório |
|---|---|---:|---|
| Revisão BMJ sobre adjuvantes de alumínio | Alegações causais | 59 chunks | Avalia desfechos separadamente: ausência de suporte para danos graves não apaga evidência de nódulos locais incomuns. |
| Revisão MDPI sobre vacinação covid-19 e reprodução assistida | Alegações causais | 47 chunks | Escopo é reprodução assistida, com estudos limitados e heterogêneos; não generalizar para fertilidade populacional ou outras vacinas. |
| Meta-análise da TAK-003 | Eficácia e imunogenicidade | 36 chunks | Preservar sorostatus, sorotipo, idade, doses e heterogeneidade; diretriz brasileira prevalece para recomendação. |
| Revisão/meta-regressão global de rotavírus | Eficácia e imunogenicidade | 40 chunks | Separar eficácia de ensaio, efetividade observada e previsões do modelo por país. |
| Revisão viva de vacinas covid-19 na gestação | Populações especiais | 20 páginas / 95 chunks | Evidência em 177 estudos, mas com certeza baixa a muito baixa e recorte até outubro de 2023. |
| Conitec nº 871 — TAK-003 | Vacinas específicas | 123 páginas / 295 chunks | Separar submissão do demandante, síntese GRADE, análise econômica, consulta pública e decisão. |
| Conitec nº 975 — VSR em gestantes | Vacinas específicas | 116 páginas / 308 chunks | Preservar idade gestacional, desfechos infantis, GRADE e conflitos da submissão. |
| OMS 2026 — vacinas, tiomersal e autismo | Alegações causais | 56 páginas / 181 chunks | Edição final sob CC BY-NC-SA 3.0 IGO, distinta do rascunho de 2025 rejeitado por restrição de uso. |

## Material retido

| Documento | Motivo |
|---|---|
| Resumo de evidência de segurança da AHRQ | A extração passou, mas a rota NCBI Bookshelf restringe recuperação automatizada sistemática fora do subconjunto aberto. Buscar distribuição autorizada antes de reconsiderar. |
| Revisão sobre número de doses de HPV | Manuscrito acessível no PubMed Central, porém nenhuma licença aberta explícita foi identificada. A disponibilidade para leitura não foi tratada como permissão de ingestão. |
| CDC — contraindicações e precauções | O servidor retornou HTTP 403; sem bytes, recibo e extração, não há auditoria reproduzível. |
| CDC — imunocompetência alterada | O servidor retornou HTTP 403; permanece candidato e não será indexado. |

## Auditoria técnica e jurídica

Os PDFs tiveram capa, licença, páginas de conteúdo e páginas finais amostradas
visualmente. As páginas finais dos dois relatórios da Conitec são decorativas e
vazias; a página 2 da OMS é uma página reversa vazia. Não se observou truncamento.
Os artigos científicos foram obtidos como XML JATS integral pelo serviço oficial
Europe PMC e o novo extrator preserva títulos, parágrafos e células de tabela em
blocos separados.

BMJ e Springer usam CC BY-NC 4.0; os dois artigos MDPI e o artigo da
eClinicalMedicine usam CC BY 4.0; a OMS usa CC BY-NC-SA 3.0 IGO; os relatórios da
Conitec permitem reprodução parcial ou total com atribuição e sem finalidade
comercial. O uso planejado permanece local, acadêmico e sem orçamento. Os arquivos
brutos, textos e chunks não entram no Git, e a licença MIT do código não os
relicencia.

## Guardrails metodológicos

- Revisões e relatórios não são votos independentes quando reutilizam os mesmos
  ensaios; a pipeline deve preservar a proveniência dos estudos subjacentes.
- `Não encontrou associação` não significa `provou risco zero`, e evidência baixa
  ou muito baixa não pode sustentar linguagem categórica.
- Associação temporal, estudo observacional e previsão de modelo não serão
  convertidos em causalidade.
- Resultados restritos a covid-19, reprodução assistida, gestação, país, idade,
  sorotipo ou período não podem ser generalizados além desse recorte.
- Relatórios da Conitec combinam evidência, modelo econômico, participação social e
  decisão pública; esses componentes devem aparecer identificados nos chunks.
- Nenhuma mensagem real de usuário foi armazenada ou transformada em dado de
  pesquisa, e nenhuma alegação do dataset final foi criada neste lote.

## Reprodução

```powershell
.\.venv\Scripts\python.exe scripts\audit_corpus_batch.py --batch 004
```

O comando retorna código 1 enquanto as duas páginas do CDC permanecerem sem recibo;
isso representa a falha de fonte registrada, não falha dos dez documentos auditados.
O relatório `batch_004.audit.json` contém somente metadados, hashes e métricas. Os
textos integrais permanecem no diretório local ignorado pelo Git.

## Publicação e validação

A aprovação conjunta promoveu somente os oito documentos marcados `approved`.
O corpus passou de 32 documentos e 4.252 chunks para **40 documentos e 5.313
chunks**, na versão
`sha256:2a2ed2ce976165327677dd7f238d31407a93cdb3428f9e449bc25a7a955e92cc`.
O índice incremental BGE-M3 reutilizou 4.252 vetores e calculou 1.061 novos em CPU,
offline, em 508,95 segundos.

A migration `0002_allow_jats_xml.sql` ampliou a restrição de formato do PostgreSQL
para aceitar `xml`, além de `pdf` e `html`. O banco recebeu os 5.313 embeddings e
só então ativou a nova versão, arquivando a anterior. A conferência direta encontrou
40 documentos, 5.313 chunks e 5.313 embeddings na versão ativa: 9 documentos HTML,
27 PDF e 4 XML.

Consultas diagnósticas recuperaram cada documento novo no top 10 híbrido, com
posições entre 1 e 8. Em uma consulta sobre tiomersal e autismo, o top 10 denso do
pgvector foi idêntico ao índice NumPy local e a nova revisão da OMS ficou em primeiro.
No piloto antigo de 12 consultas, o híbrido obteve Recall@5 de 0,667, Recall@10 de
0,833, MRR de 0,376 e nDCG@10 de 0,483. A queda em relação ao snapshot anterior é
diagnóstica: chunks novos ainda não têm julgamentos de relevância e podem ser
pertinentes sem constar dos rótulos antigos.

Na pipeline completa, a alegação sintética `Vacinas com tiomersal causam autismo.`
foi classificada como `REFUTED`, com citações programáticas para Ministério da
Saúde, revisão final da OMS e página de segurança da OMS, em 21,40 segundos. Esse
caso é teste de fumaça, não estimativa de acurácia.

Validação final de software: **181 testes aprovados** — 180 na suíte geral e um
teste de integração executado em base PostgreSQL exclusiva e descartável —, além
de Ruff sem apontamentos. A base de teste foi removida depois da conferência; o
banco de desenvolvimento e a versão ativa permaneceram íntegros.
