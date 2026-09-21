# Secondary selected-control self-collision v1

Development 0.37.13 adds an opt-in **Self-Collision** mode to the standalone Bforartists secondary-motion workflow. It treats each selected World-space Location control as an equal finite sphere with the authored **Self Radius**. A deterministic bounded pair-projection solver separates overlapping selected controls across the generated samples, while preserving authored priority poses and publishing ordinary editable Location curves. The behavior is verified in the exact v0.37.38 archive.

The mode requires World space, Location output, at least two selected controls and complete Location curves for every selected control. It is mutually exclusive with the external collider path so the correction contract remains explicit. Priority frames that already overlap reject before publication; generated samples use at most eight deterministic pair-projection iterations. Final evaluated selected-control positions are rechecked with a 1e-6 penetration tolerance.

The report uses schema 19 and backend `implicit_selected_control_secondary_self_collision_v1`. This is selected-control procedural separation, not a full-body/deformable contact model, exact continuous swept-sphere collision, learned motion, or a Cascadeur comparison.

## Evidence

- Focused host math: 32 tests, 0 failures/errors/skips.
- Exact archive: `releases/b4artists_ml_v0.37.13-dev.zip`, SHA-256 `aac2565258011874d90f53d3af3be1fba6fc4fac42154b9223199dedb1ce2a31`.
- Exact-package Bforartists binding: 2/2 in 4.860 seconds.
- Exact v0.37.38 package receipt: 2/2, including the single-control fail-closed guard and generated Rigify Default crossing-path separation.
- Exact-package affected secondary regression: 155/155 in 193.487 seconds, 0 failures/errors/skips.
- Foreground archive journey: schema 19, 9 self-collision samples, `1.0617051512951114e-07` final penetration, Escape cancellation, native Undo/Redo, Restore Input, Keep and Restore Source all passed.
- The Bforartists 5.2 Alpha process still reports the known post-result `ucrtbase.dll` shutdown access violation; assertions and durable reports complete before that fault.

See `SELF-COLLISION-BFORARTISTS-REGRESSION-v1.json` and `secondary-ui-self-collision-ui-v1.json`.
