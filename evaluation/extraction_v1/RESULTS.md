# Resultados do benchmark de extração extraction_v1 (17/10/2026)

Execução final única de cada condição, com código, fontes e modelos congelados (`freeze.json`,
commit `ea86f8c`), sobre os 48 itens v4 de `test` em 19 modelos de entrada (912 casos por condição,
mais 48 referências em texto limpo). Artefatos: `results/final/*_verdict_run1.jsonl` e
`results/final/analysis.json` (`scripts/analyze_extraction.py --phase final`). A métrica principal é
a concordância do veredito obtido pela entrada multimodal com o veredito do texto limpo na mesma
execução.

## Decisão

**Nenhuma condição foi promovida.** `improved` e `improved_vision` passam em G1–G5 e reprovam em
G6, porque as falhas técnicas passam do limite fixo de 2%: 2,19% e 2,40%. A linha de base teve
3,85%. Pela regra pré-registrada (seção 6 do protocolo), `EXTRACTION_VERSION=v1` continua padrão e a
v2 fica disponível como opção.

| Gate | Critério | `improved` | `improved_vision` |
|---|---|---|---|
| G1 | Concordância geral: Δ ≥ +0,10 e IC > 0 | ✅ +0,101 (IC +0,074 a +0,129) | ✅ +0,110 (IC +0,087 a +0,137) |
| G2 | Modelos reservados: Δ ≥ +0,05 e IC > 0 | ✅ +0,068 (IC +0,023 a +0,117) | ✅ +0,086 (IC +0,042 a +0,135) |
| G3 | Imagem limpa: Δ ≥ −0,05 | ✅ 0,000 | ✅ 0,000 |
| G4 | CER ≤ e marcadores ≥ baseline | ✅ 0,035 / 0,917 | ✅ 0,016 / 0,935 |
| G5 | P95 ≤ 45 s por modalidade | ✅ ≤ 18,0 s | ✅ ≤ 18,6 s |
| G6 | Falhas ≤ 2% e rejeições ≤ baseline | ❌ 2,19% (21/960); 8 rejeições | ❌ 2,40% (23/960); 0 rejeições |

## Visão geral

| | `baseline` | `improved` | `improved_vision` |
|---|---|---|---|
| Concordância geral | 0,630 | 0,731 | 0,740 |
| Concordância nos modelos reservados | 0,586 | 0,654 | 0,672 |
| Imagem / link / mensagem / texto | 0,77 / 0,41 / 0,10 / 0,80 | 0,81 / 0,67 / 0,24 / 0,88 | 0,82 / 0,66 / 0,27 / 0,87 |
| CER médio das imagens | 0,038 | 0,035 | 0,016 |
| Marcadores preservados nas imagens | 0,917 | 0,917 | 0,935 |
| Rejeições de imagem | 11 | 8 | 0 |
| Falhas técnicas | 37 (3,85%) | 21 (2,19%) | 23 (2,40%) |
| Macro-F1 contra o gabarito (casos multimodais; referência 0,583) | 0,504 | 0,532 | 0,535 |

## Concordância por modelo de entrada

Modelos reservados em itálico.

| Modelo | `baseline` | `improved` | `improved_vision` |
|---|---|---|---|
| imagem/clean (controle) | 0,94 | 0,94 | 0,94 |
| imagem/whatsapp_light | 0,83 | 0,85 | 0,88 |
| imagem/social_light | 0,77 | 0,85 | 0,85 |
| imagem/photo_whatsapp_light | 0,81 | 0,83 | 0,85 |
| imagem/low_res_forward | 0,77 | 0,88 | 0,85 |
| imagem/story_overlay | 0,77 | 0,77 | 0,79 |
| *imagem/whatsapp_dark* | 0,83 | 0,85 | 0,83 |
| *imagem/meme* | 0,58 | 0,60 | 0,69 |
| *imagem/photo_social_dark* | 0,62 | 0,67 | 0,71 |
| link/news_article | 0,62 | 0,75 | 0,69 |
| link/long_page | 0,10 | 0,77 | 0,77 |
| *link/blog_divs* | 0,33 | 0,56 | 0,58 |
| *link/pdf_report* | 0,58 | 0,58 | 0,60 |
| mensagem/comment_with_link | 0,10 | 0,23 | 0,27 |
| *mensagem/link_then_question* | 0,10 | 0,25 | 0,27 |
| texto/forward_emoji | 0,73 | 0,98 | 0,98 |
| texto/caps_shout | 0,83 | 0,81 | 0,81 |
| *texto/inline_url* | 0,81 | 0,88 | 0,85 |
| *texto/two_claims* | 0,81 | 0,83 | 0,83 |

