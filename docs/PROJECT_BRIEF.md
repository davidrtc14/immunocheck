# Brief do projeto

## Contexto fixo

O ImmunoCheck é um TCC de Ciência da Computação da UNIPÊ, desenvolvido sem
orçamento. Seu objetivo é analisar alegações e conteúdos sobre vacinação humana
recebidos como texto, imagem ou link e entregar um veredito fundamentado em fontes
válidas e verificáveis.

A pipeline deve envolver LLM, RAG e técnicas complementares adequadas. Toda
ferramenta, API, modelo ou dataset precisa admitir uso acadêmico gratuito. LGPD,
ética em IA e direitos humanos fazem parte do desenho desde o início.

## Usuário e proposta de valor

O usuário recebeu uma notícia, mensagem, print ou link e deseja compreender sua
acurácia. O sistema não substitui profissional de saúde: compara uma alegação
factual com evidências documentais e expõe fontes para verificação independente.

## Escopo da v1

### Entradas

- Texto: uma mensagem, até 4.096 caracteres.
- Imagem: PNG, JPEG ou WebP; uma imagem; até 10 MB e 12 megapixels; conteúdo
  predominantemente textual.
- Link (protótipo experimental, ADR-053): uma URL HTTPS pública; HTML, texto ou PDF
  textual; até três redirecionamentos, 10 segundos de timeout, 5 MB de download e 50 mil
  caracteres úteis extraídos. Continua no bot com as mesmas proteções, mas fora do escopo
  avaliado, que é texto e imagem.

Quando houver várias alegações, a v1 verifica a principal e informa essa limitação.
OCR ilegível, conteúdo ambíguo, páginas inacessíveis ou alegações fora do domínio
geram resposta transparente, sem tentativa de adivinhação.

### Saídas

- `SUPPORTED`, `REFUTED`, `MISLEADING` ou `INSUFFICIENT_EVIDENCE`;
- explicação curta e acessível;
- fato correto quando aplicável;
- omissão ou distorção quando o conteúdo for enganoso;
- fontes com título, instituição, data, página e URL quando disponíveis;
- aviso claro de que não se trata de orientação médica individual.

## Fora da v1

- Vídeo e áudio.
- WhatsApp.
- Cache ou memória conversacional.
- Aconselhamento médico individual.
- Fine-tuning.
- Painel administrativo React.
- Hospedagem pública permanente.
- Atualização automática do corpus.

## Restrições operacionais

- Execução local em RTX 4060 de 8 GB e 32 GB de RAM.
- LLM e recuperação locais; nenhuma API paga ou LLM externa em produção.
- Bot por Telegram long polling, sem endpoint público obrigatório.
- Produção sem persistência de mensagens, imagens, links, respostas ou IDs.
- Avaliação offline pode persistir apenas dados curados, sem usuários reais.

## Critério geral de sucesso

O protótipo deve receber uma alegação, recuperar evidências confiáveis, produzir um
veredito rastreável, abster-se quando necessário e operar no hardware doméstico com
qualidade e latência reportadas de maneira reproduzível.
