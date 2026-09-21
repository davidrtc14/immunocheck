# Relatório do ensaio ao vivo no Telegram

## Identificação e escopo

- Data: 20–21/09/2026.
- Commits executados: `cc880e6` no ensaio funcional e `33b5dfa` na repetição
  instrumentada, ambos em `develop`.
- Ambiente: computador de referência e Telegram Bot API real por long polling.
- Dados: somente alegações sintéticas e uma página pública do Ministério da Saúde.
- Privacidade: nenhum conteúdo, identificador, `file_id` ou token foi gravado no
  repositório ou nos logs. O bot foi encerrado ao final.

Este ensaio é operacional. Ele não altera nem reexecuta o teste final congelado e
não autoriza recalibração da configuração a partir dos resultados definitivos.

## Resultado dos casos

| Caso | Resultado funcional | Tempo total informado | Observação |
|---|---|---:|---|
| Comando de privacidade | Aprovado | N/A | Informou processamento local, ausência de memória e participação do Telegram. |
| Texto | Aprovado | 16,93 s | Resposta conclusiva, duas fontes e aviso de saúde. |
| Imagem decorada inicial | Reprovado | 18,13 s | OCR legível, mas o extrator não isolou a alegação entre título e rodapé metalinguísticos. |
| Imagem tipográfica controlada | Aprovado | 13,19 s | OCR e alegação preservados; resposta conclusiva com duas fontes. |
| Link HTTPS público | Aprovado | 9,23 s | HTML extraído e resposta conclusiva com duas fontes. |
| Vídeo sintético | Aprovado | Imediato | Recusa clara, sem iniciar a pipeline fora do escopo da v1. |

Os quatro fluxos funcionais previstos foram exercitados com sucesso usando a imagem
controlada como fixture oficial. A tentativa inicial permanece registrada porque
revelou uma limitação real: cards com títulos ou rodapés metalinguísticos podem
levar o extrator a não identificar a alegação, mesmo quando o OCR é legível.

## Desvios operacionais

O processo registrou duas ocorrências em que o envio da confirmação de processamento
excedeu o objetivo de dois segundos, associadas aos fluxos de imagem controlada e
link. Também houve uma indisponibilidade transitória da Bot API, recuperada pelo
backoff previsto. Nenhuma dessas ocorrências impediu a resposta final.

Uma repetição instrumentada foi executada em 21/09/2026 com texto, imagem controlada
e link. As confirmações foram enviadas, sempre antes da pipeline, em `2,743 s`,
`0,712 s` e `0,699 s`. A mediana foi `0,712 s`; duas de três medições atenderam ao
objetivo, e a maior o excedeu em `0,743 s`. Houve nova indisponibilidade transitória
da Bot API, recuperada pelo backoff.

O limite de dois segundos é descrito no roadmap como objetivo operacional, não como
garantia de SLA sobre uma API externa. Como não ocorreu falha funcional, inversão da
ordem do feedback ou atraso local da pipeline antes da confirmação, a variação é
aceita como ressalva não bloqueante. Os números não sustentam alegação de que o tempo
será sempre inferior a dois segundos.

## Condições para a apresentação

1. Usar a imagem tipográfica controlada, sem cabeçalho ou rodapé metalinguístico.
2. Fazer uma passagem informal de conectividade antes da banca, sem convertê-la em
   novo experimento ou escolher resultados favoráveis.
3. Manter como limitação explícita a variabilidade da Bot API e não prometer SLA.
4. Manter como limitação explícita a sensibilidade a texto decorativo em imagens.
5. Não reexecutar nem usar o conjunto final de qualidade para qualquer ajuste.

## Veredito

**Gate de ensaio ao vivo: aprovado com ressalva operacional não bloqueante.** A
funcionalidade obteve 4/4; a extrapolação isolada do objetivo temporal e a limitação
da imagem decorada permanecem explícitas. A pendência institucional LGPD/CEP continua
separada.
