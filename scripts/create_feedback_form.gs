/**
 * Cria no Google Forms o questionário anônimo de docs/USABILITY_QUESTIONNAIRE.md.
 *
 * Uso: em https://script.google.com, crie um projeto, cole este arquivo, preencha CONTACT e execute
 * createImmunoCheckForm. Os links de resposta e de edição aparecem no registro de execução.
 *
 * O formulário nasce fechado para respostas (OPEN_FOR_RESPONSES = false), porque a aplicação depende
 * da decisão ética descrita em docs/PRIVACY_AND_ETHICS.md. Abra-o no próprio Google Forms, em
 * Respostas → "Aceitando respostas", quando a aplicação for liberada.
 */

// Contato institucional exibido aos participantes; vazio omite a linha.
const CONTACT = '';
const OPEN_FOR_RESPONSES = false;

const AGREEMENT = ['Discordo totalmente', 'Concordo totalmente'];

function createImmunoCheckForm() {
  const form = FormApp.create('Avaliação do ImmunoCheck');
  form
    .setDescription(introduction_())
    .setCollectEmail(false)
    .setLimitOneResponsePerUser(false)
    .setAllowResponseEdits(false)
    .setShowLinkToRespondAgain(false)
    .setProgressBar(true)
    .setConfirmationMessage('Obrigado pela participação!')
    .setAcceptingResponses(OPEN_FOR_RESPONSES);

  // Consentimento e maioridade; "não" encerra o formulário. O Google Forms só aceita um desvio por
  // seção, por isso cada pergunta fica na sua.
  gate_(form, 'Você leu as informações acima e concorda em participar?',
    'Sim, concordo em participar', 'Não concordo');
  form.addPageBreakItem().setTitle('Idade');
  gate_(form, 'Você tem 18 anos ou mais?', 'Sim', 'Não');

  form.addPageBreakItem().setTitle('Perfil').setHelpText('Nenhuma pergunta identifica você.');
  choice_(form, 'Faixa etária', ['18–24', '25–34', '35–44', '45–59', '60 ou mais']);
  choice_(form, 'Você trabalha ou estuda na área da saúde?',
    ['Sim', 'Não', 'Prefiro não responder']);
  choice_(form, 'Com que frequência você recebe mensagens sobre vacinas em redes sociais ou aplicativos?',
    ['Nunca', 'Raramente', 'Às vezes', 'Frequentemente', 'Muito frequentemente']);

  form.addPageBreakItem().setTitle('Uso do bot');
  choice_(form, 'Quantas alegações você enviou ao bot?', ['1', '2 a 3', '4 a 5', '6 ou mais']);
  form.addCheckboxItem()
    .setTitle('Que tipos de conteúdo você enviou?')
    .setChoiceValues(['Texto', 'Imagem (print)', 'Link'])
    .setRequired(true);
  choice_(form, 'Algum envio terminou sem resposta ou com mensagem de erro?',
    ['Não', 'Sim, uma vez', 'Sim, mais de uma vez']);

  form.addPageBreakItem()
    .setTitle('Percepção das respostas')
    .setHelpText('De 1 (discordo totalmente) a 5 (concordo totalmente).');
  scale_(form, 'A explicação das respostas foi fácil de entender.');
  scale_(form, 'As fontes apresentadas pareceram confiáveis.');
  scale_(form, 'O tempo de espera pela resposta foi aceitável.');
  choice_(form,
    'Quando o bot respondeu "evidência insuficiente", a orientação dada foi útil.',
    ['1 — Discordo totalmente', '2', '3', '4', '5 — Concordo totalmente',
      'Não recebi essa resposta']);
  scale_(form, 'Eu confiaria no veredito do ImmunoCheck para decidir se compartilho uma mensagem.');
  scale_(form, 'Os vereditos recebidos pareceram corretos, pelo que eu sei sobre o assunto.');
  choice_(form, 'Você abriu algum link das fontes?', ['Sim', 'Não']);

  // System Usability Scale (Brooke, 1996): ordem e alternância originais, adaptadas ao bot.
  form.addPageBreakItem()
    .setTitle('Facilidade de uso')
    .setHelpText('De 1 (discordo totalmente) a 5 (concordo totalmente).');
  [
    'Eu acho que gostaria de usar o ImmunoCheck com frequência.',
    'Eu achei o ImmunoCheck desnecessariamente complexo.',
    'Eu achei o ImmunoCheck fácil de usar.',
    'Eu acho que precisaria da ajuda de alguém com conhecimento técnico para usar o ImmunoCheck.',
    'Eu achei que as diversas funções do ImmunoCheck estavam bem integradas.',
    'Eu achei que havia muita inconsistência no ImmunoCheck.',
    'Eu imagino que a maioria das pessoas aprenderia a usar o ImmunoCheck rapidamente.',
    'Eu achei o ImmunoCheck muito complicado de usar.',
    'Eu me senti confiante ao usar o ImmunoCheck.',
    'Eu precisei aprender muitas coisas antes de conseguir usar o ImmunoCheck.',
  ].forEach((title, index) => scale_(form, `${index + 1}. ${title}`));

  form.addPageBreakItem().setTitle('Comentários (opcionais)');
  form.addParagraphTextItem()
    .setTitle('Alguma resposta pareceu errada ou confusa? Descreva o tema em poucas palavras.')
    .setHelpText('Não copie mensagens de outras pessoas nem informe dados pessoais. '
      + 'Exemplo: "vacina da gripe e gestantes".');
  form.addParagraphTextItem().setTitle('O que você mudaria no ImmunoCheck?');

  Logger.log('Link para os participantes: %s', form.getPublishedUrl());
  Logger.log('Link de edição (só para você): %s', form.getEditUrl());
  Logger.log('Aceitando respostas: %s', OPEN_FOR_RESPONSES);
}

