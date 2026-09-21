# Observed-motion-conditioned learned trajectories v15

Research component correction verified; full learned-motion quality remains rejected. Runtime/package 0.16.1 and the bundled pose models are unchanged. The full standalone/Cascadeur comparison goal remains incomplete.

## Correction and prospective experiment

The preceding models could invent motion from identical observed poses. V15 scales each semantic joint's learned positional correction by observed endpoint displacement plus optional half-duration times incoming/outgoing context speed. Rotation6 corrections use the analogous matrix chordal movement. Missing context contributes nothing, there is no positive amplitude floor, and the temporal basis uses unit duration. This teaches relative trajectory shape while guaranteeing zero correction when observed motion is zero. Gradients include the same channel scaling; no labels are divided by small amplitudes and no rejected model is clipped after validation.

The four neural configurations and training-only catalog-group folds remain as frozen in v14. Trial 1 (64 hidden units, regularization 0.0001, forty epochs) wins excluded-group selection. The final full-training model is saved and hashed before validation is loaded. All original projected baseline metrics reproduce exactly. Final learned SHA: `efacc156fc3e86e81278b5e0d5a012b9c8adf41c5f2c6318c66fae2f22b16e6f`.

An independent complete rerun reproduces all 18 NPZ artifacts and every non-runtime report field exactly. No new data or confirmation was accessed. Validation remains historically observed, and catalog groups are not asserted to be independent actors.

## Stationary preservation

All 186 controlled stationary-observation cases now equal their procedural baseline exactly, with no learned correction. Reported point drift versus the repeated pose is at most 2.49e-16 and rotation drift 9.38e-16 radians, arising from baseline floating-point reconstruction. The prior neural model's maximum normalized point drift was 2.343 in the same diagnostic.

Nine new tests cover explicit/compressed loss and gradients, actual hidden-feature learning, reproducibility/serialization, exact priorities, stationary preservation, continuous near-zero behavior, masked context, individually stationary joints and equal endpoints with nonzero surrounding velocity. Together with preserved neural, trajectory, projection, observation and kinematic suites, all 51 focused native cases pass.

The exact trained candidate also passes eight ordinary moving-pose rig/action/source-recovery checks. A separate sixteen-case actual-host stationary test covers all eight profiles with and without stored stationary context: BoneForge, basic/default generated Rigify, basic/default metarigs, Mocap, Unity and Unreal. It checks every generated world-position and orientation-matrix sample, editable candidate creation, Discard and source restoration. Both-context cases include four stored priorities. Maximum observed position component drift is 4.64e-6 and rotation-matrix component drift 5.68e-6, within the existing 2e-5 host numerical tolerance. All sixteen sources are restored. These checks establish the bounded stationary behavior, not general multi-priority learned-animation usability.

## Comparative quality still fails

| Metric | Ratio to best projected control | Existing limit |
|---|---:|---:|
| Position | 0.99857 | <=0.95 |
| Rotation | 1.07754 | <=1.02 |
| Velocity | 1.08824 | <=1.05 |
| Acceleration | 1.16021 | <=1.05 |
| Worst cohort position | 7.27210 | <=1.1 |

Position error 0.09342491 is about 0.14% better than the best projected position control, short of the required 5% improvement. Endpoint and physical-edge invariants pass. The procedural Hermite control still wins the combined position/rotation score. No new temporal model is bundled or offered as a qualified workflow.

Stationary preservation is a real improvement over v14, but transfer, rotation and continuity remain weak. The current correction envelope preserves priority values while allowing learned changes to boundary velocity. Next, prospectively test a representation that also preserves the velocity implied by known surrounding poses, with a contextual baseline and a correction envelope whose first derivative vanishes at the priorities. Verify derivative/priority/stationary invariants independently, use the same training-only design selection, and retain all original projected quality gates. This is a testable next step, not a claim that it will solve every failure or remove the need for broader data/physics/animator evidence.

## Evidence and limits

Under `training/b4artists_ml/`: `results/conditioned_trajectory_v15/`, `results/conditioned_trajectory_v15_repeat/`, `results/conditioned-trajectory-reproduction-v15.json`, `results/stationary-anchors-v15.json`, `results/conditioned-trajectory-native-v15-regression.json`, `results/conditioned-trajectory-host-v15.json`, and `results/stationary-trajectory-host-v15.json` with their process reports.

Bforartists again exits with its previously observed shutdown access violation 3221225477 after assertions. Host lifecycle remains failed. Ordinary and stationary host checks overlapped, so their timings are not comparative performance evidence. Existing 303 native / 110 offline / two packaged-window checks apply to unchanged runtime/package bytes and were not rerun here.

No install, release, commit or push occurred. Ghost Tool and Anim Assist remain unchanged. Learned multi-priority/partial-body/style/contact workflows, physics/refinement, production rigs/quadrupeds, rights, responsiveness/resources, connector and independent animator/Cascadeur comparison remain original requirements. No full implementation milestone or parity is credited for this research component.
