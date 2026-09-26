# Plano congelado — triagem do seletor MMR

Data de registro: 26/09/2026. Esta triagem deve ser versionada antes de calcular os
rankings MMR nos 36 itens conclusivos da calibração v2.

## Registro de incidente pré-experimental

Durante a validação local da interface, o comando foi chamado indevidamente com
`--help` antes de o parser existir. O processo calculou os rankings, mas falhou por
permissão ao tentar gravar o primeiro artefato; nenhuma métrica foi impressa,
persistida ou inspecionada. O parser seguro foi incluído antes da execução oficial.
Por transparência, esta triagem é tratada como diagnóstico de desenvolvimento, não
como confirmação independente, ainda que parâmetros e gates abaixo não tenham sido
alterados após o incidente.

## Hipótese

O top 20 denso contém ao menos um chunk anotado em 26/36 itens conclusivos, contra
21/36 no top 6, mas enviar os 20 trechos diretamente à LLM falhou. A hipótese é que
MMR preserve mais dessa cobertura ao selecionar seis trechos menos redundantes, sem
o custo de aproximadamente 10 segundos do reranker neural já medido.

Configuração única, sem ajuste posterior de hiperparâmetro:

- candidatos: BGE-M3 denso top 20;
- seletor: Maximal Marginal Relevance;
- peso de relevância: 0,70;
- saída: 6 trechos;
- vetores: o mesmo índice BGE-M3 congelado.

A triagem não chama LLM. Usa somente as alegações extraídas e evidências anotadas da
calibração. Não carrega o teste v1 nem cria ou abre o holdout v2.

## Gates para autorizar avaliação fim a fim

Todos devem passar:

1. Hit@6 global MMR ≥ 24/36, ganho mínimo de três itens sobre o denso top 6;
2. Hit@6 de `MISLEADING` ≥ 8/12;
3. nenhuma redução de Hit@6 em `SUPPORTED` ou `REFUTED`;
4. P95 do seletor MMR ≤ 100 ms.

Se qualquer gate falhar, MMR será encerrado sem novas inferências de LLM. Se todos
passarem, uma avaliação fim a fim separada ainda exigirá novo plano e commit.

## Comando e saídas

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\screen_refinement_mmr.py
```

- `evaluation/results/refinement_v2/mmr_selector_screen.json`;
- `evaluation/results/refinement_v2/MMR_SELECTOR_SCREEN.md`.
