# Lote experimental 002 — proposta para revisão

Preparado em 15/09/2026. **12 rascunhos, todos de desenvolvimento; revisão pendente.**
O lote 001 já recebeu aprovação conjunta do autor como primeira revisão assistida.
O corpus permanece com 80 documentos e versão
`sha256:d6cb49e72edbe28e0958b1e8be440e655c93c972af78383121c04687f2d984a7`.

Este lote acrescenta HPV, reações locais e limites de interpretação de revisões
sobre alumínio e BCG. São nove formulações sintéticas baseadas em fatos publicados
e três cenários fictícios indeterminados, não notícias reais nem mensagens de
usuários. Nenhuma resposta do sistema avaliado orientou a seleção ou os rótulos.
Os fatos foram conferidos nas fontes primárias abaixo; as proposições precisam
de revisão humana. Não redistribuir o texto integral das fontes.

## Itens propostos

| ID | Alegação | Rótulo proposto |
| --- | --- | --- |
| 0013 | A vacina quadrivalente contra HPV não cobre todos os tipos de HPV. | Sustentada |
| 0014 | Nódulos persistentes no local da aplicação são reações incomuns descritas após algumas vacinas com adjuvante de alumínio. | Sustentada |
| 0015 | Na revisão de BCG publicada em 2021, ensaios com recém-nascidos e crianças menores de cinco anos mostraram proteção contra tuberculose durante vários anos. | Sustentada |
| 0016 | A revisão do BMJ de 2026 concluiu que vacinas com adjuvante de alumínio causam autismo. | Refutada |
| 0017 | A vacina quadrivalente contra HPV protege somente contra os tipos 16 e 18. | Refutada |
| 0018 | A revisão de BCG de 2021 encontrou o mesmo resultado de proteção em todos os ensaios, independentemente do contexto epidemiológico. | Refutada |
| 0019 | A vacina quadrivalente inclui proteção contra os tipos 16 e 18, então protege contra qualquer tipo de HPV. | Enganosa |
| 0020 | A revisão do BMJ relata reações locais após vacinas com alumínio, portanto demonstra que elas causam danos sistêmicos graves. | Enganosa |
| 0021 | A revisão de 2021 encontrou proteção da BCG na primeira infância, então esse efeito é permanente em qualquer contexto epidemiológico. | Enganosa |
| 0022 | A vacina contra HPV usada na campanha deste mês deixou de proteger os participantes. | Evidência insuficiente |
| 0023 | O caroço no braço que apareceu depois da vacinação foi causado pelo adjuvante de alumínio. | Evidência insuficiente |
| 0024 | O surto de tuberculose na escola demonstra que a BCG aplicada aos alunos neste ano falhou. | Evidência insuficiente |

## Evidências e pontos de revisão

- 0013, 0017 e 0019: [Ministério da Saúde — HPV](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/h/hpv), seção de prevenção, chunk `ms_hpv:p1:c5:d2c96edbaf75`. Produto quadrivalente; não confundir cobertura de tipos com proteção individual garantida.
- 0014, 0016 e 0020: [BMJ — revisão sistemática sobre adjuvantes de alumínio, 2026](https://www.bmj.com/content/393/bmj-2025-088921), resultados e discussão. Reações locais documentadas não demonstram dano sistêmico; ausência de associação detectada não significa prova de risco zero.
- 0015, 0018 e 0021: [Thorax — revisão e metanálise de efetividade da BCG, 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8526882/), resumo e conclusões. Preservar subgrupos, contexto epidemiológico e duração de seguimento; não transformar uma hipótese explicativa em lei universal.
- 0022–0024: eventos fictícios sem dados específicos, portanto sem chunks conclusivos. Estudos gerais não comprovam nem desmentem esses eventos.

Os IDs completos, famílias e justificativas propostas estão em `batch_002.jsonl`.
Revisar especialmente 0019–0021: premissa factual e inferência distorcida devem
estar claramente identificadas. A fronteira com refutada e a atomicidade podem
levar à correção ou exclusão. Não forçar cotas de três itens por classe.

## Limitações e aceite

O lote é calibração de desenvolvimento, não um teste de desempenho real. A origem
sintética e a proximidade lexical com fontes precisam ser reportadas. Nenhuma das
famílias pode aparecer depois no teste. O teste futuro precisa ampliar fontes e
estilos e ser separado antes de ajuste; não basta gerar paráfrases destes itens.

Aprovar ou corrigir os itens em conjunto, indicando IDs de exceções. Até lá todos
permanecem `draft` e não entram em `items.jsonl`. Aprovação do autor é primeira
revisão assistida, não revisão cega ou especializada nem segunda anotação.

## Validação técnica

Em 15/09/2026, os 12 candidatos passaram na validação estrutural contra os chunks
do corpus. A suíte aprovou 197 testes; um teste de integração PostgreSQL não foi
executado por ausência de base exclusiva configurada. Ruff passou. Testes também
verificam a preservação dos itens aprovados, a ausência de segunda anotação fictícia,
a recusa de candidatos em modo de revisão obrigatória e a unicidade do conjunto
acumulado de 24 itens. Nenhum desses resultados valida semanticamente os rótulos.
