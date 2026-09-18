# Reprodução e roteiro de demonstração

## Finalidade e estado

Este guia reproduz o protótipo local e organiza uma apresentação sem reexecutar o
teste congelado. A configuração final foi avaliada uma única vez em 18/09/2026;
os comandos de demonstração validam integração e não podem substituir ou ampliar o
resultado confirmatório.

## Ambiente de referência

- Windows 11, Ryzen 5 7500F, 32 GB DDR5 e RTX 4060 de 8 GB;
- Python 3.12.x — o projeto recusa Python 3.13+;
- Docker Desktop com Compose v2;
- PostgreSQL 17 + pgvector 0.8.6 pela imagem fixada em `compose.yaml`;
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
$env:DATABASE_URL = "postgresql://immunocheck:immunocheck-local-only@localhost:5432/immunocheck"
docker compose up -d postgres
python scripts/migrate_database.py
ollama pull qwen3:8b
```

O `.env` é local e nunca deve ser commitado; o protótipo não o carrega
automaticamente, por isso as variáveis necessárias são definidas na sessão. O valor
padrão da senha do Compose é somente para desenvolvimento em `127.0.0.1`; use outro
segredo se a porta puder ser acessada por terceiros.

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

## Teste local do protótipo

Com o Ollama ativo e o índice construído:

```powershell
python -m immunocheck.cli "A vacina contra HPV faz parte da rotina de vacinação de adolescentes."
python -m immunocheck.cli "Toda vacina contra HPV exige três doses para qualquer adolescente."
```

Verifique a estrutura, não um rótulo decorado: veredito válido, alegação analisada,
explicação curta, fontes programáticas quando houver conclusão, aviso médico e
tempo total. Uma abstenção é saída válida e não deve ser manipulada durante a
apresentação.

## Telegram

```powershell
$env:TELEGRAM_BOT_TOKEN = Read-Host "Token do bot" -MaskInput
python -m immunocheck.telegram
```

Use uma conta e um bot de demonstração. Não projete o token, terminal com variáveis,
conversas pessoais ou notificações. O Telegram recebe a mensagem antes do
processamento local; a demonstração deve usar somente alegações sintéticas.

## Roteiro de 8–10 minutos

1. **Problema e limite (1 min):** checagem acadêmica de vacinação, não diagnóstico,
   sem vídeo/WhatsApp e sem memória conversacional.
2. **Arquitetura (1 min):** entrada → normalização → BGE-M3 → Qwen3 local → validação
   de citações/auditoria → resposta ou abstenção.
3. **Privacidade (1 min):** mostrar `/privacidade`, processamento local e fronteira
   externa do Telegram; não usar dados pessoais.
4. **Texto (2 min):** enviar uma alegação sintética e abrir uma das fontes exibidas.
5. **Imagem textual (1–2 min):** enviar uma imagem criada para a apresentação com
   uma única alegação legível; explicar limiar/rejeição do OCR.
6. **Falha segura (1 min):** mostrar entrada fora de escopo, imagem ilegível ou
   pedido médico individual e a resposta transparente.
7. **Resultados (1–2 min):** apresentar macro-F1 0,416, recall zero de
   `MISLEADING`, intervalos e v3 descartada; não afirmar desempenho em notícias reais.

## Checklist anterior à banca

- [ ] Commit e branch anotados; `git status` limpo.
- [ ] Ollama, modelo, Tesseract, índice e bot verificados com antecedência.
- [ ] Modelo aquecido e latência fria identificada separadamente.
- [ ] Token e dados pessoais fora da tela e dos slides.
- [ ] Três entradas sintéticas preparadas: texto, imagem e falha segura.
- [ ] Links das fontes abertos em abas, caso a rede da apresentação falhe.
- [ ] Plano B por CLI preparado se o Telegram estiver indisponível.
- [ ] Capturas de execução rotuladas como demonstração, não como experimento.
- [ ] Limitações, resultado negativo do auditor e estado do teste apresentados.

## Critério de conclusão deste documento

O roteiro e os comandos estão definidos. A evidência operacional final ainda exige
um ensaio cronometrado completo no commit candidato, depois da decisão metodológica
sobre o auditor. Esse ensaio deve registrar duração, falhas e divergências do roteiro
sem alterar o conjunto de teste.
