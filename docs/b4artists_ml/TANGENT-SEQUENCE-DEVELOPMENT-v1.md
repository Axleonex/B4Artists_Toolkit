# Tangent-conditioned sequence development

The tested tangent-conditioning configuration does not pass the original development requirements. No model is promoted or bundled. A completed fit and stronger context response cannot substitute for the failed gates.

Both 60-epoch fits and the protocol were frozen before evaluation. All 768 original development windows were evaluated; the three projected procedural controls reproduced the original references exactly. Old, new and combined partitions retain their original gates.

| Seed | Position ratio | Velocity ratio | Acceleration ratio | Worst cohort ratio | All partitions pass |
|---|---:|---:|---:|---:|---|
| 20260909 | 1.058 | 1.117 | 1.239 | 8.999 | False |
| 20260910 | 1.027 | 1.094 | 1.200 | 7.971 | False |

Ratios below 1 mean lower error. Original requirements include position at most 0.95, velocity/acceleration at most 1.05, and each cohort at most 1.10. Endpoints and physical edge checks remain separate.

## Context diagnostic

tangent-direct-20260909
- context0: position error 0.168098, previous model 0.161593, shape control 0.161724.
- context1: position error 0.129315, previous model 0.161651, shape control 0.119397.

tangent-direct-20260910
- context0: position error 0.160669, previous model 0.162192, shape control 0.161724.
- context1: position error 0.127954, previous model 0.162231, shape control 0.119397.

These context summaries are equally weighted cohort means and do not replace acceptance aggregation. Development data has been repeatedly exposed; it is not an unbiased confirmation set. All six confirmation clips remain unopened.

No new fit follows automatically from this result. Preserve both seeds and failure evidence. A further learned-motion experiment requires a new bounded hypothesis rather than adjacent tuning. Continue the independent responsiveness and full physics/intent/workflow requirements.

Evidence: training/b4artists_ml/results/sequence-tangent-development-v1/report.json and comparison-to-previous.json. The original goal, deadline, evaluation ceiling and qualification requirements remain unchanged.
