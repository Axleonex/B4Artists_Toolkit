# Pole Bend Status v1

Status: implemented and verified in development source as a read-only extension of the humanoid Align/Flip/Distance workflow.

## Animator workflow

In **Humanoid Whole-Body Pose**, expand **Pose Targets**. Each supported Hand and Foot pole row now reports a compact **Current** status beneath its distance control:

- `aligned` means the helper points along the current evaluated elbow or knee bend plane.
- `opposite` means it points to the opposite side, matching the existing Flip Side operation.
- `off-plane` means the helper is valid but does not currently request either side within the five-degree display tolerance.

The status is informational only. It does not enable the pole, move the helper, solve the rig, change the source Action, or alter the saved requested distance. Align Bend, Flip Side and Set Distance remain the explicit editing actions.

## Contract and compatibility

The status reads the existing semantic 17-joint limb, the owned pole helper and the saved native-motion transform. It uses the same frame invariant as the editing actions and fails closed when the helper, saved frame, rig or bend direction is invalid. A nearly straight limb is reported as unavailable rather than being assigned a misleading side. No solver residual, iteration budget or acceptance tolerance changed.

The focused Bforartists suite covers BoneForge, generated Rigify Basic/Default, both Rigify metarigs and an independently authored Unity-style FBX humanoid through the existing Align suite. Its UI helper test verifies that the label is actionable and read-only while the source pose remains unchanged.

## Evidence

| Artifact | Scope | Result | SHA-256 |
|---|---|---:|---|
| `training/b4artists_ml/results/pole-align-v1.json` | Existing six-adapter Align suite plus aligned/opposite/off-plane status and UI-label checks | 6/6 pass | `33b126222438c35ce513139b2715b4786af9c9b633ee1b3f1d5cca41b7f86957` |
| `training/b4artists_ml/results/pole-status-affected-v1-regression.json` | Pole Align, Flip, Distance, Body Controls, Context Preview and Base suites against the status-enabled source | 67/67 pass | `405c5b086f171d5ddef62ee24921f58a8919a4df05ac25eeb6034061eae2cf48` |
| `training/b4artists_ml/results/pole-status-shared-v1-regression.json` | Shared per-target Reset and Mirror suites against the status-enabled source | 15/15 pass | `f16d5db1008fb353139c7d419070146bed83b2e3ba1e6eab656ae53a19a6992e` |
| `b4artists_ml/body_preview.py` | Read-only semantic status and saved-frame validation | source recorded | `2bb04693cd77302bc6849e079a624cdddeed7f16d6b82a1669b758c7244d1dcb` |
| `b4artists_ml/ui.py` | Compact read-only status label in the humanoid Pole Targets panel | source recorded | `70418b80fd5f26e3c60416685ed8650a434d4f1f9f40e1ebe12606df563a972d` |
| `tests/test_b4artists_ml_pole_align_v1.py` | Status geometry, UI wiring and source-preservation assertions | source recorded | `036bb6953ae6259d2c4481429c3ff42b77fee955a6e6f08a4c4f7911354be281` |

The assertions complete before the known alpha-host `ucrtbase.dll` shutdown access violation; the host exit is therefore recorded as shutdown-only, not clean.

## Claim boundary

Pole Bend Status is procedural animator feedback. It does not infer intent, learn motion, qualify temporal generation, establish human usability, or establish Cascadeur parity.
