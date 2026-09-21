# Solicitação pronta de decisão institucional — LGPD e CEP/CONEP

## Como usar

Copiar a mensagem abaixo para o e-mail ou canal institucional do orientador. Inserir
nomes e contatos somente fora do repositório público. Anexar ou apontar para
`docs/INSTITUTIONAL_GATE_PACKAGE.md` caso seja solicitado o fundamento completo.

## Mensagem para encaminhamento

**Assunto:** Confirmação institucional de LGPD e enquadramento ético — TCC ImmunoCheck

Prezado(a),

solicito uma confirmação escrita sobre o enquadramento institucional do TCC
ImmunoCheck antes de fechar a versão destinada à apresentação.

O projeto é um protótipo acadêmico local que usa LLM e RAG para analisar alegações
sobre vacinação humana. A avaliação foi realizada exclusivamente com documentos
públicos e alegações sintéticas. Não houve recrutamento, entrevistas, observação de
participantes, coleta de mensagens reais nem uso de interações do Telegram como
dataset.

A demonstração prevista é restrita: somente o autor insere entradas sintéticas de um
roteiro previamente definido. Membros da banca e terceiros não devem improvisar ou
enviar entradas ao bot. O Telegram atua como canal de transporte; o computador
processa o conteúdo localmente e não grava mensagens, imagens, URLs, respostas,
`chat_id` ou `file_id`. O bot permanecerá desligado fora da demonstração e esta
versão não será oferecida como serviço público de saúde.

A política pública do Telegram descreve infraestrutura em diferentes jurisdições e
não oferece, para este projeto, garantia de processamento exclusivamente no Brasil.
Por isso, o uso do canal pode envolver transferência internacional e deve ser
avaliado pela instituição também à luz do art. 33 da LGPD.

Peço a confirmação das decisões abaixo:

1. A instituição confirma o uso exclusivamente acadêmico, restrito e sem
   participantes ou disponibilização pública nesta versão?
2. Confirma que interações do Telegram não serão coletadas, exportadas, observadas
   como dados de pesquisa nem usadas nos resultados do TCC?
3. Considerando esse desenho, o projeto não requer submissão, requer consulta formal
   ou requer submissão ao CEP/CONEP? Solicito indicar o fundamento, parecer ou número
   de protocolo aplicável.
4. Quem deve ser registrado como controlador e quem atua como operador ou pessoa
   autorizada durante a demonstração?
5. Qual hipótese legal institucional deve ser registrada para o tratamento
   transitório de dados comuns e para eventual dado sensível enviado apesar dos
   avisos?
6. Qual canal institucional de privacidade/encarregado deve constar no aviso ao
   usuário?
7. A instituição aceita o Telegram como canal apenas para a demonstração restrita,
   considerando que a plataforma recebe o conteúdo antes do processamento local e
   que isso pode envolver transferência internacional? Qual fundamento, mecanismo ou
   salvaguarda deve ser registrado para o art. 33 da LGPD?
8. Confirma-se a regra de que somente o autor poderá inserir as entradas sintéticas
   do roteiro, sem improviso ou participação interativa da banca e de terceiros?
9. O controle atual para envio acidental de dado sensível é suficiente? Atualmente
   há aviso prévio, processamento transitório em memória e descarte sem log, mas não
   há segunda tela de confirmação nem detecção de dado sensível antes da análise. Se
   não for suficiente, qual salvaguarda deve ser implementada?
10. Confirma-se ausência de arquivo de log e encerramento do terminal sem exportação?
11. Qual função ou canal institucional deve receber comunicação imediata de eventual
    incidente?
12. Há alguma salvaguarda adicional obrigatória antes da apresentação?

As recomendações técnicas, o inventário de dados, os controles implementados e as
referências oficiais estão no pacote institucional do projeto. Uma resposta por
e-mail, ata, parecer ou protocolo é suficiente, desde que cubra os pontos acima.

Atenciosamente,

**[preencher fora do repositório público]**

## Posição técnica recomendada

Esta tabela adianta as respostas que podem ser decididas pela engenharia. Ela não
substitui a confirmação institucional dos campos marcados como pendentes.

