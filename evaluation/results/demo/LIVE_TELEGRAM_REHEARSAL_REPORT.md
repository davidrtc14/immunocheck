# Relatório do ensaio ao vivo no Telegram

## Identificação e escopo

- Data: 20–21/09/2026.
- Commit executado: `cc880e6` em `develop`.
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

Como o checklist pré-registrado exige feedback em até dois segundos, o ensaio fica
classificado como **concluído com pendência operacional**, e não como aprovação final
do gate. A parte funcional obteve 4/4; a conformidade temporal precisa de uma
repetição única em conexão estável antes da promoção para `main`.

## Próxima verificação

1. Usar a imagem tipográfica controlada, sem cabeçalho ou rodapé metalinguístico.
2. Repetir texto, imagem e link uma vez com o ambiente da apresentação.
3. Confirmar feedback em até dois segundos nos três casos aceitos.
4. Manter como limitação explícita a sensibilidade a texto decorativo em imagens.
5. Não reexecutar nem usar o conjunto final de qualidade para qualquer ajuste.

## Veredito

**Funcionalidade ao vivo: aprovada. Gate de ensaio ao vivo: pendente apenas da
repetição da meta temporal.** A pendência institucional LGPD/CEP permanece separada.
