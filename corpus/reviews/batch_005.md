# Lote documental 005 — decisão e publicação

Preparado e aprovado conjuntamente pelo autor em 10/09/2026. A aprovação vale
somente para os bytes identificados pelos SHA-256 em `batch_005.csv`: dez
documentos foram promovidos e duas páginas da FDA permaneceram retidas.

## Resultado executivo

- 12 candidatos foram examinados para composição, eficácia, populações especiais
  e vacinas específicas.
- Dez documentos foram coletados integralmente: nove artigos em XML JATS oficial e
  um relatório em PDF. Eles somam 147 páginas/unidades documentais, 721.446
  caracteres e 766 chunks potenciais.
- **Foram aprovados os dez documentos coletados.** Todos têm licença aberta
  explícita e utilidade temática, mas vários exigem ressalvas fortes de escopo,
  heterogeneidade, risco de viés ou conflito de interesses.
- **Foram retidas duas páginas da FDA.** O conteúdo e a condição de uso são
  adequados, porém o coletor Python não conseguiu validar a cadeia TLS; não há bytes
  nem recibos auditáveis e a validação não será desativada.
- Não foram encontradas duplicatas exatas dentro do lote nem contra o corpus já
  validado.

## Documentos aprovados

| Documento | Tema | Volume | Utilidade e cuidado obrigatório |
|---|---|---:|---|
| Revisão de dose única de HPV | Eficácia e imunogenicidade | 62 chunks | Dados disponíveis concentram-se em jovens saudáveis do sexo feminino; não converter anticorpos ou infecção em câncer evitado. |
| Revisão de vacinas de influenza aprimoradas | Eficácia e imunogenicidade | 46 chunks | Compara produtos novos à vacina padrão somente em adultos; efeito varia por produto, temporada e desenho. |
| Meta-análise de dTpa na gestação | Populações especiais | 40 chunks | Combina ensaios e caso-controle, majoritariamente de países de alta renda, com heterogeneidade relevante. |
| Meta-análise de hepatite B em crianças africanas | Vacinas específicas | 26 chunks | Mede soroproteção, não efetividade clínica direta; I² de 99,4% e protocolo não registrado impedem generalização. |
| Meta-análise de varicela | Vacinas específicas | 25 chunks | A maioria dos estudos é observacional, 21 têm risco crítico de viés e o estudo foi financiado por fabricante. |
| Meta-análise de duração da proteção contra febre amarela | Vacinas específicas | 35 chunks | Mede sobretudo soroproteção; 23 de 36 estudos têm alto risco de viés e há poucos dados em imunodeficientes. |
| Revisão de vacinas maternas em ensaios | Populações especiais | 43 chunks | Apenas seis ensaios de quatro plataformas; não combinar vacinas, desfechos ou níveis de certeza. |
| HTA de PCV10 e PCV13 | Vacinas específicas | 138 páginas / 392 chunks | Separar anticorpos, seroinfecção, doença invasiva, cenário modelado e avaliação econômica. |
| Revisão de efetividade da BCG | Vacinas específicas | 38 chunks | O efeito depende de idade, carga e momento da exposição à tuberculose e duração do acompanhamento. |
| Revisão de vacinas meningocócicas | Vacinas específicas | 59 chunks | Evidência até março de 2017 e sem avaliação individual de risco de viés; preservar sorogrupo, produto, país e período. |

## Material retido

| Documento | Motivo |
|---|---|
| FDA — ingredientes comuns em vacinas aprovadas | A página é oficial e, salvo exceções indicadas, conteúdo da FDA é de domínio público; a cadeia TLS apresentada ao Python não pôde ser validada. Sem coleta reproduzível, não será indexada. |
| FDA — tiomersal e vacinas | Mesma falha TLS. Além disso, formulações e disponibilidade descritas são específicas dos Estados Unidos e temporalmente mutáveis. |

## Auditoria técnica e jurídica

