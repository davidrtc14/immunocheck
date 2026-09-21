# Estado do release candidate

## Veredito

O commit `1b56d22` em `develop` passou nas 18 verificações técnicas obrigatórias do
preflight em 18/09/2026. O projeto está **tecnicamente pronto como release
candidate**, mas ainda **não está autorizado para promoção a `main`**. O ensaio ao
vivo foi aprovado posteriormente com ressalva operacional; resta somente o gate
institucional.

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

## Gate ainda aberto

1. **Decisão institucional LGPD/CEP:** preencher e obter o registro indicado em
   `docs/INSTITUTIONAL_GATE_PACKAGE.md`.

Esse gate não é uma falha do software. Ele impede que uma validação técnica substitua
a decisão institucional necessária. Até seu fechamento, não criar tag estável nem
mesclar `develop` em `main`.

O ensaio ao vivo está fechado com 4/4 fluxos funcionais. Na repetição instrumentada,
as confirmações levaram 2,743 s, 0,712 s e 0,699 s. A extrapolação isolada de 0,743 s
foi aceita como ressalva não bloqueante de uma API externa; não constitui promessa de
SLA. O relatório desidentificado do ensaio real está em
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
