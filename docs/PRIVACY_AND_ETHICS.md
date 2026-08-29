# Privacidade, ética e direitos humanos

## Princípios

- Minimização de dados por arquitetura.
- Transparência sobre automação, limitações e fontes.
- Abstenção diante de incerteza.
- Supervisão humana na construção do dataset e interpretação dos resultados.
- Não discriminação e análise de erros por tema, vacina e tipo de alegação.
- Direito à informação: o usuário recebe fundamentos verificáveis, não apenas rótulo.

## Dados de usuários

Em produção, o sistema não persiste mensagens, imagens, URLs, identificadores do
Telegram, vereditos ou histórico. Arquivos temporários são eliminados ao final da
requisição. Logs contêm apenas eventos técnicos agregados, códigos de erro e tempos,
sem conteúdo ou IDs.

O aviso de privacidade deverá informar:

- finalidade exclusiva de checagem de alegações sobre vacinação;
- que o Telegram processa a mensagem para entregá-la ao bot;
- que o conteúdo é processado localmente pelo ImmunoCheck;
- ausência de memória entre mensagens;
- proibição de enviar dados médicos pessoais desnecessários;
- limitações e canal institucional de contato.

## Dados de pesquisa

O corpus é documental. O dataset de avaliação usa alegações públicas reescritas e
curadas, sem perfis ou identificadores de autores. Logs experimentais contêm apenas
IDs dos itens curados, configurações, resultados e métricas.

Antes de testes com participantes ou coleta de mensagens reais, o projeto deve
consultar formalmente o orientador e a instância ética competente da UNIPÊ. Nenhum
teste com pessoas será iniciado apenas por decisão técnica.

## Riscos e controles

| Risco | Controle mínimo |
|---|---|
| Confundir falta de evidência com falsidade | Classe `INSUFFICIENT_EVIDENCE` e limiar de suficiência. |
| Censura ou autoridade indevida | Critérios públicos, fontes visíveis e análise de conflitos. |
| Alucinação | Geração restrita às evidências, IDs válidos e auditoria pós-geração. |
| Conselho médico | Filtros de entrada/saída e respostas fixas de redirecionamento. |
| Prompt injection | Conteúdo externo tratado como dado, nunca como instrução. |
| Vazamento de dados | Processamento local, ausência de logs de conteúdo e segredos fora do Git. |
| SSRF e download malicioso | HTTPS, bloqueio de redes privadas, limites, timeout e tipos permitidos. |
| Viés do corpus | Diversidade de fontes, documentação de cobertura e análise de erros. |
| Falsa precisão | Confiança qualitativa apenas quando calibrada; apresentar limitações. |

## Direito de contestação

O sistema não se apresenta como árbitro definitivo. A resposta deve convidar à
consulta das fontes e explicar como uma conclusão pode mudar com novas evidências.
Erros identificados no conjunto de avaliação devem ser corrigidos de forma
versionada, preservando histórico e justificativa.
