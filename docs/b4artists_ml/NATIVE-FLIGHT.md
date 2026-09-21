# Native COM flight integration

Experimental 0.14.0, following 0.13.1. Native Motion Layer is a procedural gravity correction method; it is not learned temporal animation. Final product acceptance and Cascadeur comparison remain incomplete.

## Workflow

1. Capture priority poses and generate an interpolation candidate. Initialize the mass model, author airborne intervals, and ensure held/blended contacts do not overlap their interiors.
2. In COM Flight, choose Native Motion Layer and Preview COM Flight. Escape cancels generation and restores the input. The method evaluates the original rig at its original coordinates and moves a native collection instance using editable residual curves and gravity drivers.
3. Inspect the displayed character. Keep retains both the pose action and motion layer. Restore Before Flight removes the correction from the current candidate. Discard restores the original animation.
4. After Keep, Restore Source Animation preserves a complete alternative under Saved Motion Results, including the trajectory drivers and an independent pose-action copy. Preview Saved Motion creates a separate editable candidate; Discard returns to the source.
5. Keep an animation candidate before opening the existing whole-body or limb posing tools. Helpers, contact captures and support analysis account for native translation. Captured pose anchors remain in source rig space. Restore the kept source before generating another interpolation candidate.

## Behavior and limits

The native backend uses half-frame residual segments and validates COM/rigid-translation/bone-basis error against the existing 2e-4 body-scale tolerance. Two quarter-frame sampling grids, one shifted by 0.137 frames, test acceleration against the existing 0.1 world-units/s^2 p95 budget. Priority poses and motion outside airborne intervals must remain unchanged. Strong stylistic motion or longer intervals may fail and roll back; no tolerance is silently relaxed.

Motion-layer authoring supports translation. Apply orientation and uniform scale to the source rig before creating the layer; manually rotating/scaling the instance or changing the collection instance offset is rejected by authoring tools. Animated armature object transforms and animated gravity are rejected. Native flight does not guarantee momentum continuity across takeoff/landing, collision avoidance, secondary motion or plausible learned inbetweens.

Sources use persistent ID-based collection ownership. Original collection deletion or foreign reuse stops recovery before deletion; the user must resolve the conflicting links or supply a recovery destination. Saved result carriers are unlinked native objects with fake users; their action copies and self-targeted drivers survive save/reload. Production character attachments beyond the armature and bound meshes need further coverage.

Current implementation and tests are summarized below; the shared goalpost records the final evidence fingerprint. Bforartists still has the reproduced shutdown access violation after assertions complete. Automated UI events do not count as independent animator usability or visual-quality acceptance.


## Edited pose convergence

A transformed BoneForge hand target moved 0.03 world units toward the pelvis missed the 2e-4 pin gate with the original 50-iteration request, both without native translation (0.000231028) and with it (0.000211085). An experimental 100-iteration fit passed both unchanged gates. The preview now retries once only for a near-converged plain positional request (pin error above 2e-4 and at most 1e-3, with the other accuracy gates passing). It restores the previous preview before retry, exposes a cancellation boundary and rejects targets changed between attempts. Ordinary successes and directed/limited/balanced requests retain their original budgets.

The actual edited native preview passes save/reload, Keep and source restoration: final pin error 0.0000418439, length error 0.000000605819, two attempts and 2.94 seconds of solver work on this machine. This is a bounded fixture result. The failed v1 outward-hand and v2 50-iteration logs remain in cache; no failed run is relabeled as passing.


## Input changes and failed construction

At cooperative boundaries, changes to raw pose controls or rig modes reject the native job. Both guard rejection and direct cancellation preserve newer pose or playhead edits. A script-driven edit repro previously lost a 0.125-unit hip translation; native-external-pose-v1.json retains that failure. The regression now checks rejection before and after instance creation, direct cancellation and changed-frame preservation.

The generated residual action is marked as owned immediately after its first key is created. An injected cubic-handle failure previously leaked a fake-user action; native-allocation-failure-v1 retains that failed assertion. The final regression requires unchanged action/object/collection inventories after the same failure. User-authored and shared actions retain the existing conservative recovery rules.

## Validation artifacts

- native-integration-v3-regression.json: 225 tests on the complete pre-guard 0.14.0 runtime; subsequent changes are confined to native_flight.py.
- native-final-v1-regression.json: current native integration and motion-ownership suites, including the input-edit and partial-construction failures.
- native-research-regression-v1.json: 70 passing offline research/evaluator tests and one host-only skip; native-semantic-v1-regression.json separately passes that host case.
- offline-v0.14.0.json: 63 package workflow checks with networking/process launches blocked. offline-native-final-v1.json rechecks the final changed native module; all other packaged file hashes remain identical.
- native-ui-v5.json: final packaged operator lifecycle; earlier v4 evidence is retained. The flight performance protocol records separate sequential measurements.
- native-saved-body-v3.json: edited translated hand target, save/reload/Keep/source restoration.
- native-flight-playback-v2-verify.json: final-package 60-frame default Rigify flight and bound geometry reopened in a fresh host without the add-on or auto-execution.

Results live under training/b4artists_ml/results unless a UI receipt is named (docs/b4artists_ml). Logs and disposable scenes live under training/b4artists_ml/cache. These tests cover generated fixtures and synthetic bound geometry, not production character assets or an independent animator study. Canonical S3 review is INCONCLUSIVE because its report-only adapter has no configured reviewer; native-motion-review-v1.json records this limitation.
