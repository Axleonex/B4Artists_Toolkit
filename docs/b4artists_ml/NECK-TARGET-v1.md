# Semantic Neck Target v1

Status: implemented and verified in development 0.33 source. It is not included in the experimental 0.32.0 archive, and no 0.33 package has been created.

## Animator workflow

Start **Humanoid Whole-Body Pose**, expand **Pose Targets**, and use the semantic **Neck** row. Position and **Rot** start unchecked and can be enabled independently. Move the helper to request joint-3 position, rotate it to request evaluated skeletal Neck orientation, then run a single solve or Live Solve. The compact `Rot` label is used so the control remains readable in the narrow Bforartists sidebar; its tooltip retains the full Rotation description.

Reset restores the Neck helper's preview-start position and orientation without changing its toggles or current rig pose. Keep, Cancel, Escape, native Undo/Redo, save/reload and source-mode restoration use the existing whole-body lifecycle. Chest and Neck remain released by default, so starting a new preview does not add torso constraints unless the animator chooses them.

## Architecture and compatibility

Neck maps semantic joint 3 of the existing 17-joint representation through the verified adapter. Position uses the ordinary sparse target residual. Rotation compares the evaluated skeletal Neck frame and distributes the correction through verified writable spine controls. This constrains the existing pose proposal; it does not alter or retrain the bundled contextual network.

Controls version 5 adds the Neck row. Versions 1 through 4 retain their exact prior target rows and cannot accidentally read or author Neck state; restart an older saved preview to obtain the new helper. Invalid, replaced or reflected helpers and non-finite or incompatible transforms fail before mutation. Recovery also requires the current native-motion transform to match the saved preview-start frame with strict absolute tolerance, including at large world coordinates.

Focused tests exercise BoneForge, generated Rigify Basic and Default, Rigify Basic and Default metarigs, and an independently authored Unity-style FBX humanoid. They cover opt-in position plus rotation, independent toggles, Reset, Rigify Basic save/reload/Keep, legacy version-4 rows and reflected-axis rejection. A foreground generated-Rigify-Default journey covers the visible Neck row, modal solving, Escape, Undo/Redo, Keep and source-mode recovery.

## Evidence

| Artifact | Scope | Result | SHA-256 |
|---|---|---:|---|
| `training/b4artists_ml/results/neck-target-v1.json` | Six adapters, toggle semantics, Reset/reload/Keep and version/reflection rejection | 4/4 pass | `e5c11bb67da7c9e980dd0bb8d2bdc0cc74e30ae6476997ca48b11ef1388a97af` |
| `training/b4artists_ml/results/chest-orientation-v1.json` | Existing semantic Chest orientation compatibility | 3/3 pass | `32a6215c0f0f67a95c61cb5b94f3c83595ec1f8f0d110c31fa016369b5e7d941` |
| `training/b4artists_ml/results/chest-target-v1.json` | Existing semantic Chest position compatibility | 3/3 pass | `8bf223f853b1d821d84b9df722235fc6abb71b560e4d7d7f6075c4fbfcf3079f` |
| `training/b4artists_ml/results/body-controls-target-reset-v2.json` | Existing target controls after version-5 initialization | 8/8 pass | `b3a20ca43810fadd5f8c83699fa53ee8ef7693b1930dbe119611e19643f9a738` |
| `training/b4artists_ml/results/target-reset-v1.json` | Existing per-target Reset compatibility | 8/8 pass | `ece65e77606fdc5482cf7aa9531962d43e18dcb308f0517d27adba7dbd22190d` |
| `training/b4artists_ml/results/target-mirror-v1.json` | Existing semantic mirror compatibility | 7/7 pass | `1a9431e91e2a4f54c8375e7fa9e49f2d96c7d4bea15230c2adf59ec08087980d` |
| `docs/b4artists_ml/body-preview-test-v0.32.0.json` | Existing preview lifecycle; historical filename retained | 10/10 pass | `9e1ae97e8e36cce04743f54b4359a50add46b30977fa482b7d3c6eea0c22bcc4` |
| `docs/b4artists_ml/body-preview-ui-vneck-target-v1.json` | Rigify Default foreground modal/Escape/Undo/Redo/Keep journey | PASS | `e1fc16e9c76918766647b2ab4b7ed1d4ecd884fc85c5f508a6bd136149e74e80` |
| `training/b4artists_ml/cache/body-preview-ui-vneck-target-v1.png` | Screenshot from the passing foreground journey | Captured and inspected | `81b44a1de357cbd16ac080e3c12a23ff7065551939845a32ce34d35fa98b4e23` |

The six-adapter position error is at most `1.08e-4` body scales and orientation error is at most `3.47e-6` radians. The real-window Rigify Default journey reaches `7.47e-7` radians after 1,637 evaluations and 11.94 seconds of solver work. The affected Neck, Chest orientation, Chest position, Body Controls, Reset, Mirror, Context Preview, Joint Limits, Bend Limits and Pole Distance suites pass 67/67 methods; the base suite passes 33/33, for 100/100 current affected and base methods.

All assertions complete before the installed Blender 5.2 Alpha host's known `ucrtbase.dll` shutdown crash. Process exits are not described as clean.

## Execution record and claim boundary

Harness/profile: Codex workspace. Authorization risk tier: `workflow_scaffolding`. The required Prime preflight stopped in its configured `uv` trampoline with `entity not found` before emitting `recommended_lane` or `actual_lane`; neither lane is inferred. The execution-value policy SHA-256 was `74041cc3740f3165b7a3280583628c2fbe21b60b626d08045eb0560771492466`, and the active adaptive policy SHA-256 was `c0dce1c33ee9d164c51df0ceab2e8022e9e8a35ae98a0bb1f7c33c5e731502a2`. The tightly coupled runtime/UI/test/document packet continued serially under the recoverable pre-host-apply fallback, with one parent owning integration and zero lane escalations. The adaptive reviewer authority did not validate in this process, so review remains serial and career overlays neutral.

This is procedural rig projection around the existing learned pose proposal. It does not learn Neck motion, qualify learned inbetweening, or establish Cascadeur parity. No activation, package, commit, merge or push occurred.
