# Correções e notas de auditoria — acompanha TASKS_preenchido.md

Responsável: usr_002-independente. Data: 2026-09-16 (versão 2, após o retorno das
diligências documentais). Documento avulso, para não inserir seções no bloco de
decisão de `TASKS.md`. Nenhuma resposta original foi alterada: as duas rodadas
permanecem como estão no snapshot, e as correções abaixo são registros da
adjudicação.

## 0. Snapshot consultado e integridade

Conferi os hashes por conta própria, e não apenas por leitura do retorno:

- `corpus/raw/ms_escolas_2025.pdf` — SHA-256
  `9afcf8cb3dd03ea04c94bf1c19e9b11c7db94d0e08dd0f0f980d8e4b9c52d885`,
  4.550.864 bytes. Confere.
- `corpus/raw/ms_multivacinacao_2026.pdf` — SHA-256
  `3f1edcd8a0481374f77ad46e6966b81e45a23b8187c9c1abfadef085b1b302df`,
  935.928 bytes. Confere.

Ambos coincidem com o `document_sha256` dos chunks publicados. Os arquivos não
foram copiados nem redistribuídos.

Distingo, nos blocos de decisão, dois níveis de conferência, porque isso muda o
peso da evidência:

- **Lida por mim no documento**: ms_escolas_2025 (itens 026 e 044) e
  ms_multivacinacao_2026 (itens 022, 023 e 030).
- **Transcrita no retorno de diligências**: who_como_vacinas_funcionam (038),
  ms_guia_dengue_butantan_2026 (039), acsomega (015) e ms_calendario_2026 (030).
  Registrei o rótulo com base nelas, sinalizando em cada bloco que a transcrição
  não foi validada por mim no arquivo. Para o item 038, em que a transcrição é o
  fundamento único da mudança de rótulo, peço validação no snapshot antes do
  congelamento.

## 1. Resolução das quatro pendências

Nenhum caso permanece PENDENTE. Todos se resolveram pelas condições que eu havia
enunciado, e não por aproximação aos rótulos anteriores:

- **022 → SUPPORTED** (ação: manter). A nota da Figura 2, p.7 do arquivo digital
  (p. impressa 6), define o incremento percentual pela diferença entre o período
  atual e o anterior, dividida pelo valor do período anterior, multiplicada por
  100. A multiplicação por 100 apenas expressa o quociente em pontos percentuais.
- **023 → REFUTED** (ação: manter). Mesma nota: há divisão pelo valor anterior,
  o que contradiz literalmente a alegação de diferença simples.
- **026 → REFUTED** (ação: manter). Quadro 3, p.13 do arquivo digital
  (p. impressa 12), bloco "Obtenção de Autorização dos Pais": definir processo de
  consentimento, criar formulários, definir meios para a coleta e registro das
  autorizações com prazos claros e monitorar a taxa de respostas.
- **044 → REFUTED** (ação: corrigir, de MISLEADING). O documento atribui o
  processo à Coordenação de Educação, com instrumentos, prazos e monitoramento, e
  no Quadro 4 manda oferecer o termo de recusa para assinatura; nada nele faculta
  à escola dispensar a etapa.

Retiro as sugestões de correção textual que eu havia feito em 022 e 023 (nomear o
documento na redação): o chunk versionado ancora a alegação, e a mudança seria
material, exigindo nova anotação sem ganho de verificabilidade.

## 2. Item 038 — condição cumprida, rótulo alterado

Minha decisão preenchida dizia que, se a fonte enunciasse que a proteção coletiva
não é completa, o rótulo migraria de MISLEADING para REFUTED. A passagem da OMS
afirma que nenhuma vacina confere 100% de proteção e que a imunidade de grupo não
confere proteção total às pessoas que não podem ser vacinadas com segurança. Deixa
de ser caso de ausência de menção e passa a ser contradição direta. Rótulo final:
**REFUTED**, ação corrigir. A mudança decorre da evidência, não de convergência.

## 3. Correções registradas (as respostas originais ficam preservadas)

**3.1. Caso 033 — inconsistência com o resumo da rodada.** O campo individual da
segunda rodada trazia REFUTED; as observações finais escreviam "catorze"
insuficientes para 12 IDs listados e incluíam o 033 entre eles. Os campos
individuais são a fonte de verdade: havia 11 insuficientes (010, 012, 017, 020,
021, 022, 023, 027, 028, 041 e 047). Sem efeito sobre métricas já calculadas.
Rótulo adjudicado do item: MISLEADING, `adjudication_basis=annotation_disagreement`.

