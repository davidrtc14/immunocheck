# Lote documental 002 - parecer para revisão conjunta

Preparado e aprovado pelo autor em 06/09/2026; publicado e validado em
07/09/2026. A aprovação abrange somente os cinco PDFs identificados abaixo e os
bytes registrados pelos respectivos SHA-256 em `batch_002.csv`. Os outros 15
itens do lote permanecem fora do índice.

## Resultado executivo

- 20 candidatos examinados: 19 novas entradas e a retomada do CRIE do lote 001.
- 19 downloads íntegros e extraíveis; uma coleta rejeitada por não retornar PDF.
- **Cinco documentos aprovados e incluídos**, todos com CC BY-NC-SA 4.0 explícita.
- 13 páginas HTML retidas por avisos de uso conflitantes.
- Um calendário retido por problemas de estrutura e edição, além de licença pendente.
- Catálogo total: 41 entradas. Corpus ativo: 21 documentos e 3.532 chunks.
- A publicação do lote não equivale ao fechamento da Fase 5.

## Documentos aprovados

Todos são publicações do Ministério da Saúde. A licença consta da página física 3
de cada PDF: atribuição obrigatória, uso não comercial e compartilhamento sob a
mesma licença quando aplicável. Não republicar os PDFs, textos ou chunks no GitHub;
a licença MIT do código não relicencia esses documentos.

