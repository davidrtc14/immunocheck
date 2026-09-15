# Índice de revisão — todos os lotes experimentais

Snapshot preparado em 15/09/2026, a pedido do autor para revisar lote por lote.
**160 propostas no total: 12 com primeira revisão assistida e 148 pendentes.**
O lote 002 ainda não foi aprovado. Os lotes 003–012 foram preparados conjuntamente;
esta preparação não registra aprovação de nenhum deles.

| Lote | IDs | Itens | Tema | Split previsto | Estado humano |
| --- | --- | --- | --- | --- | --- |
| [001](batches/batch_001.md) | 0001–0012 | 12 | Mecanismos, conservação e causalidade | Desenvolvimento | Primeira revisão aceita |
| [002](batches/batch_002.md) | 0013–0024 | 12 | HPV, alumínio e BCG | Desenvolvimento | Pendente |
| [003](batches/batch_003.md) | 0025–0036 | 12 | Componentes e fabricação | Desenvolvimento | Pendente |
| [004](batches/batch_004.md) | 0037–0048 | 12 | Vacinação materna | Desenvolvimento | Pendente |
| [005](batches/batch_005.md) | 0049–0060 | 12 | Riscos e estudos de covid-19 | Desenvolvimento | Pendente |
| [006](batches/batch_006.md) | 0061–0072 | 12 | Vacinas contra dengue | Desenvolvimento | Pendente |
| [007](batches/batch_007.md) | 0073–0084 | 12 | Normas e calendários | Desenvolvimento | Pendente |
| [008](batches/batch_008.md) | 0085–0096 | 12 | Acesso e organização | Desenvolvimento | Pendente |
| [009](batches/batch_009.md) | 0097–0112 | 16 | Rotavírus, varicela e febre amarela | Teste previsto | Pendente |
| [010](batches/batch_010.md) | 0113–0128 | 16 | Influenza, hepatite B e doença renal | Teste previsto | Pendente |
| [011](batches/batch_011.md) | 0129–0144 | 16 | Epidemiologia e vigilância | Teste previsto | Pendente |
| [012](batches/batch_012.md) | 0145–0160 | 16 | Populações especiais e indicadores | Teste previsto | Pendente |

## Como revisar sem aprovar automaticamente

Abrir cada parecer, conferir as fontes e indicar aprovação ou correções pelos IDs.
Você pode responder, por exemplo, “aprovo o lote 003; no 004, revisar o item 0043”.
Uma resposta parcial só promove os lotes explicitamente aprovados. Não precisamos
preparar um novo lote entre suas revisões: todos os pareceres já estão disponíveis.

O rótulo proposto **não é resposta da ferramenta**. Os itens foram formulados pelo
agente, sem execução do ImmunoCheck ou consulta às suas previsões. Os pareceres
mostram justificativas para ajudar o primeiro revisor; essa revisão é assistida,
não cega. Não se atribuem nomes, datas ou avaliações a um segundo humano inexistente.

## Distribuição proposta e estado real

| Classe proposta | Desenvolvimento | Teste previsto | Total |
| --- | ---: | ---: | ---: |
| Sustentada | 24 | 16 | 40 |
| Refutada | 24 | 16 | 40 |
| Enganosa | 24 | 16 | 40 |
| Evidência insuficiente | 24 | 16 | 40 |
| Total | 96 | 64 | 160 |

Essa distribuição pode mudar com a revisão. Não forçar rótulos ou aprovação para
atingir a meta. Exclusões ou mudanças poderão exigir candidatos substitutos e
nova divisão estratificada, sempre antes do congelamento.

`review_pool.jsonl` reúne um snapshot dos 12 itens já revisados em `items.jsonl`
e dos 148 rascunhos dos lotes 002–012. É um material **de revisão**, não um arquivo
de teste congelado nem autorização para executar experimentos. Depois de cada
aprovação, atualizar o snapshot e este índice sem sobrescrever os rascunhos originais.

