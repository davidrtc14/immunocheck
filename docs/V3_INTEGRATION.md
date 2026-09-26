# Integração controlada da pipeline v3

Data: 26/09/2026.

## Resultado

A candidata v3 confirmada foi integrada ao protótipo local e passou a ser o caminho
padrão do Telegram e da CLI. A v1 permanece disponível por
`PIPELINE_VERSION=v1` ou `--pipeline-version v1`; essa reversão não altera os
resultados históricos de nenhuma das versões.

A camada de integração não modifica prompts nem algoritmos congelados. Ela compõe:

1. extração local da alegação e retrieval BGE-M3 denso top 15;
2. roteamento estrutural entre decisão direta top 6, decisão relacional top 15 e
   abstenção para evento específico sem âncora;
3. seleção inicial de citações, expansão documental e seleção final;
4. validação de todos os IDs e construção programática das referências.

IDs inexistentes, rota desconhecida ou conclusão sem fonte válida falham de modo
fechado para `INSUFFICIENT_EVIDENCE`. Não há auditor factual posterior na v3,
conforme a configuração que foi confirmada experimentalmente.

## Evidência de integração

- suíte geral: 404 testes aprovados e um teste PostgreSQL opcional ignorado por falta
  de `IMMUNOCHECK_TEST_DATABASE_URL`;
- regressão dirigida: roteamento, profundidades 6/15, expansão, duas seleções,
  fontes programáticas, falha fechada e abstenções;
- privacidade: conteúdo e identificadores continuam ausentes dos logs, e nenhuma
  interação é persistida;
- apresentação: as quatro classes têm rótulo, explicação, aviso e tempo formatados;
- ensaio local multimodal, fora do conjunto confirmatório: texto 19,29 s, imagem com
  OCR real 15,71 s, link controlado 13,03 s e vídeo recusado imediatamente;
- resposta textual de fumaça: a alegação sobre tríplice viral e autismo foi refutada
  com três referências programáticas em 21,79 s;
- as 32 consultas da confirmação reproduziram exatamente, na mesma ordem, os 15
  chunks registrados no checkpoint (`32/32`).

O relatório desidentificado do ensaio está em
`evaluation/results/demo/v3_automated_rehearsal.json`. Ele valida integração e
latência observada, não substitui a avaliação de qualidade confirmatória.

## Limites de reprodução

Os hashes normalizados do código congelado e do corpus conferem. Os arquivos locais
ignorados do manifesto/NPZ do índice não têm o mesmo hash de serialização registrado
no congelamento, embora as 32 ordenações top 15 tenham sido reproduzidas exatamente.
Isso indica equivalência operacional para as consultas confirmatórias, mas não prova
identidade byte a byte do índice. Uma distribuição reprodutível futura deve arquivar
o índice congelado ou reconstruí-lo por receita e validar seus vetores, sem usar esse
ponto para recalibrar os resultados.

O ensaio substituiu a rede do Telegram e a página HTTPS por objetos em memória. O
teste ao vivo continua sendo um gate de apresentação, não de arquitetura. A v3 é um
protótipo acadêmico local: não possui validação clínica independente e não está
autorizada para implantação pública ou aconselhamento médico.
