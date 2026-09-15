# Lote documental 008 — proposta para decisão humana

Preparado em 14/09/2026. Este documento apresenta uma proposta técnica; nenhum
item deste lote está validado ou publicado no corpus ativo antes da aprovação
expressa do autor.

## Resultado executivo

- Foram examinados 14 candidatos escolhidos para cobrir exatamente a lacuna
  temática mínima restante: quatro fontes normativas, duas de eficácia, duas de
  populações especiais, duas de epidemiologia, duas de alegações causais, uma de
  vacina específica e uma de comunicação/equidade.
- Os 14 documentos passaram pela obtenção, verificação de hash e extração. O lote
  soma 566.342 caracteres e 596 chunks potenciais; não houve arquivo vazio,
  alerta técnico, caractere de substituição nem duplicata bruta ou textual.
- **A proposta é aprovar os 14 documentos**, respeitando os limites e conflitos
  declarados abaixo. Se a proposta for aprovada, o corpus passará de 66 para 80
  documentos validados e todos os mínimos temáticos planejados serão atingidos.
- A aprovação vale apenas para os bytes identificados pelos SHA-256 em
  `batch_008.csv`. Ela não autoriza usar as fontes como verdade absoluta nem
  dispensa triangulação, controle temporal e inspeção das citações.

## Documentos propostos para aprovação

| Documento | Tema | Chunks | Licença/base | Limite principal |
|---|---|---:|---|---|
| Imunização de recém-nascidos em maternidades — NT 20/2026 | Normas e calendários | 20 | Ato oficial, Lei 9.610 art. 8 IV | Preservar vigência, população e contexto operacional. |
| Dose zero contra sarampo — NT 21/2026 | Normas e calendários | 12 | Ato oficial, Lei 9.610 art. 8 IV | Dose de bloqueio não é dose do esquema de rotina. |
| Atualização da VPC20 — NT 64/2026 | Normas e calendários | 7 | Ato oficial, Lei 9.610 art. 8 IV | Correção pontual deve acompanhar o guia técnico citado. |
| Alerta de sarampo — NT Conjunta 234/2026 | Normas e calendários | 29 | Ato oficial, Lei 9.610 art. 8 IV | Indicadores epidemiológicos têm data de corte; o redirecionamento oficial contém “324” no nome do arquivo, mas o PDF assinado é a NT 234. |
| Eficácia/efetividade de vacinas pneumocócicas em adultos | Eficácia e imunogenicidade | 44 | CC BY 4.0 | PCV13/PPSV23 não sustentam extrapolação automática à PCV20. |
| Vacinação repetida contra influenza | Eficácia e imunogenicidade | 75 | CC BY 4.0 | Resultado depende de temporada, subtipo, idade e correspondência antigênica. |
| Vacinas de mRNA em imunocomprometidos | Populações especiais | 43 | CC BY-NC 4.0 | Imunogenicidade não equivale a efetividade; financiamento e participação da Moderna exigem contrapeso independente. |
| Eficácia vacinal em pessoas com DRC sem diálise | Populações especiais | 42 | CC BY 4.0 | Vacinas e desfechos distintos; separar soroconversão e proteção clínica. |
| Doença pneumocócica invasiva na América Latina e Caribe | Epidemiologia | 59 | CC BY 4.0 | Estimativa regional heterogênea não é dado brasileiro atual. |
| Surto de sarampo no Amazonas, 2018–2019 | Epidemiologia | 35 | CC BY 4.0 | Associação espaço-temporal histórica não prova causalidade individual nem retrata o Brasil atual. |
| Guillain-Barré e vacinação contra covid-19 | Alegações causais | 26 | CC BY 4.0 | Preservar plataforma, comparador, risco absoluto e incerteza causal. |
| HPV e doenças autoimunes | Alegações causais | 60 | CC BY 4.0 | Ausência de aumento detectado não significa prova de risco zero. |
| Guia da vacina contra dengue do Instituto Butantan | Vacinas específicas | 81 | CC BY-NC-SA 4.0 | Produto, faixa etária e esquema não se transferem para a TAK-003. |
| Comunicação de risco orientada à equidade | Comunicação, equidade e ética | 63 | CC BY-NC 4.0 | Revisão de escopo da pandemia, não evidência exclusiva sobre vacinação nem universal. |

## Independência, conflitos e triangulação

- A revisão de vacinas de mRNA em imunocomprometidos foi financiada pela Moderna
  e teve participação de empregados da empresa. Ela pode integrar o corpus, mas
  não deve ser a única evidência para comparação entre produtos ou para afirmações
  de superioridade.
- A revisão pneumocócica da América Latina e Caribe recebeu um *independent medical
  grant* da Pfizer e declara que o financiador não participou do desenho, análise
  ou publicação. O vínculo ainda deve acompanhar qualquer trecho recuperado.
- A revisão sobre vacinação repetida contra influenza declara financiamento
  institucional e relações de autores com fabricantes e comitês consultivos. Isso
  não invalida os resultados, mas exige triangulação e preservação das limitações.
- Os demais artigos registram as declarações de financiamento e conflitos
  disponíveis nos bytes coletados. “Sem conflito declarado” não equivale a prova
  de independência absoluta.

## Auditoria jurídica e técnica

As quatro notas técnicas são textos de atos oficiais. A classificação
`official-act-BR-L9610-art8-IV` está limitada ao texto normativo conforme o art. 8,
IV, da Lei 9.610/1998; autoria, origem, vigência e integridade permanecem
registradas. Ela não se estende automaticamente a fotografias ou outras obras
incorporadas.

Os artigos obtidos em XML JATS declaram suas licenças Creative Commons nos bytes
coletados. O PDF do artigo sobre HPV declara CC BY 4.0, e o guia da vacina contra
dengue declara CC BY-NC-SA 4.0 na página 3. A licença MIT do software não
relicencia o corpus.

O relatório `batch_008.audit.json` contém somente metadados, hashes e métricas. Os
arquivos integrais, textos extraídos e chunks permanecem locais e ignorados pelo
Git. Nenhuma interação real de usuário foi coletada ou usada na seleção.

## Guardrails metodológicos

- Normas brasileiras vigentes têm precedência para calendário, elegibilidade e
  conduta; documentos científicos não criam regra operacional.
- Produto, plataforma, dose, faixa etária, população, comparador, desfecho e
  período devem acompanhar cada conclusão recuperada.
- Imunogenicidade, eficácia de ensaio e efetividade observacional não são medidas
  intercambiáveis.
- Associação após vacinação não demonstra causalidade; risco relativo não pode
  ocultar risco absoluto, taxa de base ou incerteza.
- Evidência histórica ou regional não deve ser apresentada como situação
  epidemiológica brasileira em tempo real.
- Conflitos não implicam rejeição automática, mas devem reduzir a autossuficiência
  da fonte e acionar busca por evidência independente.
- O sistema deve continuar escolhendo “evidência insuficiente” quando os trechos
  recuperados não sustentarem integralmente a explicação.

## Reprodução

```powershell
.\.venv\Scripts\python.exe scripts\audit_corpus_batch.py --batch 008
```

## Estado

**Aguardando decisão humana.** A proposta é aprovar conjuntamente os 14 documentos.
Somente depois de uma aprovação expressa o catálogo poderá ser alterado para
`validated` e uma nova versão do corpus poderá ser construída, importada e ativada.
