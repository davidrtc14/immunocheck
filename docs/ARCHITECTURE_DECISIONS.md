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
| ADR-009 | BGE-M3 + BM25 + RRF | Aceita como hipótese | Retrieval híbrido será comparado ao dense-only; ganho não será presumido. |
| ADR-010 | Reranker condicionado ao experimento | Aceita | Só entra no caminho final se melhorar relevância o suficiente para justificar latência. |
| ADR-011 | PostgreSQL + pgvector | Aceita | Solução gratuita e madura para metadados, texto, vetores e rastreabilidade. |
| ADR-012 | Sem pesos editoriais manuais na primeira versão | Aceita | Evita viés e hiperparâmetros frágeis em conjunto pequeno. |
| ADR-013 | Produção sem persistência de interações | Aceita | Minimização por desenho e menor risco sob LGPD. |
| ADR-014 | Verificação pós-geração obrigatória | Aceita | Reduz citações inválidas e afirmações sem suporte; efeito será medido. |
| ADR-015 | Python 3.12 | Aceita | Base estável e reproduzível para o ecossistema de ML e OCR. |
| ADR-016 | Quatro classes com abstenção | Aceita | Evita binarização indevida e diferencia falta de evidência de falsidade. |

## Política de alteração

Uma ADR aceita pode ser alterada quando houver evidência experimental, inviabilidade
técnica comprovada ou mudança de requisito. A alteração deve registrar data,
evidência, impacto metodológico e plano de migração; preferência tecnológica isolada
não é justificativa suficiente.
