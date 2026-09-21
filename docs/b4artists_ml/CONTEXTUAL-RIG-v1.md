# Contextual whole-body rig adapter V1

Status: research API with actual-rig validation; not a released or interactive product feature. Full goal ACTIVE and incomplete. The 0.4 add-on and ZIP remain unchanged.

## Implemented behavior

`training/b4artists_ml/context_rig.py` bridges the trained contextual model to actual editable FK controls. `Session(obj)` snapshots source transforms and IK/FK modes, normalizes supported input rigs, and establishes rest geometry and an explicit pelvis frame. `solve(world_targets_17x3, mask_17, learned_influence=1)` proposes a body pose and fits the actual evaluated skeleton. `cancel()` restores the source setup. No animation keys, actions, helpers, constraints or mechanism transforms are created or edited.

Model inputs remain pelvis-relative when the requested pelvis moves. The corresponding world translation is reintroduced when fitting the rig. Existing hand, foot and head orientations and the pelvis orientation are preserved rather than inferred. Arbitrary requested orientations, animator pole targets and anatomical limits are still required work.

Mappings were checked against actual BoneForge and Rigify builders. BoneForge uses its full FK spine and clavicle controls; Rigify uses evaluated ORG landmarks with writable hips/chest/spine/neck/shoulder/FK controls; metarigs include their intermediate spine and neck bones. The 17 semantic links are not assumed to be physical bones. The adapter reads actual bone lengths through the rig hierarchy and never writes generated ORG/MCH/DEF bones.

Fitting uses finite-difference control derivatives, scale-aware damped least squares and quaternion-vector orientation residuals. A final constraint pass gives explicit pins priority over the learned suggestion. Unconverged or stretched results raise and restore the preceding preview. All host mutation remains on the main thread. This establishes actual rig behavior but is computationally expensive.

## Tests and measurements

The main host run passed three test methods with five real-rig subcases and zero skips. A separate fourth test passed object rotation, translation and uniform scale with a real source action. Fixture targets came from poses authored on actual controls and included moved head, wrists, ankles and pelvis. Each rig was solved with learned influence zero and one; the difference below is measured at actual elbow joints, so model execution or geometric fallback alone cannot pass learned participation.

| Fixture | Maximum pin error / torso length | Maximum tracked length change | Learned elbow change / torso length | Learned solve seconds |
|---|---:|---:|---:|---:|
| boneforge | 4.44e-05 | 8.55e-07 | 0.048 | 1.88 |
| rigify_basic | 7.58e-06 | 2.8e-06 | 0.250 | 5.44 |
| rigify_default | 7.58e-06 | 2.8e-06 | 0.250 | 17.10 |
| metarig_basic | 2.68e-06 | 9.95e-07 | 0.163 | 1.57 |
| metarig_default | 2.68e-06 | 9.95e-07 | 0.163 | 2.90 |

Each rig also has a weighted triangle following an actual deform bone. Deformation matches the evaluated bone transform and changes from rest. This is a small mathematical deformation fixture, not production-character mesh or visual acceptance. Constraint names/types/influence/mute state are retained. Cancel restores original controls and mode values. An impossible request verifies rollback, a model-input probe verifies zero-origin pelvis conditioning, and the transformed/action case verifies source action identity, slot, keyframe values and handles.

Host: `X:/5.1.0/bforartists.exe`, core 5.2.0 Alpha, build dd23ab17120d. The existing Ryzen 7 5800XT machine was used. The primary run took 70.37 seconds including fixture building and both solver variants. Reported per-rig times include fitting and dependency-graph evaluation; generation and model/session setup are outside them. Results are single-run measurements, not latency distributions or hardware coverage. The 17.10-second default Rigify result is unsuitable for live interaction.

All assertions passed before the known `ucrtbase.dll` shutdown access violation, signed exit -1073741819 / unsigned 3221225477. Host process exit is unclean.

## Reproduce

```powershell
# [PowerShell]
& 'X:\5.1.0\bforartists.exe' --background --factory-startup --python tests/test_b4artists_ml_context_rig.py
```

Needs the existing local BoneForge source and host Rigify generator only for constructing test fixtures, plus the frozen contextual weights. The adapter imports neither builder and has no runtime dependency on either installed companion add-on. Run in a disposable session. `B4ML_CONTEXT_RIGS` can narrow rig subcases; `B4ML_CONTEXT_TEST` selects one test and writes the supplemental report. A narrowed run does not prove all fixtures.

Evidence: `training/b4artists_ml/results/context_rig_v1.json`, `context_rig_supplement_v1.json`; ignored logs `cache/context-rig-final.log` and `cache/context-rig-transform.log`. Model SHA-256 remains `919de9c772a521d6531f692b8903d0392fb981bf79896f40a8ff893d746a6f96`.

## Failures resolved and remaining work

The initial full fit missed pins on all five rigs. Per-iteration evidence showed slow convergence. Scale-aware damping, a stable orientation residual and a separate pin-priority pass resolved the tested failures without relaxing tolerances. A pelvis-coordinate correction removed an input mismatch with model training. The numerical pass does not resolve the model's earlier-pose quality regressions documented in CONTEXTUAL-POSE-RESULTS-v1.md.

Next, reduce thousands of dependency-graph evaluations per solve while retaining the dense solver as a correctness reference. Evaluate cached/analytic rig kinematics or controlled derivative reuse against actual-rig results, not only backend timing. Then integrate cancellable previews, editable anchors/actions, save/reload and undo into the add-on. The current Python Session is synchronous, one-frame and not persistent; it must not be exposed as a production live solver.

Broader proportions/imported rigs, production meshes, joint/twist limits, pole/orientation inputs, contact/balance/physics, learned motion, secondary motion, quadrupeds and the optional connector remain incomplete. No new visual judgment, animator correction-count study or direct Cascadeur comparison was performed.

## Execution and preservation

The required router was called locally, required the approved remote executor, then reported that the remote `/mnt/x/...` workspace was absent. It emitted no lane or patch. Native continuation followed STATIC-NATIVE-EXECUTION-POLICY.md for recoverable pre-host-application infrastructure failures. Scope: contextual rig adapter, its tests and project evidence; no installed-addon or history changes. Runtime add-on bytes still match the 0.4 ZIP; Ghost Tool and Anim Assist tracked diffs remain empty. No commit, merge or push.
