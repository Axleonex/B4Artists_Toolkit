# Quadruped Head Orientation target v1

Status: implemented and verified on development 0.35 source; not packaged.

## Animator workflow

Generated Rigify cat, horse, and wolf rigs now start **Quadruped Whole-Body Pose** with six helpers: Body, four paws, and Head. Move Body and the paw helpers as before. Rotate the arrow-shaped **Head** helper to orient the detected semantic animator head control. Its location remains locked because this slice controls head orientation only. Disable the Head Rotation option to release that request.

**Solve Quadruped Pose** restores the captured source pose, applies the requested Head world orientation, then performs the existing bounded Body and paw residual solve. **Keep as Pose Anchor** captures the solved animator-control pose and restores the source. **Cancel** restores the source without an anchor. A changed target must be solved again before Keep.

This workflow is deterministic. The original Head target slice applies the requested orientation directly. The current development source can optionally distribute that request through semantic Chest and Neck controls using the separately verified **Quadruped Head-to-Spine Follow v1** extension. It does not infer head motion, generate gait, or use a quadruped learned model.

## Safety and recovery

The Head mapping must resolve to a detected animator control for the generated Rigify profile. Locked, constrained, or driven Head controls fail before preview creation or solve. Reflected, collapsed, nonuniform, or sheared rig space is rejected before helper creation and during recovery because world-orientation conversion requires a rigid frame.

The Head helper must remain owned by the active preview, unparented, location-locked, at its captured position, unit-scaled, and free of active constraints, actions, drivers, NLA strips, and delta transforms. Unsupported external ownership fails before the rig pose changes. These guards prevent a visible Head position from being silently ignored by the rotation-only solver.

The original Head slice introduced payload schema 2. Default current previews use schema 3 for the optional Spine Follow settings; opt-in Pole Targets use schema 4 while retaining the Head and Spine Follow request. Pending schema-1 Body + Four Paws, schema-2 direct-Head, and schema-3 Head-to-Spine previews remain recoverable without fabricating newer requests, and the panel labels inapplicable legacy controls. Source pose, action, action slot, IK/FK values, helper ownership, Cancel, Keep, native Begin-session Undo/Redo, and save/reload recovery are covered.

## Verification

The focused Bforartists suite passes 7/7 tests on the current development source. It generates Rigify cat, horse, and wolf rigs, rotates each semantic Head control, retains Body and paw pins, cancels back to the exact source, rejects locked/constrained/driven controls and unsupported rig spaces, rejects moved or externally controlled Head helpers, recovers schema 1, exercises native Undo/Redo, and keeps a solved preview after save/reload.

The measured Head orientation residual is zero for the three sampled requests. Maximum paw residuals are `1.27e-7` for cat, `4.84e-7` for horse, and `2.53e-7` for wolf, each below its scale-aware tolerance.

The affected regression passes 71/71 tests across Head posing, prior quadruped posing, four-paw correction and suggestions, quadruped adapter detection/interpolation, contact visualization, visible-state tracking, cleanup, and base registration/recovery. The aggregate binds all 43 runtime Python source hashes.

The real-window cat journey starts and solves through the visible operator, shows the Head Rotation row with the Body and paw controls, reports zero Head rotation residual and `2.67e-7` maximum paw error, captures the sidebar and helpers, then cancels and restores the source.

Evidence:

- `training/b4artists_ml/results/quadruped-head-v1.json` — 7/7 focused tests on current source, SHA-256 `c907524c2d7874e0cc0664b37e1c495bd4dc146348bd94ab14498e4fc44dd5fa`.
- `training/b4artists_ml/results/quadruped-head-affected-final-v1-regression.json` — historical 71/71 affected tests and 43 runtime source hashes for the original Head slice, SHA-256 `6573917fe041589e1516b8c4388b7511f955570ef96c12798f733c5d439a1902`.
- `docs/b4artists_ml/quadruped-head-ui-v1.json` — foreground journey PASS, SHA-256 `3f997b72b8b8f7170eb7c9cc689c6d18d99197af93450d9a4f66606571958e3b`.
- `training/b4artists_ml/cache/quadruped-head-ui-v1.png` — visually inspected real-window evidence, SHA-256 `a209563e58f8809a6c0b0c699ee0a3cd34906956e9a0b6f98c3a85e3be8f55bd`.

Every Bforartists process completed its assertions and evidence writes before the independently isolated Bforartists 5.2 Alpha `ucrtbase.dll` shutdown fault. Clean process exit remains unqualified.

## Routing and review

The assignment was submitted to `hermes-agent-self-evolution/scripts/prime-code-execute.py`. Its `uv` trampoline failed before lane evaluation, so it emitted no T0–T4 `actual_lane` or policy fingerprint. The owner-production verifier also stopped before harness, expiry, signature, and source-binding validation because the native Python environment lacks `rfc8785`. The active policy was read but not renewed or changed. Work therefore used the static-native `DEGRADED_NATIVE_CONTINUE` serial fallback.

One read-only serial reviewer found unsupported rig-space conversion, a silently ignored movable Head position, stale schema-1 UI text, and helper ownership bypasses through NLA and delta transforms. The final review passed after rigid-space guards, strict rotation-only helper invariants, schema-aware UI, expanded atomic tests, and native Undo/Redo evidence were added.

## Remaining scope

Lower-spine shaping targets, automatic native pole-mode matching, procedural gait-phase assistance, imported/custom quadruped adapters, automatic contacts, quadruped balance and flight, learned quadruped posing or temporal motion, human animator assessment, packaging, and equivalent Cascadeur comparison remain open. This slice establishes no parity or superiority claim.
