# Contact Interval Editing v1

Status: implemented and verified on development 0.34 source; not packaged.

## Animator workflow

Select a humanoid hand/foot contact or a generated Rigify quadruped paw contact. **Go Start** and **Go End** move the playhead to the exact fractional boundary without changing the contact or animation. Move the playhead to a new boundary and use **Set Start** or **Set End**. The same controls appear in both contact panels.

Set operations require the active interpolation candidate. They validate the new boundary against the candidate's priority-pose span and the complete set of enabled accepted or proposed intervals before changing the selected property. A start after the end, an end before the start, an out-of-range frame, or overlapping same-limb hold/blend influence is rejected atomically. Rejected/disabled rows and active animation jobs cannot be inspected or trimmed through these controls. The guard includes temporal interpolation, contact correction/suggestion, flight, secondary-motion, cleanup, body, posing, and quadruped jobs. Direct numeric fields remain available for deliberate editing and receive the same complete validation when contact correction runs.

The interval operator changes only the selected Start or End property and the status message. It does not edit the action, pose, rig modes, object transform, contact point, orientation, blend, strength, review decision, or any other interval. Native Undo/Redo reverses and restores the edit. Fractional boundaries survive `.blend` save/reload.

## Verification

The focused Bforartists suite passes 6/6 tests across a generated Rigify Default humanoid, BoneForge, and a generated Rigify cat. It covers fractional inspection and trimming, the shared humanoid/quadruped operator, candidate and job ownership, invalid ordering, same-limb overlap, disabled/rejected rows, source/candidate/pose/mode/object preservation, operator metadata, and save/reload.

The affected regression passes 70/70 tests across seven suites with one 42-file runtime source hash set. It includes existing humanoid contact correction, generated quadruped contact correction, contact review, cleanup, support analysis, and base registration/recovery coverage.

The real-window generated-Rigify-Default journey uses Set Start at frame 4.5, proves native Undo restores frame 2 and Redo restores 4.5, uses Go End to reach frame 10, and captures the actual narrow-sidebar controls. Assertions finish before the independently isolated Bforartists 5.2 Alpha `ucrtbase.dll` shutdown fault; no clean-exit claim is made.

Evidence:

- `training/b4artists_ml/results/contact-interval-edit-v1.json` — 6/6 focused tests, SHA-256 `5d22202c8e966e0aaa3e368c49804a5521292b7392f9ef941531872108d102d5`.
- `training/b4artists_ml/results/contact-interval-affected-final-v2-regression.json` — 70/70 affected tests, SHA-256 `7dce7e1b2ea74c3902dbb102b503a43b3c76cd0be703d7e5e02f110d931591ab`.
- `docs/b4artists_ml/contact-interval-edit-ui-v1.json` — foreground journey PASS, SHA-256 `c5f6b20ee0eb764a2011dfe58c93cb3d0bfb5d2543c241fa344488ab382475b4`.
- `training/b4artists_ml/cache/contact-interval-edit-ui-v1.png` — visually inspected UI, SHA-256 `61f3c0acacb8d910c2a0cdc7ce5739eb946652e2ee4ba14b6724b78f025c9c2a`.

## Routing and claim boundary

The assignment was submitted to `hermes-agent-self-evolution/scripts/prime-code-execute.py` with exact source, test, and documentation paths. Its `uv` trampoline failed before lane evaluation, so no `actual_lane`, `actual_lane_reason`, or policy fingerprint was emitted. The signed production consumer also remains unvalidated in this Codex runtime because `rfc8785` is absent. The active policy was not changed; implementation and review used the static native serial fallback.

This is deterministic contact authoring UX. It does not detect contacts, follow props or moving surfaces, improve the geometric solver, add collision, infer intent, add learned motion, or establish Cascadeur parity. Explicit hand-to-prop holds remain the next achievable 0.34 feature.
