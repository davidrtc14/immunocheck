# Relatório do ensaio automatizado da demonstração

## Resultado

O ensaio local executado em 18/09/2026 foi aprovado nos quatro cenários previstos.
Ele usou entradas sintéticas, a configuração final congelada e o adaptador Telegram
com cliente em memória. Não houve acesso ao Telegram real nem a servidores externos.

| Cenário | Tempo total | Resultado |
|---|---:|---|
| Texto | 7,55 s | Aprovado |
| Imagem PNG com OCR real | 7,80 s | Aprovado |
| Link HTML controlado | 7,76 s | Aprovado |
| Vídeo fora do escopo | 0,011 ms | Recusado de forma transparente |

Nos três fluxos analisados, a confirmação de processamento foi enviada antes da
pipeline ou do download, todas as seções públicas obrigatórias apareceram e cada
mensagem respeitou o limite de 4.096 caracteres. O vídeo não iniciou a pipeline e
recebeu uma única orientação sobre o escopo da v1.

## O que o ensaio valida

- integração entre roteamento do Telegram, normalização e pipeline final;
- feedback anterior ao processamento;
- OCR e extração HTML no caminho de demonstração;
- estrutura pública da resposta e particionamento em mensagens;
- recusa de um formato fora do escopo.

## O que permanece humano

Este ensaio não valida Bot API, conexão da banca, projeção, ocultação visual do token,
clareza da fala nem duração total de 8–10 minutos. Antes da apresentação, o autor
deve executar o checklist de `docs/REPRODUCTION_AND_DEMO.md` com o bot e o computador
que serão usados. Isso é uma passagem operacional, não novo experimento de qualidade.

O registro estruturado está em `automated_rehearsal.json`; ele não contém o texto das
respostas, identificadores reais ou mensagens de usuários. Nenhum resultado foi
comparado a gabarito ou usado para ajustar a configuração após o teste final.
