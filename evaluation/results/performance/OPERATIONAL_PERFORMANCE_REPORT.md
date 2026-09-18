# Relatório de desempenho operacional multimodal

## Conclusão executiva

O ensaio pré-registrado foi executado em 18/09/2026 no commit `b80828a`, sem
reabrir o teste de qualidade. Foram 90 medições: 30 imagens, 30 links controlados e
30 confirmações locais do adaptador Telegram. Não houve falha técnica. As metas de
latência e recursos foram atendidas nas condições controladas do protocolo.

Isso demonstra que o protótipo cabe no computador de referência e processa as três
rotas de entrada de forma estável no laboratório. Não demonstra latência da internet,
da Bot API, de páginas públicas ou de imagens fotográficas difíceis.

## Configuração

- Ryzen 5 7500F, 32 GB DDR5 e RTX 4060 de 8 GB;
- Windows 11 e Python 3.12.14;
- Qwen3-8B local, BGE-M3 denso em CPU, `top_k=6`, sem reranker e auditor v2;
- 1 aquecimento textual excluído das estatísticas;
- protocolo: `docs/OPERATIONAL_PERFORMANCE_PROTOCOL.md`;
- candidato de qualidade preservado: `52ab0bdef6b9c8649c8e1ee2b56996d24d0f0ac3`.

## Resultados

| Modalidade | n | Sucesso | Mediana total | P95 total | Meta P95 | Resultado |
|---|---:|---:|---:|---:|---:|---|
| Imagem tipográfica, OCR real | 30 | 100% | 8,10 s | 10,29 s | 60 s | Atendida |
| Link controlado, parser real | 30 | 100% | 7,61 s | 9,07 s | 45 s | Atendida |
| Feedback local do Telegram | 30 | 100% | 0,009 ms | 0,015 ms | 2 s | Atendida localmente |

O OCR teve mediana de 124,92 ms e P95 de 132,42 ms. A extração controlada de
HTML, texto ou PDF teve mediana de 0,334 ms e P95 de 1,230 ms. O restante da
latência corresponde principalmente à extração da alegação, recuperação, geração e
auditoria locais.

Cada formato de imagem (PNG, JPEG e WebP) e de recurso de link (HTML, texto e PDF)
teve dez execuções. Os 90 identificadores são únicos e nenhum registro contém
conteúdo ou identificador de usuário real.

## Recursos

O amostrador coletou 852 pontos a cada 0,5 s sobre o sistema inteiro:

| Recurso | Baseline | Pico | Meta | Resultado conservador |
|---|---:|---:|---:|---|
| RAM física usada no sistema | 14,89 GiB | 20,28 GiB | 24 GiB | Atendida |
| VRAM usada na GPU | 6,82 GiB | 6,83 GiB | 7,5 GiB | Atendida |

Esses valores incluem Windows e outros processos. O incremento observado foi de
5,39 GiB de RAM e 0,012 GiB de VRAM depois do baseline, mas esse delta não deve ser
interpretado como consumo exclusivo do ImmunoCheck: o modelo já estava carregado
após o aquecimento e processos externos podem variar.

## Limitações e interpretação

- Links foram recursos HTTPS sintéticos mantidos em memória. Os parsers e a
  pipeline são reais, mas DNS, TLS, download, redirecionamentos e servidor remoto
  não entram no tempo.
- O feedback do Telegram usou um cliente em memória. O resultado valida o custo do
  adaptador, não a latência da Bot API ou da rede. O fluxo real já foi verificado
  funcionalmente na Fase 3, sem uma distribuição de 30 envios externos.
- Imagens foram limpas, horizontais e tipográficas; não representam toda a variedade
  de prints e fotos recebidos no mundo real.
- Alegações e resultados desta bateria servem apenas ao desempenho. Nenhum veredito
  foi comparado ao gabarito, e nenhuma saída orientou alteração pós-teste.
- Os números valem para este hardware, versões e estado aquecido. Não são promessa
  de nível de serviço nem evidência de prontidão para implantação pública.

## Artefatos e reprodução

- registros: `evaluation/results/performance/operational_records.jsonl`;
- resumo estruturado: `evaluation/results/performance/operational_performance.json`;
- executor: `scripts/benchmark_operational_modalities.py`.

SHA-256 dos registros: `3813d04573f0c67f872870ff593ee4e05412e1664347a1e78a350a62830a6d97`.
SHA-256 do resumo normalizado em LF:
`c9b1cbddd7ad6715e9d7adfd5afc6ff3b2a897da70b8d742c34211f3e0b76d20`.

Uma reprodução deve escrever em novos caminhos e ser rotulada como réplica. Os
artefatos originais não devem ser sobrescritos.
