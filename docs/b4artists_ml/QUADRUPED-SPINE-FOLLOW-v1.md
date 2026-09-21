# Quadruped Head-to-Spine Follow v1

Status: implemented and verified on development 0.35 source; not packaged.

## Animator workflow

Generated Rigify cat, horse, and wolf **Quadruped Whole-Body Pose** previews now expose **Spine Follow** and **Neck Share** beside the existing Body, four-paw, and Head requests. Rotate the location-locked Head helper as before. Spine Follow selects how much of that Head turn should be carried below the Head control. Neck Share assigns that amount between the semantic Neck control and the semantic Chest control.

For a Spine Follow value f and Neck Share value n, Chest receives f(1-n) and Neck receives fn. The solver evaluates the real Rigify dependency graph: it writes Chest first, reevaluates Neck, writes Neck second, and finally corrects Head to the exact requested world orientation. The Body and four paw targets retain their existing bounded residual solve. A zero Spine Follow preserves direct Head-only behavior.

The settings are editable before starting and during a schema-3 preview. Changing either setting after Solve invalidates the solve signature, so Keep requires another Solve. **Keep as Pose Anchor** stores the resulting animator-control pose and restores the source. **Cancel** restores the source without an anchor.

This is deterministic semantic control distribution. It does not infer a natural neck curve, generate gait, use learned quadruped weights, or establish Cascadeur parity.

## Rig and safety contract

The workflow resolves the profile's semantic chest, neck, and head roles and verifies that they are distinct detected animator controls. It does not assume a fixed spine_fk count: generated cat, horse, and wolf have different lower-spine chains, while their high-level Chest and Neck controls provide the verified distribution interface.

Only controls with a positive requested allocation must be writable. Neck Share 0 supports Chest-only follow even when Neck is locked; Neck Share 1 supports Neck-only follow even when Chest is locked. A positively weighted control with a partial rotation lock, active constraint, or rotation driver fails before pose mutation. The existing rigid object-space, action, frame, rest-signature, IK/FK, helper ownership, source restoration, and Body/paw/Head validation remain active.

New sessions use payload schema 3 and bind the detected Chest/Neck mapping. Schema-1 Body/four-paw sessions and schema-2 direct-Head sessions remain recoverable with Spine Follow disabled. Their recovery UI hides the inapplicable sliders and labels the limitation. Invalid JSON and valid JSON with a non-object top level are normalized in the panel so recovery controls still draw.

## Verification

The focused Bforartists suite passes 8/8 tests. It covers:

- generated Rigify cat, horse, and wolf with exact Head, Chest, and Neck orientation checks;
- Body and four-paw pin preservation and exact Cancel restoration;
- zero-follow compatibility and Neck Share endpoint writability;
- locks, constraints, drivers, stale setting signatures, and atomic failure;
- schema-2 direct-Head recovery;
- schema-3 save/reload Keep;
- invalid and non-object panel payload normalization.

For the sampled three-profile request, Head, Chest, and Neck orientation residuals are zero. Maximum paw residuals are 1.91e-7 for cat, 5.42e-7 for horse, and 4.80e-7 for wolf, each below its scale-aware tolerance.

The original affected regression passes 79/79 tests across ten suites: Spine Follow, Head posing, prior quadruped posing, generated-quadruped adapter/interpolation, four-paw contacts, paw suggestions, contact visualization, cleanup, visible-state handling, and base registration/recovery. Its aggregate binds all 43 runtime Python source hashes. The later Pole Targets aggregate reverified this suite as part of an 85/85 affected regression on the current runtime source hashes.

The real-window generated-wolf journey starts and solves through the visible operator with Spine Follow 0.64 and Neck Share 0.72. The panel shows both controls, zero Head/Chest/Neck rotation residual, 2.11e-7 maximum paw error, and Keep/Cancel. The captured screenshot was visually inspected, and Cancel restored the source.

Evidence:

- training/b4artists_ml/results/quadruped-spine-follow-v1.json — 8/8 focused tests, SHA-256 5752c5dae383c8d5117b3a88d8a12efdbfd9c60dc6196478548a6a89de770db3.
- training/b4artists_ml/results/quadruped-spine-follow-affected-v1-regression.json — 79/79 affected tests, ten suite reports, and 43 runtime hashes, SHA-256 947a6c5c70f4d8843616c45597fb68fd54b6cf76616bf8c32137740776eb5cad.
- docs/b4artists_ml/quadruped-spine-follow-ui-v1.json — foreground journey PASS, SHA-256 96315625fc67815d91153a9bb742acf5d7afb0f6668ff3c38d6bf5292a370053.
- training/b4artists_ml/cache/quadruped-spine-follow-ui-v1.png — visually inspected real-window evidence, SHA-256 8842552f73dff5c78d5af100c278d40236cd2061f41e6dab2a302b387300b71e.

Every Bforartists process completed its assertions and evidence writes before the independently isolated Bforartists 5.2 Alpha ucrtbase.dll shutdown fault. Clean process exit remains unqualified.

## Routing and review

The assignment was submitted to hermes-agent-self-evolution/scripts/prime-code-execute.py. Its uv trampoline failed before lane evaluation, so it emitted no T0–T4 actual_lane or policy fingerprint. The owner-production verifier also stopped before harness, expiry, signature, and source-binding validation because the native environment lacks rfc8785. The active policy was read but not renewed or changed. Work used the static-native DEGRADED_NATIVE_CONTINUE serial fallback with one writer.

The serial read-only reviewer found zero-weight writability, legacy slider, and non-object JSON panel issues. Positive-weight preflight, schema-aware UI, payload normalization, and boundary tests resolved them. The final review returned PASS.

## Remaining scope

Automatic native Rigify Pole Vector matching and procedural gait-phase assistance are the next achievable 0.35 features. Imported/custom quadruped adapters, automatic contacts, quadruped balance and flight, learned quadruped posing or temporal motion, human animator assessment, packaging, milestone-wide validation, and equivalent Cascadeur comparison remain open.
