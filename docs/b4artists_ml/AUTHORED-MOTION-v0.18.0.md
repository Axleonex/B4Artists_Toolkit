# Experimental 0.18.0: authored whole-body motion

The standalone addon now exposes a cancellable Whole-body Motion method alongside existing Pose Blending. It observes authored endpoints only, builds a shape-preserving body-position trajectory through all priorities, interpolates endpoint orientations with SLERP, and fits actual humanoid controls. Publication uses the existing isolated candidate and Keep/Discard recovery path. Explicit contacts remain a separate animator-controlled correction.

This method is procedural. The two previously bundled learned pose models remain unchanged; no temporal weights were added or qualified. Ghost Tool and Anim Assist remain unchanged. Bforartists exclusivity remains covered by the original host-guard regression.

## Validation

- 369 native cases across 36 suites pass on the exact current source, including 24 new math, generation lifecycle and registered operator/controller checks.
- All three actual crouch/recover fixtures match the frozen research result exactly and pass unchanged contact and source-preservation gates.
- Seven exact-extracted-package workflows pass with Python network/process-launch calls denied: four existing learned-live/Keep/Discard cases and three authored-motion/contact/Keep/Restore cases. All loaded addon modules resolve inside the extracted archive.
- The source audit proves 23 copied definitions unchanged, four new modules, and only UI/version/contact-key changes to existing packaged files. No training module is imported by the runtime.

| Rig | Contact drift after correction (limb units) | Generation max tick ms | Generation p95 tick ms |
|---|---:|---:|---:|
| boneforge | 0.000148346 | 77.84 | 26.50 |
| rigify_basic | 0.000055492 | 99.15 | 43.05 |
| rigify_default | 0.000055492 | 144.44 | 79.00 |

Contact tolerance remains 0.0002 of evaluated two-segment limb length and 0.001 radians, with no refinement-cap increase. Measurements are headless and partly overlap short regression jobs; no isolated speed improvement or viewport responsiveness is claimed.

## Remaining quality gaps

Around the middle crouch priority, the smallest derivative probe measures rotation-velocity jumps of 2.737 rad/s on the BoneForge body trajectory and 2.177 rad/s on Rigify. Contact correction reduces them to 0.414 and 0.372 rad/s respectively. Root velocity also remains discontinuous after baking. These are a local diagnostic, not a motion-quality pass. SLERP, integer-frame baking and contact resampling do not establish C1 continuity or preserve character style generally.

Current modal viewport interaction and independent animator usability remain unverified. Full fits take seconds and some steps exceed 50 ms. All host processes retain the separately reproduced shutdown access violation after assertions; test success is not clean process-exit qualification. Production character meshes, broader reach/walk/run/jump/land/turn references, learned temporal quality, further physics, quadrupeds and the separate optional connector remain required. Cascadeur parity or superiority is unverified.

## Local artifact

releases/b4artists_ml_v0.18.0.zip; 40 files; 265463 bytes; SHA256 d867368c63f145aa123c5e995762958745941076a21298f3215d1fdf9f07aea6. Exact package/worktree equality verified. Not installed, committed, merged or pushed. See USER_GUIDE.md for usage and package-test-v0.18.0.json for qualification.

The original goal remains active and incomplete. The 75 total evaluation ceiling and existing September 9, 19:24:05 UTC deadline remain unchanged.
