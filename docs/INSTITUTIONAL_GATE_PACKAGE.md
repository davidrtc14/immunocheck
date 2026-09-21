# Pacote de decisão institucional — LGPD e CEP/CONEP

## Finalidade

Este pacote transforma as pendências institucionais do ImmunoCheck em decisões
objetivas para o autor, o orientador e, quando indicado pela instituição, o
encarregado de dados e o CEP/UNIPÊ. Ele não é parecer jurídico e não autoriza piloto
público. A engenharia já adotou minimização e processamento local, mas o código não
pode escolher papéis legais ou dispensar avaliação ética.

Para encaminhamento imediato ao orientador, com mensagem pronta, recomendações
pré-preenchidas e bloco de retorno desidentificado, usar
`docs/INSTITUTIONAL_DECISION_REQUEST.md`.

## Resumo para encaminhamento

O ImmunoCheck é um TCC de Ciência da Computação que executa localmente uma pipeline
de LLM e RAG para analisar alegações sintéticas sobre vacinação. A avaliação usa
documentos públicos e benchmark sintético; não usa mensagens de usuários nem dados
de participantes. A demonstração prevista usa o Telegram apenas como canal, sem
persistência local de mensagens ou identificadores. O Telegram recebe o conteúdo
antes do computador local. O protótipo não deve ser aberto ao público nesta versão.
Na banca, somente o autor insere fixtures sintéticas de um roteiro fechado; terceiros
não improvisam entradas.

Mesmo sem persistência, o trânsito de `chat_id`, mensagem, imagem ou URL constitui
tratamento. A LGPD exige finalidade, transparência e direitos do titular; a ANPD
esclarece que a finalidade acadêmica não elimina a necessidade de enquadramento nos
arts. 7º e 11 e que agentes não qualificados como órgão de pesquisa precisam de
outra hipótese legal adequada. A Resolução CNS nº 510/2016 possui hipóteses que não
são registradas nem avaliadas pelo sistema CEP/CONEP, mas também contém regra
específica para TCCs no contexto de atividades de ensino. O enquadramento deve ser
confirmado por escrito pela instituição, não inferido pelo desenvolvedor. A
Resolução CNS nº 674/2022 disciplina a tramitação e, no art. 26, mantém hipóteses de
dispensa quando a pesquisa se enquadra exclusivamente nelas; seu inciso VIII,
alínea `a`, impede tratar TCC como dispensado apenas por ser atividade de ensino. O
Ofício Circular CONEP nº 17/2022 reforça a análise integral das hipóteses.

## Recomendação técnica a ser confirmada

| Tema | Recomendação para a v1 | Quem confirma |
|---|---|---|
| Uso | Demonstração acadêmica restrita, sem bot público e sem recrutamento | Autor + orientador |
| Entradas | Somente alegações sintéticas, sem dados médicos ou identificadores de terceiros | Autor + orientador |
| Operação | Somente o autor insere fixtures do roteiro; sem improviso da banca ou terceiros | Autor + orientador |
| Dados de pesquisa | Corpus público e benchmark sintético; nenhuma interação do Telegram vira dataset | Orientador |
| CEP/CONEP | Solicitar classificação escrita antes da defesa; não presumir dispensa | Orientador + CEP/UNIPÊ |
| Controlador/operador | Registrar a posição institucional; não atribuir esses papéis apenas pelo código | Encarregado/UNIPÊ |
| Base legal | Definir para o tratamento transitório do canal antes de qualquer uso por terceiros | Encarregado/UNIPÊ |
| Transferência internacional | Avaliar o Telegram e registrar fundamento/mecanismo aplicável ao art. 33 da LGPD | Encarregado/UNIPÊ |
| Canal do titular | Usar canal institucional publicado, não contato pessoal do aluno | Encarregado/UNIPÊ |
| Logs | Console técnico sem conteúdo/IDs; não redirecionar para arquivo na demonstração | Autor |
| Incidente | Interromper bot, revogar token e escalar ao contato institucional definido | Autor + instituição |
| Dado sensível acidental | Não reproduzir/exportar; memória descartada sem log; decidir se o aviso basta ou se exige confirmação prévia | Autor + instituição |
| Após a defesa | Manter o bot desligado; qualquer piloto público exige nova aprovação e avaliação | Autor + orientador |

## Perguntas fechadas para o orientador e a instituição

Preencher sem alterar a formulação das perguntas:

1. **Escopo acadêmico:** confirma-se que a v1 será apenas demonstração restrita com
   entradas sintéticas, sem participantes e sem disponibilização pública?
   **Resposta:** [ ] Sim  [ ] Não — justificar: ________________________________
