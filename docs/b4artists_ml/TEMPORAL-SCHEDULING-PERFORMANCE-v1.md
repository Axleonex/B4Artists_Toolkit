# Temporal research scheduling: performance follow-up

Two bounded changes reduce research-generator stalls: restore only changed pose/mode channels, then yield after each known-pose observation. Original source pose and playhead remain visible at pauses. Closing or rejecting a resumed observation preserves newer animator edits. Hidden inbetween samples are never read. This is research code; add-on and ZIP 0.17.5 are unchanged.

The optimized restoration passed 25 native workflow and recovery methods. Cooperative observations then passed 28 methods: those same 25 plus exact observations across eight rigs with both context settings, interruption after each observation, and cancellation without candidate creation or leaked resources. There are 16 exact observation comparisons, 16 edit-preservation cases and four observation cancellation cases. Existing reference-transform tolerance remains 2e-6; authored samples are exact.

## Measured tradeoff

Each comparison uses 24 counterbalanced runs across BoneForge, basic Rigify and default Rigify, with and without context. Generated samples and deterministic solver metrics match exactly. Added observation phases are filtered only when checking that the original solver-phase sequence remains identical.

| Default Rigify | Restore all ? selective: average worst step | Synchronous ? cooperative observations: average worst step | Observation scheduling total work |
|---|---|---|---|
| Without context | 217 ? 153 ms | 206 ? 156 ms | +1.2% |
| With context | 268 ? 230 ms | 246 ? 174 ms | +8.4% |

These are separate loaded-host comparisons; do not combine them into one speedup. Two training jobs ran throughout. The second comparison also overlapped native correctness tests. Its predeclared research budget allowed up to 25% additional total work for finer scheduling; measured increases across all fixtures were 1.1?9.5%. BoneForge with context increased its average worst step by 4.2%, within the predeclared 5% comparison bound. This does not change any full-product regression floor or the original 50 ms responsiveness requirement, which still fails.

## Evidence and remaining work

`training/b4artists_ml/results/temporal-observer-verification-v1.json` consolidates source, runtime, package and result hashes. The two benchmark reports and their frozen plans retain every run. Prior source versions are under `results/temporal-restore-baseline-v1` and `results/temporal-observer-baseline-v1`. Production runtime hashes match the prior 345 native cases and four packaged offline cases; those were retained, not rerun.

The trained-provider cooperative checker is prepared but unexecuted while both v26 jobs generate training labels. No temporal weights are qualified, bundled or promoted. Product UI integration, action-publication latency, full 50 ms responsiveness, the host shutdown access violation, independent code review, animator assessment and the full original goal remain unresolved. The extra scheduling points do not demonstrate Cascadeur parity.
