# Semantic Pose Asset v1

Status: implemented and verified in development 0.33 source. It is not included in the experimental 0.32.0 archive.

## Animator workflow

1. Start Humanoid Whole-Body Pose on a supported humanoid.
2. Arrange the eight semantic targets and choose the active position, Rotation, elbow/knee direction and pole-distance requests.
3. Solve Whole Body. After the solve succeeds and no target has changed, click **Save Solved Pose** under Pose Targets.
4. Start a controls-version-5 whole-body preview on another supported humanoid in the same scene and click **Apply Pose**.
5. Solve the applied request, inspect the result, then Keep as Pose Anchor or Cancel Preview.

The scene stores one compact asset. Apply Pose reconstructs the saved target and pole deltas in the destination rig's verified body frame and body scale. It updates helpers and their request flags without moving the armature, editing the action or changing rig modes. Applying always invalidates the preceding solve signature, including when the resulting helper layout is unchanged, so Keep requires a successful solve of the applied request.

## Representation and validation

The versioned `semantic_target_delta_body_v1` payload contains all eight semantic labels in canonical order. Each row records a normalized position delta, position pin, body-frame orientation delta and orientation pin. Hand and foot rows also record an elbow/knee direction-helper delta, direction pin and normalized pole distance. The source adapter profile is diagnostic metadata. `learned=false` keeps the procedural boundary explicit.

Save requires a stopped whole-body preview at controls version 5, an unchanged verified solve, the original native motion-layer transform and owned, unparented, unconstrained, undriven helpers. Apply accepts only the exact schema, canonical labels, Boolean flags, unit quaternions, finite bounded vectors, a pinned Pelvis position and supported rotation requests. Pole rows have an exact schema and a distance from 0.1 to 4 body scales. The serialized scene value is capped at 65,536 characters.

Validation and transform construction complete before any helper changes. A failed application restores target matrices, pole matrices, toggles, pole distances, rig pose, rig modes, preview payload and status. A successful application leaves the rig pose and source animation unchanged until the animator explicitly solves.

## Compatibility and evidence

The focused Bforartists suite is `tests/test_b4artists_ml_pose_asset_v1.py`. Five workflows pass:

- one verified BoneForge source request applies with exact normalized semantics to BoneForge controls, generated Rigify Basic and Default, Basic and Default human metarigs, and an independently authored Unity Humanoid FBX convention;
- BoneForge to generated Rigify Basic applies, solves, survives save/reload and keeps as an editable anchor;
- unsolved capture plus malformed, oversized, wrong-schema, empty-profile, unpinned-Pelvis, non-finite, duplicate-label and unknown-field payloads fail without partial changes;
- the Save and Apply operators plus the scene property survive save/reload.
- cold-runtime old-preview and deep-invalid rejections preserve pose, modes, helpers, payload, status and owner state; successful cold Apply preserves the rig and releases its temporary recovered owner.

Focused result: `training/b4artists_ml/results/pose-asset-v1.json`, SHA-256 `dd062c94b9dae895484d43f2273efb9f0ac97388be6096c6f4abf1d1e008e6fe`.

The existing Neck, target Reset, target Mirror, body controls, pole distance and whole-body preview suites pass 42/42 tests. The base suite passes 33/33. These are direct module totals from the final source runs; they are not a full 0.33 release regression.

The generated-Rigify-Default foreground journey invokes Save Solved Pose and Apply Pose, verifies the helper delta, completes the modal solve, cancels a repeat solve with Escape, performs native Undo/Redo, then Keeps while restoring source modes. Report: `docs/b4artists_ml/body-preview-ui-vpose-asset-v1.json`, SHA-256 `e4ce7ee7b7d2aa30b1638b464404062c69d7b50b7bf3a10d0b042f2824117ec5`. Screenshot: `training/b4artists_ml/cache/body-preview-ui-vpose-asset-v1.png`, SHA-256 `2c2cd9f8403361e891c2b6a7faa3680e621a5278b3f0991c2168f1306a4dfdee`.

All assertions complete before the installed Bforartists 5.1.0 / Blender 5.2 Alpha host's independently isolated `ucrtbase.dll` shutdown crash. The process exit is not described as clean.

## Claim boundary

This is deterministic semantic target-request transfer. It is a single scene-local slot, not a global asset browser or external interchange format. It does not transfer raw control transforms, deform bones, a complete authored pose, animation curves, contacts, timing or character style. Destination quality still depends on the existing rig adapter and whole-body solver, and production characters outside the tested adapters remain unverified. It adds no model or weights and does not advance learned temporal motion, independent animator quality or Cascadeur parity claims.

Bounded manual mapping corrections are now implemented and verified in development 0.33 source. Practical Contact Expansion is the next achievable-first slice. The deferred lower-Spine target still requires coupled pelvis/spine parameterization documented in `SPINE-TARGET-v1.md`.
