# Questionário de avaliação por testadores (rascunho para aprovação)

**Estado: não aplicar.** Pela seção "Pesquisa com participantes" de `docs/PRIVACY_AND_ETHICS.md`,
qualquer teste com pessoas depende de apresentação do protocolo ao orientador e de consulta à
instância ética da UNIPÊ. Este documento existe para essa consulta. Um questionário anônimo de
opinião pode se enquadrar no parágrafo único do art. 1º da Resolução CNS nº 510/2016 (pesquisa de
opinião com participantes não identificados), mas quem decide o enquadramento é a instituição, não
o autor. Até a decisão, o uso autorizado do bot continua sendo a demonstração local com dados
sintéticos.

## Desenho

- **Instrumento:** formulário anônimo (Google Forms, gratuito), aplicado depois de uma sessão livre
  de uso do bot de no máximo 15 minutos.
- **Medidas:** System Usability Scale (SUS; Brooke, 1996), percepção de clareza, utilidade das
  fontes, confiança e tempo de espera, além de duas perguntas abertas.
- **O que não se coleta:** nome, e-mail, telefone, usuário do Telegram, matrícula, texto das
  mensagens enviadas ao bot e qualquer dado de saúde. O bot já não grava as interações (ADR de
  persistência e `docs/TELEGRAM.md`).
- **Natureza do resultado:** descritiva e exploratória. Não mede a acurácia do veredito, que já foi
  avaliada nos conjuntos congelados, e não deve ser usada para recalibrar o sistema.

## Configuração do Google Forms

O script `scripts/create_feedback_form.gs` cria o formulário com o texto abaixo e as configurações
desta seção. Para usá-lo, crie um projeto em https://script.google.com, cole o arquivo, preencha
`CONTACT`, execute `createImmunoCheckForm` e autorize o acesso ao Google Forms. Os links de resposta
e de edição aparecem no registro de execução. O formulário nasce fechado para respostas e só deve ser
aberto depois da decisão ética.

- Em Configurações → Respostas: **não** coletar e-mails e **não** limitar a uma resposta (essa opção
  exige login com conta Google e identifica o respondente).
- Todas as perguntas fechadas obrigatórias; as abertas, opcionais.
- Exportar as respostas em CSV para uma pasta fora do repositório. No Git entram só os agregados
  (média do SUS, distribuições) e a decisão ética, nunca as respostas brutas.
- Ao fim da coleta, fechar o formulário e excluir as respostas no Google após a exportação, no prazo
  definido com o orientador.

## Texto do formulário

### Seção 1 — Apresentação e consentimento

> **Avaliação do ImmunoCheck**
>
> Você está sendo convidado(a) a avaliar o ImmunoCheck, protótipo de Trabalho de Conclusão de Curso
> em Ciência da Computação no Centro Universitário UNIPÊ, orientado pelo Prof. Thiago Rodrigues
> Medeiros. O ImmunoCheck é um bot do Telegram que compara alegações sobre vacinação com documentos
> oficiais e científicos.
>
> - A participação é voluntária e anônima: não pedimos nome, e-mail, telefone nem usuário do
>   Telegram.
> - O questionário leva cerca de 5 minutos. Você pode desistir a qualquer momento, sem prejuízo,
>   apenas fechando a página.
> - Ao usar o bot, envie apenas alegações gerais sobre vacinas (por exemplo, algo que circulou em
>   redes sociais). **Não envie dados pessoais nem informações sobre a sua saúde ou de outras
>   pessoas.** O bot não grava as mensagens, mas o Telegram as processa conforme a política dele.
> - O ImmunoCheck é um protótipo acadêmico e não substitui orientação de um profissional de saúde.
> - As respostas serão usadas apenas de forma agregada no TCC.
> - Dúvidas: [contato institucional do pesquisador, a definir com o orientador].

1. **Você leu as informações acima e concorda em participar?** *(obrigatória)*
   - Sim, concordo em participar
   - Não concordo *(encerra o formulário)*

