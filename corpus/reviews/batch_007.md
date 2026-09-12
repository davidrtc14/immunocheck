# Lote documental 007 — parecer para aprovação

Preparado em 12/09/2026. Nenhum documento deste lote foi promovido ao corpus. As
decisões abaixo são propostas e dependem da aprovação conjunta do autor. A eventual
aprovação valerá somente para os bytes identificados pelos SHA-256 em
`batch_007.csv`.

## Resultado executivo

- Treze candidatos foram examinados nas quatro lacunas prioritárias: normas,
  composição e fabricação, segurança e vacinas específicas.
- Todos foram obtidos por endpoints oficiais e passaram pela extração técnica. O
  lote soma 1.203.329 caracteres e 1.243 chunks potenciais.
- **Propõe-se aprovar oito artigos**, todos com licença Creative Commons explícita,
  somando 503.254 caracteres e 510 chunks potenciais.
- **Propõe-se reter quatro documentos normativos da OMS:** os PDFs são íntegros e
  gratuitos para leitura, mas não declaram licença ou permissão de reutilização nos
  bytes coletados.
- **Propõe-se rejeitar um registro duplicado:** o artigo de rotavírus de 2025 possui
  bytes idênticos a uma fonte já validada no lote 004.

## Documentos propostos para aprovação

| Documento | Tema | Volume | Utilidade e cuidado obrigatório |
|---|---|---:|---|
| Mecanismos e plataformas de adjuvantes | Composição e fabricação | 132 chunks | Revisão narrativa ampla, com adjuvantes licenciados e experimentais; não demonstra a composição de um produto específico nem oferece busca sistemática. |
| Otimização de adjuvantes de alumínio | Composição e fabricação | 68 chunks | Explica físico-química, formulação e interação com excipientes; não é síntese clínica de segurança e possui vínculos industriais e patentes declarados. |
| Anafilaxia a aditivos em vacinas | Composição e fabricação | 52 chunks | Diferencia excipientes, resíduos e contaminantes; contexto regulatório alemão e relatos raros não permitem incidência universal. |
| Linhagens celulares na fabricação de vacinas virais | Composição e fabricação | 112 chunks | Esclarece que substrato de produção não equivale a células intactas no produto final; revisão narrativa não substitui bula ou controle de qualidade por produto. |
| Incidência de Guillain-Barré após vacinação em massa | Segurança e farmacovigilância | 29 chunks | Resume coincidência temporal em dados de vigilância, não causalidade; há heterogeneidade, limitada representatividade e possível viés de detecção. |
| Miocardite/pericardite após vacinas de mRNA | Segurança e farmacovigilância | 54 chunks | Sete estudos observacionais e poucos casos; preservar risco absoluto, comparador, idade, sexo, produto, dose, infecção e conflitos declarados. |
| Queda da efetividade de vacinas acelulares contra coqueluche | Vacinas específicas | 29 chunks | Evidência restrita ao esquema dos EUA e poucos estudos; queda exponencial foi modelada e vários autores trabalhavam para fabricante. |
| Fatores da resposta à vacina contra hepatite B em adultos | Vacinas específicas | 34 chunks | Meta-análise de resposta sorológica, não efetividade clínica; houve heterogeneidade, viés de publicação e formulações diferentes. |

## Material proposto para retenção ou rejeição

| Documento | Proposta | Motivo |
|---|---|---|
| Posição da OMS sobre HPV — 2022 | Reter | PDF bilíngue íntegro, porém sem licença ou permissão explícita nos bytes; recomendação global e com uso off-label, não calendário brasileiro. |
| Posição da OMS sobre rotavírus — 2021 | Reter | PDF bilíngue íntegro, porém sem licença ou permissão explícita nos bytes; sua data e escopo global exigem controle de vigência e jurisdição. |
| Posição da OMS sobre hepatite B — 2017 | Reter | PDF bilíngue íntegro, porém sem licença ou permissão explícita nos bytes; material de 2017 não deve ser tratado como calendário brasileiro vigente. |
| Posição da OMS sobre pólio — 2022 | Reter | Além da ausência de licença nos bytes, a página da OMS informa atualização parcial da recomendação pelo SAGE em março de 2025. |
| Estimativas globais de eficácia e efetividade contra rotavírus — 2025 | Rejeitar | O SHA-256 bruto coincide com `eclinm_rotavirus_global_2025`, já validado e publicado; uma segunda entrada produziria duplicação e peso indevido no retrieval. |

## Auditoria técnica e jurídica

Os nove artigos foram obtidos como XML JATS integral pelo Europe PMC. Oito são
fontes novas recomendadas para aprovação: sete declaram CC BY 4.0 e uma declara
CC BY-NC 4.0. O nono XML também declara CC BY 4.0, mas é duplicata exata de um
documento já validado. Licença aberta não justifica indexar a mesma evidência duas
vezes.

Os quatro *position papers* foram obtidos diretamente pela API oficial do
repositório IRIS/OMS. A extração não encontrou licença, link Creative Commons ou
permissão expressa em nenhum dos PDFs. A página de publicação informa autoria e
copyright da OMS, mas a decisão do corpus permanece vinculada aos bytes
reproduzíveis coletados. Acesso gratuito não foi tratado como autorização de
reutilização.

Não houve duplicata textual entre os demais documentos nem coincidência bruta com
o corpus validado. Arquivos brutos, extrações e chunks continuam ignorados pelo
Git; a licença MIT do código não relicencia nenhuma fonte documental.

## Guardrails metodológicos

- Adjuvante, conservante, estabilizante, resíduo de fabricação e antígeno são
  categorias diferentes; presença, função e dose precisam ser ligadas ao produto e
  à formulação corretos.
- Linhagens celulares usadas como plataforma industrial não significam que a dose
  contenha tecidos ou células intactas; limites de resíduos e controles variam por
  processo e produto.
- Revisões narrativas sustentam explicações de mecanismo e fabricação, mas não
  recebem o peso de revisões sistemáticas para estimar risco clínico.
- Evento em janela pós-vacinação não implica causalidade. Síndrome de Guillain-Barré
  deve manter vacina, período de risco, definição de caso e taxa de base.
- Para miocardite/pericardite, risco relativo não pode ocultar o risco absoluto nem
  ser extrapolado entre idade, sexo, dose, produto ou histórico de infecção.
- A estimativa de queda da proteção contra coqueluche depende de modelo, estudos
  observacionais e esquema norte-americano; não vira taxa brasileira.
- Resposta sorológica à vacina contra hepatite B não é sinônimo de proteção clínica
  individual e não autoriza aconselhamento médico personalizado.
- Vínculos industriais e conflitos declarados não excluem automaticamente uma
  fonte, mas devem acompanhar a interpretação e a triangulação da evidência.
- Normas globais, quando futuramente licenciadas, não substituem o calendário e as
  orientações brasileiras vigentes.
- Nenhuma mensagem real de usuário foi armazenada ou utilizada, e nenhuma alegação
  do conjunto de teste foi criada a partir destas fontes.

## Reprodução

```powershell
.\.venv\Scripts\python.exe scripts\audit_corpus_batch.py --batch 007
```

O relatório `batch_007.audit.json` contém somente proveniência, hashes e métricas;
os textos integrais permanecem locais e fora do Git.

## Estado

**Aguardando aprovação humana conjunta.** Se o parecer for aprovado, somente os
oito documentos marcados `approve` serão promovidos e indexados. Os quatro
documentos da OMS permanecerão candidatos retidos, e a duplicata será marcada como
`rejected`. Nenhuma alteração será aplicada ao corpus ativo antes dessa decisão.