| Tema | Recomendação técnica | Estado |
|---|---|---|
| Escopo | Demonstração restrita, pelo autor, somente com entradas sintéticas | Recomendada e implementada |
| Participantes | Não recrutar, observar, entrevistar ou coletar mensagens de terceiros | Recomendada e implementada |
| Operação da banca | Somente o autor insere fixtures sintéticas pré-definidas; sem improviso de terceiros | Regra operacional documentada |
| Dataset | Corpus público e benchmark sintético; nenhuma interação vira dado de pesquisa | Implementada |
| Disponibilização | Manter bot desligado fora da apresentação; não oferecer serviço público | Recomendada |
| Persistência | Não gravar conteúdo, respostas, URLs ou identificadores | Implementada e testada |
| LLM e embeddings | Processamento local; nenhum conteúdo enviado a modelos externos | Implementada |
| Logs | Somente eventos e tempos, sem conteúdo ou identificadores; não exportar terminal | Implementada |
| Incidente | Parar bot, revogar token e comunicar o responsável institucional | Implementada parcialmente; falta canal institucional |
| Dado sensível acidental | Processar somente em memória e descartar sem log; parar a demonstração e não reproduzir/exportar o conteúdo | Parcialmente implementada; não há confirmação prévia nem detecção automática |
| Transferência internacional | Tratar o Telegram como terceiro que pode processar dados em outras jurisdições | Pendente de fundamento/salvaguarda institucional |
| CEP/CONEP | Solicitar classificação escrita; não presumir dispensa | Pendente de orientador/CEP |
| Controlador e operador | Registrar a posição da instituição | Pendente institucional |
| Base legal | Registrar a hipótese indicada pela instituição para o desenho efetivo | Pendente institucional |
| Canal do titular | Usar contato institucional, nunca contato pessoal do aluno | Pendente institucional |

## Bloco de retorno desidentificado

Após receber a decisão, criar uma síntese sem nomes, e-mails, telefones, matrícula ou
assinatura usando o formato abaixo:

```text
Data da decisão: AAAA-MM-DD
Instâncias consultadas: [funções, sem nomes pessoais]
Commit analisado: [hash do commit efetivamente encaminhado]
Escopo restrito confirmado: SIM/NÃO
Ausência de participantes e coleta de interações confirmada: SIM/NÃO
Enquadramento CEP/CONEP: NÃO REQUER / CONSULTA / SUBMISSÃO
Fundamento ou protocolo público: [preencher ou NÃO PUBLICÁVEL]
Controlador: [posição institucional]
Operador/pessoas autorizadas: [posição institucional]
Base legal para dados comuns: [posição institucional]
Base legal para eventual dado sensível: [posição institucional]
Canal institucional do titular: [descrição ou URL pública]
Telegram aceito para demonstração restrita: SIM/NÃO/COM CONDIÇÕES
Transferência internacional avaliada: SIM/NÃO — fundamento/salvaguarda: [preencher]
Somente o autor pode inserir fixtures do roteiro: SIM/NÃO
Controle de dado sensível acidental aceito: SIM/NÃO/EXIGE SALVAGUARDA
Ausência de logs persistentes confirmada: SIM/NÃO
Canal/função de incidente: [posição institucional]
Salvaguardas adicionais: [nenhuma ou descrição]
Resultado do gate: APROVADO / PENDENTE / REPROVADO
```

Não versionar o e-mail ou parecer original se ele contiver dados pessoais. Guardar o
original no canal institucional adequado e publicar apenas a síntese necessária.

## Fontes oficiais revalidadas em 21/09/2026

- [Lei nº 13.709/2018 — LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [Guia da ANPD para fins acadêmicos e pesquisas](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-orientativo-tratamento-de-dados-pessoais-para-fins-academicos-e-para-a-realizacao-de-estudos-e-pesquisas)
- [Resolução CNS nº 510/2016](https://www.gov.br/conselho-nacional-de-saude/pt-br/atos-normativos/resolucoes/2016/resolucao-no-510.pdf/view)
- [Resolução CNS nº 674/2022](https://www.gov.br/conselho-nacional-de-saude/pt-br/acesso-a-informacao/atos-normativos/resolucoes/2022/resolucao-no-674.pdf/view)
- [Ofício Circular CONEP nº 17/2022](https://www.gov.br/conselho-nacional-de-saude/pt-br/acesso-a-informacao/camaras-tecnicas-e-comissoes/conep/legislacao/oficios-circulares/oficio-circular-no-17-de-5-de-julho-de-2022.pdf)
- [Política de Privacidade do Telegram](https://telegram.org/privacy)
- [Orientações do CEP/UNIPÊ para submissão](https://www.unipe.edu.br/comite-de-etica-em-humanos/como-submeter-o-projeto/)

Este material é apoio técnico para decisão institucional; não é parecer jurídico nem
declara, por si só, dispensa ou aprovação ética.

## Prazo de encaminhamento

Encaminhar imediatamente e, sempre que possível, com pelo menos quatro semanas de
antecedência. Esse intervalo não é garantia: a Resolução CNS nº 674/2022 prevê até
sete dias para checagem documental e, conforme a tramitação, até 15, 21, 30 ou 45
dias para emissão do parecer; resposta a pendência reinicia a contagem. Se a defesa
já estiver próxima, informar a data ao orientador/CEP sem solicitar redução de rigor
ou presumir aprovação tácita.
