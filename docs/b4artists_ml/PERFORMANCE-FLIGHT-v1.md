# Flight workflow performance findings, v1

Measured against byte-identical experimental 0.13.0 on Ryzen 7 5800XT, Windows 11, Bforartists core 5.2.0 Alpha dd23ab17120d. Six fresh host processes ran sequentially; first flight follows fixture creation, so this is not disk-cache cold. Three solves per completed case.

| Rig | Span | First solve | Warm solves | Worst step | Sampled RSS growth |
|---|---:|---:|---:|---:|---:|
| boneforge | 10 | 1.21s | 1.44s, 1.46s | 53.8ms | 16.6 MiB |
| boneforge | 60 | 7.93s | 10.09s, 10.45s | 155.7ms | 44.4 MiB |
| boneforge | 240 | 32.24s | 41.65s, 44.21s | 1103.2ms | 95.9 MiB |
| rigify_default | 10 | 5.37s | 8.02s, 8.26s | 162.3ms | 22.2 MiB |
| rigify_default | 60 | Rejected | Unavailable | Unavailable | Unavailable |
| rigify_default | 240 | Rejected | Unavailable | Unavailable | Unavailable |

All four completed cases preserved source animation and passed cancellation after candidate allocation. Every case with three completed previews left two unused superseded flight actions, including after Discard. The 240-frame BoneForge maximum step failed the predeclared 250ms budget. First/warm solve, step p95, abort-call and sampled-memory budgets passed in completed cases; this does not establish full workflow acceptance.

Default Rigify 60/240-frame flights rejected when relative facial-bone basis error reached 0.000229128/0.000200177, exceeding the unchanged 0.0002 tolerance. Failed-case rollback was not independently asserted by this benchmark. They are failed coverage cases, not fast results.

A separate cProfile run identified 1,388,166 nearest-key distance evaluations: key_at consumed 0.995s of a 1.358s profiled construction step. Signature checking took another 0.239s. Profiling timings include overhead and are not substituted into the timing table.

Every host process still exited 3221225477 after producing observations. No clean host lifecycle, independent animator usability, learned temporal performance or Cascadeur comparison is established.

Reproduction: run training/b4artists_ml/benchmark_flight_workflow.py with Python; it launches isolated host cases and refuses overwriting its v1 evidence. The frozen method and budgets are in PERFORMANCE-FLIGHT-PROTOCOL-v1.md. Results include raw steps, memory counters, exceptions and actual process exits.

Next: indexed key lookup with fractional-frame equivalence tests; cancellable construction/signature work; careful generated-action ownership cleanup; investigate Rigify precision and failed-job recovery. No runtime optimization is claimed by this measurement-only milestone.
