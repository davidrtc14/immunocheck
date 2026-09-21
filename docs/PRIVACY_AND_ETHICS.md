# Revisão de privacidade, ética e direitos humanos

Revisão técnica concluída em 18/09/2026. Este documento registra decisões de
engenharia e questões que exigem validação institucional. Ele não é parecer
jurídico nem declara conformidade integral com a LGPD.

Referências oficiais consultadas:

- [Lei nº 13.709/2018 — LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm);
- [Guia da ANPD para fins acadêmicos e pesquisas](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-orientativo-tratamento-de-dados-pessoais-para-fins-academicos-e-para-a-realizacao-de-estudos-e-pesquisas);
- [Guia da ANPD sobre agentes de tratamento e encarregado](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-orientativo-para-definicoes-dos-agentes-de-tratamento-de-dados-pessoais-e-do-encarregado);
- [Guia da ANPD sobre segurança da informação](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/processo-guia-orientativo-sobre-seguranca-da-informacao-para-agentes-de-tratamento-de-pequeno-porte.pdf);
- [Resolução CNS nº 510/2016](https://www.gov.br/conselho-nacional-de-saude/pt-br/atos-normativos/resolucoes/2016/resolucao-no-510.pdf/view).
- [Resolução CNS nº 674/2022](https://www.gov.br/conselho-nacional-de-saude/pt-br/acesso-a-informacao/atos-normativos/resolucoes/2022/resolucao-no-674.pdf/view).
- [Ofício Circular CONEP nº 17/2022](https://www.gov.br/conselho-nacional-de-saude/pt-br/acesso-a-informacao/camaras-tecnicas-e-comissoes/conep/legislacao/oficios-circulares/oficio-circular-no-17-de-5-de-julho-de-2022.pdf).
- [Política de Privacidade do Telegram](https://telegram.org/privacy).

## Escopo desta revisão

O protótipo é executado localmente para demonstração acadêmica. Não há piloto
público, cadastro, memória conversacional, perfil de usuário nem uso de mensagens
reais no dataset. A avaliação offline usa documentos públicos e alegações
sintéticas curadas. Qualquer estudo futuro com participantes ou mensagens reais é
uma nova operação de tratamento e não está autorizado por este documento.

## Inventário e fluxo de dados

| Dado | Finalidade | Local/processador | Retenção local | Observação |
|---|---|---|---|---|
| Texto, imagem ou URL enviados | Executar uma checagem | Telegram → memória do computador | Nenhuma | Pode conter dado pessoal ou dado sensível de saúde mesmo sem solicitação. |
| `chat_id`, `file_id` e metadados da atualização | Receber arquivo e devolver resposta | Telegram e memória do adaptador | Nenhuma | São identificadores pessoais; não entram nos logs. |
| Texto extraído, embeddings da consulta e resposta | RAG, geração e auditoria | Tesseract, BGE-M3 e Qwen3 locais | Nenhuma | Não são enviados a LLM ou embedding externo. |
| URL informada | Baixar conteúdo público | Computador e servidor do endereço | Nenhuma | O servidor acessado observa a requisição; URL pode conter identificadores. |
| Eventos técnicos e tempos | Operação e diagnóstico | Log local | Conforme política do operador | Mensagem, URL, resposta e identificadores são excluídos por desenho. |
| Corpus e benchmark | Conhecimento e avaliação offline | Arquivos/PG local e Git quando permitido | Versionada | Documentos públicos; alegações sintéticas sem perfis de autores. |
| Token do bot e senhas locais | Autenticação operacional | Variáveis de ambiente | Não versionada | Devem ser rotacionados em caso de exposição. |

O tratamento transitório ainda é tratamento de dados; ausência de persistência não
elimina obrigações. Além disso, o Telegram recebe o conteúdo antes do ImmunoCheck e
aplica suas próprias políticas, infraestrutura e prazos de retenção. Sua política
pública descreve infraestrutura em diferentes jurisdições e não garante ao projeto
processamento exclusivo no Brasil; o possível enquadramento como transferência
internacional deve ser avaliado institucionalmente segundo o art. 33 da LGPD.

## Regra operacional da demonstração

Somente o autor pode enviar as fixtures sintéticas do roteiro previamente definido.
Membros da banca e terceiros não devem digitar exemplos, encaminhar mensagens ou
improvisar testes. O bot fica ligado apenas durante a passagem controlada e é
encerrado ao final.

Se, apesar dessa regra, chegar conteúdo possivelmente pessoal ou sensível, o autor
deve interromper a demonstração, não ler, reproduzir, capturar ou exportar a mensagem
e encerrar o bot. O adaptador não grava conteúdo nem identificadores e descarta as
referências em memória ao término do processo, mas não existe confirmação anterior
ao processamento nem classificador automático de dado sensível. O Telegram pode
conservar sua própria cópia; por isso a exclusão local não equivale a eliminação na
plataforma. A instituição deve decidir se o aviso e a restrição operacional bastam ou
se uma confirmação adicional é condição para a apresentação.

## Princípios aplicados por desenho

- **Finalidade e adequação:** somente checagem de alegações sobre vacinação humana.
- **Necessidade:** sem conta própria, histórico, cache conversacional ou telemetria
  de conteúdo; uma alegação principal por requisição.
- **Transparência:** `/start` e `/privacidade` explicam processamento local,
  participação do Telegram, ausência de memória e proibição de dados médicos
  pessoais desnecessários.
- **Segurança e prevenção:** segredos fora do Git, SSRF bloqueado, limites de
  download, conteúdo externo não confiável, logs sanitizados e modelos locais.
- **Não discriminação:** resultados devem ser analisados por classe, tema e tipo de
  entrada quando houver amostra; atributos pessoais não são inferidos.
- **Prestação de contas:** decisões, corpus, hashes, falhas e resultados negativos
  são versionados; a v3 descartada foi preservada em vez de ocultada.

## Papéis e base legal: decisão institucional pendente

O código não pode definir quem é controlador, operador ou encarregado. Antes de
qualquer piloto aberto, UNIPÊ, orientação e autor devem registrar quem decide a
finalidade e os meios do tratamento, quem opera o sistema e qual canal atenderá os
titulares. Também devem determinar a base legal aplicável ao uso pretendido,
inclusive para dado sensível de saúde eventualmente enviado espontaneamente.

Não se presume consentimento nem se presume automaticamente a hipótese de estudos
por órgão de pesquisa. A aplicabilidade dessas bases depende do responsável
institucional e do desenho real do piloto. Até essa decisão, a demonstração deve
usar somente entradas sintéticas e não identificáveis.

## Direitos dos titulares e contestação

Como o ImmunoCheck não retém interações, normalmente não haverá conteúdo local para
acessar, corrigir ou eliminar após a resposta. Ainda assim, um piloto público deve
oferecer canal institucional para perguntas, oposição e relato de incidente, além
de explicar separadamente como exercer direitos perante o Telegram.

No plano ético, o usuário pode contestar um veredito e verificar as fontes. O
sistema não remove conteúdo, pune autores nem se apresenta como árbitro definitivo.
Correções no corpus ou benchmark são versionadas com justificativa e histórico.

## Direitos humanos e riscos de IA

| Risco | Controle existente | Limitação residual |
|---|---|---|
| Censura ou autoridade indevida | Fontes visíveis, quatro classes e linguagem não punitiva | Seleção institucional do corpus influencia o enquadramento. |
| Confundir ausência de evidência com falsidade | Classe `INSUFFICIENT_EVIDENCE` | Auditor atual apresenta falsos positivos de abstenção. |
| Desinformação produzida pelo sistema | RAG local, IDs válidos, schema e auditor | Gerador e auditor usam o mesmo modelo; erros são correlacionados. |
| Conselho médico individual | Prompt, guarda determinística e aviso | Formulações indiretas podem escapar; não substitui profissional. |
| Viés geográfico/institucional | Proveniência e cobertura temática documentadas | Corpus prioriza português e instituições oficiais; validade externa é limitada. |
| Exclusão por acessibilidade | Chat textual, linguagem curta e fontes legíveis | Telegram, OCR e links ainda criam barreiras; não houve teste com participantes. |
| Mudança temporal de recomendações | Datas, versões e atualização manual do corpus | Não há atualização automática; respostas podem envelhecer. |
| Falsa precisão | Abstenção e publicação de métricas/intervalos | Benchmark sintético tem atalhos lexicais e amostra pequena. |

O direito à saúde e à informação exige não só combater alegações incorretas, mas
também evitar segurança excessiva, ocultação de incerteza e aconselhamento pessoal.
Uma resposta sempre deve permitir inspeção das referências e informar que novas
evidências podem mudar a conclusão.

## Pesquisa com participantes

O benchmark atual não contém mensagens de usuários nem dados coletados de
participantes. Antes de teste de usabilidade, entrevista, observação de pessoas ou
coleta de mensagens reais, o autor deve apresentar o protocolo ao orientador e
consultar a instância ética competente da UNIPÊ. A Resolução CNS nº 510/2016 cobre
pesquisas em Ciências Humanas e Sociais com dados obtidos diretamente de
participantes, informações identificáveis ou riscos superiores aos cotidianos; a
instituição, não o software, decide o enquadramento e a tramitação aplicáveis.

## Resposta a incidente

1. Interromper o bot e preservar somente evidência técnica necessária, sem copiar
   conteúdo de usuários para o relatório.
2. Revogar token do Telegram e credenciais afetadas; isolar a máquina se necessário.
3. Registrar natureza, alcance, dados potencialmente afetados, controles e ações.
4. Comunicar imediatamente o responsável institucional definido para avaliar
   risco, titulares afetados e eventual comunicação à ANPD.
5. Corrigir a causa, testar a correção e documentar a retomada.

## Evidências técnicas verificadas

- Adaptador sem repositório de interações; estado de fila e offset só em memória.
- Logs usam mensagens fixas e não interpolam conteúdo, URL, `chat_id` ou `file_id`.
- Imagem, HTML e PDF são processados em memória.
- Testes automatizados cobrem ausência de conteúdo/identificadores nos logs,
  rejeição de tipos e tamanhos, SSRF, prompt injection e orientação médica direta.
- `.gitignore` exclui `.env`, corpus bruto, modelos, bancos e artefatos locais.

## Pendências antes de piloto público

- [ ] Identificar formalmente controlador, operador e contato de privacidade.
- [ ] Registrar finalidade operacional, base legal e prazo dos logs técnicos.
- [ ] Avaliar transferência e riscos do Telegram com o responsável institucional.
- [ ] Decidir com orientador/instância ética se o protocolo exige CEP/CONEP.
- [ ] Definir procedimento institucional de incidente e exercício de direitos.
- [ ] Fazer teste de acessibilidade/usabilidade somente após a decisão ética.

Enquanto essas pendências estiverem abertas, o uso autorizado é demonstração local
com dados sintéticos, não serviço público de saúde nem estudo com participantes.
O formulário de decisão para orientador, encarregado e CEP está consolidado em
`docs/INSTITUTIONAL_GATE_PACKAGE.md`.

Além da Resolução CNS nº 510/2016, a decisão deve considerar a Resolução CNS nº
674/2022 e o Ofício Circular CONEP nº 17/2022. Essas referências não autorizam uma
autodeclaração de dispensa: o enquadramento integral do protocolo deve ser confirmado
pela instância institucional competente.
