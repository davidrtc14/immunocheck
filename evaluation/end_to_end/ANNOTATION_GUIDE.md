# Guia de anotação fim a fim

A importação em lote das decisões humanas e os limites da verificação automática
estão em `independent_review/adjudication/README.md`. O comando
`scripts/check_adjudication.py` é somente leitura: não promove dataset nem congela
teste. Auditoria documental de erro compartilhado pode usar o campo opcional
`adjudication_basis=evidence_audit`, com responsável/data, preservando os dois
rótulos originais. Isso não cria uma terceira anotação independente.

## Unidade e evidência

Anotar uma proposição factual sobre vacinação humana, não a intenção do autor,
uma opinião ou a pessoa que a publicou. Separar listas de afirmações independentes.
Uma premissa e sua conclusão podem permanecer juntas quando o objeto é justamente
a inferência ou a distorção de escopo; a atomicidade precisa de revisão humana.

Ler diretamente as fontes e o contexto dos chunks. A origem da alegação não prova
seu conteúdo. Registrar produto, população, território e data quando necessários;
não preencher informação ausente com suposições. Documentos normativos são
avaliados no recorte temporal declarado, não como aconselhamento atual individual.

## Rótulos operacionais

| Rótulo | Critério |
| --- | --- |
| `SUPPORTED` | Evidência documental sustenta diretamente a proposição e seu escopo. |
| `REFUTED` | Evidência contradiz diretamente a proposição central; mera ausência de menção não basta. |
| `MISLEADING` | Há conteúdo factual sustentado, mas contexto, alcance ou inferência foi distorcido de modo material. Identificar expressamente a parte sustentada e a distorção. |
| `INSUFFICIENT_EVIDENCE` | O corpus e as informações disponíveis não permitem sustentar nem contradizer a proposição com segurança. Não equivale a verdade, falsidade ou inexistência de evidência em todo o mundo. |

A fronteira `MISLEADING`/`REFUTED` pode ser ambígua: se não houver uma parte
factual relevante efetivamente sustentada, preferir `REFUTED`. Registrar dúvidas
e revisar o manual de forma consistente no desenvolvimento. Nunca preservar um
rótulo apenas para atingir cotas. Casos ambíguos não resolvidos ficam pendentes
ou são excluídos, com justificativa, antes do congelamento.

Rótulos conclusivos exigem `evidence_chunk_ids` diretamente pertinentes e uma
justificativa humana. Abstenções ficam sem evidência conclusiva; a justificativa
descreve informação ausente e a busca documental feita, sem transformar normas
gerais em prova de um evento específico.

## Processo humano e independência

1. O lote candidato conserva `status=draft`; `label` é uma proposta do agente,
   não uma anotação humana nem uma previsão do sistema avaliado.
2. O autor revisa todos os itens, confirma ou corrige rótulos, escopo e evidências.
   Registrar identificador interno do anotador, data e justificativa; preencher
   `primary_label` com seu rótulo e marcar `reviewed` somente após essa revisão.
3. Um segundo humano distinto anota pelo menos 30% do dataset, com amostragem
   estratificada por classe e split. Entregar-lhe alegação, recorte e acesso ao
   corpus, ocultando propostas, justificativas, rótulos do primeiro anotador e
   respostas do sistema. Guardar a seleção e as instruções usadas.
4. Preservar `primary_label` e `second_label` originais. Calcular Cohen's kappa
   nominal e concordância **antes** da adjudicação, com tamanho e distribuição
   da amostra. Não calcular concordância entre rótulo adjudicado e segundo rótulo.
5. Divergências exigem adjudicador e data, idealmente com apoio de especialista;
   `label` passa a ser a decisão final e `rationale` explica a resolução. Os dois
   rótulos independentes nunca são sobrescritos.

Aprovação conjunta pelo autor é primeira revisão, não segunda anotação. Um agente
de IA não substitui o segundo humano. O validador detecta identificadores iguais,
mas não certifica identidade, competência ou cegamento: isso exige registro do
procedimento. Campos novos são opcionais para leitura de arquivos legados, mas
`primary_label` e `claim_family` são obrigatórios no aceite `--ready`.

## Separação e limitações

Agrupar paráfrases e versões relacionadas em `claim_family`, usando identificadores
consistentes e revisão semântica manual. Nenhuma família atravessa desenvolvimento
e teste. Planejar seleção por famílias para satisfazer 60%/40% por classe: o alvo
é 160 itens (40/classe); o mínimo é 100 (25/classe). Para contagens indivisíveis,
o validador usa `round(n * 0.60)` itens de desenvolvimento por classe.

O lote 001 é sintético e exclusivamente de desenvolvimento, útil para calibrar o
manual. Não representa a distribuição de notícias nem demonstra desempenho real.
Itens futuros devem ampliar temas, fontes e estilos, com origem rastreável e sem
dados pessoais. Alegações públicas reescritas precisam ser selecionadas antes de
consultar previsões do sistema; se vierem de fact-checkers, suas respostas não
podem integrar o corpus. Não coletar mensagens reais do Telegram para pesquisa.

O teste definitivo deve ser congelado com hashes, versão do corpus, famílias e
anotações antes do ajuste final. Não usar seus erros para ajustar prompts ou
limiares. A checagem de chunks existentes é estrutural, não prova que sustentam
o rótulo. A validade científica depende da revisão humana e da análise de vieses.
