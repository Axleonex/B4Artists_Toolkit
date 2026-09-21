# Record-copy and bounded-cache research result

The research-only cache passes its scoped timing and correctness gates. It is not integrated into production source or the0.17.4ZIP.

| Rig | Idle p95 ratio | Total active-work ratio | Worst tick ratio | Exact poses/signatures/metrics |
|---|---:|---:|---:|---|
| boneforge | 0.813 | 0.955 | 0.871 | True |
| rigify_default | 0.674 | 0.865 | 0.875 | True |
| rigify_basic | 0.849 | 0.920 | 0.916 | True |
| metarig_basic | 0.783 | 0.931 | 0.893 | True |
| metarig_default | 0.572 | 0.899 | 0.970 | True |

For default Rigify, idle p95 improves32.6%, total active work13.5% and worst ticks12.5%. Worst-tick averages remain52.67ms versus60.21ms, still above the full50ms target. The fixed scoped thresholds were idle p95ratio<=0.85, total-work ratio<=1.05 and worst-tick ratio<=1.10; every profile retains exact pose/signature/metric and source parity. Counterbalanced base/current/current/base runs were used on BoneForge/default Rigify, and base/current on the other three profiles. No concurrent host workload or profiler ran during the comparison. UI queue latency and human usability are not measured.

The initial actual-preview microbenchmark measured JSON, deepcopy, and locally generated pickle/marshal copies on five rigs,200calls per method and profile. Default Rigify median JSON decoding was3.1245ms versus0.6841ms for fresh marshal reconstruction; deepcopy was slower. All methods preserved exact records and nested mutation isolation. This motivated the fixed follow-up cache; the microbenchmark alone did not establish live-solve speed.

The prototype stores up to four exact-payload keys, each limited to512Ki characters and a1MiB immutable encoded blob. Blobs are generated only from the original JSON decoder inside the host, never accepted from external binary input or persisted. Every hit reconstructs an independent mutable tree; every miss returns an independently decoded record. Invalid decoding is never cached; oversized payloads/blobs bypass storage. Original payload comparisons, structural validation, ownership, current target sampling and source recovery remain active.

All seven existing record-read guards and eight live-preview guards pass under the prototype. Additional invariants check independent nested mutation, bounded entry eviction, failed-decoding exclusion, oversized bypass and explicit clearing. All host shutdowns still record3221225477after successful assertions. This remains a failed supported-host lifecycle condition.

Production integration still requires cache lifecycle/cleanup and failure handling, broader malformed-input coverage, full regression, memory/resource measurement and exact-package validation. No production source, package, neural model or confirmation data changed. Prior330-case runtime coverage and one newer source-isolation test remain retained under unchanged source hashes; the15prototype guards are not a fresh full run.

The full original standalone posing, learned temporal workflow, physics/refinement, humanoid/quadruped coverage, optional connector, distribution, responsiveness, independent animator and equivalent Cascadeur requirements remain incomplete. The original endpoint,50-evaluation ceiling and fixed15-hour deadline are unchanged. See RECORD-CACHE-PLAN-v1.md and the versioned JSON evidence.
