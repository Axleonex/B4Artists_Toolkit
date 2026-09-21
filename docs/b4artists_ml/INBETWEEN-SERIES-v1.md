# Procedural Inbetween Series v1

Status: verified development source in 0.37.0. This feature is newer than the frozen 0.36.0 package.

## Animator workflow

Select a supported armature with two or more compatible Pose Blending anchors, then place the playhead strictly inside the interval to expand. Click **Procedural Inbetween Series**, choose one to eight inbetweens, and confirm. The tool creates editable priority-pose anchors at evenly divided positions between the original interval endpoints.

Each new pose samples the interval that existed before insertion. It uses the destination pose's effective easing, Breakdown Bias, Departure Hold, and Arrival Hold, including a destination override when present. This avoids repeatedly inserting Breakdown Poses and changing the interval after every insertion.

The original source Action is not edited. Existing anchors, including their names and serialized payloads, remain exact. New anchors intentionally start without incoming timing metadata, so later transitions into those anchors use ordinary destination-owned timing behavior. Native Undo removes the complete series as one operation, and Redo restores it.

## Bounds and failure behavior

- Count is an integer from one through eight.
- The resulting collection may contain at most 128 anchors and must remain within the existing serialized-payload limit.
- Proposed frame values are rounded to Blender's RNA float storage before any mutation.
- Stored frames must remain interior, unique, separated by more than the anchor ambiguity tolerance, and within one percent of the ideal interval step. A high absolute frame range that would produce visibly uneven float32 spacing is rejected.
- Active preview/generation work, a retained Native Motion Layer, or NLA strips reject the request before mutation.
- Every payload and frame is prepared before the first collection write. A write failure removes all newly appended anchors in reverse order and restores the prior status.

## Verification

`training/b4artists_ml/results/inbetween-series-v1.json` records 8/8 focused tests on Bforartists 5.2.0 Alpha. The tests cover one- and eight-pose numeric oracles, destination timing with holds, representable fractional frames, high-frame collapse and uneven-spacing rejection, hostile counts, collection and payload limits, busy-state rejection, forced partial-write rollback, operator execution, and save/reload. SHA-256: `1586a2b3c1b73cc16ee989aeb4232c7fef8461bfcd2c648c00573198861905f5`.

`training/b4artists_ml/results/inbetween-series-affected-v1-regression.json` binds 81/81 passing tests across seven affected suites to one 44-file runtime source set. SHA-256: `4faf57f1b0cc71ade2f53014e74f3bac27ededb5b9e8289654296e4fc4b9239c`.

`inbetween-series-ui-v1.json` records a foreground dialog/operator journey. It creates three anchors, proves the two existing anchors remain byte-identical, removes and restores the whole series through native Undo/Redo, previews the generated midpoint, discards the candidate, and verifies the source Action digest throughout. Report SHA-256: `5f36a65c152feda375e302ddc6ec208f409020fa9430885d1f16a1add3eb0170`. Screenshot SHA-256: `964d39abeb83a3d22affc0a8b023b975c0864f9570f85e918cb233b43b09e9be`.

The host completed every assertion before its known shutdown access violation. This evidence does not label shutdown as clean.

## Claim boundary

Procedural Inbetween Series is deterministic pose sampling. It does not infer intent, learn motion style, generate unseen trajectories, solve balance or physics, or qualify Cascadeur parity. It reduces repetitive authoring while the separate learned temporal and comparison requirements remain active.
