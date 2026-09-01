# Fase 4 — Imagem e link

## Resultado

Imagem textual e URL HTTPS convergem para a mesma `FactCheckPipeline` usada pelo texto:

```text
Telegram → validação/feedback → normalização local → extração da alegação
         → retrieval → geração → fidelidade → resposta e fontes
```

Nenhuma modalidade cria uma segunda lógica de veredito. Bytes da imagem, URL e conteúdo
baixado existem somente em memória durante a requisição e não entram em banco, arquivo ou
log.

## Imagem

Entradas aceitas: JPEG, PNG ou WebP, até 10 MB e 12 megapixels. Fotos do Telegram e imagens
enviadas como documento são suportadas. O fluxo é:

1. recusar tamanho ou dimensões declaradas fora do limite antes do download quando possível;
2. baixar no máximo 10 MB pela Telegram Bot API;
3. validar assinatura, formato e dimensões reais com Pillow;
4. decodificar em escala de cinza, ampliar imagens pequenas, suavizar e aplicar Otsu com
   OpenCV;
5. executar Tesseract em português por `stdin`/`stdout`, sem arquivo temporário;
6. reconstruir linhas e calcular qualidade a partir do TSV por palavra.

O limiar inicial exige pelo menos três palavras, doze caracteres alfanuméricos, confiança
média ponderada de 55/100 e razão alfanumérica de 0,5. Texto acima de 12 mil caracteres é
recusado com pedido de recorte. Esses valores são controles de engenharia, não uma medida de
veracidade ou certeza clínica, e deverão ser calibrados com imagens anotadas na Fase 6.

## Link

Entradas aceitas: uma URL HTTPS pública, com até 2.048 caracteres. O downloader online é
separado do coletor do corpus e aplica:

- somente porta 443, sem usuário ou senha na URL;
- resolução DNS a cada salto e rejeição se qualquer resposta não for IP global;
- conexão fixada ao IP validado, mantendo SNI e validação TLS para o hostname;
- no máximo três redirecionamentos, todos revalidados;
- prazo total de 10 segundos verificado entre os passos;
- `Accept-Encoding: identity`, máximo de 5 MB e leitura incremental;
- somente HTML/XHTML, texto simples ou PDF com assinatura compatível.

HTML remove script, estilo, navegação, cabeçalho, rodapé, formulários e outros elementos sem
conteúdo principal. PDFs são processados em memória, precisam possuir texto selecionável e
têm limite adicional de 100 páginas. O texto útil deve ter entre 40 e 50 mil caracteres; o
sistema não trunca silenciosamente conteúdo acima desse teto.

## Rejeições transparentes

São recusados, sem tentativa de adivinhação:

- imagem corrompida, tipo falso, dimensões inconsistentes ou OCR abaixo do limiar;
- áudio, vídeo e arquivos que não sejam imagens aceitas;
- HTTP, porta alternativa, credenciais, IP privado/local ou DNS misto;
- redirecionamentos excessivos, timeout, compressão inesperada ou mais de 5 MB;
- páginas sem texto útil, dependentes exclusivamente de JavaScript ou protegidas por login;
- PDF digitalizado sem camada textual, acima de 100 páginas ou 50 mil caracteres.

## Evidências de validação

Em 31/08/2026:

- imagem sintética curta foi reconhecida pelo Tesseract e percorreu OCR, RAG, geração e
  fidelidade, retornando veredito refutado com fontes programáticas;
- página pública de vacinação do Ministério da Saúde produziu 5.552 caracteres úteis e
  percorreu a pipeline, que se absteve quando a auditoria de fidelidade não aprovou a
  conclusão;
- uma página de PDF público do corpus produziu 2.185 caracteres sem gravação temporária;
- testes bloquearam loopback, rede privada, endereço de metadados, DNS público/privado
  misto, quarto redirecionamento, estouro de tamanho e prazo.

Os exemplos são ensaios técnicos, não dados de participantes. Métricas de acurácia do OCR,
latência em distribuição e desempenho fim a fim pertencem ao protocolo da Fase 6.

## Limitações

- O tempo de resolução DNS depende do resolvedor do sistema operacional; o prazo é
  reavaliado imediatamente após a resolução, mas uma chamada DNS bloqueada pode ultrapassar
  o objetivo antes de devolver controle ao processo.
- Conteúdo principal pode não ser recuperado em páginas renderizadas apenas por JavaScript.
- PDF escaneado não recebe OCR na v1; o usuário deve enviar a página relevante como imagem.
- O caminho de até 50 mil caracteres ainda precisa ser incluído nos ensaios de memória e
  contexto do Qwen3 no hardware-alvo.
