# Learned context control and bounded motion coverage, v6-v8

Research only. No temporal weights are bundled in experimental 0.14.2; the full goal remains incomplete.

## V6: learned selection of motion context

A supervised two-output kernel controller chooses how much observed root and quaternion context to blend into the frozen V3 articulated predictor. Inputs contain only known poses, velocities and timing. Training-only least-squares projection provides bounded root/rotation targets. No-context windows retain V3. The selected compact model (width 2, regularization 0.1) improves validation position by 9.95% and velocity by 9.97% relative to the strongest protocol baseline. Rotation, acceleration, endpoints and edge checks also pass. Worst cohort position remains 1.728 times its strongest baseline and observed-development position is 4.29% worse, so qualification fails.

## V7: rejected complexity

An independent 24-output controller with training-only mean priors and no-context denoising was prospectively tested. None of its eighteen fits beats V6 selection. V6 remains the incumbent. Six new tests preserve per-joint targets, mean-prior behavior, missing-context isolation, saved inference, priorities, edges and bounded strengths. Failed candidates are retained, not promoted.

## V8: coverage expansion and untouched confirmation

All previously unused cached clips belonged to earlier test/confirmation sets and remained excluded from training. The new split was frozen from the pinned catalog before downloading motion: eight train clips (subjects 90/91), four validation clips (118/122), and three confirmation clips (143/137). Total raw acquisition was 8,269,596 bytes across fifteen files, under the declared 20,000,000-byte cap. Existing split identifiers and hashes remain unchanged. Exact clip IDs/content hashes are disjoint; this does not prove actor independence or rule out semantic near-duplicates.

The source is the existing [pinned CMU BVH mirror](https://github.com/una-dinosauria/cmu-mocap/tree/09a07f54f3bbb58797325f009282d0b2048a2871). The converter's [usage notice](https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/09a07f54f3bbb58797325f009282d0b2048a2871/READMEFIRST.txt) was accessible; the direct CMU publisher page timed out again. Existing attribution remains. This is local research, not new distribution-rights clearance.

Expanded training uses 2,912 windows; combined validation has 480 windows. Base/controller settings were fixed before training. The expanded pair improved combined selection score from 0.092766 to 0.092417 while satisfying the declared old-validation guard. Selection and both weight hashes were frozen before the three confirmation files were downloaded or read. The 144 untouched confirmation windows then failed: position ratio 1.0662 and worst-cohort ratio 2.1568. Combined validation still fails its cohort gate (1.8521). The previous observed development set fails too. No quality gate was lowered and no unqualified model was shipped. These confirmation clips are now observed; future tuning cannot call them fresh again.

Seven mocked acquisition tests cover byte caps, split/content duplication, unrecorded files, changed-model refusal and immutable first-confirmation ownership. A second training run reproduces both expanded models byte for byte and identical complete quality reports. It preserves the first confirmation receipt and explicitly labels subsequent use as reproduction, not a second blind study.

## Actual host scope

The twelve V6/V7 controller tests pass in Bforartists core 5.2.0 Alpha with NumPy 2.3.4. Both selected research pairs run local inference on 33 query frames with exact priorities and source edge error below 4.5e-16. Measured first/warm-p95 inference: V6 8.67/7.31 ms; V8 10.97/9.65 ms. Loading is 61.30/76.21 ms respectively. These exclude actual control-rig fitting and viewport application; they are not end-to-end performance acceptance. Every host process still encounters the known shutdown access violation.

Evidence lives in training/b4artists_ml/results/context_gate_v6/, context_gate_v6_repeat/, context_gate_v7/, motion_expansion_v8/ and motion_expansion_v8_repeat/. Acquisition plans/protocols and complete split hashes are retained alongside them. context-gate-host-v1.json records the host inference scope; temporal-controller-reproduction-v8.json records exact replication.

## Remaining integration work

Learned temporal quality is still unqualified. Actual BoneForge/Rigify temporal retargeting, multiple priority poses, partial-body intent, contacts, momentum/secondary motion, production/quadruped coverage and independent animator/Cascadeur comparisons remain open. Before more tuning, inspect the now-observed failure cohorts and establish a rigorous canonical rig-to-model encoding and reversible application path. Preserve the rejected-model boundary and obtain new untouched confirmation for any later quality claim.
