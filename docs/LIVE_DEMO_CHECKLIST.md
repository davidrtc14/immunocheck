# Checklist do ensaio ao vivo

## Instruções

Executar uma única passagem com o computador, a conta e o bot previstos para a
apresentação. Usar somente as entradas sintéticas abaixo. Não registrar mensagens,
`chat_id`, `file_id`, token, nome de usuário, capturas de conversas pessoais ou
qualquer dado médico real.

Preencher apenas resultados operacionais. Se o bot falhar, registrar a categoria da
falha sem copiar o conteúdo da mensagem ou identificadores.

## Identificação técnica

- Data e hora: __________________________
- Commit: _______________________________
- Branch: _______________________________
- Computador de referência: [ ] Sim  [ ] Não
- Bot exclusivo de demonstração: [ ] Sim  [ ] Não
- Token fora da tela e do histórico do terminal: [ ] Sim  [ ] Não
- `python scripts/release_preflight.py --with-tests --output output/live-preflight.json`
  concluiu com `technical_ready: true`: [ ] Sim  [ ] Não

## Preparação

- [ ] Notificações pessoais ocultadas.
- [ ] Ollama e `qwen3:8b` disponíveis.
- [ ] Tesseract disponível.
- [ ] Terminal sem impressão do token.
- [ ] Bot iniciado por `python -m immunocheck.telegram`.
- [ ] `/privacidade` explica processamento local, ausência de memória e participação
      do Telegram.

## Entradas sintéticas

| Caso | Entrada | Feedback em até 2 s | Resposta completa | Sem falha técnica |
|---|---|---:|---:|---:|
| Texto | `A vacina tríplice viral causa autismo.` | [ ] | [ ] | [ ] |
| Imagem | PNG preparado com `Vacinas contêm microchips para rastrear pessoas.` | [ ] | [ ] | [ ] |
| Link | URL HTTPS pública sem identificadores, escolhida antes do ensaio | [ ] | [ ] | [ ] |
| Fora do escopo | Um arquivo de vídeo sintético sem dados pessoais | N/A | [ ] Recusa clara | [ ] |

Para as três análises aceitas, conferir:

- [ ] veredito pertencente às quatro classes válidas;
- [ ] alegação analisada e explicação legíveis;
- [ ] fontes verificáveis ou declaração transparente de insuficiência;
- [ ] aviso de que não substitui profissional de saúde;
- [ ] nenhuma orientação médica individual;
- [ ] nenhuma mensagem excedeu o limite do Telegram.

## Plano B e encerramento

- [ ] Os mesmos exemplos estão disponíveis pela CLI se Telegram ou internet falhar.
- [ ] Links das fontes importantes foram preparados para abertura manual.
- [ ] O bot foi encerrado após o ensaio.
- [ ] O terminal não foi exportado nem transformado em dataset.
- [ ] Nenhum token ou dado pessoal apareceu em captura, commit ou relatório.

## Resultado desidentificado

- Resultado geral: [ ] APROVADO  [ ] REPROVADO
- Quantidade de casos aprovados: ____ / 4
- Categorias de falha, se houver, sem conteúdo de usuário:
  _____________________________________________________________________________
- Ação corretiva necessária antes da banca:
  _____________________________________________________________________________

Responsável pelo ensaio: **não inserir assinatura, matrícula ou contato neste
arquivo público**. Preservar a identificação, se exigida, apenas no registro
institucional apropriado.

## Regra de fechamento

O gate do roadmap só pode ser marcado quando todos os controles de preparação e
encerramento estiverem confirmados, os quatro casos tiverem sido aprovados e não
houver ação corretiva pendente. O ensaio valida operação e apresentação; não permite
recalibrar o sistema com base no teste final.
