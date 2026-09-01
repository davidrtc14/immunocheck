# Registro de decisões arquiteturais

| ID | Decisão | Estado | Justificativa |
|---|---|---|---|
| ADR-001 | Telegram na v1 | Aceita | Gratuito, simples, long polling local e sem exigência de infraestrutura pública. |
| ADR-002 | WhatsApp fora da v1 | Aceita | Maior complexidade operacional; reavaliar somente após o protótipo funcional. |
| ADR-003 | Texto, imagem textual e link na v1 | Aceita | São requisitos do problema e viáveis localmente; vídeo tem custo desproporcional. |
| ADR-004 | Vídeo como trabalho futuro | Aceita | Transcrição, quadros, direitos e custo computacional formariam uma subpesquisa. |
| ADR-005 | Sem cache conversacional | Aceita | Simplifica privacidade, avaliação e comportamento do protótipo. |
| ADR-006 | Execução e demonstração locais | Aceita | Evita dependência de hospedagem gratuita sem garantia. |
| ADR-007 | Qwen3-8B local como única LLM principal | Aceita | Reprodutibilidade, gratuidade e nenhuma transferência de conteúdo para terceiros. |
| ADR-008 | Gemini excluído da produção | Aceita | O tier gratuito tem implicações de uso de dados e criaria diferença entre avaliação e entrega. |
| ADR-009 | BGE-M3 + BM25 + RRF | Aceita | O piloto obteve o mesmo Recall@10 do dense e melhor MRR/nDCG@10; promovido ao fluxo real em 01/09/2026. |
| ADR-010 | Reranker condicionado ao experimento | Aceita | Só entra no caminho final se melhorar relevância o suficiente para justificar latência. |
| ADR-011 | PostgreSQL + pgvector | Aceita | Solução gratuita e madura para metadados, texto, vetores e rastreabilidade. |
| ADR-012 | Sem pesos editoriais manuais na primeira versão | Aceita | Evita viés e hiperparâmetros frágeis em conjunto pequeno. |
| ADR-013 | Produção sem persistência de interações | Aceita | Minimização por desenho e menor risco sob LGPD. |
| ADR-014 | Verificação pós-geração obrigatória | Aceita | Reduz citações inválidas e afirmações sem suporte; efeito será medido. |
| ADR-015 | Python 3.12 | Aceita | Base estável e reproduzível para o ecossistema de ML e OCR. |
| ADR-016 | Quatro classes com abstenção | Aceita | Evita binarização indevida e diferencia falta de evidência de falsidade. |
| ADR-017 | Fontes parciais em abstenções | Aceita | Fontes consultadas podem ser exibidas como não conclusivas, sem fingir que sustentam um veredito. |

## Histórico de alterações

- **01/09/2026 — ADR-009:** a hipótese híbrida foi promovida após a comparação piloto
  documentada em `RETRIEVAL_PHASE2.md`. O caminho online passou a carregar o índice BGE-M3 local,
  combinar top 60 lexical e denso por RRF 60 e entregar top 6 ao gerador. `RETRIEVAL_MODE=bm25`
  permanece somente para ablação e diagnóstico; o reranker continua desativado por padrão.
- **01/09/2026 — ADR-017:** o teste com alegação composta mostrou que descartar todas as referências
  após a auditoria reduzia a transparência. A resposta agora separa fontes conclusivas de fontes
  parciais consultadas; nenhuma interação passou a ser persistida.

## Política de alteração

Uma ADR aceita pode ser alterada quando houver evidência experimental, inviabilidade
técnica comprovada ou mudança de requisito. A alteração deve registrar data,
evidência, impacto metodológico e plano de migração; preferência tecnológica isolada
não é justificativa suficiente.
