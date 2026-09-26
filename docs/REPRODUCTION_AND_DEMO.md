# Reprodução e roteiro de demonstração

## Finalidade e estado

Este guia reproduz o protótipo local e organiza uma apresentação sem reexecutar os
conjuntos congelados. A v1 histórica foi testada em 18/09/2026 e a v3 atual foi
confirmada em 26/09/2026; comandos de demonstração validam somente integração e não
podem substituir, ampliar ou recalibrar esses resultados.

## Ambiente de referência

- Windows 11, Ryzen 5 7500F, 32 GB DDR5 e RTX 4060 de 8 GB;
- Python 3.12.x — o projeto recusa Python 3.13+;
- Docker Desktop com Compose v2, necessário apenas para reproduzir a persistência;
- PostgreSQL 17 + pgvector 0.8.6 pela imagem fixada em `compose.yaml`, fora do
  caminho online do bot;
- Ollama local com `qwen3:8b`;
- Tesseract OCR disponível no `PATH` ou em `TESSERACT_CMD`;
- BGE-M3 na revisão fixada pelo código e cache local de modelos.

Registre para cada reprodução: commit, branch, `python --version`, `docker version`,
`docker compose version`, `ollama --version`, `ollama list`, versão do Tesseract,
GPU/driver, CPU, RAM, data e estado frio/aquecido do modelo.

## Instalação limpa

```powershell
git clone https://github.com/davidrtc14/immunocheck.git
Set-Location immunocheck
git switch develop
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
ollama pull qwen3:8b
```

Para reproduzir também a persistência opcional do corpus:

```powershell
$env:DATABASE_URL = "postgresql://immunocheck:immunocheck-local-only@localhost:5432/immunocheck"
docker compose up -d postgres
python scripts/migrate_database.py
```

O `.env` é local e nunca deve ser commitado. O inicializador
`scripts/run_telegram_local.py` lê somente a lista explícita de chaves necessárias
ao bot; os demais comandos continuam recebendo variáveis pela sessão. O valor padrão
da senha do Compose é somente para desenvolvimento em `127.0.0.1`; use outro segredo
se a porta puder ser acessada por terceiros.

## Corpus e índice

O corpus bruto, os modelos e o índice vetorial não são versionados. A reprodução
integral depende de disponibilidade e licenças das fontes registradas no catálogo.

```powershell
python scripts/download_corpus.py --status validated
python scripts/build_pilot_corpus.py
python scripts/build_dense_index.py
python scripts/import_corpus_database.py --activate
python scripts/import_dense_embeddings.py
```

Depois que os pesos estiverem no cache, `python scripts/build_dense_index.py
--offline` impede novo acesso ao repositório do modelo. Falhas de download não devem
ser contornadas com cópias sem proveniência; registre a indisponibilidade.

## Validação automatizada

```powershell
python -m ruff check .
python -m pytest -q
python scripts/validate_end_to_end_dataset.py --ready
```

O teste de integração PostgreSQL exige `IMMUNOCHECK_TEST_DATABASE_URL`; sem essa
variável ele é corretamente ignorado. Os 64 itens de teste congelado não devem ser
executados para depuração, demonstração ou escolha de configuração.

Resultados publicados de desenvolvimento ficam em
`evaluation/results/development/`. Os scripts de avaliação que aceitam
`--overwrite` só devem usá-lo em reprodução declarada, nunca para substituir a
primeira execução sem preservar o artefato anterior.

## Desempenho operacional multimodal

O resultado original está em `evaluation/results/performance/` e não deve ser
sobrescrito. Para uma réplica explicitamente separada, use caminhos novos:

```powershell
python scripts/benchmark_operational_modalities.py `
  --records evaluation/results/performance/replica_records.jsonl `
  --output evaluation/results/performance/replica_summary.json
```

O ensaio executa 30 imagens, 30 links controlados e 30 confirmações locais. Ele
requer Ollama, índice BGE-M3 e Tesseract, leva vários minutos e não acessa a rede do
Telegram nem servidores dos links. Consulte `docs/OPERATIONAL_PERFORMANCE_PROTOCOL.md`
antes de interpretar ou reproduzir os números.

## Teste local do protótipo

Com o Ollama ativo e o índice construído:

```powershell
python -m immunocheck.cli "A vacina contra HPV faz parte da rotina de vacinação de adolescentes."
python -m immunocheck.cli "Toda vacina contra HPV exige três doses para qualquer adolescente."
```

Esses comandos usam a v3. Acrescente `--pipeline-version v1` apenas para reproduzir
o caminho histórico; não misture saídas das duas versões em uma mesma métrica.