function introduction_() {
  const lines = [
    'Você está sendo convidado(a) a avaliar o ImmunoCheck, protótipo de Trabalho de Conclusão de '
      + 'Curso em Ciência da Computação no Centro Universitário UNIPÊ, orientado pelo Prof. Thiago '
      + 'Rodrigues Medeiros. O ImmunoCheck é um bot do Telegram que compara alegações sobre vacinação '
      + 'com documentos oficiais e científicos.',
    '',
    '• A participação é voluntária e anônima: não pedimos nome, e-mail, telefone nem usuário do '
      + 'Telegram.',
    '• O questionário leva cerca de 5 minutos. Você pode desistir a qualquer momento, sem prejuízo, '
      + 'apenas fechando a página.',
    '• Ao usar o bot, envie apenas alegações gerais sobre vacinas. Não envie dados pessoais nem '
      + 'informações sobre a sua saúde ou de outras pessoas. O bot não grava as mensagens, mas o '
      + 'Telegram as processa conforme a política dele.',
    '• O ImmunoCheck é um protótipo acadêmico e não substitui orientação de um profissional de saúde.',
    '• As respostas serão usadas apenas de forma agregada no TCC.',
  ];
  if (CONTACT) {
    lines.push(`• Dúvidas: ${CONTACT}`);
  }
  return lines.join('\n');
}

function gate_(form, title, yes, no) {
  const item = form.addMultipleChoiceItem().setTitle(title).setRequired(true);
  item.setChoices([
    item.createChoice(yes, FormApp.PageNavigationType.CONTINUE),
    item.createChoice(no, FormApp.PageNavigationType.SUBMIT),
  ]);
}

function choice_(form, title, values) {
  form.addMultipleChoiceItem().setTitle(title).setChoiceValues(values).setRequired(true);
}

function scale_(form, title) {
  form.addScaleItem()
    .setTitle(title)
    .setBounds(1, 5)
    .setLabels(AGREEMENT[0], AGREEMENT[1])
    .setRequired(true);
}
