# Lote documental 003 - parecer para revisão conjunta

Preparado em 07/09/2026, aprovado pelo autor e publicado em 09/09/2026. A
aprovação abrange somente os 11 PDFs íntegros e os bytes registrados pelos
respectivos SHA-256 em `batch_003.csv`; a nota técnica de febre amarela permaneceu
retida porque a URL oficial retornou HTTP 404.

## Resultado executivo

- 12 candidatos oficiais do Ministério da Saúde foram examinados.
- 11 PDFs foram obtidos e auditados: 309 páginas físicas, 621.402 caracteres e
  720 chunks potenciais.
- **Os 11 PDFs foram aprovados e incluídos**, com ressalvas explícitas
  sobre tempo, causalidade, tabelas e uma inconsistência editorial em mpox.
- Cinco documentos declaram CC BY-NC-SA 4.0; seis trazem permissão textual de
  reprodução parcial ou total, com atribuição e sem finalidade comercial.
- Uma nota técnica ficou retida por falha de coleta e licença não verificada.
- Catálogo total: 53 entradas. Corpus ativo: 32 documentos e 4.252 chunks.

## Documentos aprovados

| Documento | Tema primário | Páginas / chunks potenciais | Utilidade e cuidado principal |
|---|---|---:|---|
| Multivacinação 2026 | Normas e calendários | 47 / 96 | Esquemas e atualização da caderneta; tabelas precisam de leitura visual e validade temporal. |
| Vacinação nas escolas 2025 | Comunicação, equidade e ética | 30 / 66 | Acesso escolar e busca de não vacinados; não rotular estudantes ou famílias. |
| Operação Gota 2026 | Comunicação, equidade e ética | 54 / 105 | Acesso em áreas remotas e indígenas; não associar identidade ou território a risco biológico. |
| Retirada da VOPb e esquema exclusivo com VIP | Vacinas específicas | 22 / 43 | Mudança normativa da poliomielite; tratar como documento histórico de 2024. |
| Informe Poliomielite/PFA | Epidemiologia das doenças | 12 / 25 | Vigilância da PFA e pólio; um indicador de vigilância não mede sozinho risco vacinal. |
| Segurança da vacina mpox | Segurança e farmacovigilância | 8 / 19 | Notificações após vacinação; não converter associação temporal em causalidade. |
| Segurança das vacinas do calendário em 2024 | Segurança e farmacovigilância | 16 / 48 | Frequências agregadas e denominadores; preservar vacina, idade, período e classificação do evento. |
| Segurança da vacina contra dengue 2024-2025 | Segurança e farmacovigilância | 18 / 60 | Monitoramento pós-implementação; preservar população, denominador e avaliação causal. |
| Estratégia de vacinação contra a covid-19, 2024, 2ª ed. | Vacinas específicas | 48 / 99 | Esquemas e rede de frio; não apresentar recomendação de 2024 como vigente sem confronto temporal. |
| Cenário dos vírus respiratórios em 2025 | Epidemiologia das doenças | 44 / 125 | Incidência, hospitalizações e mortalidade publicadas em 2026; não atribuir tendências à vacina sem desenho causal. |
| Informe de meningites, 2010 ao 1º semestre de 2025 | Epidemiologia das doenças | 10 / 34 | Série histórica por etiologia e faixa etária; gráficos não substituem interpretação do texto e das notas. |

Os 11 documentos acrescentaram 720 chunks ao corpus, que passou a 32 documentos
e 4.252 chunks. O déficit para o mínimo temático de 80 caiu de 59 para 48
documentos. Esses números medem volume e cobertura, não acurácia.

## O que foi conferido

A auditoria reproduzível verificou PDF real, recibo de download, tamanho e SHA-256,
extração de todas as páginas, caracteres problemáticos e segmentação potencial.
Não houve página vazia nem caractere de substituição. Os 11 hashes de bytes são
distintos. Capa, identificação institucional, declaração de uso e uma página de
conteúdo de cada documento foram também inspecionadas visualmente, incluindo
tabelas, gráficos e diagramas.

O relatório [batch_003.audit.json](batch_003.audit.json) registra métricas e hashes;
[batch_003.csv](batch_003.csv) registra a decisão, o responsável e a data.
Para uma revisão dirigida, os PDFs e textos completos permanecem apenas no ambiente
local ignorado pelo Git:

| Documento | Páginas físicas sugeridas | Texto extraído local |
|---|---|---|
| Multivacinação | 1-3; 36 | [Texto local](../raw/reviews/batch_003/ms_multivacinacao_2026.txt) |
| Escolas | 1-3; 10 | [Texto local](../raw/reviews/batch_003/ms_escolas_2025.txt) |
| Operação Gota | 1-3; 20 | [Texto local](../raw/reviews/batch_003/ms_operacao_gota_2026.txt) |
| Poliomielite/VIP | 1-3; 10 | [Texto local](../raw/reviews/batch_003/ms_polio_vip_2024.txt) |
| PFA | 1; 5; 12 | [Texto local](../raw/reviews/batch_003/ms_pfa_2025.txt) |
| Mpox | 1; 4; 8 | [Texto local](../raw/reviews/batch_003/ms_mpox_seguranca_2025.txt) |
| Segurança do calendário | 1; 5; 16 | [Texto local](../raw/reviews/batch_003/ms_seguranca_calendario_2024.txt) |
| Segurança da dengue | 1; 5; 18 | [Texto local](../raw/reviews/batch_003/ms_dengue_seguranca_2025.txt) |
| Covid-19 | 1-3; 17 | [Texto local](../raw/reviews/batch_003/ms_covid_vacinacao_2024_2ed.txt) |
| Vírus respiratórios | 1; 8; 44 | [Texto local](../raw/reviews/batch_003/ms_respiratorios_2025.txt) |
| Meningites | 1; 4; 10 | [Texto local](../raw/reviews/batch_003/ms_meningite_2025.txt) |

