# Semantic target mirroring v1

Status: implemented in development 0.33 source; no 0.33 package has been created.

## Animator workflow

The expanded **Pose Targets** section now starts with **Mirror L to R** and **Mirror R to L**. One click copies the authored helper changes for both hands and both feet from the chosen side to the other side. The matching elbow and knee direction helpers are copied at the same time.

Mirroring copies changes relative to each helper's own preview-start transform. It reflects those changes through the verified humanoid sagittal plane, then applies them to the other side's preview-start transform. This retains the destination side's original proportion and asymmetry instead of replacing it with the source helper's absolute world transform. Position deltas, supported target rotation deltas and pole-position deltas are included.

The source helpers and the current rig pose do not change. Destination position, Rotation and direction toggles also remain unchanged. If copied channels are active, **Keep as Pose Anchor** requires a new solve. Changes to fully inactive paired helpers do not create a false solve requirement.

## Safety and compatibility

The reflection frame comes from the active rig adapter's saved semantic body axes and the native motion-layer rotation. It does not infer left and right from bone names. The operation supports current previews and compatible serialized controls-version 1 previews that contain saved helper origins and a motion transform on the existing BoneForge, Rigify and imported-FK humanoid adapters. Older records without that recovery metadata require a new preview.

Both source and destination helpers must retain session ownership. Parented, constrained, animated, driven or delta-transformed helpers are rejected before mutation. Malformed saved matrices and body axes are also rejected before runtime recovery. Native motion axes must have uniform scale and no shear because a Euclidean mirrored rotation is otherwise ambiguous.

A running manual solve or Live Solve must be stopped before mirroring. Any failure restores destination helper matrices, the prior rig pose, rig modes and status. Cleanup removes only the exact runtime session reconstructed by the operation; a foreign solver-session owner is preserved.

## Verification

Thirty-six affected Bforartists tests pass across five suites under the final source:

| Evidence | Coverage | Result | SHA-256 |
|---|---|---:|---|
| `training/b4artists_ml/results/target-mirror-v1.json` | Semantic position/rotation/pole reflection; both directions; BoneForge, generated Rigify Default and independently authored Unity-style FBX; serialized v1 recovery; atomic rejection including preservation of a foreign solver owner; stale-request behavior; UI wiring | 7/7 pass | `1a9431e91e2a4f54c8375e7fa9e49f2d96c7d4bea15230c2adf59ec08087980d` |
| `training/b4artists_ml/results/body-controls-target-mirror-v3.json` | Existing six-orientation/four-pole behavior, save/reload, cancellation and source restoration | 8/8 pass | `048b14e570a2b759c0c30d50c9e1a305794a93891a3bd76597f41c16c25c521b` |
| `training/b4artists_ml/results/target-reset-target-mirror-v3.json` | Existing exact Reset, ownership including preservation of a foreign solver owner, external-transform rejection, v1 recovery and stale-Keep behavior | 8/8 pass | `ece65e77606fdc5482cf7aa9531962d43e18dcb308f0517d27adba7dbd22190d` |
| `training/b4artists_ml/results/chest-target-mirror-v3.json` | Existing semantic Chest behavior across six rig variants | 3/3 pass | `8bf223f853b1d821d84b9df722235fc6abb71b560e4d7d7f6075c4fbfcf3079f` |
| `docs/b4artists_ml/body-preview-test-v0.32.0.json` | Existing whole-body lifecycle; filename retains unchanged 0.32.0 version metadata | 10/10 pass | `9e1ae97e8e36cce04743f54b4359a50add46b30977fa482b7d3c6eea0c22bcc4` |

The passing real-window generated Rigify Default journey is `docs/b4artists_ml/body-preview-ui-vtarget-mirror-v4.json` (SHA-256 `0edd58879c83211364689f48a92e69e220e99a0e03523e16681ad2f58f69a989`). It invokes semantic mirroring, runs the proxy-backed modal solve, cancels a repeat solve with Escape, performs Undo/Redo, keeps the anchor and restores source modes. The inspected screenshot is `training/b4artists_ml/cache/body-preview-ui-vtarget-mirror-v4.png` (SHA-256 `99b06f0fbeb532ae59359b160be436062918a4056cf8abed4a13b53127ce6619`) and visibly places both mirror actions above the target rows.

The first real-window run used a deliberately displaced two-hand request that the ordinary solver rejected at a normalized pin error of `0.0236652`; its report is retained as `docs/b4artists_ml/body-preview-ui-vtarget-mirror-v1-failed.json` (SHA-256 `3bbf6590dca83f7b0abd642806c63ae698d012784d1b10a9f91197f18a430c3b`). The v2 journey passed but exposed that the buttons were below the visible target list. The v3 layout moved them to the top; v4 repeats that journey against the final ownership-fixed source. An initial focused run also caught a pre-depsgraph source-matrix assertion in the test fixture; the final report uses evaluated matrices.

Bforartists 5.2 Alpha writes each passing report and then still exits through the known `ucrtbase.dll` shutdown fault. Test success and clean process shutdown remain separate claims.

## Claim boundary

This is deterministic helper reuse. It does not mirror an existing solved animation, infer intent, add a learned model, improve learned pose quality, or establish Cascadeur parity. Chest orientation is now recorded separately in `CHEST-ORIENTATION-v1.md`; finer spine shaping, broader pole ergonomics, cross-rig pose assets, bounded mapping corrections, independent animator assessment and matched Cascadeur evaluation remain open.
