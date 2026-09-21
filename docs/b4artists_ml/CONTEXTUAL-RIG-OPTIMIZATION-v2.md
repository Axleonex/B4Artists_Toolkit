# Contextual rig optimization and cooperative execution V2

Status: research API improved; full product goal ACTIVE and incomplete. No new add-on release or installed-addon changes.

## Changes

`context_rig.Session.solve` now defaults to derivative reuse. The dense finite-difference method remains available as `jacobian_mode="dense"` for comparison. The optimized method updates its derivative estimate from accepted steps, refreshes every three iterations or after two rejected steps, and resets when entering the final pin-priority phase. It retains the same pin, length and pelvis-orientation thresholds.

The independent rank-one secant implementation follows the general method described by [Broyden (1965)](https://www.ams.org/journals/mcom/1965-19-092/S0025-5718-1965-0198670-6/S0025-5718-1965-0198670-6.pdf). No external code or weights were copied. Periodic finite-difference refresh and actual-rig validation are necessary; no convergence guarantee is claimed for arbitrary rigs.

`solve_steps` is a cooperative generator for a future main-thread viewport operator. It yields during derivative batches and after fitting steps, restoring the accepted iterate before yielding so a finite-difference probe is never left visible. Completion returns the verified result via `StopIteration.value`. Closing it or requesting cancellation restores the preceding preview. Synchronous `solve` exhausts the same engine without scheduling overhead.

One active iterator per Session and one contextual Session per rig are enforced. The ownership registry releases on successful session cancellation. This does not yet integrate ownership with every existing add-on/UI workflow. Session state is still Python-owned and does not survive save/reload.

## Comparison gates and results

Each pair uses the same fixture, targets, learned model, iteration budget and projection tolerances. Optimized output must pass maximum pin error 2e-4 torso lengths, maximum tracked length change 0.002 and pelvis angle 0.001 radians. Mean distance to the learned proposal must be within 5% of the dense result, with fewer than half as many rig evaluations. This proposal-distance gate is an optimization regression check, not visual quality or preservation-of-intent acceptance.

| Nominal fixture | Dense seconds | Reuse seconds | Speedup | Dense / reuse evaluations |
|---|---:|---:|---:|---:|
| boneforge | 1.889 | 0.696 | 2.71x | 2470 / 895 |
| rigify_basic | 5.564 | 2.238 | 2.49x | 2553 / 1010 |
| rigify_default | 19.437 | 8.456 | 2.30x | 2553 / 1010 |
| metarig_basic | 1.537 | 0.569 | 2.70x | 2651 / 981 |
| metarig_default | 2.901 | 1.103 | 2.63x | 2651 / 981 |

Four additional pairs used reversed (-0.75) and larger (2.0) authored control edits on BoneForge and basic generated Rigify, with 80 iterations for both algorithms. They also passed all gates. Across the nine final pairs the measured speedup was 2.3-2.9x. These are ordered dense-then-reuse measurements on one machine/run, not randomized timing distributions; dependency-graph evaluation counts independently confirm reduced work.

The first reuse candidate refreshed every five iterations. It passed nominal fixtures but failed the reverse Rigify proposal-distance gate. That failure remains in `context_rig_reuse_varied_v1.json`. Refreshing every three iterations passed the same threshold; the gate was not weakened. The reverse Rigify proposal error remains about 4.1% above dense, so this is a bounded computational tradeoff, not a claim of better pose quality.

## Cancellation and scheduling

The complete host suite passed ten test methods with zero skips, including five real-rig deformation/influence fixtures, nine dense/reuse pairs, source action/slot/keyframe/handle preservation under rotation and uniform scale, impossible-target rollback, zero-origin pelvis conditioning, cancellation after 20 evaluation probes, generator close/reentrancy protection, synchronous/cooperative equivalence and session ownership release.

A separate default-generated-Rigify scheduling run passed and produced 150 checkpoints. Per-`next()` median was 68.16 ms, p95 96.28 ms and maximum 116.51 ms. Synchronous reuse took 7.54 seconds; cooperative completion took 9.98 seconds, including additional state restoration/validation around yields. Final joint positions matched the synchronous result exactly in that run. Construction/model loading and waiting between scheduled calls are outside these timings.

The iterator provides opportunities for a UI scheduler to process input; there is no implemented modal operator or verified Escape-key/viewport interaction yet. Total fitting time remains several seconds on complex Rigify rigs. This is not live 60-fps posing.

## Evidence and reproduction

Host: `X:/5.1.0/bforartists.exe`, core 5.2.0 Alpha, build dd23ab17120d, on the previously recorded Ryzen 7 5800XT machine. The final full suite ran in 139.42 seconds. Assertions passed before the existing `ucrtbase.dll` shutdown access violation, exit -1073741819 / 3221225477. Do not report a clean process exit.

Results: `training/b4artists_ml/results/context_rig_optimized_all_v2.json`, `context_rig_reuse_varied_v2.json`, `context_rig_progress_default_v2.json`. Earlier results retain earlier algorithm settings and remain historical evidence.

```powershell
# [PowerShell]
$env:B4ML_CONTEXT_RESULT='context_rig_optimized_all_v2.json'
& 'X:\5.1.0\bforartists.exe' --background --factory-startup --python tests/test_b4artists_ml_context_rig.py
```

For the separate scheduling test, set `B4ML_CONTEXT_TEST=ContextRigTests.test_progress_exhaustion_matches_synchronous_result`, `B4ML_PROGRESS_RIG=rigify_default`, and choose a separate result filename. The test script supports narrowed cases for diagnosis; narrowed runs are not full compatibility evidence.

## Next work and unchanged scope

Integrate the cooperative engine with a real modal preview, visible progress, keep/discard, editable pose anchors, undo and persistent source recovery. Preserve operation ownership and frame/action validation across UI events. Investigate cached mathematical forward kinematics to remove most dependency-graph work, using actual evaluated rigs as the reference. The dense method remains a useful verifier.

Current model quality regressions, anatomical limits, pole/orientation input, temporal contacts, learned inbetweening, balance/physics, secondary motion, quadrupeds, production meshes and optional connector remain unfinished. No animator visual judgment or direct Cascadeur comparison was performed.

The 0.4 source and ZIP remain byte-identical. Ghost Tool and Anim Assist are unchanged. No commit, merge, push, model retraining or asset download occurred in this checkpoint. The approved execution router could not access remote `/mnt/x/...`; it emitted no lane or patch. Native continuation followed the canonical recoverable-infrastructure policy within the authorized project scope.
