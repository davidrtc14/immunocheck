# Protocolo de desempenho operacional multimodal

## Estado e objetivo

Pré-registrado antes das medições de imagem, link e feedback do Telegram. O ensaio
caracteriza a configuração definitiva da v1; não autoriza recalibração posterior ao
teste final e não altera prompts, retrieval, modelo, auditor ou limiares.

## Hardware e configuração

- Ryzen 5 7500F, 32 GB DDR5 e RTX 4060 de 8 GB;
- Python 3.12, Qwen3-8B local, BGE-M3 em CPU e auditor v2;
- retrieval denso, `top_k=6`, sem reranker;
- OCR Tesseract local com a política já validada na Fase 4.

Versões, commit, sistema operacional, modelo e hashes relevantes serão gravados no
resultado. O executor recusará menos de 30 execuções por modalidade.

## Amostra e ordem

1. Um aquecimento textual completo, excluído das estatísticas.
2. Trinta imagens sintéticas, formadas por dez alegações públicas de teste em PNG,
   JPEG e WebP. O caminho medido inclui validação, pré-processamento, OCR e a pipeline
   RAG completa.
3. Trinta links sintéticos HTTPS, com as mesmas dez alegações em HTML, texto simples
   e PDF textual. O fetcher controlado mantém em memória os corpos e o extrator,
   parser e pipeline são os componentes reais.
4. Trinta confirmações no adaptador Telegram, com cliente em memória e sem executar a
   análise. Mede-se o intervalo entre o início de `prepare` e o retorno do envio.

As entradas são sintéticas e não contêm mensagens, imagens, URLs ou identificadores
de usuários reais. A ordem é determinística e não será escolhida pelos resultados.

## Métricas e gates

- latência total e de normalização: mínimo, média, mediana, P95 pelo posto mais
  próximo, máximo e desvio-padrão;
- conclusão sem falha técnica, contando falhas no denominador;
- meta P95 de 60 s para imagem e 45 s para link;
- meta de ao menos 95% de conclusão por modalidade;
- meta local de 2 s para a confirmação do adaptador Telegram;
- uso de RAM total do sistema e VRAM total da GPU amostrado durante o ensaio, quando
  disponível, com baseline e pico explicitamente identificados.

## Limites de interpretação

O ensaio de links elimina a rede para obter repetibilidade; portanto não mede DNS,
download nem variabilidade de servidores públicos. O ensaio do Telegram mede apenas
o adaptador local e não a Bot API ou a rede. Esses resultados não podem ser descritos
como latência ponta a ponta da internet. RAM e VRAM totais incluem processos alheios
ao ImmunoCheck e são limites conservadores, não atribuição causal ao aplicativo.

As imagens são tipográficas e limpas; o resultado não caracteriza fotos inclinadas,
compressão agressiva, fontes decorativas ou fundos complexos. O desempenho é válido
para o computador e a configuração registrados, não para outros equipamentos.
