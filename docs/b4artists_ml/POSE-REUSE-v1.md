# Reusable pose anchors v1

Status: implemented and verified in development 0.33 source. It is not included in the experimental 0.32.0 archive.

## Animator workflow

1. Capture a pose on the source frame.
2. Move the playhead to a different frame.
3. Click the duplicate icon beside the stored anchor.
4. Continue authoring anchors or generate a Pose Blending candidate.

When a rig has more than ten stored poses, use **Pose Page** to reach every anchor in the supported 128-anchor collection.

The operation copies the validated source payload to the current frame as another authored priority pose. It is useful for holds, repeated poses and timing changes. Reusing onto an existing anchor replaces that destination anchor. The rig does not jump to the copied pose and no action is created until the animator explicitly generates a candidate.

This is a same-armature workflow. It does not retarget poses, translate between different control layouts, save a global pose library or claim learned completion.

## Validation and ownership

Before changing the anchor collection, the operation validates the complete local anchor set:

- finite, distinct frames and the existing bounded preview range;
- matching armature rest signature, schema and rig-mode mapping;
- unchanged IK/FK and space properties;
- existing controls, rotation modes and writable channel locks;
- finite transforms and unit quaternions;
- at most 128 anchors and an aggregate serialized payload limit of 8 MiB.

An active pose, whole-body, quadruped or interpolation preview, including running whole-body motion generation, blocks reuse. A retained motion layer or NLA also blocks it. Invalid, oversized, over-count, ambiguous and stale payloads fail before anchor mutation. Serialization also completes before a destination entry is added or overwritten. The copied payload stays local to the armature object. Rig pose, object transform, current action, action slot, keyframe data and rig modes remain unchanged.

## Evidence

The focused Bforartists suite is `tests/test_b4artists_ml_pose_reuse_v1.py`. Eight tests pass:

- exact frame 1 to frame 5 reuse on BoneForge, generated Rigify Default, independently authored Unity Humanoid FBX and generated Rigify Cat;
- exact priority-pose reproduction after generating a candidate;
- unchanged rig pose, object transform, action data and modes;
- one-anchor reuse and destination overwrite;
- busy, missing, same-frame, range, malformed, deeply nested, non-finite extra-field, over-count, per-item oversized, aggregate oversized and ambiguous-anchor rejection;
- paging access to anchors beyond the first ten;
- operator execution and save/reload persistence.

Focused result: `training/b4artists_ml/results/pose-reuse-v1.json`, SHA-256 `e0f2230660a61e9deb4e388934c9282982edb8bef64c81d91cbc1cdebbb7a971`.

The unchanged preview lifecycle passes 10/10 tests. Its report SHA-256 is `9e1ae97e8e36cce04743f54b4359a50add46b30977fa482b7d3c6eea0c22bcc4`. The base suite passes 33/33.

Seven direct anchor-consumer regression module runs pass with no failures or errors: temporal projection 24/24, native contacts 13/13, temporal cooperative 19/19, authored cooperative 27/27, temporal runtime 27/27, smoothed contacts 7/7 and temporal private 28/28. These module totals include inherited/shared test classes where the modules expose them; they are recorded per run rather than claimed as a new unique-test total.

The generated-Rigify-Default real-window journey passes reuse, native Undo, native Redo, modal solve, Escape cancellation and final Keep. Report: `docs/b4artists_ml/body-preview-ui-vpose-reuse-v3.json`, SHA-256 `a8f8f4575de382e8e0963f01f2046b5d2bda2770f6760e35ee6884c50860bd17`. Screenshot SHA-256: `67c6a59be2b60919d69e40aa7c5d7ff8866128aa959d949869091c22baa49be7`.

All assertions complete before the installed Blender 5.2 Alpha host's known `ucrtbase.dll` shutdown crash. The process exit is not described as clean.

## Remaining 0.33 work

The separate scene-local Semantic Pose Asset now transfers verified sparse target requests across supported humanoid adapters; see `POSE-ASSET-v1.md`. It does not change this same-armature anchor workflow or transfer raw control poses. Finer head/spine shaping and bounded manual mapping corrections remain open. This procedural authoring shortcut does not advance learned temporal-motion or Cascadeur parity claims.
