# Protocolo: linha de base sem recuperação (ADR-058)

Registrado em 01/11/2026, antes de qualquer execução da condição, a pedido do orientador: medir quanto
a arquitetura RAG contribui para o veredito, comparando a v7 com o mesmo modelo decidindo sozinho.

## Condição `no_rag`

- **Modelo:** `qwen3:8b` (`500a1f067a9f`) pelo Ollama local, com o mesmo cliente da v7
  (`_build_llm_client`): temperatura 0, semente 42, contexto de 8.192 tokens, sem raciocínio.
- **Decisão:** uma única chamada por alegação (`src/immunocheck/application/closed_book.py`), com as
  mesmas quatro classes e as mesmas regras de explicação do decisor da v3, mas sem trechos do corpus,
  sem extração da alegação, sem roteamento, sem verificação e sem fontes. A abstenção é permitida,
  inclusive para relatos individuais.
- **Entrada:** o texto bruto de cada alegação, como nas execuções da Fase 20.

## Conjuntos

O teste do C7 (207 itens) e o teste externo 2 (304 itens), com os mesmos congelamentos da Fase 20
(`evaluation/refinement_v7/freeze.json` e `external2/freeze.json`), conferidos pelo executor.
**Reuso declarado:** os dois conjuntos já foram usados na execução única de 20/10. Esta condição não
concorre a promoção e não altera nenhuma decisão anterior: a v7 continua sendo a versão final do
trabalho, qualquer que seja o resultado. Cada conjunto é executado uma vez.

## Métricas e comparações

Iguais às da Fase 20 (`evaluation/refinement_v7/PROTOCOL.md`), por `scripts/analyze_no_rag.py`:

- **C7:** macro-F1, erro grave, recall por classe, falhas e P95; diferença v7 − sem RAG no macro-F1
  e no erro grave, com bootstrap pareado por família (10.000 reamostras, semente 42).
- **Teste externo 2:** precisão das conclusões (sustentada × não sustentada), erro grave, cobertura e
  falhas; diferenças v7 − sem RAG com bootstrap por item (10.000 reamostras, semente 42).
- **Reanálise das conclusões (sem execução nova):** para v3, v7 e sem RAG, a acurácia exata em quatro
  classes entre as respostas conclusivas, geral e por classe do gabarito, e a comparação com o
  classificador trivial que responde "refutada" para tudo (93,1% de acurácia no teste externo 2,
  pois 283 das 304 alegações são refutadas).

**Leitura registrada antes da execução:** é uma comparação descritiva, sem regra de decisão. A
contribuição da recuperação é estimada pela diferença v7 − sem RAG; um IC de 95% que não inclua zero
indica contribuição detectada nessa métrica. Como a condição sem RAG não exibe fontes, a
rastreabilidade das respostas não é comparada: ela só existe na v7, por construção.

## Limitações

- A condição sem RAG não tem extração da alegação; as alegações do C7 e do teste externo 2 já são
  curtas e diretas, o que reduz esse efeito.
- O prompt precisou mudar ("use somente o seu conhecimento" em vez de "use somente as evidências").
- O C7 foi gerado do próprio corpus e favorece a v7; o teste externo 2 é quase todo de alegações
  falsas, e o conhecimento do modelo sobre mitos vacinais conhecidos pode favorecer a condição sem RAG.

## Execução

```powershell
.venv\Scripts\python.exe scripts\run_no_rag_baseline.py --write-freeze
.venv\Scripts\python.exe scripts\run_no_rag_baseline.py --dataset c7
.venv\Scripts\python.exe scripts\run_no_rag_baseline.py --dataset external2
.venv\Scripts\python.exe scripts\analyze_no_rag.py --write
```

Registros por item em `output/no_rag_runs/` (fora do Git); resumo em `results.json` e
`RESULTS.md`.
