# Experimento fim a fim v2 — desenvolvimento

Execução concluída em 17/09/2026 com o extrator congelado no commit `276755c`.
A emenda foi registrada antes da primeira inferência. Os 96 itens e 33 famílias
de desenvolvimento foram processados; o relatório declara `test_items_loaded: 0`.
O checkpoint v2 tem SHA-256
`208f6195a2477dd2139cb5b2b4066bb07f1cbc9c12a04e9ba20af51aa8be90f1`.

## Resultados v2

| Condição | Macro-F1 | IC 95% por família | Recall `MISLEADING` | F1 abstenção | Citação relevante | Mediana | P95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| BM25, sem auditor | 0,490 | 0,411–0,564 | 0,421 | 0,138 | 0,403 | 7,9 s | 10,0 s |
| BGE-M3, sem auditor | 0,577 | 0,490–0,662 | 0,474 | 0,214 | 0,542 | 7,7 s | 9,4 s |
| BGE-M3 + auditor | 0,528 | 0,416–0,636 | 0,158 | 0,448 | 0,542 | 9,0 s | 11,3 s |
| Híbrido + reranker + auditor | 0,464 | 0,391–0,534 | 0 | 0,424 | 0,681 | 19,3 s | 22,4 s |

O denso sem auditor teve o maior ponto estimado. O auditor menos o denso sem
auditor apresentou delta mediano de -0,049 macro-F1 (IC 95% -0,137 a +0,035).
Híbrido + reranker + auditor menos denso sem auditor teve -0,109 (IC 95%
-0,231 a +0,007). Os intervalos ainda incluem empate, mas não sustentam promover
o caminho mais lento.

## Comparação pareada v1 → v2

O extrator mudou em 55 itens, passou de três recusas de escopo para zero e
aumentou as correspondências exatas com a alegação original de 32 para 75.
Preservação exata não é objetivo por si só; neste ensaio ela registra a aplicação
da guarda em entradas curtas, sem provar equivalência semântica universal.

| Condição | Macro-F1 v1 | Macro-F1 v2 | Delta mediano | IC 95% do delta | Melhoraram | Pioraram |
|---|---:|---:|---:|---:|---:|---:|
| BM25, sem auditor | 0,401 | 0,490 | +0,091 | -0,015 a +0,188 | 13 | 5 |
| BGE-M3, sem auditor | 0,381 | 0,577 | +0,197 | +0,114 a +0,281 | 15 | 0 |
| BGE-M3 + auditor | 0,418 | 0,528 | +0,107 | +0,015 a +0,198 | 10 | 4 |
| Híbrido + reranker + auditor | 0,446 | 0,464 | +0,016 | -0,035 a +0,073 | 6 | 5 |

A correção do extrator teve efeito claro no denso, com e sem auditor. Ela não
resgatou o caminho rerankeado nem resolveu sozinha a classe `MISLEADING`.

## Trade-off do auditor

Sem auditor, o denso recuperou apenas 3 das 24 abstenções humanas (recall 0,125),
apesar do maior macro-F1. Com auditor, recuperou 15/24 (0,625), mas a precisão da
abstenção foi 0,349: muitas conclusões possíveis foram recusadas.

O auditor alterou 39 resultados densos. Doze mudanças corrigiram o rótulo, 19
estragaram uma previsão correta e oito continuaram erradas. Entre os 19 itens
`MISLEADING`, seis previsões corretas foram convertidas em abstenção; apenas três
permaneceram corretas. Assim, o auditor melhora segurança contra conclusões sem
base, mas não melhora qualidade geral de forma monotônica.

## Decisões

1. A guarda do extrator é mantida: os ganhos pareados no denso foram positivos e
   os três falsos “fora do escopo” foram recuperados.
2. BGE-M3 substitui o híbrido RRF no caminho sem reranker.
3. O reranker fica fora do caminho online: maior custo, zero recall de
   `MISLEADING` e ausência de ganho fim a fim.
4. O auditor não é descartado porque aumenta substancialmente o recall de
   abstenção, requisito de segurança em saúde. Ele permanece em calibração e não
   pode ser descrito como melhoria geral de acurácia.
5. Nenhuma configuração avança ainda ao teste. O próximo gate é uma avaliação
   pré-especificada do auditor e da fronteira `MISLEADING`/`REFUTED`, limitada ao
   desenvolvimento.

## Limitações

- O ajuste v2 foi motivado e medido nos mesmos 96 itens de desenvolvimento;
  portanto, o ganho não é confirmação externa.
- O dataset é sintético e o baseline lexical ainda tem macro-F1 0,610, superior
  ao melhor RAG pontual da v2.
- Gerador e auditor usam o mesmo Qwen3-8B, logo a auditoria não é independente.
- A métrica de citação considera os chunks humanos anotados e pode subestimar
  outras evidências válidas no corpus.
- Repetir ajustes no mesmo desenvolvimento aumenta risco de sobreajuste. Uma
  próxima iteração deve ser única, pequena e pré-registrada antes de selar a
  configuração para o teste.
