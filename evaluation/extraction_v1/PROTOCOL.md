# Protocolo extraction_v1: benchmark sintético de extração multimodal (ADR-050)

Registrado em 16/10/2026, antes de qualquer mudança no código de extração. A linha de base de
desenvolvimento (seção 5) foi executada antes da regra de decisão (seção 6); a execução final
acontece uma única vez, com código e benchmark congelados por hash (`freeze.json`).

## Motivação

A extração de imagem, link e texto nunca teve a qualidade medida. O benchmark operacional
(`evaluation/results/performance/`) mediu só latência, em imagens tipográficas limpas. Não há CER,
nem comparação do veredito obtido por imagem ou link com o veredito do mesmo texto digitado. O código
tem lacunas conhecidas:
- OCR em uma única passada (Otsu global, PSM 6, só `por`, sem filtro de interface);
- legenda da foto ignorada;
- URL acompanhada de comentário tratada como texto puro;
- HTML limpo só por lista de tags;
- corte silencioso dos primeiros 6.000 caracteres;
- nenhuma limpeza de marcadores de encaminhamento.

## Hipótese

Uma camada de compreensão da entrada, entre o normalizador e o extrator de alegação, faz o veredito
obtido por imagem, link ou mensagem ruidosa concordar mais com o veredito da alegação limpa. Essa
camada reúne OCR em várias passadas com filtro de interface, roteamento de mensagens com link,
extração do conteúdo principal da página com seleção da alegação, e limpeza de texto encaminhado. A
latência e o comportamento com entradas limpas não podem piorar.

## Desenho do benchmark (`src/immunocheck/evaluation/extraction_benchmark.py`)

- **Itens:** as 96 alegações rotuladas de `evaluation/refinement_v4/items.jsonl`. Cada uma é embutida
  em entradas geradas por código, com semente derivada do `case_id`. Nenhuma entrada real é usada, e
  as imagens e páginas não são versionadas (são reproduzíveis pelo código e pelas fontes, cujos hashes
  ficam em `freeze.json`).
- **Modelos:**

| Modalidade | Desenvolvimento | Reservados (só na execução final) | Controle |
|---|---|---|---|
| Imagem | `whatsapp_light`, `social_light`, `photo_whatsapp_light`, `low_res_forward`, `story_overlay` | `whatsapp_dark`, `meme`, `photo_social_dark` | `clean` |
| Link | `news_article` (banner, "leia também", comentários), `long_page` (alegação depois de 6.000 caracteres) | `blog_divs` (sem `main`/`article`, barra lateral antes do texto), `pdf_report` (alegação na página 2) | — |
| Mensagem | `comment_with_link` | `link_then_question` | — |
| Texto | `forward_emoji`, `caps_shout` | `inline_url`, `two_claims` | — |

  Os distratores ("leia também", barra lateral, segunda alegação) são alegações de outras famílias
  do mesmo split.
- **Splits:**
  - **desenvolvimento:** itens `development` com os modelos de desenvolvimento e o controle;
  - **final:** itens `test` com todos os modelos.

  Os modelos reservados testam a generalização para estilos que não foram vistos na iteração.
- **Referência do veredito:** a mesma alegação enviada como texto limpo ao mesmo pipeline, na mesma
  execução (registro `reference`).
- **Pipeline:** v3, que é o padrão do bot. A extração não depende da versão do veredito.

## Métricas

- **Concordância do veredito:** veredito do caso igual ao veredito da referência do mesmo item. Uma
  rejeição da entrada (`ContentExtractionError`) ou uma falha técnica conta como discordância.
- **CER na alegação:** distância de edição entre a alegação e o melhor trecho do texto extraído,
  dividida pelo tamanho da alegação, com início e fim livres. Assim o texto de interface ao redor não
  pesa. Reportada também sem acentos.
- **Preservação de marcadores:** os números e as negações da alegação continuam no texto extraído.
- **Taxa de rejeição**, **falhas técnicas** e **latência** de ponta a ponta (P50/P95), por modalidade.
- **Intervalos de confiança:** bootstrap pareado por família de alegação, com 10.000 reamostras e
  semente 42.

## 5. Linha de base de desenvolvimento

Executada com a extração atual (`--condition baseline --phase dev`) antes de qualquer mudança.
Resultados em `results/dev/baseline_extract_run1.jsonl` e `results/dev/baseline_verdict_run1.jsonl`;
o resumo está na seção 7.

## 6. Condições e regra de decisão

Registrada em 16/10/2026, depois da linha de base de desenvolvimento e da iteração da extração
nova somente na etapa `extract` do desenvolvimento, que não usa LLM. Antes de qualquer execução
de veredito da condição nova e antes de qualquer contato com os itens `test` ou com os modelos
reservados.