Verifique a estrutura, não um rótulo decorado: veredito válido, alegação analisada,
explicação curta, fontes programáticas quando houver conclusão, aviso médico e
tempo total. Uma abstenção é saída válida e não deve ser manipulada durante a
apresentação.

## Telegram

```powershell
Copy-Item .env.example .env  # somente se o .env local ainda não existir
# Preencha TELEGRAM_BOT_TOKEN no .env local, que é ignorado pelo Git.
python scripts/run_telegram_local.py
```

Use uma conta e um bot de demonstração. Não projete o token, terminal com variáveis,
conversas pessoais ou notificações. O Telegram recebe a mensagem antes do
processamento local; a demonstração deve usar somente alegações sintéticas. Somente
o autor envia as fixtures pré-definidas. Não aceitar exemplos improvisados da banca
ou de terceiros. Se alguém enviar conteúdo não previsto, interromper a passagem e
seguir o protocolo de `docs/PRIVACY_AND_ETHICS.md`.

## Roteiro de 8–10 minutos

1. **Problema e limite (1 min):** checagem acadêmica de vacinação, não diagnóstico,
   sem vídeo/WhatsApp e sem memória conversacional.
2. **Arquitetura (1 min):** entrada → normalização → BGE-M3 top 15 → roteamento →
   especialista direto/relacional → citações hierárquicas → resposta ou abstenção.
3. **Privacidade (1 min):** mostrar `/privacidade`, processamento local e fronteira
   externa do Telegram; não usar dados pessoais.
4. **Texto (2 min):** enviar uma alegação sintética e abrir uma das fontes exibidas.
5. **Imagem textual (1–2 min):** enviar uma imagem criada para a apresentação com
   uma única alegação legível; explicar limiar/rejeição do OCR.
6. **Falha segura (1 min):** mostrar entrada fora de escopo, imagem ilegível ou
   pedido médico individual e a resposta transparente.
7. **Resultados (1–2 min):** separar a v1 histórica (macro-F1 0,416 e recall zero
   de `MISLEADING` no teste de 64 itens) da confirmação v3 (macro-F1 0,846 contra
   0,482 da v1 nos mesmos 32 itens novos, recall `MISLEADING` 0,625 e citação exata
   0,833). Declarar que o gabarito v3 teve curadoria do pesquisador apoiada por IA,
   sem validação clínica independente, e não afirmar desempenho em notícias reais.

## Evidência do ensaio local

O executor `scripts/rehearse_demo.py` aprovou texto, imagem, link controlado e recusa
de vídeo pelo adaptador em memória. O registro atual da v3 está em
`evaluation/results/demo/v3_automated_rehearsal.json`. Para repetir sem sobrescrever
o registro original:

```powershell
python scripts/rehearse_demo.py `
  --pipeline-version v3 `
  --output evaluation/results/demo/v3_automated_rehearsal_replica.json
```

Essa automação não substitui a passagem ao vivo com o bot e o ambiente da banca.

## Checklist anterior à banca

- [ ] Commit e branch anotados; `git status` limpo.
- [ ] Ollama, modelo, Tesseract, índice e bot verificados com antecedência.
- [ ] Modelo aquecido e latência fria identificada separadamente.
- [ ] Token e dados pessoais fora da tela e dos slides.
- [ ] Três entradas sintéticas preparadas: texto, imagem e falha segura.
- [ ] Regra anunciada: somente o autor envia fixtures; não haverá improviso externo.
- [ ] Links das fontes abertos em abas, caso a rede da apresentação falhe.
- [ ] Plano B por CLI preparado se o Telegram estiver indisponível.
- [ ] Capturas de execução rotuladas como demonstração, não como experimento.
- [ ] Limitações da v1, confirmação positiva da v3 e estado dos conjuntos apresentados.

O preenchimento operacional único, pronto para devolução, está em
`docs/LIVE_DEMO_CHECKLIST.md`. Antes dele, executar o preflight sem sobrescrever o
registro original:

```powershell
python scripts/release_preflight.py --with-tests `
  --output output/live-preflight.json
```

No preflight atual, Docker, Compose e PostgreSQL são diagnósticos opcionais porque o
bot lê corpus e índice em arquivo. Python, artefatos, corpus/índice, Ollama, Tesseract,
Ruff e pytest permanecem obrigatórios.

## Critério de conclusão deste documento

O roteiro, os comandos, o ensaio automatizado e a passagem ao vivo com o bot real
estão concluídos. Antes da banca, cabe apenas uma checagem informal de conectividade,
sem transformá-la em novo experimento nem ajustar a configuração a partir do teste
congelado. A apresentação depende ainda do gate institucional registrado em
`docs/INSTITUTIONAL_GATE_PACKAGE.md`.
