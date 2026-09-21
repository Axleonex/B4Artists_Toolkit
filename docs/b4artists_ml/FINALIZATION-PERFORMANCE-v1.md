# Finalization performance and recovery

The finishing stage now shares the existing per-tick read cache for read-only validation and target checks. Completion still obtains an independent mutable record. Final effector rotations keep their original order, with cancellable checkpoints after every two updates. Each resumed checkpoint validates the source again. No finite-difference probes, objective weights, model parameters or final acceptance tolerances changed.

A failure test found that corruption of the public preview record during completion could prevent restoration of the preceding verified preview. The released 0.17.3 ZIP reproduced this on both BoneForge and default Rigify. Each running job now holds the valid serialized start record for rollback. The fixed comparison restores the verified preview on both rigs, while preserving source actions and keys. This transient record is released with the job; it does not change the saved schema.

Bulk RNA matrix reads reduce structural-validation work. Matrix data is read afresh on every call, transposed from RNA column order into the existing saved row order, and returned in the same dictionary format. Repeated alternating reads on five actual rig profiles matched the original JSON bytes exactly. Default Rigify median read time fell from 2.170 ms to 1.049 ms in that local prototype. Additional tests cover empty rigs, renaming, reparenting and a rest edit that must invalidate an active session, followed by exact restoration.

| Default Rigify, final fixed comparison | Released 0.17.3 | Candidate |
| --- | ---: | ---: |
| Average finishing tick | 77.99 ms | 48.03 ms |
| Average of each solve's worst tick | 77.99 ms | 56.23 ms |
| Total active solve work ratio | 1.000 | 0.920 |

The final comparison passes the original gates: finishing tick reduction at least 25%, worst-tick average reduction at least 20%, total active work no greater than 110%, and identical final poses, authored requests, accuracy metrics, evaluation counts and iteration counts on all five profiles. BoneForge/default Rigify use archive/current/current/archive order with two solves per run; three other profiles use one archive/current pair. These are headless tick-work measurements with a deterministic logical clock and no profiler, not UI queue-latency measurements.

The first candidate comparison is retained as a failed result: finishing ticks improved 31%, but the worst-tick reduction was 18.5% against the required 20%. Hot-tick profiling then identified the private-rig prune stage and repeated structural reads. The bulk-read change was declared and tested before the second comparison; no threshold was lowered.

The remaining worst ticks still exceed 50 ms and complete solves take seconds. Full responsiveness and resource qualification remain incomplete. Current-package UI interaction, independent animator quality and equivalent Cascadeur comparison remain unverified. The known host shutdown crash persists after otherwise passing assertions. Learned temporal candidates remain unqualified and are not bundled.

Evidence: finalization-profile-v1.json, hot-tick-profile-v1.json, finalization-checks-v1.json (original failure), finalization-checks-final-v1.json, finalization-fault-comparison-v1.json, bulk-rest-read-v1.json, bulk-structure-checks-v1.json and finalization-benchmark-v1/v2.json in training/b4artists_ml/results. All 330 regression cases pass on current behavior; only the version literal changed afterward. Four exact-archive offline cases also pass, with outbound Python networking/process launches denied. The 0.17.4 ZIP is ready for local testing, with current-package UI events and independent human assessment explicitly unverified.
