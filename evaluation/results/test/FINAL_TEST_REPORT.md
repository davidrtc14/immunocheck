# Avaliação definitiva no teste congelado

## Identidade da execução

- Data: 18/09/2026.
- Configuração: BGE-M3 denso, top 6, extrator v2, Qwen3-8B e auditor v2.
- Commit candidato: `52ab0bdef6b9c8649c8e1ee2b56996d24d0f0ac3`.
- Freeze: `sha256:a352d9f93032b87652b38ffea2b855cef393bd822f04142dbfbd5830ad609666`.
- Dataset: `5caabdab9347c13dd270e6a335599dc5e213f5ad814312f6bcdf45731a67a5bf`.
- Checkpoint: `30090bfcd3bb53ebac03ac8c261d8cee025af32b6991f8e7abcfffd955f1c4ac`.
- Amostra: 64 itens, 16 famílias, quatro classes.
- Ambiente: Python 3.12.14, Windows 11 e `qwen3:8b` local.
- Falhas técnicas: zero.

O relatório JSON declara `post_test_changes_allowed: false`. Quantidade, ordem,
hash do checkpoint, freeze e commit candidato foram verificados depois da execução.

## Métricas principais

| Métrica | Estimativa | IC 95% bootstrap por família |
|---|---:|---:|
| Macro-F1 | 0,416 | 0,308–0,507 |
| Balanced accuracy | 0,444 | 0,330–0,551 |
| Acurácia | 0,469 | 0,344–0,594 |
| Recall de abstenção | 0,750 | 0,500–0,938 |
| Recall `MISLEADING` | 0 | 0–0 |

Outras métricas: precisão de abstenção 0,308; F1 de abstenção 0,436; taxa de
citação relevante 0,438 nos 48 itens conclusivos de referência; auditor invocado
em 92,2% dos itens e aprovado em 42,4% das invocações.

| Classe | Precisão | Recall | F1 | Suporte |
|---|---:|---:|---:|---:|
| `SUPPORTED` | 1,000 | 0,625 | 0,769 | 16 |
| `REFUTED` | 0,533 | 0,400 | 0,457 | 20 |
| `MISLEADING` | 0 | 0 | 0 | 12 |
| `INSUFFICIENT_EVIDENCE` | 0,308 | 0,750 | 0,436 | 16 |

Matriz de confusão, linhas como referência e colunas como previsão, na ordem
`SUPPORTED`, `REFUTED`, `MISLEADING`, `INSUFFICIENT_EVIDENCE`:

```text
[[10, 1, 0,  5],
 [ 0, 8, 0, 12],
 [ 0, 2, 0, 10],
 [ 0, 4, 0, 12]]
```

O sistema produziu 10 `SUPPORTED`, 15 `REFUTED`, zero `MISLEADING` e 39
`INSUFFICIENT_EVIDENCE`. Dos 12 itens `MISLEADING`, dez viraram abstenção e dois
foram classificados como `REFUTED`.

## Desempenho

- Latência mediana: 9,43 s.
- P95: 12,42 s.
- Requisições sem falha técnica: 100%.

A condição textual ficou abaixo da meta de engenharia de P95 até 45 s. Esta
medição não cobre o tempo da rede do Telegram nem valida P95 de imagem e link.

## Interpretação

A escolha conservadora cumpriu seu objetivo restrito de aumentar abstenção: 75%
dos casos de referência insuficiente foram recusados. Porém, a precisão de
abstenção foi baixa; somente 12 das 39 abstenções eram esperadas. O sistema deixou
de oferecer uma classificação conclusiva em muitos casos nos quais o benchmark
possuía evidência.

O principal resultado negativo é o recall zero de `MISLEADING`, repetindo e
agravando o padrão observado no desenvolvimento. Portanto, não é válido afirmar
que o ImmunoCheck identifica adequadamente todas as formas de desinformação sobre
vacinas. A classe `SUPPORTED` foi a mais confiável neste teste, mas a amostra é
pequena e sintética.

O macro-F1 caiu de 0,528 no desenvolvimento para 0,416 no teste. Essa comparação
é descritiva: conjuntos e famílias são diferentes. O teste não será usado para
escolher novo prompt, limiar, retrieval ou auditor nesta versão.

## Conclusão de validade

O projeto demonstra integração local de texto, RAG, LLM, citações programáticas,
auditoria, abstenção e medição reproduzível sem APIs pagas. Também atingiu latência
textual compatível com demonstração e não apresentou falhas técnicas na rodada.

Os resultados **não sustentam implantação pública** nem uso como árbitro de
veracidade em saúde. A versão deve ser apresentada como protótipo acadêmico de
prova de conceito, com utilidade limitada pelo excesso de abstenções, ausência de
reconhecimento de `MISLEADING`, benchmark sintético e dependência do mesmo modelo
para gerar e auditar.

## Regra pós-teste

Nenhuma mudança de configuração será realizada com base nestes resultados. Uma
versão futura precisará de nova hipótese, novo conjunto de calibração e nova
avaliação independente; não poderá reutilizar este teste como desenvolvimento.