2. **Você tem 18 anos ou mais?** *(obrigatória)*
   - Sim
   - Não *(encerra o formulário)*

### Seção 2 — Perfil (sem identificação)

3. **Faixa etária:** 18–24 · 25–34 · 35–44 · 45–59 · 60 ou mais
4. **Você trabalha ou estuda na área da saúde?** Sim · Não · Prefiro não responder
5. **Com que frequência você recebe mensagens sobre vacinas em redes sociais ou aplicativos?**
   Nunca · Raramente · Às vezes · Frequentemente · Muito frequentemente

### Seção 3 — Uso do bot

6. **Quantas alegações você enviou ao bot?** 1 · 2 a 3 · 4 a 5 · 6 ou mais
7. **Que tipos de conteúdo você enviou?** *(múltipla escolha)* Texto · Imagem (print) · Link
8. **Algum envio terminou sem resposta ou com mensagem de erro?** Não · Sim, uma vez · Sim, mais de
   uma vez

### Seção 4 — Percepção das respostas

Escala de 1 (discordo totalmente) a 5 (concordo totalmente):

9. A explicação das respostas foi fácil de entender.
10. As fontes apresentadas pareceram confiáveis.
11. O tempo de espera pela resposta foi aceitável.
12. Quando o bot respondeu "evidência insuficiente", a orientação dada foi útil. *(com a opção "Não
    recebi essa resposta")*
13. Eu confiaria no veredito do ImmunoCheck para decidir se compartilho uma mensagem.
14. Os vereditos recebidos pareceram corretos, pelo que eu sei sobre o assunto.
15. **Você abriu algum link das fontes?** Sim · Não

### Seção 5 — System Usability Scale (SUS)

Escala de 1 (discordo totalmente) a 5 (concordo totalmente). Os itens seguem a ordem e a alternância
originais do SUS, adaptados para o bot:

16. Eu acho que gostaria de usar o ImmunoCheck com frequência.
17. Eu achei o ImmunoCheck desnecessariamente complexo.
18. Eu achei o ImmunoCheck fácil de usar.
19. Eu acho que precisaria da ajuda de alguém com conhecimento técnico para usar o ImmunoCheck.
20. Eu achei que as diversas funções do ImmunoCheck estavam bem integradas.
21. Eu achei que havia muita inconsistência no ImmunoCheck.
22. Eu imagino que a maioria das pessoas aprenderia a usar o ImmunoCheck rapidamente.
23. Eu achei o ImmunoCheck muito complicado de usar.
24. Eu me senti confiante ao usar o ImmunoCheck.
25. Eu precisei aprender muitas coisas antes de conseguir usar o ImmunoCheck.

### Seção 6 — Comentários (opcionais)

26. **Alguma resposta pareceu errada ou confusa? Descreva o tema em poucas palavras**, sem copiar
    mensagens de outras pessoas e sem dados pessoais (por exemplo: "vacina da gripe e gestantes").
27. **O que você mudaria no ImmunoCheck?**

> Obrigado pela participação!

## Análise prevista

- **SUS:** para cada respondente, itens ímpares valem (resposta − 1), itens pares valem
  (5 − resposta); a soma multiplicada por 2,5 dá a pontuação de 0 a 100. Reportar média, desvio
  padrão, mediana e número de respondentes; a média de referência da literatura é 68 (Sauro, 2011).
- **Itens 9 a 14:** distribuição de frequências por ponto da escala e mediana.
- **Abertas:** agrupamento temático simples, sem citar respostas que possam identificar alguém.
- Com poucos respondentes (por exemplo, menos de 10), apresentar como observação exploratória, sem
  generalização.

## Referências

- BROOKE, J. SUS: a "quick and dirty" usability scale. In: JORDAN, P. W. et al. (ed.). *Usability
  Evaluation in Industry*. London: Taylor & Francis, 1996. p. 189–194.
- SAURO, J. *A Practical Guide to the System Usability Scale*. Denver: Measuring Usability LLC, 2011.
- BRASIL. Conselho Nacional de Saúde. Resolução nº 510, de 7 de abril de 2016.
