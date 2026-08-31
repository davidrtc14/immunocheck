# Piloto de relevância query–chunk

Este diretório contém consultas e julgamentos destinados exclusivamente ao conjunto
de desenvolvimento da recuperação. Ele não é o dataset final de alegações nem mede
o veredito produzido pela LLM.

## Fluxo de anotação

1. Execute `python scripts/prepare_retrieval_annotations.py` para gerar a planilha
   local `artifacts/retrieval_annotation_candidates.csv`.
2. Para cada consulta, leia os chunks candidatos no contexto da fonte e marque os
   IDs que contêm evidência diretamente útil.
3. Atualize `pilot_judgments.jsonl`: preencha `relevant_chunk_ids`, altere `status`
   para `reviewed` e registre `reviewer` e `reviewed_at` em ISO 8601.
4. Uma segunda pessoa deve revisar parte do dataset definitivo. No piloto, uma
   revisão adicional é desejável quando houver dúvida de domínio.
5. Só então execute `python scripts/evaluate_retrieval.py`.

Consultas em estado `draft` são recusadas pelo executor de métricas. Os candidatos
gerados pelos próprios métodos servem para agilizar a leitura, mas não são um
gabarito: o anotador pode pesquisar e incluir outros chunks do corpus.

O arquivo CSV contém texto do corpus e fica em `artifacts/`, fora do Git. Entradas
reais de usuários não devem ser utilizadas neste processo.