2. **Dados de pesquisa:** confirma-se que interações do Telegram não serão coletadas,
   observadas, exportadas ou usadas nos resultados do TCC?
   **Resposta:** [ ] Sim  [ ] Não — justificar: ________________________________
3. **CEP/CONEP:** após avaliar objetivo, método e fontes de dados, qual é o
   enquadramento institucional?
   **Resposta:** [ ] Não requer submissão  [ ] Consulta formal  [ ] Submissão
   **Fundamento/registro institucional:** ______________________________________
4. **Controlador:** qual pessoa jurídica ou arranjo institucional decide finalidade
   e meios do tratamento transitório durante a demonstração?
   **Resposta:** _______________________________________________________________
5. **Operador/pessoas autorizadas:** quem executa o bot e sob quais instruções?
   **Resposta:** _______________________________________________________________
6. **Base legal:** qual hipótese cobre os dados pessoais comuns e qual cobre eventual
   dado sensível enviado apesar dos avisos?
   **Resposta:** _______________________________________________________________
7. **Canal do titular/encarregado:** qual contato deve aparecer no aviso de
   privacidade da demonstração?
   **Resposta:** _______________________________________________________________
8. **Telegram e transferência internacional:** a instituição aceita o uso controlado
   do canal, inclusive o possível tratamento em outras jurisdições, e qual
   fundamento/mecanismo deve ser registrado para o art. 33 da LGPD?
   **Resposta:** [ ] Sim  [ ] Não  [ ] Exige salvaguardas: ______________________
9. **Operação da banca:** confirma-se que somente o autor inserirá fixtures
   sintéticas pré-definidas, sem improviso ou interação de terceiros?
   **Resposta:** [ ] Sim  [ ] Não — condição: __________________________________
10. **Dado sensível acidental:** o aviso prévio e o descarte em memória sem log são
    suficientes, mesmo sem segunda confirmação ou detecção automática?
    **Resposta:** [ ] Sim  [ ] Não — salvaguarda exigida: _______________________
11. **Retenção técnica:** confirma-se que não haverá arquivo de log e que o terminal
   da demonstração será encerrado sem exportação?
   **Resposta:** [ ] Sim  [ ] Não — prazo/finalidade: ___________________________
12. **Responsável por incidente:** quem recebe a comunicação imediata?
    **Nome/função/canal:** _____________________________________________________

## Evidência mínima a arquivar

- data e participantes da decisão;
- versão deste pacote e commit analisado;
- resposta às doze perguntas;
- e-mail, ata, parecer ou número de protocolo que sustente o enquadramento de CEP;
- identificação do canal institucional de privacidade;
- eventuais condições impostas e evidência de que foram implementadas.

Não versionar assinatura, e-mail pessoal, telefone, matrícula ou documento de
identidade no repositório público. O Git deve receber apenas uma síntese
desidentificada da decisão e, se houver, o número público do protocolo.

## Critério de fechamento

O gate fecha somente quando as doze respostas estiverem documentadas e eventuais
salvaguardas tiverem sido implementadas. Até lá, o estado autorizado permanece:
desenvolvimento local e demonstração pelo próprio autor com conteúdo sintético.

## Referências oficiais consultadas em 18/09/2026 e revalidadas em 21/09/2026

- [Lei nº 13.709/2018 — LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [Guia da ANPD para fins acadêmicos e pesquisas](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-orientativo-tratamento-de-dados-pessoais-para-fins-academicos-e-para-a-realizacao-de-estudos-e-pesquisas)
- [Resolução CNS nº 510/2016](https://www.gov.br/conselho-nacional-de-saude/pt-br/atos-normativos/resolucoes/2016/resolucao-no-510.pdf/view)
- [Resolução CNS nº 674/2022](https://www.gov.br/conselho-nacional-de-saude/pt-br/acesso-a-informacao/atos-normativos/resolucoes/2022/resolucao-no-674.pdf/view)
- [Ofício Circular CONEP nº 17/2022](https://www.gov.br/conselho-nacional-de-saude/pt-br/acesso-a-informacao/camaras-tecnicas-e-comissoes/conep/legislacao/oficios-circulares/oficio-circular-no-17-de-5-de-julho-de-2022.pdf)
- [Orientações do CEP/UNIPÊ para submissão](https://www.unipe.edu.br/comite-de-etica-em-humanos/como-submeter-o-projeto/)

## Prazo

Encaminhar com a maior antecedência possível. Como referência operacional, a
Resolução CNS nº 674/2022 prevê até sete dias para checagem documental e, conforme a
tramitação, até 15, 21, 30 ou 45 dias para parecer; pendências reiniciam a contagem.
Quatro semanas são uma margem prudente mínima, não garantia de conclusão.
