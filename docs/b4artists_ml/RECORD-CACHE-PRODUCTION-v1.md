# Experimental 0.17.5 record reconstruction

The local experimental 0.17.5 package integrates bounded record reconstruction. All 345 native regression cases and four exact-package offline live/Keep/Discard cases pass. Default Rigify idle p95 improves 44.4%, total active work 14.3%, and worst-tick averages 13.3%, with exact five-profile poses, signatures and solver metrics. Each read returns an independent mutable tree; source validation remains unchanged. Cache keys/blobs stay within 4 MiB plus bounded container overhead and are released at preview/lifecycle boundaries. Worst ticks still exceed 50 ms. Current UI interaction, independent animator assessment, full learned motion and Cascadeur parity remain unverified; the known host shutdown crash persists. See RECORD-CACHE-PRODUCTION-v1.md and package-test-v0.17.5.json. The original goal remains active and incomplete.

The comparison uses separate headless host processes, two live solves and 100 idle ticks per run, a fixed logical clock and no profiler. BoneForge/default Rigify use baseline/current/current/baseline order; the other three profiles use baseline/current. Ratios are current divided by baseline; below one indicates less elapsed work. These timings do not measure input-event queues, viewport drawing or independent animator usability.

| Rig | Idle p95 ratio | Active work ratio | Worst tick ratio | Exact result/source parity |
|---|---:|---:|---:|---|
| boneforge | 0.7432 | 0.9784 | 0.9749 | Pass |
| rigify_default | 0.5561 | 0.8573 | 0.8672 | Pass |
| rigify_basic | 0.7634 | 0.9187 | 1.0403 | Pass |
| metarig_basic | 0.7440 | 0.9003 | 0.8703 | Pass |
| metarig_default | 0.6444 | 0.9510 | 1.0023 | Pass |

Default Rigify worst-tick averages change from 65.37 to 56.69 ms. Basic generated Rigify has a 4% higher worst-tick average in this run; no blanket worst-tick improvement is claimed. All preset scoped gates pass, while the original full-responsiveness requirement remains unmet.

The cache retains at most four exact JSON payloads and locally encoded primitive blobs. Eligible payloads are capped at 524288 characters and blobs at 1048576 bytes; the total measured key/blob allocation is capped at 4194304 bytes. OrderedDict overhead is bounded by four entries. The allocation stress test verifies retained growth under this budget plus 64 KiB overhead, peak traced allocation below 10 MiB for its fixed ASCII workload, and release after clearing. These are cache-local Python allocations, not whole-host or GPU memory qualification. Oversized input bypasses caching; unsupported schema, malformed JSON and invalid top-level values fail without retention.

Fresh reconstruction preserves nested mutation isolation. Real helper, transform, structural and ownership validation runs as before. Successful Keep/Discard and save/reset/unregister clear the cache. Existing JSON records and packaged models are unchanged; no data migration or external binary input is used.

Fourteen new tests plus the prior 331 cases all pass freshly on the integrated source. The only subsequent runtime edit is the verified version literal. Four exact-archive offline cases pass with outbound Python network/process calls denied and cache cleanup verified. The host still exits with 3221225477 after assertions; this is recorded separately and is not a clean-exit qualification.

All temporal candidates remain frozen and unqualified; sealed confirmation data remains absent. Full physics/refinement, broader rigs and quadrupeds, optional connector, distribution/hardware qualification, independent usability and equivalent Cascadeur comparison remain part of the unchanged original goal. No commit, push or installation was performed.
