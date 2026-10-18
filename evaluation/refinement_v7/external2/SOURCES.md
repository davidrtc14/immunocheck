# Teste externo 2 — Fase 19 (ADR-052)

Alegações sobre vacinação humana checadas por agências brasileiras, tiradas do feed público de
marcação ClaimReview do Data Commons
(`https://storage.googleapis.com/datacommons-feeds/factcheck/latest/data.json`, compilação sob
CC BY 4.0; baixado em 17/10/2026, `dateModified` 2026-10-18T00:40Z, sha256 em `freeze.json`). Montado
por `scripts/build_external2_testset.py`, **sem curadoria manual** e **sem nenhuma inferência do
ImmunoCheck**, e congelado em `freeze.json` antes de qualquer execução.

## Artefatos

| Arquivo | Conteúdo | Versionado |
|---|---|---|
| `manifest.jsonl` | 304 itens: URL da checagem, rótulo mapeado, agência, data, tema, cobertura e `claim_sha256`, **sem o texto da alegação** | sim |
| `output/external2_v7/items.jsonl` | os mesmos itens com o texto, reconstruídos do feed local | **não** |
| `build_report.json` | contagens por filtro, rótulos, agências, anos e cobertura | sim |
| `freeze.json` | sha256 do feed, do manifesto, dos itens locais e do script, e o hash de cada alegação | sim |

Nenhuma marcação em português declara licença própria (`sdLicense`), e o texto das alegações pertence
às agências; por isso só a referência é versionada, como no teste externo 1. Para reconstruir, baixe
o feed para `output/external2_v7/download/data.json` e rode o script: ele recusa um feed com sha256
diferente do congelado (o feed "latest" muda com o tempo, então a reconstrução exata depende de uma
cópia local do arquivo de 17/10/2026).

## Regras

As mesmas do teste externo 1 (`evaluation/refinement_v6/external/SOURCES.md`), importadas de
`scripts/build_external_testset.py` sem alteração: vacinação humana; 25 a 280 caracteres, sem
pergunta, truncamento ou veredito embutido; sem artefato de mídia; sem ator político (também pela
URL); rótulo mapeável; sem quase duplicata de alegação já usada em `evaluation/` nem do suplemento do
teste externo 1; quase duplicatas internas ficam uma vez, e grupos com rótulos conflitantes saem.

## Composição

304 itens de 2020 a 2024: 283 `REFUTED`, 20 `MISLEADING` e 1 `SUPPORTED` (Boatos.org 196, Lupa 64,
Comprova 33, SBT News 11). O conjunto é quase todo de alegações falsas, então mede sobretudo o erro
grave (falsa respondida como `SUPPORTED`), a precisão das conclusões e a cobertura.
