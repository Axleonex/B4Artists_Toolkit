# Per-target Reset Helper v1

Status: implemented in development 0.33 source; no 0.33 package has been created.

## Animator workflow

Every active Humanoid Whole-Body Pose target row now has **Reset**. The action restores only that target helper to the transform created at the start of the preview. For hands and feet it also restores the associated elbow or knee direction helper. The position-pin, Rotation and direction toggles remain as the animator set them.

Reset changes helper objects only. It does not rewrite the current rig pose, source action, action slot, rig modes, anchors or learned-model data. If the restored request differs from the last solved request, **Keep as Pose Anchor** continues to reject it until **Solve Whole Body** completes again.

A running manual solve and Live Solve must be stopped before Reset. Missing, replaced, foreign-session, malformed and unknown targets are rejected before any selected helper is changed. Controls-version 1 previews continue to use the original six target rows and can reset those helpers without requiring Chest.

## Implementation boundary

This is a procedural preview usability control around the existing hybrid pose proposal and geometric projection. It does not add learned pose or motion capability, infer animator intent, improve model quality, or establish Cascadeur parity.

The implementation uses the active verified rig adapter and semantic target row. It does not guess a bone from its name. Target orientation returns to the session-start orientation only where that semantic target already supports Rotation. Chest remains position-only.

## Verification

Twenty-nine affected Bforartists tests pass across four suites:

- training/b4artists_ml/results/target-reset-target-mirror-v3.json (SHA-256 ece65e77606fdc5482cf7aa9531962d43e18dcb308f0517d27adba7dbd22190d): eight focused tests. They cover exact evaluated transform restoration, toggle preservation, rejection of parented, delta-transformed, constrained, driven and animated helpers, atomic ownership rejection, preservation of a foreign solver-session owner, malformed-metadata pre-validation, running-solve and Live Solve refusal, stale-Keep protection, serialized controls-version 1 recovery and exact UI row binding. The transform workflow runs on BoneForge, generated Rigify Default and an independently authored Unity-style FBX rig.
- training/b4artists_ml/results/body-controls-target-mirror-v3.json (SHA-256 048b14e570a2b759c0c30d50c9e1a305794a93891a3bd76597f41c16c25c521b): eight existing orientation/pole, reload, cancellation and source-restoration tests.
- training/b4artists_ml/results/chest-target-mirror-v3.json (SHA-256 8bf223f853b1d821d84b9df722235fc6abb71b560e4d7d7f6075c4fbfcf3079f): three existing semantic Chest tests across six rig variants.
- docs/b4artists_ml/body-preview-test-v0.32.0.json (SHA-256 9e1ae97e8e36cce04743f54b4359a50add46b30977fa482b7d3c6eea0c22bcc4): ten existing whole-body lifecycle tests from current development source. The filename retains the add-on's unchanged 0.32.0 version metadata.

The passing real-window journey is docs/b4artists_ml/body-preview-ui-vtarget-reset-v5.json (SHA-256 87623ff1b6b20812bdb0b8bef98ba20892e6c467bdb98ed1d76d1c462fa3f91c). It invokes the Reset operator on generated Rigify Default, runs the proxy-backed modal solve, cancels a repeat solve with Escape, performs Undo/Redo, keeps the anchor and restores source modes. Its screenshot is training/b4artists_ml/cache/body-preview-ui-vtarget-reset-v5.png (SHA-256 ff351eb09717595db92728a1514f5fb8b2277b98016d9c29a7b2742fed9027a4); the target rows visibly include Reset. This is automated interface and lifecycle evidence, not independent animator usability or pose-quality review.

The earlier UI attempts remain as evidence: v1 failed because it omitted Bforartists' required event-simulation flag, v2 failed because it compared Reset with an already-authored goal rather than the recorded preview-start origin, and v3 passed before the serial correctness review. The reviewer-fixed v4 journey superseded v3; v5 repeats it against the final ownership-fixed source.

Bforartists 5.2 Alpha writes each passing report and then still exits through the known ucrtbase.dll shutdown fault. Test success and clean process shutdown remain separate claims.