## Leitura

- **A extração nova melhora a entrada de forma consistente.** O ganho aparece em 15 dos 19 modelos e
  também nos modelos reservados, que não foram usados no desenvolvimento. Os maiores ganhos estão
  onde a extração antiga falhava por construção: página longa (0,10 → 0,77, porque a alegação ficava
  depois do corte de 6.000 caracteres), página com `div`s (0,33 → 0,56) e texto encaminhado com
  emoji (0,73 → 0,98).
- **As falhas que reprovam no G6 não vêm da extração.** As 21 falhas da `improved` são todas
  `ModelOutputError` do extrator de alegação da v3, que vem depois da camada nova e não foi alterado.
  Elas se espalham pelas modalidades (inclusive uma referência em texto limpo). Todas as 21 se
  repetem na `improved_vision`, que recebe o mesmo texto, e 12 se repetem na linha de base. A camada
  nova reduz as falhas em relação à linha de base (37 → 21), mas a regra fixou 2% como limite
  absoluto, e ela não é reinterpretada depois do resultado.
- **A visão melhora a transcrição quando é acionada, mas custa latência por pedido.** Ela foi
  acionada em 10 de 432 imagens (6 memes, 2 fotos de tela escura, 1 story, 1 imagem de baixa
  resolução), reduziu o CER médio de 0,035 para 0,016 e zerou as rejeições. Cada pedido com visão
  levou de 41 a 52 s (8 de 10 acima de 45 s), por causa da troca entre `qwen3.6` e `qwen3:8b`. O P95
  por modalidade fica abaixo de 45 s só porque a visão é rara. A diferença de concordância para a
  `improved` (+0,009) fica abaixo do desempate de 0,02.
- **Mensagem com link continua fraca, por causa do extrator de alegação.** O texto extraído da
  mensagem é o mesmo do link isolado, só precedido do comentário ("Isso procede?"). O link isolado
  concorda 0,75 e a mensagem, 0,23: a moldura "Mensagem de quem enviou / Conteúdo do link" confunde o
  extrator de alegação da v3, que em geral conclui que não há alegação verificável
  (`INSUFFICIENT_EVIDENCE`). Na calibração, com 16 itens, a mensagem tinha chegado a 0,75; o
  resultado nos itens de teste não se manteve.
- **A imagem limpa não muda**, o que confirma que a camada nova não prejudica a entrada que já
  funcionava.

## Ameaças à validade

- O benchmark é sintético: o texto é renderizado por nós, com fontes do Windows, e as degradações são
  simuladas. Os modelos reservados reduzem, mas não eliminam, o ajuste às formas do benchmark.
- A concordância mede a fidelidade ao veredito do texto limpo, não a correção do veredito. O
  macro-F1 contra o gabarito é descritivo.
- 48 itens de teste em 12 famílias: os IC são por família e largos nos recortes por modelo (48 casos
  cada).
- A execução da `improved` foi interrompida no caso 468 e retomada pelo checkpoint em 17/10/2026. O
  caso seguinte (`ref4-0044-image-social_light`) incluiu o carregamento dos modelos (22,9 s); o
  efeito no P95 é desprezível.
- O limite do G6 inclui falhas de um componente fora da camada avaliada. Isso foi uma escolha do
  pré-registro e é registrado aqui como lição: em uma próxima regra, o limite de falhas deveria ser
  relativo à linha de base ou restrito às falhas da etapa avaliada.

## Próximos passos possíveis (fora desta execução)

- Entregar ao extrator de alegação só o conteúdo do link, com o comentário como contexto secundário,
  e medir de novo a modalidade mensagem.
- Reduzir as falhas `ModelOutputError` do extrator da v3 (tentativa com reparo do JSON), que afetam
  todas as condições.
- Na v5, que tem extrator próprio, repetir a medição da camada nova.
