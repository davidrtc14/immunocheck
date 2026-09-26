# Triagem do seletor MMR — calibração v2

A triagem usa somente 36 itens conclusivos da calibração, sem chamadas de LLM,
teste v1 ou holdout v2.

| Sistema | Hit@6 | MRR@6 | SUPPORTED | REFUTED | MISLEADING |
|---|---:|---:|---:|---:|---:|
| Denso top 6 | 21/36 (58.3%) | 0.345 | 8/12 | 7/12 | 6/12 |
| Denso 20 → MMR 6 | 12/36 (33.3%) | 0.255 | 5/12 | 4/12 | 3/12 |

## Gates

| Gate | Valor | Limite | Estado |
|---|---:|---:|---|
| `global_hit_at_6` | 12 | ≥ 24 | Falhou |
| `misleading_hit_at_6` | 3 | ≥ 8 | Falhou |
| `supported_no_hit_loss` | -3 | ≥ 0 | Falhou |
| `refuted_no_hit_loss` | -3 | ≥ 0 | Falhou |
| `selection_p95_ms` | 0.416700029745698 | ≤ 100.0 | Passou |

**Decisão:** seletor MMR não elegível para avaliação fim a fim.

MMR mede diversidade no espaço BGE-M3; não demonstra suficiência factual nem
substitui a avaliação fim a fim.
