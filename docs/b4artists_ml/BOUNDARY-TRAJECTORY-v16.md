# Context reference and boundary correction experiment v16

Status: research-only. The learned candidate wins the combined validation score, but fails original acceptance and is not promoted. Runtime/package 0.16.1, bundled pose models, Ghost Tool and Anim Assist remain unchanged. The full goal remains incomplete.

## Prospective comparison and pre-fit repair

Four ablations cross the existing linear/contextual-Hermite reference with C0/C1 learned correction envelopes. All retain v15 observed-motion scaling, a 64-unit tanh model, regularization 0.0001, forty epochs, the original data identities and identical physical projection. C1 multiplies the four-term 4*t*(1-t) basis by another 4*t*(1-t), making correction value and first derivative zero at both priorities. This preserves the raw reference proposal derivative; it does not guarantee continuity after nonlinear rig projection or exact angular velocity from the existing quaternion tangent approximation.

The unchanged near-correct-curve learning test found optimizer overshoot before corpus fitting: initial loss 1.2954e-8 became 3.1488e-8. The failed source and result are preserved in `results/boundary-trajectory-prefit-source-v16.txt` and `results/boundary-trajectory-prefit-correction-v16.json`. Bounded per-batch backtracking now accepts only finite non-increasing objective updates (up to eight half-step attempts), otherwise retaining parameters. Adam moments still advance. This repair applies to every ablation; no test or quality gate was weakened.

All twelve new module tests pass, covering explicit/compressed trajectory loss, gradients for all network parameters, actual learning, stationary/masked-context/priority/serialization invariants, C1 endpoint derivatives and nonzero learned correction derivative convergence. Together with preserved suites, all 63 focused native cases pass.

## Selection and validation

Training-only excluded catalog groups select trial 2: contextual Hermite reference with C0 correction. The C1 counterpart scores 0.23720 against C0's 0.23460 on pooled internal held-out position+0.1*rotation, so C1 is not forced into the selected model. The model therefore does not claim boundary-velocity preservation. Normalization and learned features are trained within each fold; catalog grouping does not prove actor independence.

The full-training model is saved and hashed before loading validation. Its SHA is `9b27322e12c3ef0fdac00ca338c2c37b228b16922e92dd9631867bf807fc7814`. Every original projected baseline metric reproduces exactly. An independent complete repeat reproduces all 18 NPZ artifacts and every non-runtime report field exactly. No confirmation data or new assets are read, and validation has prior research exposure.

| Metric | Selected candidate ratio | Existing limit |
|---|---:|---:|
| Position | 0.99377 | <=0.95 |
| Rotation | 1.03636 | <=1.02 |
| Velocity | 1.07552 | <=1.05 |
| Acceleration | 1.16564 | <=1.05 |
| Worst cohort position | 11.45237 | <=1.1 |

Projected position error is 0.09297588: about 0.62% better than the best procedural position control, short of the required 5%. Endpoint and physical-edge invariants pass. The candidate wins the combined position/rotation selection score for this validation comparison, but selection is not qualification. No new temporal weights enter the add-on.

## Actual-rig and stationary behavior

All sixteen ordinary moving-pose tests pass: eight profiles with context off/on, candidate-action creation, priority preservation, Discard and source recovery. This explicitly tests the contextual reference on real rigs. Another sixteen stationary-rig checks pass with the existing 2e-5 numerical tolerance; maximum position component drift is 4.64e-6 and rotation-matrix component drift 5.68e-6. All sources are restored. The 186 controlled stationary observations still have exactly zero learned correction; remaining baseline reconstruction error is below 1e-12.

Profiles are BoneForge, basic/default generated Rigify, basic/default metarigs, Mocap, Unity and Unreal. These bounded fixtures do not establish production coverage, full multi-priority/partial-body/style/contact integration or independent animator usability. The ordinary and stationary host checks overlapped, so their timings are not comparative performance evidence.

Bforartists again exits with its previously observed shutdown access violation 3221225477 after assertions. Host lifecycle remains failed. Existing 303 native / 110 offline / two packaged-window evidence applies to unchanged package/runtime bytes and was not rerun here. No release, install, commit or push occurred.

## Next full-goal work

The learned-motion branch remains unresolved; this experiment does not justify another unbounded architecture or threshold sweep. Preserve its exact failed gates and all earlier failures. Inspection of `b4artists_ml/native_flight.py` confirms that native flight reports ballistic entry/exit velocities but does not apply continuous takeoff/landing velocity corrections. The roadmap and requirements still list this original-scope physics feature as missing.

Next implement a prospective native velocity-transition workflow: animator-controlled transition spans, preserved flight/outer priority poses, explicit contact/overlap validation, editable native results and full cancellation/Keep/Discard/save recovery. Measure whether it reduces the documented boundary mismatch on real BoneForge/default Rigify. Distinguish linear COM velocity/momentum matching from full angular-momentum conservation or dynamic balance. This advances another required part of the same product while learned motion quality, broad physics, rig/quadruped coverage, rights, performance, connector and independent Cascadeur comparison remain required.

Evidence under `training/b4artists_ml/`: `results/boundary_trajectory_v16/`, its independent `_repeat/` directory, `results/boundary-trajectory-reproduction-v16.json`, `results/boundary-trajectory-native-v16-regression.json`, `results/boundary-trajectory-host-v16.json`, `results/stationary-trajectory-host-v16.json`, `results/stationary-anchors-v16.json` and associated process reports. No full implementation milestone or parity is credited.