### Licença e permissão de uso

Multivacinação, Escolas, Operação Gota, Poliomielite/VIP e Covid-19 exibem na
página física 3 a licença CC BY-NC-SA 4.0. PFA, Mpox, Segurança do calendário,
Segurança da dengue, Vírus respiratórios e Meningites permitem expressamente a
reprodução parcial ou total com citação da fonte e vedação a venda ou finalidade
comercial. A segunda redação é uma permissão específica do Ministério, não foi
renomeada como licença Creative Commons.

O uso é local, acadêmico e sem orçamento. PDFs, textos e chunks continuam
fora do Git; a licença MIT do código não relicencia o corpus. Uma eventual
redistribuição pública dos documentos exigirá nova análise do escopo das permissões.

### Limitações e ressalvas

- O PDF de mpox tem capa e conteúdo coerentes com o informe de abril de 2025, mas
  o rodapé final diz `Informe: Distribuição de imunobiológicos` e traz copyright
  2024. A divergência editorial fica preservada; o documento foi aprovado com aviso,
  não como se o rodapé tivesse sido corrigido.
- Multivacinação e o boletim de vírus respiratórios contêm 53 e 28 caracteres de
  controle, respectivamente, associados a marcadores. Não houve caractere de
  substituição ou perda de página detectada.
- Tabelas e gráficos foram amostrados visualmente, mas a extração linear não preserva
  todas as relações espaciais. Antes de usar uma linha ou célula como evidência de
  avaliação, será obrigatório conferir o PDF e suas notas.
- Boletins de segurança registram eventos notificados após vacinação. A pipeline
  não pode transformar coincidência temporal, sinal ou taxa bruta em causalidade.
- Recomendações e cenários epidemiológicos têm recorte temporal. A versão do
  documento deverá acompanhar todo chunk e a resposta deve abster-se quando uma
  alegação atual exigir fonte mais recente.
- Materiais do mesmo Ministério podem compartilhar dados e referências; resultados
  concordantes não devem ser contados automaticamente como evidência independente.
- O lote amplia normas, acesso, vacinas específicas, epidemiologia e segurança, mas
  não resolve sozinho a lacuna de estudos causais revisados por pares sobre mitos
  recorrentes. Essa seleção será um lote próprio, com avaliação metodológica.
- Nenhuma alegação do dataset foi criada e nenhuma mensagem real de usuário foi
  armazenada ou usada como dado de pesquisa.

## Material retido

A Nota Técnica nº 18/2025 sobre ESAVI na vacinação contra febre amarela retornou
HTTP 404 no endereço oficial em 07/09/2026. Sem bytes locais não foi possível
confirmar integridade, conteúdo nem permissão de uso; ela continua `candidate` e a
decisão proposta é `hold`. A existência de uma página em mecanismos de busca não
substitui a coleta reproduzível do PDF.

## Reprodução e publicação

```powershell
.\.venv\Scripts\python.exe scripts\audit_corpus_batch.py --batch 003
.\.venv\Scripts\python.exe scripts\audit_corpus_coverage.py --output corpus\coverage_report.md
```

O primeiro comando retorna código 1 enquanto a nota de febre amarela estiver sem
recibo; isso é uma falha de fonte registrada. Ele não baixa, promove ou publica
documentos. A aprovação conjunta foi registrada antes da promoção e não vale para
bytes futuros diferentes na mesma URL.

A publicação gerou a versão
`sha256:8e605597e2cc3d55a09cffbb7dde6396d5df34452b22179dee0fa65585959364`,
com 32 documentos e 4.252 chunks. O índice incremental reutilizou 3.532 vetores e
gerou 720 novos localmente, em CPU e modo offline, em 356,41 segundos. O PostgreSQL
foi atualizado somente depois de receber os 4.252 embeddings; a versão anterior
permaneceu arquivada.

Consultas diagnósticas distintas recuperaram cada um dos 11 documentos novos no
top 10 híbrido: dez em primeiro lugar e PFA em segundo. O top 10 denso do pgvector
coincidiu com o NumPy em uma consulta sobre segurança da dengue. No piloto de 12
consultas já anotadas, o RRF preservou Recall@10 de 0,917; Recall@5, MRR e nDCG@10
ficaram em 0,583, 0,389 e 0,510. A queda dessas métricas de posição em relação ao
corpus piloto é apenas diagnóstica: os novos chunks ainda não receberam julgamentos
de relevância e podem constituir evidência pertinente não rotulada.

Na pipeline completa, a alegação de que a Operação Gota amplia o acesso à vacinação
em áreas de difícil acesso geográfico recebeu `SUPPORTED`, com três citações do novo
guia, em 15,47 segundos. Duas formulações sobre a substituição VOPb→VIP produziram
abstenção, apesar de recuperar a página correta: a fonte de 2024 anuncia a mudança
em tempo futuro, mas as alegações a descreviam como fato consumado. O comportamento
conservador evita inferir implementação posterior; o futuro dataset deverá incluir
casos temporais desse tipo.

Validação de software após a publicação: **166 testes aprovados**, um teste de
integração PostgreSQL opcional ignorado por não haver base de teste exclusiva, e
Ruff sem apontamentos. A Fase 5 continua aberta: faltam 48 documentos para o mínimo
temático, o dataset definitivo, a segunda anotação e o congelamento do teste.
