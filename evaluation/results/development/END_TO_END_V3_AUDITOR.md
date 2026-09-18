# Calibração do auditor v3 — desenvolvimento

Execução concluída em 17/09/2026. A emenda e a implementação foram registradas
no commit `4b9fc0d` antes da primeira inferência. O replay processou os 96 itens
e 33 famílias de desenvolvimento e declara `test_items_loaded: 0`; nenhum dos
64 itens de teste foi carregado.

O checkpoint v3 tem SHA-256
`d29a727a5c8c1a43e239cc3e4680eb8969da4eba0dfb5d84e2ce1176d76aff8f` e está
vinculado ao checkpoint v2
`208f6195a2477dd2139cb5b2b4066bb07f1cbc9c12a04e9ba20af51aa8be90f1`.

## Intervenção isolada

Extração, seis chunks densos e rascunho do gerador foram reproduzidos diretamente
dos registros v2. Somente o auditor foi chamado novamente. A variante deixou de
reclassificar a resposta e recebeu a tarefa exclusiva de verificar se os fatos da
explicação, `correct_fact` e `omitted_or_distorted` estavam cobertos pelos chunks
citados. Guardas médicas e validações estruturais permaneceram ativas.

## Resultados

| Condição | Macro-F1 | Recall `MISLEADING` | Recall abstenção | Precisão abstenção | Citação relevante | Mediana | P95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Denso sem auditor, congelado v2 | 0,577 | 0,474 | 0,125 | 0,750 | 0,542 | 7,7 s | 9,4 s |
| Auditor v2 | 0,528 | 0,158 | 0,625 | 0,349 | 0,542 | 9,0 s | 11,3 s |
| Auditor factual v3 | 0,405 | 0 | 0,708 | 0,288 | 0,542 | 9,4 s | 11,6 s |

O delta de macro-F1 v3 menos v2 teve mediana -0,122 e IC 95% por família
-0,212 a -0,024. Contra o denso sem auditor, o delta teve mediana -0,171 e IC
95% -0,267 a -0,072. A v3 mudou 20 previsões em relação à v2: quatro melhoraram,
14 pioraram e duas permaneceram erradas.

F1 por classe na v3: `SUPPORTED` 0,650; `REFUTED` 0,560; `MISLEADING` 0;
`INSUFFICIENT_EVIDENCE` 0,410. A única falha técnica (1/96) já estava presente
na saída densa v2 reutilizada e não foi criada pelo replay do auditor.

## Gates pré-registrados

| Gate | Limite | Resultado | Decisão |
|---|---:|---:|---|
| Macro-F1 | ≥ 0,528 | 0,405 | Falhou |
| Recall `MISLEADING` | ≥ 0,35 | 0 | Falhou |
| Recall de abstenção | ≥ 0,50 | 0,708 | Passou |
| Citação relevante | ≥ 0,50 | 0,542 | Passou |
| Falha técnica | ≤ 0,02 | 0,010 | Passou |
| P95 total estimado | ≤ 12 s | 11,6 s | Passou |
| Melhora sobre v2 | macro-F1 ou `MISLEADING` | piora nos dois | Falhou |

## Decisão e interpretação

A variante v3 foi descartada. O resultado refuta a hipótese de que remover a
reclassificação do auditor resolveria o colapso de `MISLEADING`: o mesmo Qwen3-8B
passou a rejeitar todos os nove rascunhos densos classificados como `MISLEADING`,
indicando instabilidade e possível cobertura factual insuficiente nos campos de
omissão/distorção. Isso não prova que todos esses rascunhos sejam inválidos, pois
o auditor não é uma referência humana independente.

O prompt v2 foi restaurado no caminho de produção apenas como alternativa
conservadora provisória; ele também não foi promovido à avaliação definitiva.
Conforme o pré-registro, não será criada uma quarta variante orientada pelos mesmos
96 itens. O próximo passo metodologicamente aceitável é obter validação externa
das saídas auditadas ou construir um conjunto de calibração novo, com decisão do
orientador, antes de abrir o teste.

## Limitações

- O replay isola o auditor, mas usa rascunhos escolhidos após análise da v2.
- Gerador e auditor compartilham o mesmo modelo e não são avaliações independentes.
- O benchmark é sintético e contém atalhos lexicais já medidos.
- O número de exemplos `MISLEADING` é pequeno: 19 referências e nove rascunhos
  densos com esse rótulo.
- Latência total é estimada somando a medição densa v2 à nova chamada de auditor;
  não é uma nova execução integral da pipeline.