Corpus fixado para esta proposta:
`sha256:d6cb49e72edbe28e0958b1e8be440e655c93c972af78383121c04687f2d984a7`
(80 documentos / 7.585 chunks). Nenhum documento novo foi ingerido.

`review_pool_manifest.json` registra hashes SHA-256 com finais de linha normalizados
em LF para os JSONL dos 12 lotes, itens aprovados e pool. É um manifesto de revisão,
com `test_frozen=false`, não um ato de congelamento. Atualizar seus hashes e contagens
quando houver alterações aprovadas. São 33 identificadores de família no
desenvolvimento e 16 no teste previsto; essa contagem nominal não certifica
independência semântica entre famílias ou fontes compartilhadas.

## Limitações que a contagem não resolve

- Todos os itens são sintéticos: 120 formulações baseadas em fatos das fontes e
  40 cenários fictícios indeterminados. Não há amostra de notícias reais.
- Formar afirmações a partir das próprias fontes favorece cobertura e proximidade
  lexical. O conjunto avalia um benchmark controlado; não comprova generalização
  para conteúdos espontâneos de usuários. Antes de chamá-lo dataset definitivo,
  revisar com o orientador a adequação ou necessidade de itens públicos reescritos.
- Alguns grupos contrastam uma afirmação sustentada, uma contradita e uma inferência
  distorcida. Padrões de redação e proximidade entre versões podem facilitar a tarefa.
  A revisão deve buscar casos artificiais demais, duplicação semântica e rótulos
  ambíguos, especialmente `MISLEADING`.
- Famílias foram atribuídas semanticamente e não atravessam splits nos arquivos.
  O validador detecta IDs iguais de família, não paráfrases com nomes diferentes;
  a auditoria humana continua necessária. Compartilhar um tema amplo não é o mesmo
  que repetir a proposição; avaliar relações entre lotes, não só textos idênticos.
- Itens correlacionados não são 160 observações independentes. Na Fase 6, reportar
  número e composição de famílias e fazer análise de sensibilidade da incerteza
  por família, além das métricas por item. Não apresentar bootstrap de itens como
  se eliminasse essa dependência.
- Abstenções exploram falta de identificação ou dados de casos; não cobrem toda
  forma de insuficiência, como lacunas científicas ou fontes contraditórias.
- O mesmo agente participou da formulação de desenvolvimento e teste. Não houve
  ajuste de pipeline nesta preparação. Preparadores conhecem os itens de teste:
  ajustes futuros devem usar somente desenvolvimento e registrar essa limitação.
- As alegações são unidades textuais. Ensaios de imagem/link e de latência permanecem
  na Fase 6; gerar 160 alegações não valida OCR ou extração de páginas.

## O que ainda impede concluir a Fase 5

1. Primeira revisão dos 148 candidatos pendentes e eventuais correções/substituições.
2. Segundo humano independente em pelo menos 30% (48 itens se forem mantidos 160),
   com seleção estratificada e pacote cego sem os rótulos ou justificativas daqui.
3. Concordância pré-adjudicação e resolução das divergências, preservando rótulos.
4. Auditoria de famílias, validade do benchmark, splits e evidências; congelamento
   com hashes antes do ajuste final. `--ready` não certifica esses atos humanos.

Consultar `ANNOTATION_GUIDE.md`. Não usar mensagens reais do Telegram como dataset
e não copiar respostas de fact-checkers para o corpus.

## Validação desta preparação

Em 15/09/2026, os 160 itens passaram na validação estrutural contra o corpus local:
12 revisados, zero com segunda revisão, 40 propostas por classe e split 96/64.
A suíte geral aprovou 210 testes e Ruff passou. Um teste de integração PostgreSQL
não foi executado por ausência da variável de base exclusiva; esta unidade não
alterou banco, migrations ou índices. Os testes confirmam hashes, consistência
entre pool e lotes, ausência de revisão fictícia e recusa do pool como pronto.
Esses resultados não confirmam correção dos rótulos ou adequação científica.
