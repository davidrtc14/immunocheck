# Auditoria de licenças legadas 001 — decisão e publicação

Preparada, aprovada e publicada em 14/09/2026. Esta auditoria revisita os sete
documentos que já estavam validados no corpus, mas ainda conservavam
`license_status=to_verify`. O autor aprovou conjuntamente as sete classificações e
suas restrições de uso.

## Resultado executivo

- **Foram mantidos os sete documentos.** Não foi identificada fonte que exija
  remoção imediata do corpus acadêmico local.
- Dois manuais declaram **CC BY-NC-SA 4.0** na página 3 dos próprios PDFs.
- Três páginas do portal Gov.br declaram **CC BY-ND 3.0** no rodapé dos HTMLs
  coletados. Elas podem permanecer com restrições contra distribuição de adaptação.
- Um protocolo permite expressamente reprodução parcial ou integral, desde que a
  fonte seja citada e não haja venda ou finalidade comercial.
- A Instrução Normativa do Calendário Nacional é um ato oficial. O art. 8º, IV, da
  Lei nº 9.610/1998 exclui textos de atos oficiais da proteção autoral; a conclusão
  não se estende automaticamente a ilustrações ou materiais de terceiros.

## Decisões aprovadas

| Documento | Evidência auditada | Classificação proposta | Decisão |
|---|---|---|---|
| Manual de Normas e Procedimentos para Vacinação — 2ª ed. | Página 3 do PDF | `CC-BY-NC-SA-4.0` | Manter |
| Instrução Normativa do Calendário Nacional de Vacinação 2026 | Natureza e texto do ato oficial | `official-act-BR-L9610-art8-IV` | Manter |
| Manual de Vigilância Epidemiológica de ESAVI — 4ª ed. | Página 3 do PDF | `CC-BY-NC-SA-4.0` | Manter |
| Farmacovigilância de vacinas — Anvisa | Rodapé do HTML coletado | `CC-BY-ND-3.0` | Manter com restrições |
| Vacinação contra Covid-19: medidas regulatórias — Anvisa | Rodapé do HTML coletado | `CC-BY-ND-3.0` | Manter com restrições |
| HPV: prevenção e vacinação — Ministério da Saúde | Rodapé do HTML coletado | `CC-BY-ND-3.0` | Manter com restrições |
| Protocolo de vigilância de eventos adversos da vacinação contra Covid-19 | Página 3 do PDF | `explicit-noncommercial-reuse-with-attribution` | Manter com restrições |

Os SHA-256 dos sete arquivos estão em `license_audit_001.csv`. A decisão vale apenas
para esses bytes e para o uso acadêmico local descrito no projeto.

## Publicação e validação

Como a licença integra a proveniência dos chunks, a correção criou a versão
`sha256:8dfd3d854c8855f71f34d6b5c9bba8e04acb106f43127f2a78659a2ea43d6dc9`.
Os sete documentos tiveram apenas metadados atualizados; 59 documentos foram
reutilizados e nenhum texto foi reprocessado. Todos os 6.989 vetores BGE-M3 foram
reutilizados, sem gerar embeddings novos, em 2,79 segundos.

A nova versão foi ativada no PostgreSQL com 66 documentos, 6.989 chunks e 6.989
embeddings. Uma consulta direta confirmou as sete licenças persistidas. Uma busca
exata por cosseno no pgvector, usando um chunk da Instrução Normativa como consulta,
devolveu o próprio chunk em primeiro lugar com similaridade 1,000000.

A regressão final teve 182 testes aprovados na suíte geral e um teste aprovado em
base PostgreSQL exclusiva e descartável, totalizando 183; o Ruff não apontou
problemas. A base de teste foi removida após a execução.

## Base jurídica e limites da conclusão

A licença CC BY-NC-SA 4.0 permite compartilhar e adaptar, impondo atribuição, uso
não comercial e compartilhamento pela mesma licença. A CC BY-ND 3.0 permite
reprodução, incorporação em coleção e as modificações tecnicamente necessárias para
outro meio ou formato, mas veda distribuir obra derivada. A Lei nº 9.610/1998 também
prevê que textos de atos oficiais não são objeto de proteção autoral e admite
citações justificadas para estudo, crítica ou polêmica, com indicação de autoria e
origem.

Fontes normativas consultadas:

- [Lei nº 9.610/1998 — arts. 8º e 46](https://www.planalto.gov.br/ccivil_03/leis/l9610.htm)
- [CC BY-NC-SA 4.0 — resumo oficial](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt)
- [CC BY-ND 3.0 — texto legal oficial](https://creativecommons.org/licenses/by-nd/3.0/legalcode)

Esta é uma classificação de governança do corpus, não um parecer jurídico. Uma
eventual disponibilização pública do corpus processado, uso comercial ou mudança de
jurisdição exigirá nova análise e, quando aplicável, consulta institucional.

## Restrições que passam a ser obrigatórias

- Corpus bruto, texto processado e embeddings continuam locais e fora do Git.
- Respostas devem sintetizar fatos e fornecer a citação construída a partir dos
  metadados; não devem reproduzir passagens extensas das fontes.
- Trechos literais devem ser curtos, fiéis, necessários e acompanhados de título,
  instituição e URL da fonte.
- Nas páginas CC BY-ND, a ingestão se limita ao conteúdo principal da página. Imagens,
  vídeos, anexos, marcas e materiais de terceiros não herdam automaticamente a
  licença do rodapé.
- Fontes com restrição não comercial não podem ser reaproveitadas em uma futura
  versão comercial sem nova autorização.
- A Instrução Normativa deve preservar número, ano, jurisdição e vigência; a
  classificação de ato oficial não converte elementos gráficos de terceiros em
  domínio público.

## Estado

**Aprovado, publicado e validado.** Os sete registros não possuem mais
`license_status=to_verify`. Os textos e `chunk_id`s permaneceram idênticos, mas o
manifesto recebeu uma nova versão porque a licença faz parte da proveniência. A
trilha humana está registrada em `license_audit_001.csv`.
