# Private generation - experimental 0.19.1

Whole-body Motion now solves on a temporary working rig when the rig's dependencies can be copied safely. The animator's original action, rig and playhead remain visible between steps. Rigs with unsupported copy dependencies retain the existing guarded generation workflow. There is no additional setting or runtime dependency.

Use the existing full-body capture, Generate Whole-body Preview, optional Smooth Transitions, contact correction, Keep/Discard and Restore Source Animation workflow. Editing source poses, curves, anchors, frame rate or rig state while generation is paused stops the outdated job and preserves the edit. Saving/loading, undo/redo callbacks, cancellation and addon disable clean up pending work; saved jobs do not restart automatically.

## Validation

- 408 native tests across 42 suites passed. The new private path matches the guarded generator across eight existing rig profiles. A real unrelated external-accessory dependency verifies the guarded fallback.
- The exact 42-file archive passed 13 offline workflows covering learned-live posing, Keep/Discard, and smoothed crouch/reach/turn contact recovery. The six reach/turn cases reproduce 9,813 dense contact checks and the original reference maxima exactly.
- The source transaction guards and solver mathematics are structurally unchanged. Production uses an explicit transaction dependency; research function-cloning is not shipped.
- Serial guarded/private/private/guarded timing on the same default-Rigify reach/hold scene reduced median generation work from 41.466 to 24.527 seconds (40.9% less time). All candidate keys and handles matched exactly. No task-owned training, evaluation or other native tests ran concurrently with this benchmark.

## Limits

This comparison covers one controlled reference, with smoothing enabled. It is not an OS-cold, viewport-input or broad character-performance qualification. The slowest private preview step was 0.455 seconds; full responsiveness remains unresolved.

The host still exits with its previously isolated ucrtbase.dll access violation after assertions. Clean host shutdown and current interactive human usability remain unqualified. The canonical independent-review launcher failed before it could run; author review and automated tests are not independent human approval.

The four new temporal-model fits failed the unchanged development gates and are not bundled. Existing experimental pose models are unchanged. Learned motion, broader rig/mesh coverage, full physics/refinement, quadrupeds, optional connector and equivalent Cascadeur comparison remain incomplete. The original goal stays ACTIVE.

Evidence: package-test-v0.19.1.json; private-production-full-v1-regression.json; private-production-fallback-v1-regression.json; private-production-benchmark-v1/report.json; private-runtime-package-v1.json under the documented result directories. See SEQUENCE-DEVELOPMENT-v1.md for model failures and follow-up diagnostics.
