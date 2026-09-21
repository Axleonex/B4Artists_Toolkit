# Quadruped adapter 0.27.0

Version 0.27.0 begins the second character-family track after the passing humanoid procedural slice. It adds an explicit `quadruped_v1` semantic schema for the Rigify cat, horse, and wolf conventions used by BoneForge's quadruped group.

Generated Rigify cat, horse, and wolf rigs now resolve before the overlapping humanoid Rigify signature. Their pelvis, chest, head, four upper/lower/foot/toe limb chains, spine, tail, FK controls, and known IK targets are separated from `DEF`, `MCH`, `ORG`, visual-widget, and tweak bones. Cat, horse, and wolf metarigs are also recognized. Unknown rigs report an `unknown` family instead of being described as humanoid.

The qualified workflow is deliberately bounded. On all three generated fixtures, the add-on captures two full poses, creates and reviews a nine-frame pose-blending candidate, reproduces both priority poses, preserves the original source action, and discards the candidate cleanly. Humanoid assisted posing, whole-body motion, contact, and flight paths reject the quadruped schema before changing the rig. The panel labels quadruped mode, leaves pose capture and Pose Blending available, and disables those humanoid-only controls.

The exact 0.27.0 source passed 474 tests in 50 suites with one runtime hash set. The installable archive passed 34 focused exact-package tests with outbound Python calls denied, including actual Rigify generation for cat, horse, and wolf. The package is `releases/b4artists_ml_v0.27.0.zip`, 311,900 bytes, SHA-256 `3a0415ab5a8a2e05528afd34b8ffd6aa40b199c074814465e5efe7a80d52afad`.

This is adapter and generic interpolation coverage. Quadruped whole-body posing, four-foot contact reasoning, gait-aware flight/support, learned quadruped posing or motion, imported/custom quadrupeds, natural-motion quality, human usability, and Cascadeur comparison remain open. Human reviewed cases and Cascadeur comparisons remain zero. The installed Bforartists build still reports successful assertions before its known `ucrtbase.dll` shutdown fault, so clean host shutdown is not qualified.

Evidence:

- `training/b4artists_ml/quadruped_adapter_protocol_v1.json`
- `training/b4artists_ml/results/quadruped-adapter-source-v1.json`
- `training/b4artists_ml/results/quadruped-adapter-release-v1-regression.json`
- `training/b4artists_ml/results/quadruped-adapter-package-v1.json`
- `docs/b4artists_ml/package-test-v0.27.0.json`

