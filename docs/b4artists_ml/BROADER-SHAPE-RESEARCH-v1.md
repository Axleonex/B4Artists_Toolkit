# Broader authored-motion continuity research

The 0.18.0 runtime and archive remain unchanged. Six new actual-rig references cover a reach/hold/return and a mechanical root-yaw transition on BoneForge, basic Rigify, and default Rigify. These are procedural skeleton fixtures, not learned motion or bound production characters.

## Contact-aware smoothing result

The previous body-smoothing -> contact correction -> final smoothing order passes the hand-hold cases but violates the 0.001-radian contact-orientation limit on all three turn cases; BoneForge also exceeds the 0.0002 limb-unit position limit. Failed results remain in `broader-shape-workflow-v1`.

The new research solver smooths its private corrected action before validation and checks quarter intervals. Its existing adaptive refinement then sees cubic-curve errors. Each turn passes after one refinement, with the original position/orientation limits and maximum four refinements unchanged. No failed candidate is published.

| Rig | Reference | Contact drift (limb units) | Contact rotation (rad) | Priority matrix error |
|---|---|---:|---:|---:|
| boneforge | reach_hold | 4.41693598e-07 | 0.000690533969 | 5.82076609e-11 |
| boneforge | root_yaw | 4.29447398e-05 | 0 | 8.94069672e-08 |
| rigify_basic | reach_hold | 7.02378388e-07 | 0 | 0 |
| rigify_basic | root_yaw | 3.43575603e-05 | 0.000690533969 | 1.1920929e-07 |
| rigify_default | reach_hold | 7.02378388e-07 | 0 | 0 |
| rigify_default | root_yaw | 3.43575603e-05 | 0.000690533969 | 1.1920929e-07 |

All six scenes pass 9,813 independent contact checks at 1,281 sample times per scene. A fresh process reproduces saved contact maxima exactly and checks authored priority matrices against a newly generated authored-pose preview. Keep/Restore and Discard preserve the original source and rig modes.

The revised contact solver also passes the original crouch/recover references on all three rigs, preserving contacts, priority poses and source animation. These three regression scenes are separate from the six new references.

## Local transition measurements

At the same 0.015625-frame derivative probe, maximum semantic-joint angular-velocity jumps change as follows. These local measurements do not establish full-sequence continuity, physical plausibility, or animator preference.

| Rig | Reference / authored frame | Baseline (rad/s) | Smoothed (rad/s) | Reduction |
|---|---|---:|---:|---:|
| boneforge | reach_hold / 9 | 2.15395 | 0.0623703 | 97.10% |
| boneforge | reach_hold / 12 | 1.89972 | 0.0554468 | 97.08% |
| boneforge | root_yaw / 11 | 0.0237549 | 0.00107362 | 95.48% |
| rigify_basic | reach_hold / 9 | 1.92944 | 0.0592391 | 96.93% |
| rigify_basic | reach_hold / 12 | 1.70776 | 0.0520208 | 96.95% |
| rigify_basic | root_yaw / 11 | 0.0552798 | 0.00222053 | 95.98% |
| rigify_default | reach_hold / 9 | 1.92944 | 0.0592391 | 96.93% |
| rigify_default | reach_hold / 12 | 1.70776 | 0.0520208 | 96.95% |
| rigify_default | root_yaw / 11 | 0.0552798 | 0.00222053 | 95.98% |

Four native lifecycle tests pass: failure during smoothing removes the unpublished copy; cancellation during cubic validation restores the input; a changed contact rejects without undoing the user edit; and successful correction preserves editable input and source recovery.

## Remaining work

Integrate the accepted ordering into an opt-in runtime path with explicit cancellation/rollback, contact metadata and UI behavior, then run regression and package checks. Preserve axis-angle/quaternion-sign rejection and adjacent-curve preservation. Wider animation, proportions, bound meshes, viewport usability, animator assessment and learned motion remain open. The full original goal is incomplete.

Independent review remains unavailable because its entry point fails before starting Python. Author inspection and native checks are recorded separately. The native host still reports its previously isolated shutdown access violation after completing assertions; clean process termination is not claimed.
