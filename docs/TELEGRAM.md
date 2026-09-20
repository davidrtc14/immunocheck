# Adaptador Telegram

## Escopo

O adaptador recebe mensagens por long polling e encaminha texto, imagem textual ou link
HTTPS à pipeline local. Não há webhook ou servidor público. A integração usa diretamente
a Telegram Bot API, que é gratuita para bots.

O processo mantém apenas em memória o conteúdo e o `chat_id` necessários para responder à
requisição atual. Não há escrita de mensagens, imagens, URLs, identificadores ou respostas
em arquivo ou banco. O offset de long polling também vive apenas em memória.

## Configuração segura

1. Crie o bot com o BotFather e guarde o token fora do repositório.
2. No PowerShell, dentro do ambiente virtual, defina o token sem incluí-lo no comando:

```powershell
Copy-Item .env.example .env  # somente se o .env local ainda não existir
# Edite apenas o arquivo local e preencha TELEGRAM_BOT_TOKEN.
python scripts/run_telegram_local.py
```

O corpus processado, o Ollama e o modelo configurado em `OLLAMA_MODEL` precisam estar
disponíveis antes da inicialização. O token nunca deve ser colocado em `.env.example`,
commits, capturas de tela ou relatórios.

## Comportamento

- `/start`: apresenta finalidade, limite e aviso de privacidade;
- `/ajuda` ou `/help`: explica o formato de uso;
- `/privacidade`: informa o tratamento local e o papel do Telegram;
- texto comum: envia confirmação e inicia a pipeline;
- URL HTTPS isolada: download seguro e extração de HTML, texto ou PDF textual;
- foto ou documento PNG/JPEG/WebP: download limitado e OCR local;
- áudio, vídeo ou outro arquivo: rejeição transparente;
- comando desconhecido: remete à ajuda.

A confirmação de processamento é a primeira operação externa feita para uma alegação. O
tempo até a conclusão dessa chamada é medido em memória; tempos acima de dois segundos
geram somente um aviso técnico sem conteúdo ou identificador. A entrega efetiva também
depende da rede e da infraestrutura do Telegram, portanto o relatório experimental deve
separar latência local de latência externa.

Long polling e feedback permanecem ativos enquanto uma thread exclusiva executa uma
análise por vez, evitando concorrência sobre a GPU. A fila é limitada a quatro análises e
vive somente em memória; quando cheia, novas alegações recebem uma mensagem para tentar
novamente, sem serem armazenadas.

Mensagens finais são texto simples, têm previews de links desativados e são divididas quando
excedem o limite de 4.096 caracteres do Telegram. Falhas conhecidas do corpus, do Ollama ou
da saída do modelo produzem resposta genérica; detalhes e conteúdo do usuário não entram nos
logs.

## Validação

Os testes automatizados cobrem long polling, offset em memória, limite de mensagem,
confirmação anterior à pipeline, comandos, imagem, link, sanitização de falhas e ausência
do conteúdo em logs de erro.

O aceite operacional exige ainda um teste de fumaça com um bot real:

1. enviar `/start` e conferir o aviso de privacidade;
2. enviar uma alegação textual de teste sem dados pessoais;
3. confirmar o feedback inicial em até dois segundos no ambiente de demonstração;
4. conferir veredito, explicação, aviso médico e links das fontes;
5. repetir com uma imagem textual e uma URL HTTPS pública de teste;
6. simular Ollama indisponível e conferir a resposta segura;
7. encerrar o processo e verificar que nenhum conteúdo ou identificador foi gravado.

Não usar mensagens reais de participantes como dataset. Qualquer estudo com pessoas depende
de orientação e aprovação institucional aplicável.

### Execução de referência

Em 31/08/2026, o fluxo textual foi executado com um bot real e entregou feedback e
resposta final. O ensaio revelou que a autoconfiança não calibrada do extrator podia
confundir falsidade da alegação com dificuldade de extração. O limiar foi removido, um
teste de regressão foi adicionado e a mesma alegação curta passou a percorrer retrieval,
geração, fidelidade e formatação com fontes programáticas. O conteúdo usado no ensaio não
é persistido no repositório nem tratado como dado de pesquisa.
