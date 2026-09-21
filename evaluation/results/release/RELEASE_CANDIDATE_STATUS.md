# Estado do release candidate

## Veredito

O commit `1b56d22` em `develop` passou nas 18 verificações técnicas obrigatórias do
preflight em 18/09/2026. O projeto está **tecnicamente pronto como release
candidate**, mas ainda **não está autorizado para promoção a `main`**. A parte
funcional do ensaio ao vivo foi aprovada posteriormente; permanecem a repetição da
meta temporal desse ensaio e o gate institucional.

## Verificações aprovadas

- Python 3.12.14 e pacote `0.1.0` coerente com `pyproject.toml`;
- branch `develop` limpa e sincronizada com `origin/develop`;
- nenhum segredo, corpus bruto, modelo, banco ou log proibido versionado;
- congelamento do benchmark validado por hash;
- corpus com 7.585 chunks e índice BGE-M3 íntegro;
- teste final único de 64 itens preservado sem autorização para ajuste pós-teste;
- 90 medições operacionais e 4/4 casos do ensaio automatizado presentes;
- `qwen3:8b` disponível no Ollama e Tesseract com idioma português;
- Docker Server 29.7.2, Docker Compose 5.4.0 e PostgreSQL saudável;
- Ruff aprovado;
- 327 testes aprovados e uma integração PostgreSQL ignorada por ausência da variável
  exclusiva de teste. A saúde do PostgreSQL foi verificada separadamente por
  `pg_isready`.

## Gates ainda abertos

1. **Decisão institucional LGPD/CEP:** preencher e obter o registro indicado em
   `docs/INSTITUTIONAL_GATE_PACKAGE.md`.
2. **Meta temporal do ensaio ao vivo:** a Bot API real processou os quatro fluxos
   funcionais em 20–21/09/2026, mas duas confirmações excederam o objetivo de dois
   segundos. Repetir texto, imagem controlada e link uma vez em conexão estável.

Esses gates não são falhas do software. Eles existem para impedir que uma validação
automatizada substitua decisão institucional ou uma passagem real pela rede e pela
Bot API. Até seu fechamento, não criar tag estável nem mesclar `develop` em `main`.

O relatório desidentificado do ensaio real está em
`evaluation/results/demo/LIVE_TELEGRAM_REHEARSAL_REPORT.md`. Ele registra também a
limitação observada em uma imagem com título e rodapé metalinguísticos, sem alterar
a configuração congelada nem reexecutar o teste final.

## Reprodução

```powershell
python scripts/release_preflight.py --with-tests `
  --output evaluation/results/release/release_preflight_replica.json
```

O registro estruturado original está em `release_preflight.json`. Réplicas devem
usar outro caminho e não substituir a evidência inicial.
