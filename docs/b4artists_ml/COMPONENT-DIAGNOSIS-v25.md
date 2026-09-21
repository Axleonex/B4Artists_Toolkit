# Frozen component diagnosis and current tick profile v25

The v24 regression is primarily associated with its new position selections in these fixed crossed tests. This is a diagnosis of exposed development data, not a new qualified model or proof about every possible architecture.

| Frozen position donor | Frozen rotation donor | Failed cohorts /96 | Old worst ratio | New worst ratio |
|---|---|---:|---:|---:|
| v23 | v23 | 7 | 1.586986 | 1.206508 |
| v24 | v24 | 18 | 7.864863 | 1.708019 |
| v23 | v24 | 7 | 1.482269 | 1.213228 |
| v24 | v23 | 17 | 7.951659 | 1.675202 |

The v23-position/v24-rotation combination still fails seven cohorts, with two new failures (28_01/gap8/context1 and28_02/gap16/context1) and two cleared failures (28_02/gap8/context1, 118_12/gap8/context1). Its average position gains pass and rotation accuracy improves, but all worst-cohort gates still fail. It is not promoted.

For 28_01/gap32/context1, raw positional error rises from0.099531 with v23 positions to0.481524 with v24 positions. After the same physical projection, ratios are1.587/1.482 for v23 positions with old/new rotations versus7.952/7.865 for v24 positions. The difference-in-differences interaction ratio is0.01792. Thus the largest failure exists before projection and persists with either rotation donor. This argues against treating projection as the sole cause. Other cohorts do show rotation-induced changes, so rotation selection is not universally harmless.

All four raw component combinations are evaluated on the same768windows. Raw positional scores match their position donor and raw rotation scores match their rotation donor exactly for each partition and cohort. The two new crossed combinations use the unchanged physical projection and original old/new/combined gates. Original model, code, report and data hashes remain checked. No fit, retuning, fresh confirmation access or promotion occurred.

## Current-runtime performance diagnosis

The existing hot-tick profiler was adapted to a new output tag and required exact current0.17.4 runtime hashes. It ran one warmed changed-head-target solve on BoneForge and default Rigify, with cProfile reset at every tick. Both fixtures retained original accuracy gates, source poses, modes, action and keys. The host again exited3221225477 on shutdown after these assertions.

On default Rigify, the largest instrumented tick was68.44ms during temporary-copy pruning: prepare_steps accounted for34.54ms, of which34.48ms was self time. The final ready tick was53.06ms. Another slow tick was dominated by JSON decoding. These instrumented, headless measurements identify cost centers; they are not an uninstrumented latency benchmark or human usability result.

A bounded next optimization is to remove unused private-copy bones in batches, returning to Object mode and restoring the original context before every cooperative yield. Keep dependency closure, evaluated poses, authored targets, solver metrics and recovery unchanged. Compare against the current ZIP before promotion, including cancellation and source invalidation at new boundaries. Do not yield while Edit mode or a temporary context override is active. If overhead or correctness gates fail, retain0.17.4.

No runtime/package changes occurred in this diagnostic turn. Prior330-case/31-suite and four offline package checks remain retained under exact hashes, not rerun. Full learned workflow, physics/refinement, rig/quadruped coverage, optional connector, distribution, supported-host lifecycle, responsiveness, independent animator assessment and equivalent Cascadeur comparison remain incomplete. The same goal ID, original endpoint,50total evaluations and fixed15-hour resumed deadline remain unchanged.
