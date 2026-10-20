# Análise de erros da v7 (cascata C6)

Análise descritiva feita em 20/10/2026 sobre os registros da execução única da Fase 20, **sem
reexecutar nenhuma condição** e sem alterar o sistema. Script: `scripts/analyze_v7_errors.py`;
agregados em `error_analysis.json`; códigos da amostra manual em `abstention_codes.csv`. Os registros
por item, com texto, ficam fora do Git em `output/error_analysis/`.

**Aproximação declarada.** Os registros da v3 não guardam os trechos recuperados. Para separar erro
de busca de erro de julgamento, a busca densa (BGE-M3, top 15, corpus v1) foi recalculada na CPU sobre
o texto bruto de cada alegação. A pipeline busca com a alegação extraída pelo modelo, que quase sempre
coincide com o texto, então a taxa de recuperação abaixo é uma aproximação.

## Teste do C7 (207 itens, 59 erros)

| Tipo de erro | Itens | Com o documento de origem recuperado |
|---|---:|---:|
| Alegação verdadeira derrubada (sustentada → outra) | 19 | 18 |
| Excesso de confiança em evidência insuficiente | 15 | 2 |
| Grau: refutada ↔ enganosa | 13 | 8 |
| Abstenção indevida (conclusiva → insuficiente) | 11 | 9 |
| Erro grave (não sustentada → sustentada) | 1 | 1 |
| **Total** | **59** | **38** |

**1. O gargalo é o julgamento, não a busca.** Nos 44 erros em itens com rótulo conclusivo, o
documento de origem estava entre os 15 trechos em 36 (82%). O modelo tinha a evidência e decidiu
errado. Isso confirma, com os dados da versão final, o diagnóstico que já aparecia no reordenador
(melhor busca sem melhor veredito) e no corpus v2 (mais documentos sem mais conclusões).

**2. O principal erro é derrubar alegações verdadeiras.** Das 51 sustentadas, 19 não foram
confirmadas, e em 18 delas o documento certo foi recuperado. Doze quedas já vinham da v3 (6 viraram
refutadas, 4 insuficientes e 2 enganosas); sete vieram da verificação da cascata (4 refutadas e 3
insuficientes). É o preço da segurança: o mesmo rigor que eliminou quase todo o erro grave rejeita
paráfrases verdadeiras que não batem literalmente com o trecho.

**3. Relatos individuais viram "refutada".** Os itens de evidência insuficiente do C7 são, em geral,
relatos individuais que nenhum documento confirma ou descarta. Em 14 de 58 o sistema respondeu
refutada, usando evidência geral (por exemplo, a segurança de uma vacina) contra um caso particular.
A ausência de evidência foi tratada como contradição, apesar de o prompt instruir o contrário.

**4. A fronteira refutada/enganosa depende do subtipo.** Acertos nas enganosas por subtipo:

| Subtipo | Acertos | Erro mais comum |
|---|---:|---|
| Salto causal | 16 de 19 | insuficiente (3) |
| Generalização excessiva | 8 de 9 | refutada (1) |
| Implicação falsa | 7 de 14 | refutada (5) |
| Qualificador removido | 4 de 10 | refutada (4); o único erro grave |

O sistema reconhece bem distorções explícitas (causa, alcance), mas confunde com refutação as
alegações em que a distorção está no que fica implícito ou no qualificador omitido.

**5. A cascata.** A `v5_fixed` verificou 57 respostas sustentadas da v3 e trocou 24: 13 relatos
individuais corretamente levados a insuficiente, 2 refutadas levadas a insuficiente, 1 refutada e 1
enganosa corrigidas, e 7 verdadeiras derrubadas.

## Teste externo 2 (304 alegações reais, 197 abstenções)

- **Origem das abstenções:** 191 vieram da primeira etapa (v3), 5 da verificação da cascata e 1 de
  falha técnica.
- **Similaridade com o corpus:** dividindo as alegações em terços pela similaridade do trecho mais
  próximo, a abstenção cai de 84% (terço inferior) para 64% (meio) e 46% (terço superior). Mesmo
  entre as alegações de tema coberto pelo corpus, 62% (98 de 158) terminaram em abstenção.

**Amostra manual.** Sessenta abstenções sorteadas (semente 42) foram codificadas por tipo de
alegação:

| Código | Tipo | Itens |
|---|---|---:|
| A | Caso ou evento individual, pessoa identificada ("pastor morreu um dia após a vacina") | 17 |
| B | Fato político, institucional, comercial ou dado datado de outro país ("Putin ordenou destruir as vacinas") | 22 |
| C | Conspiração ou afirmação implausível que nenhum documento trata ("nanobots nas vacinas de mRNA") | 10 |
| D | Alegação científica geral que o corpus poderia decidir | 6 |
| E | Sem proposição verificável (opinião, chamada para vídeo, aviso) | 5 |

**49 das 60 abstenções (82%) são de alegações que um corpus de documentos oficiais e científicos não
decide por natureza** (A, B e C): ninguém publica um documento técnico sobre a morte de um pastor, a
decisão de Putin ou nanobots inexistentes. Só 6 (10%) eram alegações científicas gerais em que a
abstenção foi conservadora demais. Isso explica por que o corpus v2 quase não mudou a cobertura e
indica que, para alegações reais, a abstenção é na maior parte a resposta correta do ponto de vista
documental, ainda que pouco útil ao usuário.

## Implicações (trabalhos futuros, nenhuma testada aqui)

- **Verificação menos literal das sustentadas:** permitir que a cascata troque sustentada só por
  insuficiente, nunca por refutada, e tolerar paráfrases; exige um conjunto de teste novo.
- **Separar "não refutável por documentos" de "insuficiente":** para os tipos A–C, a resposta útil
  não é um veredito, mas orientar o usuário (por exemplo, sobre como notificar um evento adverso ou
  onde procurar checagens jornalísticas).
- **Treinar o reconhecimento de relatos individuais** antes do decisor, já que o roteamento atual
  deixa passar relatos que depois viram "refutada".

## Limitações

- A recuperação é aproximada (texto bruto, não a alegação extraída).
- A amostra manual foi codificada por um único codificador, um assistente de IA (Claude), sem revisão
  humana; as categorias são descritivas e podem se sobrepor (por exemplo, B e C).
- O C7 é sintético, e o teste externo 2 é quase todo de alegações falsas.
