# Congelamento da candidata v3

Data: 26/09/2026.

## Configuração congelada

A candidata elegível para confirmação é a pipeline roteada com citações
hierárquicas registrada no commit `38e8da9`:

1. extração de alegação preservada da v1;
2. retrieval BGE-M3 denso top 15;
3. roteamento estrutural local:
   - proposição simples → decisor direto sobre top 6;
   - premissa-conclusão → decisor relacional sobre top 15;
   - evento específico sem âncora → `INSUFFICIENT_EVIDENCE`;
4. seleção inicial de até três citações no top 15;
5. expansão por documento com quatro chunks iniciais e vizinhos imediatos;
6. seleção final de até três citações, sem autoridade para mudar o veredito.

Modelo: `qwen3:8b`, digest Ollama
`500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`,
Q4_K_M, temperatura 0, semente 42 e contexto configurado em 8.192 tokens.

## Hashes congelados

| Artefato | SHA-256 normalizado |
|---|---|
| `src/immunocheck/application/text_components.py` | `053378ab07450192e9684f886e7c1a0c153789bb7f632197c4283150281915e4` |
| `src/immunocheck/retrieval/document_expansion.py` | `b00be06050c1b15811265bdbeeea06faf66c6f6e7c23e1b1d691590eacd4a1b3` |
| `scripts/evaluate_refinement_routed_v3.py` | `56db8ebdb7fe07616013fdb3546f54dc4c0ff5e6d8402eb242fab62404ce833a` |
| `scripts/evaluate_refinement_citations_v3.py` | `559c94c7c0c74290625628ae2b681e5e1f60ae1853a9c1036024bd38a05ddcf0` |
| `scripts/evaluate_refinement_hierarchical_citations_v3.py` | `6229c8d60e22193047bba37f129cfef6121a33b34a4648e1b6534bf8013c1cb3` |
| `corpus/processed/chunks.jsonl` | `401bed2cad62142b30e2879b6f91e6f05098ab9ac86191316ba65685af36b19a` |
| `corpus/processed/dense_bge_m3.json` | `2abbf3075a8d2e80258c20cad581b2a00d5ae3f8c5cdfcaa790447c1a4f6605c` |
| `corpus/processed/dense_bge_m3.npz` | `8f6c5520a79b72cdd738534d472751fef3f1138b38a479d895f5ac32d7d0ddbd` |

O tree Git do commit de resultado é
`592e859ac2bc9733bf33bffd852e1f3c3647eda5`.

## Regra de imutabilidade

Nenhum prompt, regra, modelo, top-k, método de expansão, corpus ou limiar poderá ser
alterado depois que o conteúdo confirmatório for produzido ou visto. Qualquer mudança
cria uma candidata posterior e exige outro conjunto independente.

O teste final da v1 permanece fora de escopo. A candidata congelada não está ativa no
bot e não é uma configuração de produção; o congelamento apenas autoriza construir e
revisar o conjunto confirmatório novo.
