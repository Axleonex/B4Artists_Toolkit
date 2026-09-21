# Optional semantic Chest position target v1

Status: historical evidence for the original position-only development 0.33 slice. The current development source also supports optional Chest orientation; see `CHEST-ORIENTATION-v1.md`. Neither feature is included in the 0.32.0 package.

## Animator workflow

Starting Humanoid Whole-Body Pose now creates a Chest axis helper from semantic joint 2 of the existing 17-joint body representation. The Chest pin starts disabled so established pelvis, head, hand and foot solves keep their previous constraint set. Enable Chest under Pose Targets, move its helper, and solve to guide torso position while the existing rig adapter distributes the result through its verified controls.

At this checkpoint Chest was position-only: the panel labelled it `Position only`, exposed no Rotation or pole option, and rejected scripted attempts before pose mutation. Those statements and hashes describe the original controls-version-2 slice. Current controls-version-4 previews add optional evaluated Chest orientation through the separate workflow in `CHEST-ORIENTATION-v1.md`; Chest pole control remains unsupported.

The target uses the adapter's semantic body order. It does not infer a bone from its name. BoneForge, generated Rigify, Rigify metarigs and imported FK rigs keep their existing mapping and source-recovery rules.

## Compatibility and lifecycle

- New previews store `controls_version=2` and include the optional Chest helper.
- Version-1 previews continue to use their original six target rows and do not require a Chest item. The retained authentic 0.5.1 preview also remains keepable.
- Chest participates in the same target-strength, stale-request, cooperative cancellation, Live Solve, Undo/Redo, save/reload, Keep and Cancel machinery as other position pins.
- The original action, action slot, rig modes and source pose remain the recovery authority.

## Evidence

The final affected source run covers 45 tests across six distinct suites with zero test failures or errors:

| Evidence | Coverage | Result | SHA-256 |
|---|---|---:|---|
| `training/b4artists_ml/results/chest-target-v2.json` | Three focused workflows; six rig variants including independently authored Unity FBX | 3/3 pass | `8bf223f853b1d821d84b9df722235fc6abb71b560e4d7d7f6075c4fbfcf3079f` |
| `training/b4artists_ml/results/body-controls-v1.json` | Six rotations, four poles, save/reload, cancellation, stale edits and authentic 0.5.1 preview | 8/8 pass | `7659e2825d1dc582a85d5980ce59d5b43d499da3a948e760d769e8c05391a2cc` |
| `docs/b4artists_ml/body-preview-test-v0.32.0.json` | Whole-body preview lifecycle | 10/10 pass | `9e1ae97e8e36cce04743f54b4359a50add46b30977fa482b7d3c6eea0c22bcc4` |
| `training/b4artists_ml/results/joint-limits-chest-target-v1.json` | Control and skeletal limits on affected rigs | 9/9 pass | `dff51b62d49a148fd35f1894c89063e9e668d47c4ffd5861fcb55ad82deed71d` |
| `training/b4artists_ml/results/bend-limits-chest-target-v2.json` | Directional limits with pins, rotations and poles | 10/10 pass | `bc00b4c4592f0cfab49bccdfe97d8e36a1e801de78f599128d40012eb62bc0d6` |
| `training/b4artists_ml/results/joint-limit-presets-v1.json` | Previous 0.33 preset slice under the current source | 5/5 pass | `114eaf491ccd746f7d7608616de01e5a6cd4a68f31415ab6b77693bc73fcd79b` |

Focused Chest error is normalized by the session body scale. The worst observed value was `0.00010597` on the independently authored Unity FBX, below the `0.0002` pin gate. The other five fixtures ranged from `0.00000208` to `0.00006720`.

The real-window Rigify Default journey is `docs/b4artists_ml/body-preview-ui-vchest-target-v2.json` (`cf38a30fdb589fabfea7ffa0114bd9d957802f2b2ea4eeeb2baec750be611029`). It verifies the modal proxy solve, Escape restoration, Undo/Redo, Keep and source-mode recovery. Its inspected screenshot is `training/b4artists_ml/cache/body-preview-ui-vchest-target-v2.png` (`3a6875f235facf3aad18807a76dc51a73c9f9b18e69db59e505f9dc2ad834bdd`) and shows the unchecked Chest row with the `Position only` label.

Development checks caught and corrected an overconstraint when Chest initially started enabled, rotation-index assumptions in two older test fixtures, and a transient proxy-scene timing assertion. The failed UI timing run remains in `body-preview-ui-vchest-target-v1.json`; the failed bend run remains in `bend-limits-chest-target-v1.json`.

All Bforartists test processes wrote passing reports before the known Blender 5.2 Alpha `ucrtbase.dll` shutdown crash. Clean host shutdown is still unqualified.

## Claim boundary

The Chest position pin is an explicit geometric constraint applied around the existing contextual proposal. No model, weights or learned-motion claim changed. This document retains the evidence boundary at the time of the position-only slice; current Chest orientation evidence is recorded separately in `CHEST-ORIENTATION-v1.md`. Finer spine shaping, broader pole ergonomics, cross-rig pose assets, animator assessment and Cascadeur comparison remain open.
