# Sphere Radius Fit v1

Status: development slice verified; package and milestone-wide gates remain open.

## Animator workflow

Choose a geometric object as **New Sphere Center** and click **Fit New Radius from Bounds** before adding it, or click **Fit Radius from Bounds** on an existing row. The operation replaces that explicit editable radius with a sphere that encloses the object's eight bounding-box corners around its origin.

With **Follow Radius Scale** off, fitting snapshots the current world transform so static nonuniform scale is included. With scale following on, fitting stores the local-space base radius and the existing solver multiplies it by the evaluated uniform scale at each solve frame. This avoids counting the current scale twice. The operation supports mesh, curve, surface, metaball and text bounds, uses native Undo/Redo, and changes only the chosen radius.

This is a setup helper. It does not turn the object's faces into a collision surface, compute a minimum enclosing sphere, follow later geometry edits or deformation, move the sphere center away from the object origin, or learn collider shape.

## Current evidence

- Focused Bforartists run: 5/5 tests pass for staged world-space fitting, scale-follow local-base fitting, independent list-row editing, native operator Undo/Redo, exact float32 enclosure, and atomic rejection of missing bounds, invalid indices, unavailable/degenerate geometry and an active workflow. Its five imported fixture dependencies are hash-bound. Report: `training/b4artists_ml/results/secondary-sphere-fit-focused-v1.json`, SHA-256 `c6f6bdcf3572aed5ae5174450bfcdbd825226c7ce7752866dc639b98bb7a0abf`.
- Affected regression: 192/192 tests pass across 15 suites on one frozen 44-file runtime. This includes the preceding animated-radius 15/15 path and all earlier selected-control physics paths. Report: `training/b4artists_ml/results/secondary-sphere-fit-affected-v1-regression.json`, SHA-256 `2c43ac50a1bfb97c6af1ee78ac734f258abff953c94d6d0b4334721dc92aadb7`.
- Foreground BoneForge journey: both staged radii are fitted from visible mesh bounds, added as one uniformly scaling and one static row, and used through modal and synchronous solve, native solve Undo/Redo, Restore Input, Keep and Restore Source. The 86 cooperative callbacks measured 10.91 ms p95 and 23.98 ms maximum. Python optimization is verified off; source and collider Actions pass the bounded Action/AnimData preservation digest. Evidence: `docs/b4artists_ml/secondary-sphere-fit-ui-v1.json`, SHA-256 `fe6717289e1fd61cc140c02f86a118c2af93f547d09b7ca74f485198862039bb`; screenshot SHA-256 `bfc5f4de2517a13efbd21c4d950a52171614a5089eabb710486e8e3a49b3adc1`.
- Implementation-checkpoint hashes: `secondary_motion.py` `e21e489b5f9ace4be0f6ad129e19f4e7873c0c039a2e87ef5b63ad2daa345145`; `ui.py` `4eaa960393c1503547f9e6cdeeaeb3a2afc32e016420d990d78d0402d73c89c4`; focused test `de07dd2e0d40ac1652bf911fc0e6225812273676080d3e5be251a57ca109ee61`; affected driver `a9052c4b0d07da7fd65b3d3bd082780613c2e9d37fd6de03b8870f1df4208740`; foreground driver `8db4a27b4fd6e02f687ba2e83b83970f6f874eae15695d71da3e0d98c5723ea6`. The successor Sphere Proxy from Bounds aggregate reruns this focused module at 5/5 on the current runtime; see `SECONDARY-SPHERE-PROXY-v1.md`.

The host completes assertions and writes each report before its known shutdown access violation. Clean shutdown is not claimed.

The frozen `releases/b4artists_ml_v0.36.0.zip` remains unchanged at SHA-256 `3a0423b632cdc0b279a43e45c58321d75833927fb4207d8a2b35d213e282e2e5`. This development slice is not packaged.

Arbitrary/deforming mesh collision, continuous collision, self-collision, coupled collision forces, learned motion and Cascadeur comparison remain open.