**3.2. Caso 048 — inconsistência interna da justificativa.** Onde se lia que "a
maior parte das notificações sequer é confirmada", o correto é: dos 11.937 casos
suspeitos notificados entre 1º/1/2025 e 30/6/2025, 6.169 (51,7%) foram
confirmados, ou seja, a maioria foi confirmada e cerca de 48% não. O erro não
afeta o argumento central. Rótulo final: MISLEADING.

**3.3. Caso 026 — imprecisão minha na segunda rodada (nova).** Minha justificativa
anterior descrevia "termos de consentimento assinados pelos responsáveis". A
leitura do documento mostra que o instrumento previsto é um **termo de recusa**,
de lógica opt-out: o Anexo A registra que, não devolvido o termo preenchido e
assinado até a data indicada, os profissionais poderão administrar a vacina. O
rótulo não muda, porque o documento prevê expressamente coleta e registro de
autorizações, mas a descrição do mecanismo estava imprecisa. Registro aqui, sem
alterar a resposta original.

## 4. Base de adjudicação por caso

- `annotation_disagreement`: 002, 008, 011, 013, 019, 022, 023, 030, 031, 033,
  034, 037, 038, 044, 046, 048 (as 16 divergências).
- Sem base especial: 001, 015, 018, 024, 026, 039. O caso 026 deixa de exigir
  `adjudication_basis=evidence_audit`: a pendência que eu havia aberto sobre ele
  foi resolvida pelo documento e o rótulo final coincide com o das duas rodadas,
  de modo que não há correção de erro compartilhado a registrar.

## 5. Critério uniforme aplicado nas 11 divergências MISLEADING x REFUTED

Regra única, fixada antes de olhar a distribuição resultante:

- REFUTED quando o documento-fonte enuncia explicitamente o contrário da
  proposição central, ainda que a premissa da alegação seja verdadeira.
- MISLEADING quando há parte factual relevante sustentada e a conclusão é
  extrapolação material que a fonte não contradiz explicitamente, lembrando que
  ausência de menção não refuta.

Resultado após as diligências: REFUTED em 002, 008, 011, 013, 019, 030, 034, 038
e 044; MISLEADING em 033 e 048. Os dois casos que migraram (038 e 044) migraram
porque o texto-fonte passou a exibir a contradição que antes eu supunha apenas
ausente — exatamente o que a regra prevê.

Nas divergências com INSUFFICIENT_EVIDENCE de um lado (031, 037, 046), mantive a
regra de que informação geral não decide caso local não identificado, e corrigi os
três rótulos da segunda rodada, que haviam usado literatura geral para refutar
cenários sem território, indivíduo ou período identificados.

## 6. Distribuição final dos 22 casos

- REFUTED: 001, 002, 008, 011, 013, 018, 019, 023, 026, 030, 034, 038, 044 (13).
- SUPPORTED: 015, 022, 024, 039 (4).
- MISLEADING: 033, 048 (2).
- INSUFFICIENT_EVIDENCE: 031, 037, 046 (3).
- PENDENTE: nenhum.

Ações: manter em 001, 015, 018, 022, 023, 024, 026, 031, 033, 037, 039, 046, 048
(13); corrigir em 002, 008, 011, 013, 019, 030, 034, 038, 044 (9); nenhuma
exclusão. A distribuição é consequência da regra, não objetivo, e não busquei
cotas por classe.

## 7. Efeitos sobre estratificação, antes do congelamento

- As mudanças de rótulo alteram a composição de classes em
  `influenza_repeat_comparators`, `bcg_effectiveness_context`, `hpv_type_coverage`,
  `art_fertility_scope`, `aluminum_local_reactions`,
  `rotavirus_geographic_performance`, `herd_protection`,
  `multivaccination_target_age`, `measles_manaus_historical_outbreak`,
  `yellow_fever_adult_seroprotection`, `ckd_nondialysis_population`,
  `school_vaccination_consent` e `meningitis_notifications_confirmation`.
  Reconferir mínimos por classe e o split 60/40 sem separar família.
- Atenção a duas famílias que ficaram homogêneas: `school_vaccination_consent`
  (026 e 044, ambos REFUTED, split development) e `bcg_effectiveness_context`
  (001 e 008, ambos REFUTED). Se o protocolo exigir diversidade de classes por
  família, elas precisarão de substitutos, o que é decisão do projeto e não da
  adjudicação. Em contrapartida,
  `vaccination_coverage_relative_increment` mantém SUPPORTED e REFUTED.
- Sem casos PENDENTE, o pacote está completo para a CLI montar o candidato em
  memória e reportar hash, exclusões e prontidão estrutural.
- Permanece em aberto, e não é suprida por este pacote, a auditoria geral do
  benchmark sintético: pertinência das evidências dos 48 itens, paráfrases e
  vazamento semântico entre famílias e splits, limites de validade e procedimento
  real de anotação, a discutir com o orientador antes de qualquer congelamento ou
  experimento.
