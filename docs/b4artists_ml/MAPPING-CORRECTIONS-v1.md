# Humanoid Mapping Corrections v1

Status: implemented on development 0.33 source; not packaged.

## Animator workflow

Select a recognized humanoid armature or one of its bound meshes, expand **Humanoid Mapping Corrections**, choose one of the twenty standard semantic roles, select an existing animator bone, and click **Apply Role**. These include the fourteen readiness roles plus spine.01, spine.02, chest, neck and both clavicles. The correction belongs to that armature object and is used by automatic pose capture, assisted posing, whole-body posing, rig-state snapshots, contact-aware cleanup, and Rig Mapping Diagnostics. **Clear Role** restores the detected mapping for the selected role. **Clear All Corrections** removes the complete override set, including corrupt or stale data that cannot otherwise be edited.

Corrections refine an existing humanoid animator-control adapter. They do not classify an unknown or deform-only skeleton, construct a rig, rename bones, change hierarchy or rest transforms, switch IK/FK, or make a quadruped eligible for humanoid tools. A correction identifies an animator-facing semantic control; it does not replace the generated rig's evaluated skeletal-joint adapter.

The saved JSON payload has an exact versioned schema and is bound to the detected adapter plus a SHA-256 signature of bone names, parents, connected flags, and deform flags. Proportion and rest-position edits are left to each workflow's existing geometric checks. Renaming, adding, removing, reparenting, connecting, or changing deform classification makes the payload stale. Every selected bone must exist as a pose bone, must avoid known deform/mechanism/organization/widget/tweak naming and reserved master/root controls, and every final semantic role must resolve to a distinct bone. Invalid, duplicate, oversized, corrupt, cross-family, or stale payloads fail before dependent workflow changes. Diagnostics identify the invalid state and leave Clear All available.

Mapping edits are disabled while an animation candidate, posing preview, contact job, flight job, secondary-motion job, cleanup job, or temporal job owns the armature. The operator changes only the versioned armature-object property and cached diagnostic/status UI. It does not move the armature or edit its action. Native Undo/Redo and `.blend` save/reload preserve the exact property.

## Verification

The focused Bforartists suite passes 11/11 tests. It covers BoneForge, generated Rigify Basic, generated Rigify Default, and an authored/imported Unity Humanoid FBX; verifies required and optional torso roles through capture, posing, whole-body mapping, diagnostics and the 20-role UI enum; checks save/reload and operator clearing; rejects nonexistent, case-variant structural, duplicate, unknown-role, corrupt, stale, deform-only, reserved-root and quadruped inputs; and proves rejected changes preserve the payload, pose, modes, action, and object transform. It also covers the coupled case where clearing one role would reintroduce a duplicate through the detected base mapping.

The generated-Rigify-Default foreground journey applies a Head correction, verifies the version-2 diagnostic report, proves native Undo removes it and Redo restores it, clears it through the UI operator, then completes the existing modal Solve, Escape recovery, Undo/Redo, and Keep lifecycle with source modes restored. The final panel screenshot was visually inspected with short Role/Bone labels in the narrow sidebar. Assertions finish before the independently isolated Bforartists 5.2 Alpha `ucrtbase.dll` shutdown fault; no clean-exit claim is made.

Evidence files:

- `training/b4artists_ml/results/mapping-corrections-v1.json` — 11/11 focused tests, SHA-256 `458e3bddab5e47bc43825d6b97743b9e260ca8283257bd55dacf1a9dd9347729`.
- `training/b4artists_ml/results/mapping-corrections-affected-final-v3-regression.json` — 138/138 affected tests across 11 suites with one runtime source hash set, SHA-256 `1d198b25d11482d032ba1d6b1e2ff67e8ae2b7eac6f2464e33afe68b5ed66d6b`.
- `docs/b4artists_ml/body-preview-ui-vmapping-corrections-v1.json` — foreground journey PASS, SHA-256 `567b3dcdf370150997ab7b6b07f2b66d762271100e38fe08ca60cf366f0cc86c`.
- `training/b4artists_ml/cache/body-preview-ui-vmapping-corrections-v1.png` — final narrow-sidebar screenshot, SHA-256 `a7e2dd17acbf97211a21d5c71c50a8220d55541f08a7fdabe642bbeb1c7a3a3b`.

## Routing and review boundary

The assignment was submitted to `hermes-agent-self-evolution/scripts/prime-code-execute.py` with explicit source, test, and documentation ownership. The managed runtime failed while launching its `uv` Python trampoline before parsing or lane emission, so there was no `actual_lane`, `actual_lane_reason`, or dispatch fingerprint to infer. The production authorization verifier also failed in the native Codex environment because its `rfc8785` dependency was absent. The existing active production policy was left unchanged and the signed adaptive authority was treated as unvalidated for this session. Work continued under the static native policy's bounded serial fallback. No parallel worker, adaptive reviewer, package, commit, merge, or push was used.

This feature is deterministic rig metadata and validation. It is not learned rig inference, automatic retargeting, motion generation, physics, production-rig generalization, or evidence of Cascadeur parity. Unknown/custom rigs still need a future deliberate adapter workflow, and actual production BoneForge/Rigify/imported characters need human validation.
