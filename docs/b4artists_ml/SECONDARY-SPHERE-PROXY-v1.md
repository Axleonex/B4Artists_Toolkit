# Sphere Proxy from Bounds v1

Status: development slice verified; package and milestone-wide gates remain open.

## Animator workflow

In Secondary Motion, enable **Collision**, choose **Sphere**, and set **Sphere Center / Bounds Source** to a mesh, curve, surface, metaball, or text object. Click **Create Bounds Proxy**. B4Artists Machine Learning snapshots the object's current world-space bounding box, creates an unparented Empty sphere at the bounds center, rounds its explicit radius upward so all eight corners remain enclosed after Blender float storage, and adds the new proxy to the collider set.

The source geometry can be parented because it is used only to calculate the snapshot. The generated collision object is deliberately unparented, has no constraints or animation, and remains an ordinary editable Empty. Creation resets the new row to static center and radius behavior. Native Undo/Redo removes and restores the proxy, its collider row, and the staged settings together. The source object and its geometry are not changed.

This is procedural setup assistance. It does not turn faces into collision geometry, find a minimum enclosing sphere, follow later geometry edits or deformation, infer anatomy, or satisfy learned-motion or Cascadeur-parity requirements.

## Current evidence

- Focused Bforartists run: 5/5 tests pass for offset-origin world-bounds centering, upward-rounded corner enclosure, parented source geometry, unparented proxy output, source preservation, native operator Undo/Redo, full-set rejection, and atomic invalid/busy-source rejection. The four transitive fixture sources are hash-bound. Report: `training/b4artists_ml/results/secondary-sphere-proxy-focused-v1.json`, SHA-256 `697df5e75b6f1dfa0f125f023ef868f0ae0a94abe8218c18dd61f1b7c58a81d0`.
- Affected regression: 197/197 tests pass across 16 suites on one frozen 44-file runtime, including Sphere Radius Fit 5/5, Animated Sphere Radius 15/15, and every earlier selected-control physics path. Report: `training/b4artists_ml/results/secondary-sphere-proxy-affected-v1-regression.json`, SHA-256 `d8c134bcab97f39a9bd23c84cbcaeb3f5bfbfc0cc038125be63faff246bb98fb`.
- Foreground BoneForge journey: the real operator creates a proxy from offset local bounds, proves creation Undo/Redo, displays the readable **Create Bounds Proxy** control and generated row, completes modal and synchronous solve, proves solve Undo/Redo, Restore Input, Keep, and Restore Source. The 86 cooperative callbacks measured 9.45 ms p95 and 17.03 ms maximum. Python optimization is off; source Action and bounds geometry remain unchanged. Evidence: `docs/b4artists_ml/secondary-sphere-proxy-ui-v1.json`, SHA-256 `1b4ed2d17a33fc9abf833aef6b706b31c1d4f08195e586ab4ea683479d7d7580`; screenshot SHA-256 `e685aeaeb441aa0d4bdb4edbb0a9a1caa806495d2ed0a20efa8c616a2fb8bfa8`.
- Current source hashes: `secondary_motion.py` `cf8f9b6c4ef9546d54ad57b0d10d16dd19bba6efb88f6f9f2d9d1fec82b56186`; `ui.py` `7b5f97671c2c32872dae8857505df0b3086f126b02b1924fdb0896618647ca51`; focused test `6b7ef2f60c725a2c012514d6dc1b96055dc2edc09a378633e28673f23727988e`; affected driver `6eb43199aa7e6ae27a1b32e34aebc7bd307302f4ca9569e21de8a707b6410a46`; foreground driver `32cac08b6f48b6202818ff6c7a4f149c884404bad50a58e818c73d6ee2b96101`.

The host completes assertions and writes each report before its known shutdown access violation. Clean shutdown is not claimed.

The frozen `releases/b4artists_ml_v0.36.0.zip` remains unchanged at SHA-256 `3a0423b632cdc0b279a43e45c58321d75833927fb4207d8a2b35d213e282e2e5`. This development slice is not packaged.

Arbitrary/deforming mesh collision, continuous collision, self-collision, coupled collision forces, learned motion and Cascadeur comparison remain open.
