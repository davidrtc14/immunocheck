# Pacote consolidado para o TCC

Atualizado em 26/09/2026. Este documento é um índice de redação e evidências; ele
não substitui os protocolos, datasets e relatórios versionados citados abaixo.

## Síntese executiva

O ImmunoCheck é um protótipo acadêmico local e gratuito que recebe alegações sobre
vacinação humana por texto, imagem predominantemente textual ou link HTTPS. O
sistema extrai a alegação principal, recupera evidências de um corpus curado,
produz um entre quatro vereditos e apresenta referências verificáveis. Vídeo,
WhatsApp, aconselhamento médico, memória conversacional e implantação pública
permanecem fora do escopo.

A configuração demonstrável atual é a v3: BGE-M3 denso top 15, Qwen3-8B local,
roteamento estrutural, especialistas direto/relacional, abstenção para evento
específico sem âncora e seleção hierárquica de citações. A v1 histórica continua
reproduzível e não foi apagada; ela não é a configuração padrão do bot.

## Questão e objetivos para a redação

Questão-síntese: **em que medida uma pipeline RAG totalmente local consegue
classificar alegações sobre vacinação humana em português, abster-se quando a
evidência é insuficiente e apresentar fontes rastreáveis no hardware doméstico?**

Essa formulação resume o estudo completo e não reescreve retroativamente a pergunta
experimental original de `docs/RESEARCH_PROTOCOL.md`, que orientou as comparações de
retrieval e verificação pós-geração da v1.

Objetivo geral: desenvolver e avaliar um protótipo local, gratuito e rastreável para
apoio à verificação documental de conteúdos sobre vacinação humana.

Objetivos específicos:

1. construir um corpus versionado de fontes oficiais e científicas;
2. comparar estratégias locais de recuperação e decisão;
3. distinguir sustentação, refutação, distorção parcial e insuficiência;
4. garantir que as referências exibidas venham de metadados reais do corpus;
5. integrar texto, OCR e extração segura de links ao Telegram;
6. medir qualidade, latência, recursos e falhas, explicitando limites de validade;
7. incorporar privacidade, ética, direitos humanos e possibilidade de contestação.

## Método executado

O trabalho combina construção de artefato de software com avaliação experimental
controlada. A sequência auditável foi:

1. definição de requisitos, ameaças e critérios de aceite;
2. curadoria de 80 documentos e geração de 7.585 chunks com proveniência;
3. implementação incremental de normalização, retrieval, LLM, citações e Telegram;
4. comparação offline de BM25, BGE-M3, RRF e reranking;
5. avaliação fim a fim da v1 em desenvolvimento e execução única em teste congelado;
6. linha de refinamento v2 encerrada quando nenhuma candidata passou os gates;
7. criação, congelamento e confirmação única da candidata roteada v3 em famílias
   novas, sem reabrir o teste histórico da v1;
8. integração da v3, regressão completa, ensaio multimodal e preflight de entrega.

As alegações de avaliação são sintéticas e documentais; mensagens reais de usuários
não integram o dataset. Métricas incluem macro-F1, métricas por classe, matriz de
confusão, precisão de abstenção, citação exata, falha técnica, mediana e P95. A
incerteza foi estimada por bootstrap por família quando previsto no protocolo.

## Arquitetura entregue

```text
Telegram ou CLI
  → validação de tipo, tamanho e segurança
  → texto | OCR local | extração segura de URL
  → extração da alegação principal
  → BGE-M3 denso top 15
  → roteamento estrutural
      ├─ simples: decisor direto no top 6
      ├─ premissa-conclusão: decisor relacional no top 15
      └─ evento específico sem âncora: abstenção
  → seleção inicial de fontes
  → expansão de passagens no documento
  → seleção final de até três fontes
  → referências programáticas + resposta acessível
```

Qwen3-8B, embeddings, OCR e recuperação executam localmente. A entrada existe apenas
em memória durante a requisição; mensagens, imagens, URLs, respostas e IDs não são
persistidos pela aplicação. O Telegram continua sendo um processador externo na
entrega das mensagens e deve ser apresentado como tal.

## Resultados que podem ser afirmados

