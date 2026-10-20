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

`PIPELINE_VERSION=v7` é o padrão desde a ADR-055: a cascata C6 (v3 seguida da verificação dos
`SUPPORTED` pela `v5_fixed`), confirmada na execução única da Fase 20. Com imagem, as duas etapas usam
um único OCR, descartado ao fim da requisição. Use `PIPELINE_VERSION=v3` para reverter ao padrão
anterior, ou `v1` para o caminho histórico; a seleção não muda o corpus nem persiste interações.

## Controle de acesso e limite de taxa

- `TELEGRAM_RATE_LIMIT_MESSAGES` (padrão 5) por `TELEGRAM_RATE_LIMIT_WINDOW_SECONDS`
  (padrão 60): janela deslizante por chat, mantida somente em memória, com no máximo
  10.000 chats rastreados. O chat excedente recebe um único aviso por janela.
- `TELEGRAM_ALLOWED_CHAT_IDS` (opcional): lista de IDs separados por vírgula. Quando
  definida, chats fora dela são ignorados sem resposta. É configuração do operador, não
  dado de usuário; vazia, qualquer chat é aceito.
- Nenhum identificador é gravado em disco nem registrado em log.

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
novamente, sem serem armazenadas. A confirmação informa o tempo típico da análise (15 a 40 s) e,
quando há outras análises antes, a posição na fila; durante a análise, o bot renova o indicador
"digitando…" a cada 4 s, e uma falha desse indicador não afeta a resposta.

Ao iniciar, o bot roda uma alegação sintética fixa (`WARMUP_CLAIM`, sem conteúdo de usuário) para
carregar o Qwen3-8B, o BGE-M3 e o índice antes da primeira mensagem; `BOT_WARMUP=0` desliga. Em
20/10/2026, o aquecimento levou 31 s, e uma alegação fria custava cerca de 8 s a mais que a mesma
alegação aquecida. Para que o Ollama não descarregue o modelo entre mensagens espaçadas, defina
`OLLAMA_KEEP_ALIVE=-1` no ambiente do servidor Ollama antes de iniciá-lo.

Respostas de evidência insuficiente trazem uma orientação fixa: o que a abstenção significa, que
relatos de casos individuais devem ser comunicados a uma unidade de saúde e que notícias e fatos
políticos cabem às agências de checagem. Quando nenhuma alegação é identificada, a resposta explica
como enviar uma. A orientação não depende do motivo interno da abstenção e não altera o veredito.

Mensagens finais são texto simples, têm previews de links desativados e são divididas quando
excedem o limite de 4.096 caracteres do Telegram. Falhas conhecidas do corpus, do Ollama ou
da saída do modelo produzem resposta genérica; detalhes e conteúdo do usuário não entram nos
logs.

## Validação

Os testes automatizados cobrem long polling, offset em memória, limite de mensagem,
confirmação anterior à pipeline, comandos, imagem, link, sanitização de falhas e ausência
do conteúdo em logs de erro.

Em 26/09/2026, o ensaio controlado da v3 aprovou texto, imagem com OCR real, link
extraído em memória e recusa de vídeo. Os tempos observados foram, respectivamente,
19,29 s, 15,71 s, 13,03 s e menos de 1 ms para a recusa; esses valores não incluem a
rede real do Telegram.

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

Em 20/10/2026, a v7 foi ensaiada com o bot real e alegações sintéticas digitadas pelo próprio
desenvolvedor. Funcionaram como esperado: comandos, confirmação imediata, aviso de posição na fila
(até "Há 3 análises na sua frente"), limite de taxa na sexta mensagem em 60 s, orientação nas
abstenções e instrução quando não há alegação. Os vereditos esperados foram obtidos para tríplice
viral e autismo (refutada, 14,9 s), HPV no SUS (sustentada, 19,2 s), relato individual
(insuficiente, 3,9 s) e saudação (sem alegação, 1,4 s); os demais tempos ficaram entre 8,5 s e
30,7 s, incluindo a espera na fila. A confirmação saiu em cerca de 0,7 s em 13 de 16 envios e em
2,74 s nos outros três, um atraso fixo atribuído à rede.

O ensaio expôs dois erros de julgamento já descritos na análise de erros da v7, que não foram
corrigidos para não alterar o sistema avaliado: uma alegação de "venenos" nas vacinas (mercúrio,
alumínio, vírus vivos) recebeu refutada com explicação imprecisa, quando enganosa seria o veredito
adequado; e uma notícia verdadeira sobre mortes por doenças evitáveis por vacinação, enviada por
link, foi lida como mortes causadas pela vacina e refutada por falta de evidência. Também apareceram
fontes repetidas (o mesmo documento e a mesma página listados mais de uma vez). Esses exemplos não
entram no roteiro da banca.
