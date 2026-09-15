# Índice de revisão — todos os lotes experimentais

Atualizado em 15/09/2026 após a aprovação explícita “aprovo tudo, pode seguir”.
**160 itens com primeira revisão assistida; zero com segunda anotação.**
A aprovação cobre os lotes 002–012 sem exceções e preserva o aceite anterior do 001.
Registro: [aprovação conjunta](reviews/batches_002_012.md). Não houve congelamento.

| Lote | IDs | Itens | Tema | Split previsto | Estado humano |
| --- | --- | --- | --- | --- | --- |
| [001](batches/batch_001.md) | 0001–0012 | 12 | Mecanismos, conservação e causalidade | Desenvolvimento | Primeira revisão aceita |
| [002](batches/batch_002.md) | 0013–0024 | 12 | HPV, alumínio e BCG | Desenvolvimento | Primeira revisão aceita |
| [003](batches/batch_003.md) | 0025–0036 | 12 | Componentes e fabricação | Desenvolvimento | Primeira revisão aceita |
| [004](batches/batch_004.md) | 0037–0048 | 12 | Vacinação materna | Desenvolvimento | Primeira revisão aceita |
| [005](batches/batch_005.md) | 0049–0060 | 12 | Riscos e estudos de covid-19 | Desenvolvimento | Primeira revisão aceita |
| [006](batches/batch_006.md) | 0061–0072 | 12 | Vacinas contra dengue | Desenvolvimento | Primeira revisão aceita |
| [007](batches/batch_007.md) | 0073–0084 | 12 | Normas e calendários | Desenvolvimento | Primeira revisão aceita |
| [008](batches/batch_008.md) | 0085–0096 | 12 | Acesso e organização | Desenvolvimento | Primeira revisão aceita |
| [009](batches/batch_009.md) | 0097–0112 | 16 | Rotavírus, varicela e febre amarela | Teste previsto | Primeira revisão aceita |
| [010](batches/batch_010.md) | 0113–0128 | 16 | Influenza, hepatite B e doença renal | Teste previsto | Primeira revisão aceita |
| [011](batches/batch_011.md) | 0129–0144 | 16 | Epidemiologia e vigilância | Teste previsto | Primeira revisão aceita |
| [012](batches/batch_012.md) | 0145–0160 | 16 | Populações especiais e indicadores | Teste previsto | Primeira revisão aceita |

## Procedimento e registro da revisão

Todos os lotes receberam aceite explícito do autor. Correções futuras continuam
possíveis pelos IDs, com registro e atualização dos hashes antes do congelamento.
As justificativas foram propostas pelo agente e aceitas de forma assistida; o aceite
não comprova leitura independente de cada fonte nem revisão especializada.

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

`review_pool.jsonl` e `items.jsonl` contêm os mesmos 160 itens com primeira revisão.
Os JSONL de `batches/` conservam as propostas originais como rascunhos históricos,
não pendências de aprovação. Este snapshot não é teste congelado nem autorização
para executar experimentos finais. Correções exigem sincronização dos hashes.

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

1. Segundo humano independente em pelo menos 30%. A seleção de 48 itens está em
   `independent_review/selection_manifest.json`: 12 por classe, sete de desenvolvimento
   e cinco de teste por classe (arredondamento por maiores restos; semente 20260915).
   Entregar somente a pasta `independent_review/participant`, nunca o mapa ou este
   repositório com rótulos. O pacote sem respostas facilita, mas não certifica cegamento.
2. Concordância pré-adjudicação e resolução das divergências, preservando rótulos.
3. Auditoria de famílias, validade do benchmark, splits e evidências; congelamento
   com hashes antes do ajuste final. `--ready` não certifica esses atos humanos.

Consultar `ANNOTATION_GUIDE.md`. Não usar mensagens reais do Telegram como dataset
e não copiar respostas de fact-checkers para o corpus.

## Validação histórica da preparação

Em 15/09/2026, os 160 itens passaram na validação estrutural contra o corpus local:
12 revisados, zero com segunda revisão, 40 propostas por classe e split 96/64.
A suíte geral aprovou 210 testes e Ruff passou. Um teste de integração PostgreSQL
não foi executado por ausência da variável de base exclusiva; esta unidade não
alterou banco, migrations ou índices. Os testes confirmam hashes, consistência
entre pool e lotes, ausência de revisão fictícia e recusa do pool como pronto.
Esses resultados não confirmam correção dos rótulos ou adequação científica.

## Estado após aprovação

A primeira revisão está registrada nos 160 itens (40 por classe, split 96/64).
A seleção de 48 tarefas contém campos de resposta vazios: preparar o pacote não
conta como segunda revisão. `--ready` continua recusando o dataset por cobertura
insuficiente de segunda anotação. Não houve experimento, adjudicação ou alteração
do corpus nesta unidade. A Fase 5 permanece aberta pelos atos humanos acima.

Validação da promoção e do pacote: 219 testes aprovados, Ruff e `git diff --check`
sem apontamentos; um teste PostgreSQL não executado por falta de base exclusiva.
Referências dos 160 itens passaram na checagem contra os 7.585 chunks locais.
Os testes incluem os hashes, a seleção estratificada, a ausência de respostas
fabricadas e a preservação de todos os rascunhos originais. Não comprovam validade
dos rótulos, competência dos anotadores, cegamento ou generalização.
