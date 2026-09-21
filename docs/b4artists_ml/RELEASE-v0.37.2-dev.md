# B4Artists Machine Learning 0.37.2 development archive

This archive packages the standalone development source with Static Analytic Capsule Collision and the compatibility fixes validated by the full affected secondary-motion suite.

- File: `releases/b4artists_ml_v0.37.2-dev.zip`
- Source and archive bytes are recorded in `package-test-v0.37.2-dev.json`.
- Focused host-independent validation passes 16 tests plus 6 subtests.
- Bforartists 5.1.0 / Blender 5.2.0 Alpha capsule binding validation passes 2/2.
- The affected secondary-motion regression passes 148/148 across fourteen suites with zero skips.
- The current read-only archive recheck records the 54-member count, byte count,
  archive hash and zero runtime-member hash mismatches in
  `capsule-package-reverification-v1.json`.
- The foreground Action/rig recovery rerun is recorded in
  `capsule-ui-action-fingerprint-v10.json`: the kept Action survives
  save/reload, Restore Source recovers the source Action, armature structure and
  persisted rig modes, and candidate-driven pose reevaluation is reported
  separately rather than overclaimed as a full-pose match.

The package remains experimental. The exact-package foreground lifecycle passes
visible controls, Escape cancellation, preview/generation, native Undo/Redo,
Restore Input, Keep, save/reload recovery and Restore Source. The alpha host still
returns the known `ucrtbase.dll` shutdown fault after assertions. The archive makes
no claim of learned temporal generation, independent animator usability,
Cascadeur parity, or superiority. The frozen `releases/b4artists_ml_v0.36.0.zip`
remains unchanged.
