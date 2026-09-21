# Selected-control secondary motion — experimental 0.24.0

## Implemented workflow

Secondary Motion is an opt-in refinement of the active animation candidate. The animator selects pose controls in the viewport, chooses rotation and/or location, tunes response frequency, damping, air friction, influence and boundary blend, then previews a copied result. The retained input action is never edited in place. Escape, Undo/Redo, Restore Before Secondary Motion, Keep, Discard, save/reload and Restore Source use the existing candidate lifecycle.

The solver uses an implicit damped mass-spring follower at the scene frame rate. Rotation is simulated as quaternion angular error and normalized after every step; Euler and axis-angle controls convert through continuous quaternions and return to their authored representation. Location uses the same stable vector dynamics. A smooth envelope makes the correction exactly zero at every captured priority pose. Published channels contain ordinary editable linear keys.

This backend is `implicit_selected_control_secondary_v1`. It is deterministic physics assistance and does not use learned weights. The UI says so directly.

## Evidence

Host-independent tests cover finite/stable vector dynamics, hostile time steps, quaternion normalization and sign continuity, exact priority envelopes and fail-closed settings. Real Bforartists tests cover BoneForge and full generated Rigify rotation, selected location, internal priority poses, cancellation before publication, stale settings, missing selection, repeated non-stacking regeneration, input recovery, Keep, save/reload, Restore Source and composition after COM flight.

The source real-window Rigify journey passes five lifecycle events: Escape cancellation, generation, Undo/Redo, Restore Before Secondary Motion, and Keep plus Restore Source. It records seven modal steps at 35.14 ms p95 and 38.07 ms maximum in `secondary-ui-secondary-source-v1.json`. The exact-package journey repeats those events while loading every add-on module from the extracted archive and records 35.95 ms p95 and 38.95 ms maximum. The screenshot is `training/b4artists_ml/cache/secondary-ui-secondary-package-v1.png`. These are automated operator and rendering checks, not an independent animator usability or motion-quality judgment.

The complete same-hash regression passes 458 tests in 49 suites on one 37-file runtime hash set. The deterministic 47-file archive passes 35 focused checks with outbound calls denied and zero denied runtime attempts. Results are recorded in `package-test-v0.24.0.json`. The installed Bforartists 5.1 / Blender 5.2 Alpha host still exits through the previously isolated `ucrtbase.dll` shutdown access violation after passing reports; this is not described as a clean process exit.

Package: `releases/b4artists_ml_v0.24.0.zip` (304,418 bytes; SHA-256 `ef3f784532c90eb0810667ed593b3bbce88b39637ef8e024d78699f03e24daeb`). It is ready for local testing.

## Boundaries

This first secondary-motion stage follows explicitly selected local control transforms. It does not infer which controls represent hair, cloth, tails, flesh or props. It does not add per-control gravity, global-space follow, deformation-volume dynamics, self-collision, arbitrary environment collision, moving surfaces, joint torque, restitution or friction. It samples once per animation frame and does not claim continuous-time physical accuracy.

The feature is not a learned motion model and does not establish Cascadeur parity. Learned temporal acceptance, secondary gravity/collision, production-character review, quadrupeds, the optional connector, blind animator comparison and equivalent-task Cascadeur measurements remain required by the full goal.