Os nove artigos foram obtidos como XML JATS integral pelo serviço oficial Europe
PMC. O relatório pneumocócico foi obtido na distribuição integral oficial do NIHR:
o primeiro link identificado era apenas um resumo de quatro páginas e foi
substituído antes da auditoria pelo documento de 138 páginas. Capa, licença, página
de método, uma página reversa vazia e encerramento foram inspecionados visualmente.
As dez páginas sem texto são folhas reversas ou divisórias, não truncamento.

Cinco documentos usam CC BY 4.0; três usam CC BY-NC 4.0; a revisão de febre amarela
usa CC BY-NC-ND 4.0; e a revisão da OPAS usa CC BY-NC-ND 3.0 IGO. Nos dois últimos,
o corpus preservará o texto sem alteração, a atribuição e o aviso da licença. O uso
planejado permanece local, acadêmico e não comercial. Arquivos brutos, textos e
chunks são ignorados pelo Git; a licença MIT do código não relicencia as fontes.

## Guardrails metodológicos

- Soroproteção, imunogenicidade, seroinfecção, eficácia de ensaio, efetividade real
  e impacto populacional são desfechos diferentes e não serão tratados como
  sinônimos.
- Uma estimativa agrupada não poderá apagar heterogeneidade, intervalo de confiança,
  risco de viés, desenho, país, idade, produto, dose, sorotipo ou tempo de seguimento.
- `Não houve diferença estatisticamente significativa` não equivale a provar
  equivalência, ausência de evento ou risco zero.
- Resultados de gestação deverão distinguir mãe e lactente, semana gestacional,
  vacina, comparador e desfecho; não constituem recomendação clínica individual.
- Conflitos e financiamentos declarados não invalidam automaticamente um estudo,
  mas impedem que ele seja usado isoladamente como fundamento conclusivo.
- Modelos econômicos e epidemiológicos do relatório pneumocócico são cenários, não
  observações clínicas; diretrizes brasileiras atuais prevalecem para recomendação.
- A revisão meningocócica é histórica: preços, disponibilidade e políticas citados
  em 2017 não serão apresentados como estado atual.
- Nenhuma mensagem real de usuário foi armazenada ou transformada em dado de
  pesquisa, e nenhuma alegação do conjunto de teste foi criada neste lote.

## Reprodução

```powershell
.\.venv\Scripts\python.exe scripts\audit_corpus_batch.py --batch 005
```

O comando registra falha enquanto as duas páginas da FDA permanecerem sem recibo.
Isso representa a retenção segura dessas fontes, não falha dos dez documentos
auditados. O JSON público contém somente metadados, hashes e métricas; os textos
integrais permanecem locais e ignorados pelo Git.

## Publicação e validação

A versão
`sha256:f15c0ebd67783ccf16552c5230b230c73cde02ccd42a9888102510c5cf4e0119`
foi construída com **50 documentos e 6.079 chunks**. O índice incremental BGE-M3
reutilizou 5.313 embeddings e gerou 766 novos vetores de 1.024 dimensões em CPU,
offline, em 552,95 segundos.

Os 6.079 embeddings foram importados antes da ativação transacional da versão no
PostgreSQL. A conferência direta encontrou 50 documentos, 6.079 chunks e 6.079
embeddings na versão `ACTIVE`. Uma busca exata por cosseno no pgvector, usando um
chunk do relatório pneumocócico como vetor de consulta, devolveu o próprio chunk em
primeiro lugar com similaridade 1,000000. Esta é uma verificação funcional, não o
benchmark de latência ou qualidade previsto para a Fase 6.

Consultas dirigidas e específicas para cada tema recuperaram as dez fontes novas no
top 10 híbrido. Esse ensaio confirma a acessibilidade dos documentos pelo retrieval,
mas não estima desempenho geral nem substitui o dataset congelado.

A validação final aprovou 182 testes na suíte geral, com o teste PostgreSQL omitido
por configuração, e aprovou esse teste separadamente em uma base exclusiva e
descartável. O Ruff não encontrou apontamentos.

## Estado

**Aprovado, publicado e validado.** Dez documentos estão `validated`; as duas
páginas da FDA continuam `candidate` e retidas, sem desativar a validação TLS.
