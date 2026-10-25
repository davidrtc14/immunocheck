# Demonstração remota (ADR-057)

Versão do bot que fica no ar sem o computador do autor: roda numa máquina gratuita da Oracle Cloud e
usa um modelo de linguagem por API (Groq ou Gemini). A pipeline v7, o corpus v1, o BGE-M3 e as
referências por metadados são os mesmos do sistema principal; só o modelo de linguagem muda.

**Não é o sistema avaliado.** Os vereditos podem diferir dos do Qwen3-8B local, e nenhum número do TCC
vale para esta versão. **As mensagens saem para o provedor da LLM**, que pode guardá-las conforme a
política do plano gratuito. Por isso o bot só inicia com `TELEGRAM_ALLOWED_CHAT_IDS` (testadores
avisados), avisa no `/start` e em `/privacidade`, e deve ser usado só com alegações gerais.

## 1. Contas e chaves

1. **Bot de demonstração:** crie um segundo bot no @BotFather (por exemplo, `@immunocheck_demo_bot`).
   Não reuse o token do bot principal: dois processos com o mesmo token disputam as mensagens.
2. **LLM:** crie uma chave em um provedor com API compatível com OpenAI.

   | Provedor | `LLM_API_BASE_URL` | `LLM_API_MODEL` (exemplo) | Observação |
   |---|---|---|---|
   | Groq | `https://api.groq.com/openai/v1` | `qwen/qwen3.8-27b` | Mesma família do modelo local, responde em português e aceita `json_schema`; use `LLM_API_EXTRA_JSON={"reasoning_effort": "none"}`. Os modelos `openai/gpt-oss` responderam em inglês e falharam na validação do JSON. |
   | Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` | `gemini-2.5-flash` | Aceita `json_schema`; o plano gratuito tem limite por minuto. |

   Os limites dos planos gratuitos mudam; confira na página do provedor. Em 25/10/2026, o plano
   gratuito da Groq limitava cada modelo a 8.000 tokens por minuto. Como cada alegação faz de 4 a 10
   chamadas com milhares de tokens, a resposta leva de 1 a 3 minutos (o cliente espera e tenta de novo
   quando recebe HTTP 429), e o bot avisa isso ao confirmar o recebimento. O plano pago por uso da
   Groq remove essa espera.
3. **Testadores:** cada testador descobre o próprio ID mandando uma mensagem ao @userinfobot. Os IDs
   vão em `TELEGRAM_ALLOWED_CHAT_IDS`, separados por vírgula.

## 2. Máquina na Oracle Cloud (Always Free)

1. Crie a conta em https://www.oracle.com/cloud/free/ (pede cartão só para verificação).
2. Crie uma instância **VM.Standard.A1.Flex** (ARM) com **Ubuntu 24.04**, 2 a 4 OCPUs e 12 a 24 GB de
   RAM, e baixe a chave SSH. O bot só faz conexões de saída; não é preciso abrir portas.
3. Entre por SSH (`ssh -i chave.key ubuntu@IP`) e instale as dependências:

```bash
sudo apt update && sudo apt install -y git python3.12-venv tesseract-ocr tesseract-ocr-por
git clone https://github.com/davidrtc14/immunocheck.git
cd immunocheck && python3.12 -m venv .venv && .venv/bin/pip install -e .
```

4. **Corpus processado** (não versionado, cerca de 44 MB): copie do computador do autor.

```bash
scp -i chave.key -r corpus/processed ubuntu@IP:~/immunocheck/corpus/
```

5. **BGE-M3** na mesma revisão do sistema principal (cerca de 2,3 GB):

```bash
.venv/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('BAAI/bge-m3', revision='b28ce2a6fcc9c75ef1c0619575d0ec19af760082', cache_dir='models')"
```

## 3. Configuração

Crie `~/immunocheck/.env.demo` (fora do Git; `chmod 600 .env.demo`):

```bash
TELEGRAM_BOT_TOKEN=<token do bot de demonstração>
TELEGRAM_ALLOWED_CHAT_IDS=<id1>,<id2>
LLM_BACKEND=api
LLM_API_KEY=<chave do provedor>
LLM_API_BASE_URL=https://api.groq.com/openai/v1
LLM_API_MODEL=qwen/qwen3.8-27b
LLM_API_RESPONSE_FORMAT=json_schema
LLM_API_EXTRA_JSON={"reasoning_effort": "none"}
PIPELINE_VERSION=v7
EXTRACTION_VERSION=v1
BOT_WARMUP=1
LOG_LEVEL=INFO
```

## 4. Serviço que inicia sozinho

```bash
sudo cp deploy/immunocheck-demo.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now immunocheck-demo
journalctl -u immunocheck-demo -f   # deve mostrar "Modo demonstração" e "Bot iniciado"
```

Com `enable`, o bot sobe junto com a máquina e reinicia sozinho se cair. Para ligar ou desligar de
qualquer lugar, com o computador do autor desligado:

- pelo celular, com um aplicativo de SSH (Termius, JuiceSSH): `sudo systemctl start immunocheck-demo`
  ou `sudo systemctl stop immunocheck-demo`;
- pelo console da Oracle Cloud no navegador: iniciar ou parar a instância inteira.

## 5. Atualizar e verificar

```bash
cd ~/immunocheck && git pull && .venv/bin/pip install -e . && sudo systemctl restart immunocheck-demo
```

Em 25/10/2026, a v7 rodou de ponta a ponta pelo adaptador de API, primeiro com o endpoint compatível
com OpenAI do Ollama local e depois com a Groq (`qwen/qwen3.8-27b`, `json_schema`). Os vereditos foram
os mesmos do bot local: tríplice viral e autismo refutada (57 s na Groq), HPV no SUS sustentada (172 s,
porque passa pelas duas etapas da v7) e relato individual sem conclusão (8 s). Com `json_object`, o
roteador devolveu uma rota fora do schema, por isso `json_schema` é o padrão. A Groq fica atrás do
Cloudflare, que recusa o agente padrão do Python (erro 1010); o cliente se identifica como
`ImmunoCheck-TCC`.

## Limitações

- Vereditos não avaliados; podem divergir do sistema do TCC.
- Conteúdo enviado ao provedor da LLM; só testadores avisados.
- A Oracle pode recuperar instâncias gratuitas muito ociosas; se a máquina sumir, recrie pelos passos
  acima.
- A leitura de imagens usa o Tesseract (`EXTRACTION_VERSION=v1`); a camada de visão da ADR-050 depende
  do Ollama e não está disponível neste modo.