| Documento e edição | Páginas físicas / chunks potenciais | Utilidade e cuidado |
|---|---:|---|
| [Manual CRIE - 6ª edição, 2023](https://dive.saude.sc.gov.br/index.php/component/phocadownload/category/177-a-dive/181-gedim?Itemid=101&download=1055:5-edicao-do-manual-dos-centros-de-referencia-para-imunobiologicos-especiais-crie) | 178 / 471 | Imunodepressão, condições especiais e relação benefício-risco; não substituir atualização normativa nem avaliação clínica individual. |
| [Microplanejamento - 2ª edição, 2025](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/manual-de-microplanejamento.pdf/view) | 75 / 144 | Barreiras de acesso, comunicação compreensível e acolhimento de dúvidas; não transformar hesitação em rótulo sobre pessoas. |
| [Vacinação nas fronteiras - agenda 2025 e 2026](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/guias-e-manuais/2026/estrategia-de-vacinacao-nas-fronteiras-agenda-2025-e-2026.pdf/@@download/file) | 43 / 83 | Equidade e acesso em territórios fronteiriços; não atribuir risco biológico à nacionalidade. |
| [Estratégia contra influenza - 2026](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/guias-e-manuais/2026/estrategia-de-vacinacao-contra-a-influenza-nas-regioes-nordeste-centro-oeste-sul-e-sudeste-2026.pdf/@@download/file) | 41 / 81 | Vacina, composição, precauções e grupos prioritários; recorte Nordeste, Centro-Oeste, Sul e Sudeste e campanha de 2026. |
| [Estratégia contra VSR em gestantes - 2026](https://www.gov.br/saude/pt-br/vacinacao/publicacoes/estrategia-de-vacinacao-contra-o-virus-sincicial-respiratorio-em-gestantes.pdf) | 40 / 78 | Imunização materna, eficácia por desfecho e período, eventos e limites de causalidade; não generalizar resultados de idosos para gestantes. |

Somam 377 páginas físicas e 857 chunks potenciais. As contagens não são uma
métrica de qualidade ou acurácia do sistema. São dois documentos no tema primário
de populações especiais, dois de comunicação/equidade e um de vacinas específicas.
Epidemiologia permanece uma lacuna primária; os trechos secundários nos guias não
são contados como documentos adicionais.

## O que foi efetivamente conferido

A auditoria técnica extraiu todas as páginas, verificou tamanho e SHA-256 contra
os recibos, contou páginas vazias, caracteres de substituição/controle e chunks.
O relatório [batch_002.audit.json](batch_002.audit.json) contém somente metadados
e métricas. Os hashes correspondem aos bytes baixados, não a uma promessa de que
a URL nunca mudará.

A leitura dirigida conferiu capa, instituição, edição, licença e amostras de
conteúdo com sua utilidade temática. Isso **não é revisão clínica integral** nem
segunda anotação independente. Para a revisão humana, conferir especialmente:

| Documento | Páginas físicas sugeridas | Texto extraído local, ignorado pelo Git |
|---|---|---|
| CRIE | 1-3; 37-38; 40-43 | [Texto local](../raw/reviews/batch_002/ms_crie_2023.txt) |
| Microplanejamento | 1-3; 49-51 | [Texto local](../raw/reviews/batch_002/ms_microplanejamento_2025.txt) |
| Fronteiras | 1-3; 6-10; 33-34 | [Texto local](../raw/reviews/batch_002/ms_fronteiras_2026.txt) |
| Influenza | 1-3; 18-24 | [Texto local](../raw/reviews/batch_002/ms_influenza_2026.txt) |
| VSR em gestantes | 1-3; 25-29 | [Texto local](../raw/reviews/batch_002/ms_vsr_gestantes_2026.txt) |

Os textos locais completos e os PDFs originais em `corpus/raw/` estão disponíveis
para ampliar a conferência. Nos PDFs, a paginação impressa pode diferir da física.

### Limitações registradas

- O endereço do espelho CRIE conserva `5-edicao`, mas capa e ficha bibliográfica
  confirmam a 6ª edição de 2023. A coleta anterior em DF falhou; seu histórico
  continua em `batch_001.csv`, sem fabricar uma aprovação retroativa.
- Poppler confirmou que as sete páginas sem texto do CRIE (5, 17, 21, 27, 29, 39,
  49) e as seis do Microplanejamento (13, 15, 37, 39, 57, 65) são decorativas.
- Fronteiras e VSR têm, respectivamente, 11 e 9 caracteres de controle em marcadores
  de listas. Permanecem documentados; o extrator de produção não foi alterado.
- A página física 29 do VSR menciona uma portaria `4/2027` apesar da edição 2026.
  Essa referência editorial precisa ser conferida na fonte normativa; não foi
  silenciosamente corrigida nem certificada pela auditoria.
- Tabelas, gráficos e notas exigem conferência no PDF antes de servirem como
  evidência de um item de avaliação. Extração textual não prova fidelidade de layout.
- Os anos das edições foram registrados nos títulos/notas; quando dia e mês não
  foram identificados, `publication_date` ficou vazio. Acesso em 06/09/2026 não
  significa publicação nesse dia.
- Não houve duplicidade exata de texto dentro do lote nem igualdade de bytes com
  documentos validados. Isso não descarta sobreposição parcial entre manuais:
  não tratar trechos derivados da mesma evidência como confirmações independentes.
- Nenhuma alegação de teste foi produzida, nenhum rótulo veio da LLM e nenhuma
  mensagem real de usuário foi armazenada.

## Materiais retidos e falha de coleta

As 13 páginas sobre BCG, hepatites A/B, poliomielite, rotavírus, febre amarela,
tríplice viral, varicela, DTP, dTpa, meningite, coqueluche e saúde/migração trazem
simultaneamente a licença geral CC BY-ND 3.0 do portal e um aviso específico de
direitos reservados no conteúdo. O acesso é gratuito, mas a condição de reutilização
ficou ambígua. **Retenção não significa conclusão jurídica de proibição**: esclarecer
com a instituição ou selecionar uma publicação com licença inequívoca.
A análise de conteúdo dessas páginas foi limitada após esse bloqueio.
Os URLs individuais e estados permanecem em [catalog.csv](../catalog.csv).

O [calendário de gestantes](https://www.gov.br/saude/pt-br/composicao/svsa/pni/calendario-tecnico/calendario-tecnico-nacional-de-vacinacao-gestante)
ficou retido: a leitura linear mistura colunas; a inspeção visual das páginas 2 e 4
confirmou cabeçalho 2025 em documento identificado como 2026 e um trecho sobre
outras vacinas concatenado à nota de covid-19. Não há declaração de licença no PDF.
Não se deve corrigir o texto da fonte por inferência. O guia VSR é uma alternativa
mais auditável para parte do tema, não substitui todo o calendário.

O [informe de dengue 2024](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/arboviroses/publicacoes/estrategia-vacinacao-dengue/@@download/file)
retornou HTML de acesso restrito, não PDF. O coletor recusou o arquivo.
A licença apareceu no registro público localizado na pesquisa, mas não foi
conferida em cópia local; o documento continua candidato e fora do índice.

Páginas de situação epidemiológica mutáveis e dashboards localizados na pesquisa
não foram adicionados como substitutos de boletins datados.

## Reprodução e publicação

```powershell
.\.venv\Scripts\python.exe scripts\audit_corpus_batch.py --batch 002
.\.venv\Scripts\python.exe scripts\audit_corpus_coverage.py --output corpus\coverage_report.md
```

O primeiro comando retorna código 1 enquanto o documento de dengue não tiver
recibo íntegro. Isso é uma falha de fonte registrada, não uma falha ocultada como
sucesso. O comando não baixa, não promove estados e não publica índices.
Textos integrais são gravados somente no diretório local ignorado
`corpus/raw/reviews/batch_002/`; o relatório público não contém esses textos.

A revisão humana foi registrada em `batch_002.csv` antes da promoção para
`validated`, vinculada aos hashes da auditoria. Uma aprovação em lote não vale para
bytes futuros diferentes na mesma URL.

A publicação gerou a versão
`sha256:5e21bdfbe417e471ce7ac1c34d0d239c79fb619a751228cd3616b9772da09f31`,
com 21 documentos e 3.532 chunks. O índice incremental reutilizou os 2.675 vetores
anteriores e gerou 857 novos localmente, em CPU e sem rede. No PostgreSQL, os
3.532 trechos de evidência possuem embeddings correspondentes e a
versão anterior ficou arquivada.

As cinco consultas temáticas recuperaram o respectivo documento novo no top 10 do
RRF; CRIE e Fronteiras ficaram no primeiro resultado. O top 10 denso do pgvector
coincidiu com o NumPy em uma consulta sobre VSR. No teste completo, uma alegação
sobre proteção de bebês pela vacinação materna contra VSR recebeu veredito
`SUPPORTED`, com citações do novo guia e do calendário de 2026, em 55,18 s.

Validação de software após a publicação: **166 testes aprovados**, um teste de
integração PostgreSQL opcional ignorado por não haver base de teste exclusiva, e
Ruff sem apontamentos. A base do projeto foi validada por consultas não destrutivas;
o teste de integração não foi apontado para ela.

Não avançar à Fase 6: ainda faltam 59 documentos para o mínimo temático, dataset,
segunda anotação e teste congelado. Também permanece pendente a auditoria de licença
dos sete documentos legados cujo catálogo ainda indica `to_verify`.
