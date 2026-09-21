# Real-rig semantic hierarchy packet v1

## Decision

The product-facing humanoid inference boundary is a 17-joint semantic local hierarchy. BoneForge, Rigify and imported-rig adapters own their extra spine, twist, mechanism, deformation and controller bones. A richer 23-joint source hierarchy may remain useful for training losses and motion-reference reconstruction, but it is not the portable animator-control contract.

## Evidence

The existing real-rig observation suite was expanded from five BoneForge/Rigify fixtures to eight profiles:

- BoneForge control rig;
- generated Rigify basic and default humans;
- Rigify basic and default metarigs;
- behaviorally supported Mocap, Unity and Unreal imported humanoids.

The first expanded run exposed a finite-precision defect in the Unreal fixture. Composed calibrated rotations reached an orthogonality error of `2.05107127e-5`, just above the existing `2e-5` contract. The encoder now applies the nearest proper-rotation projection after finite-precision composition. The tolerance was not weakened. A focused test perturbs otherwise valid rotations within the input tolerance and verifies determinant-one, orthonormal output to `1e-12`.

The fixed-offset diagnostic then sampled the four declared poses for every profile and tested every semantic edge against one local offset derived at the first known pose. The maximum rigid-parent reconstruction error was `8.765059452834907e-7` body scales and the maximum relative edge-length change was `1.8709782095691125e-6`. The Unreal fixture produced both maxima; the other seven fixtures were exact to numerical precision.

`semantic_hierarchy_packet_v1.py` now converts the four known 17-joint world observations into:

- normalized root positions;
- 17 ancestor-local rotation matrices;
- one fixed local offset per semantic edge;
- explicit timing and context availability;
- a 105-value per-frame state (`3 + 17 * 6`);
- a measured world-space reconstruction error.

The packet reconstructs all observed rotations within `2e-10`, rejects semantic rigs whose edge motion exceeds `2e-4` body scales, and contains no model inference or hidden inbetween reads. The expanded Bforartists suite passes 15 assertions, including transformation invariance, rest-axis calibration, cancellation, failure recovery, source/action preservation, declared-frame reads, active-owner rejection, malformed rotations and non-rigid edge rejection.

## Evidence files

- `training/b4artists_ml/results/rig-packet-eight-profiles-v1-test_b4artists_ml_rig_observations.json`: preserved initial one-assertion failure.
- `training/b4artists_ml/results/rig-packet-eight-profiles-v2-test_b4artists_ml_rig_observations.json`: proper-rotation repair, 14 assertions pass.
- `training/b4artists_ml/results/real-rig-semantic-kinematics-v1.json`: per-profile fixed-offset diagnostic.
- `training/b4artists_ml/results/rig-packet-eight-profiles-v3-test_b4artists_ml_rig_observations.json`: final 17-joint packet contract, 15 assertions pass.
- `training/b4artists_ml/results/real-rig-task-packet-v1.json`: source-hashed checkpoint binding the failure, repair, diagnostic and final suite.

The Bforartists processes still return the existing `3221225477` access-violation code during shutdown after writing complete test reports. This evidence qualifies the assertions, not host shutdown stability.

## Current-worktree safety recheck

The 2026-09-14 current worktree keeps the pure temporal observation value and interpolation helpers importable without Blender while loading host-only modules only when a live rig is sampled. The standalone sampler now rejects every active B4ML workflow flag, a retained motion layer, and an active solver owner before reading frames. This closes a state-ownership gap in the research adapter without training or promoting a model.

`training/b4artists_ml/results/current-temporal-adapter-recheck-v1.json` records 24/24 passing Bforartists assertions with zero failures, errors, or skips: eight authored temporal math checks and sixteen real-rig observation checks across the eight declared profiles. `current-temporal-adapter-recheck-validation-v1.json` verifies the six bound source hashes and the fail-closed claim boundary. The host emitted its known shutdown-only `ucrtbase.dll` fault after writing the passing receipt; exact-package, learned-quality, independent animator, and Cascadeur claims remain false.

## Remaining limits

The fixtures do not establish arbitrary production-rig compatibility. Mixed IK/FK output, nonuniform scale, unusual rest hierarchies, reflected rigs, constrained imported controls, twist-distribution retargeting, layered NLA, finger articulation and quadrupeds remain outside this packet qualification. No temporal weights are bundled or promoted, and no learned-motion or Cascadeur parity claim changes.
