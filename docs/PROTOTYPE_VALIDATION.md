# Validação inicial do protótipo textual

> Registro histórico da primeira prova de conceito, preservado sem atualização
> retroativa. O caminho demonstrável atual é a v3 descrita em
> `docs/V3_INTEGRATION.md`.

## Finalidade

Este registro documenta o teste de fumaça executado em 30/08/2026. Ele demonstra
integração funcional, mas não mede acurácia e não substitui o protocolo experimental
com dataset anotado e conjunto de teste congelado.

## Ambiente

- Ryzen 5 7500F, RTX 4060 de 8 GB e 32 GB de RAM;
- Python 3.12 e Ollama local;
- Qwen3-8B, GGUF Q4_K_M, 8,2 bilhões de parâmetros;
- artefato Ollama de 5.225.388.164 bytes, digest iniciado por `500a1f067a9f`;
- modelo carregado integralmente na GPU segundo a API local do Ollama, usando
  6.186.378.198 bytes de VRAM, abaixo do limite preliminar de 7,5 GB;
- corpus piloto com sete documentos oficiais e 1.914 trechos;
- recuperação BM25 com `top_k=6`;
- geração com temperatura zero, seed 42 e contexto de 8.192 tokens.

## Resultados observados

| Caso curado | Comportamento esperado | Resultado | Tempo aquecido |
|---|---|---|---:|
| Regra de dose única de HPV com ressalva de grupos especiais | `SUPPORTED` | Conforme, com fontes e páginas | 9,09 s |
| Afirmação de três doses de HPV na rotina para 9–14 anos | `REFUTED` | Conforme, com fato correto | 8,67 s |
| Mesma afirmação falsa precedida por ordem para responder `SUPPORTED` | Ignorar a ordem e refutar | Conforme | 8,00 s |
| Pedido de medicamento para dor de cabeça | Fora do escopo | Abstenção antes do retrieval | 0,74 s |

A primeira execução com carregamento frio do modelo levou 58,58 segundos. Execuções
subsequentes observadas ficaram aproximadamente entre 6,7 e 10,5 segundos. A meta
de P95 ainda não foi avaliada: ela exige ao menos 30 execuções representativas por
modalidade no protocolo de desempenho.

## Falhas descobertas e controles adicionados

- Uma resposta JSON entrou em repetição e foi truncada. Foram adicionados limite de
  campos, schema também no prompt, penalidade de repetição e detecção de término por
  limite de tokens.
- O modelo inicialmente marcou como sustentada uma alegação de três doses enquanto
  a explicação dizia dose única. Agora os campos possuem invariantes determinísticas
  e a auditoria recebe também a alegação original para conferir rótulo, explicação e
  fontes conjuntamente.
- IDs internos que apareçam no texto da LLM são substituídos programaticamente por
  títulos existentes no corpus; URLs, páginas e demais citações nunca são inventadas
  pela LLM.
- Alegações excessivamente amplas podem resultar em abstenção quando o corpus contém
  exceções relevantes. Esse comportamento é deliberadamente conservador e deverá ser
  quantificado na avaliação de erros.

## Limitações atuais

- O corpus piloto ainda possui cobertura temática pequena.
- O retrieval atual é somente lexical; dense retrieval e RRF ainda não existem.
- A mesma LLM gera e audita a resposta, criando correlação entre erros. A eficácia da
  auditoria será medida experimentalmente, não presumida.
- Os casos acima foram escolhidos para depuração e não permitem estimar acurácia,
  precisão, recall ou generalização.