**Condições:**
- `baseline`: extração atual (`MultimodalNormalizer`, `TesseractOCR`, `SafeLinkTextExtractor`, só
  URL isolada vira link).
- `improved`: `UnderstandingNormalizer` com `MultiPassTesseractOCR` (variantes otsu, cinza,
  adaptativa e CLAHE × PSM 6/4, correção de inclinação), remoção de interface, legenda,
  `route_message` (mensagem com URL HTTPS vira link com comentário),
  `MainContentLinkExtractor` (trafilatura), seleção de trechos por tema e limpeza de texto
  encaminhado.
- `improved_vision`: `improved` mais a transcrição pelo `qwen3.6` quando o OCR reprova ou tem
  confiança média abaixo de 70. Entra na execução final só se a latência dela na calibração
  couber no gate G5.

**Regra de decisão** (itens `test`, execução final única, cada condição contra a `baseline`, com
bootstrap pareado por família). Uma condição só vira padrão (`EXTRACTION_VERSION=v2`) se passar
em todos os critérios:

| Gate | Critério |
|---|---|
| G1 | Concordância geral (todas as modalidades e modelos): Δ ≥ +0,10 e limite inferior do IC 95% > 0 |
| G2 | Concordância só nos modelos reservados: Δ ≥ +0,05 e limite inferior do IC 95% > 0 |
| G3 | Controle `clean` (imagem limpa): Δ ≥ −0,05 |
| G4 | Imagens: CER médio ≤ ao da `baseline` e taxa de preservação de marcadores ≥ à da `baseline` |
| G5 | P95 de ponta a ponta ≤ 45 s em cada modalidade |
| G6 | Falhas técnicas ≤ 2% dos registros e rejeições de imagem ≤ às da `baseline` |

**Desempate:** se `improved` e `improved_vision` passarem, fica a de maior concordância geral; se
a diferença for menor que 0,02, fica `improved`, que é mais simples e não depende do modelo de 23
GB. Pré-condição determinística, com teste automatizado: a limpeza de texto não altera nenhuma das
96 alegações v4 nem das 192 paráfrases.

**Métrica secundária:** macro-F1 contra o gabarito v4 por condição, descritiva e sem gate. Esta
fase mede a extração, não o veredito.

## Teste rápido do qwen3.6 (V0, 16/10/2026)

Ensaio descartável com 10 itens de calibração (`development`), sem valor de avaliação:
- **v5 com o `qwen3.6` (36B MoE Q4_K_M) como único LLM:** 7 de 10 vereditos corretos, contra 5 de 10
  do `qwen3:8b` nos mesmos itens.
- **Latência:** de 17 a 27 s por item, já com o modelo carregado; o primeiro item levou 63 s porque
  incluiu o carregamento. O `qwen3:8b` levou de 5 a 16 s.
- **Memória:** pico de 31,3 de 31,6 GB de RAM e 7,5 GB de VRAM.
- **Transcrição por visão** de uma captura de WhatsApp: cerca de 3 s com o modelo carregado, com o
  texto completo transcrito.

**Conclusão:** viável como juiz (condição da Fase 18) e como alternativa de OCR. A RAM fica no limite,
e alternar entre `qwen3:8b` e `qwen3.6` no mesmo pedido custa o recarregamento do modelo, o que a
condição com visão vai medir.

## Calibração do veredito (16/10/2026)

Itens `development` e modelos de desenvolvimento. A linha de base cobre os 48 itens de calibração
(576 casos); a condição `improved`, os 16 primeiros, e a comparação usa só esses 16 (176 casos).
- **Concordância com o veredito do texto limpo:** 0,682 na linha de base e 0,852 na `improved`. Os
  maiores ganhos foram na página longa (0,06 → 0,94), no comentário com link (0,00 → 0,75) e no texto
  encaminhado com emoji (0,69 → 0,94). A `improved` não teve falhas; a linha de base teve 27 de 576
  (4,7%, `ModelOutputError` do extrator da v3). P95 da `improved`: 16,5 s.
- **Defeito encontrado:** a limpeza passava o texto em CAIXA ALTA para minúsculas, o que apagava a
  caixa dos nomes próprios, e deixava resíduos como ".!" (CAIXA ALTA: 0,94 → 0,81). Correção por
  princípio, antes do congelamento: a caixa não é mais alterada, e uma sequência de pontuação com `!`
  ou `?` fica só com o primeiro sinal. Não foram acrescentadas regras para as frases do modelo de
  texto. Com a modalidade texto refeita, a concordância geral foi a 0,864 (CAIXA ALTA 0,88; emoji 1,00).
- **Limitação mantida:** na imagem de baixa resolução, o nome do remetente sobra no texto e o OCR
  multipassada às vezes escolhe uma leitura pior de uma palavra ("Comirnaty" → "Comimaty"); não há
  correção por princípio sem ajustar ao benchmark.
