# Lote experimental 001 — proposta original e aprovação

Preparado em 15/09/2026 com 12 rascunhos de desenvolvimento. Posteriormente, o autor
aprovou conjuntamente os 12 itens como **primeira revisão assistida**.
O JSONL desta pasta preserva a proposta original; os itens revisados estão em
`../items.jsonl` e o registro de aprovação em `../reviews/batch_001.md`.
Não confundir com o lote documental 001. O corpus continua com 80 documentos;
estes itens são perguntas de avaliação, não novas fontes do RAG.

Snapshot de evidência:
`sha256:d6cb49e72edbe28e0958b1e8be440e655c93c972af78383121c04687f2d984a7`.

Nove formulações originais baseadas em fatos das fontes e três cenários fictícios
sem identificação suficiente. Nenhum item veio de mensagem real ou de uma execução
do ImmunoCheck. O equilíbrio de três propostas por classe não obriga a revisão a
preservá-lo. A limitação de redação sintética próxima às fontes será reportada;
este lote não constitui o teste definitivo.

## Itens propostos

| ID | Alegação | Rótulo proposto | Motivo a revisar |
| --- | --- | --- | --- |
| 0001 | Algumas vacinas precisam de várias doses para desenvolver uma resposta imune duradoura. | Sustentada | Fonte descreve múltiplas doses e memória imune. |
| 0002 | A segurança das vacinas continua sendo monitorada depois que elas começam a ser usadas. | Sustentada | Monitoramento pós-aprovação. |
| 0003 | Armazenamento em temperatura inadequada pode reduzir a eficácia de uma vacina. | Sustentada | Possibilidade geral, não prova sobre um lote específico. |
| 0004 | Todas as vacinas contêm o agente infeccioso vivo. | Refutada | Plataformas que não contêm agente vivo são contraexemplos. |
| 0005 | Todo evento adverso pós-vacinação é, por definição, causado pela vacina. | Refutada | Ocorrência temporal não define causalidade. |
| 0006 | Anticorpos contra um agente infeccioso protegem universalmente contra todos os outros agentes infecciosos. | Refutada | Especificidade não sustenta proteção universal. |
| 0007 | A faixa de 2 a 8 °C descrita para a maioria das vacinas serve para armazenar qualquer vacina. | Enganosa | Faixa majoritária real extrapolada às exceções. |
| 0008 | A existência de proteção coletiva significa que quem não pode se vacinar está totalmente protegido. | Enganosa | Proteção indireta real transformada em garantia total. |
| 0009 | A indicação da dose zero na Nota Técnica 21/2026 torna a vacinação contra sarampo aos 6 meses uma regra de rotina para todos os bebês no Brasil. | Enganosa | Indicação específica extrapolada à rotina nacional. |
| 0010 | As vacinas de um lote enviado ontem estavam contaminadas. | Evidência insuficiente | Cenário fictício sem lote, produto, data ou laudo. |
| 0011 | As vacinas guardadas no posto perderam a eficácia depois que faltou energia. | Evidência insuficiente | Cenário fictício sem registros de conservação. |
| 0012 | A morte ocorrida depois da vacinação foi causada pela vacina aplicada. | Evidência insuficiente | Caso fictício sem dados para avaliação causal. |

Revisar especialmente 0007–0009: a classificação como enganosa exige concordância
sobre a premissa factual e a distorção. É legítimo corrigir para refutada ou excluir
um item ambíguo. 0010–0012 também não autorizam concluir que o evento é falso.

## Fontes e localização

- 0001, 0004, 0006 e 0008: [OMS — Como funcionam as vacinas](https://www.who.int/pt/news-room/feature-stories/detail/how-do-vaccines-work).
- 0002, 0003 e 0007: [OMS — Fabrico, segurança e controlo de qualidade](https://www.who.int/pt/news-room/feature-stories/detail/manufacturing-safety-and-quality-control).
- 0005: [Ministério da Saúde — Manual de vigilância de eventos adversos pós-vacinação, 4ª edição](https://www.gov.br/saude/pt-br/vacinacao/manuais/manual_eventos-_adversos_pos_vacinacao_4ed_atualizada.pdf), página impressa 45 / física 46.
- 0009: [Ministério da Saúde — Nota Técnica 21/2026](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/notas-tecnicas/2026/nota-tecnica-no-21-2026-cgici-dpni-svsa-ms.pdf/@@download/file), páginas 1–2, no recorte do snapshot.

Os IDs completos dos chunks, famílias e notas estão em `batch_001.jsonl`.
Os cenários 0010–0012 não possuem fonte conclusiva porque são indeterminados.
Não reproduzir o texto integral de documentos com restrições de redistribuição.

## Aprovação

Ler o guia de anotação e as fontes; confirmar ou corrigir cada proposta. É possível
responder em conjunto, apontando IDs de exceções. Os rótulos da primeira revisão
foram registrados após a confirmação conjunta. Ainda faltam a segunda anotação
independente, a ampliação até o mínimo de 100 e o congelamento do teste.

## Validação técnica

Em 15/09/2026, o validador aceitou os 12 rascunhos e confirmou que os chunks
referenciados existem no corpus local. A suíte geral aprovou 194 testes; um teste
PostgreSQL foi ignorado por não haver base exclusiva configurada. Ruff passou.
Um teste verifica que o lote é recusado quando se exige revisão humana. Esses
resultados validam a estrutura e as regras, não a correção dos rótulos propostos.