| Evidência | Configuração e amostra | Resultado principal | Interpretação permitida |
|---|---|---|---|
| Teste histórico v1 | 64 itens, 16 famílias | macro-F1 0,416; acurácia 0,469; recall `MISLEADING` 0; falha 0; P95 12,42 s | A primeira configuração era funcional, mas excessivamente abstencionista e inadequada para reconhecer distorção parcial. |
| Confirmação v3 | 32 itens, 8 famílias novas | macro-F1 0,846; acurácia 0,844; recall `MISLEADING` 0,625; citação exata 0,833; falha 0; P95 19,35 s | A v3 superou a v1 nos mesmos itens novos e passou 8/8 gates; sustenta integração ao protótipo, não implantação pública. |
| Desempenho multimodal histórico | 30 imagens, 30 links, 30 feedbacks locais | P95 10,29 s, 9,07 s e 0,015 ms; zero falhas | O sistema cabe no hardware e foi estável em condições controladas; não mede rede real nem imagens difíceis. |
| Ensaio integrado v3 | texto, imagem, link e vídeo fora do escopo | 4/4 fluxos aprovados; 19,29 s, 15,71 s e 13,03 s nos aceitos | Valida integração atual, não acurácia estatística. |
| Preflight v3 | 15 controles técnicos obrigatórios | 15/15 aprovados; 409 testes aprovados e 1 opcional ignorado | O protótipo local está tecnicamente demonstrável no commit registrado. |

A comparação 0,846 versus 0,482 usa somente o conjunto confirmatório v3. Não se deve
comparar diretamente 0,846 com 0,416 como se viessem da mesma amostra. O teste v1
permanece congelado e não foi usado para selecionar a v3.

## Ameaças à validade e limitações obrigatórias

- alegações sintéticas e balanceadas podem conter atalhos lexicais;
- o conjunto confirmatório v3 tem apenas 32 itens e oito famílias;
- o gabarito v3 foi curado pelo pesquisador com apoio de IA e evidência rastreável,
  sem validação clínica independente nem concordância entre anotadores;
- corpus prioritariamente oficial e em português limita validade geográfica,
  editorial e temporal;
- `MISLEADING` envolve julgamento contextual e permaneceu a classe mais difícil;
- três de quatro misses de citação apontaram outro trecho do mesmo documento, mas a
  métrica oficial conservadora por ID não foi alterada;
- OCR foi medido principalmente em imagens tipográficas limpas;
- latência de links controlados e feedback local não representa internet ou Bot API;
- a mesma LLM participa do roteamento, decisão e seleção, permitindo erros
  correlacionados;
- o protótipo não oferece diagnóstico, conduta clínica ou garantia de veracidade.

## LGPD, ética e direitos humanos

O desenho aplica minimização, processamento local, ausência de histórico, logs sem
conteúdo, abstenção e transparência das fontes. O usuário pode inspecionar e
contestar o resultado; o sistema não remove conteúdo nem pune autores.

O gate institucional permanece aberto para definir controlador/operador, base legal,
canal do titular, transferência internacional pelo Telegram, resposta a incidente e
enquadramento CEP/CONEP. Até haver retorno formal, o uso permitido é demonstração
controlada pelo autor com entradas sintéticas, não piloto público ou pesquisa com
participantes.

## Índice de evidências

| Tema | Fonte principal |
|---|---|
| Escopo e requisitos | `docs/PROJECT_BRIEF.md` |
| Arquitetura atual | `docs/ARCHITECTURE.md` |
| Decisões e mudanças | `docs/ARCHITECTURE_DECISIONS.md` |
| Protocolo original | `docs/RESEARCH_PROTOCOL.md` |
| Corpus e dataset | `docs/CORPUS_DATASET_PHASE5.md` |
| Resultado v1 | `evaluation/results/test/FINAL_TEST_REPORT.md` |
| Refinamento v2 negativo | `evaluation/refinement_v2/CONSOLIDATION_REPORT.md` |
| Confirmação v3 | `evaluation/refinement_v3/confirmatory/RESULTS.md` |
| Integração v3 | `docs/V3_INTEGRATION.md` |
| Desempenho multimodal | `evaluation/results/performance/OPERATIONAL_PERFORMANCE_REPORT.md` |
| Privacidade e ética | `docs/PRIVACY_AND_ETHICS.md` |
| Reprodução e apresentação | `docs/REPRODUCTION_AND_DEMO.md` |
| Preflight atual | `evaluation/results/release/v3_integration_preflight.json` |

## Comandos mínimos de banca

```powershell
# Verificação técnica sem reexecutar conjuntos de qualidade
python scripts/release_preflight.py --with-tests --output output/preflight-banca.json

# Plano A: Telegram, com token somente no .env ignorado
python scripts/run_telegram_local.py

# Plano B: CLI usando a v7 padrão (cascata, ADR-055)
python -m immunocheck.cli "A vacina tríplice viral causa autismo."
```

Não executar scripts de avaliação confirmatória durante a apresentação. Não aceitar
entradas improvisadas de terceiros nem transformar mensagens da demonstração em
dataset.

## Estado de entrega

- código e documentação técnica: concluídos em `develop`;
- v3 integrada e demonstrável: concluída;
- testes e preflight técnico: concluídos;
- documentação consolidada para redação: este pacote;
- decisão institucional LGPD/CEP: pendente;
- promoção `develop` → `main`: bloqueada até o gate institucional ou decisão formal
  de escopo que mantenha somente demonstração acadêmica controlada.
