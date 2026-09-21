# Experimental COM flight correction (0.13.0)

This increment applies procedural constant-gravity motion to the center of mass of an authored humanoid FK candidate. It does not add learned temporal motion, dynamic balance, collision response or momentum-continuous takeoff/landing. Full product acceptance and Cascadeur comparison remain open.

## Workflow

1. Capture priority poses and generate an interpolation candidate.
2. Open Airborne Motion. Initialize the editable mass model if needed; inspect/change masses under Center of Mass / Support.
3. Add an airborne interval and select two priority-pose frames as Takeoff and Landing. Up to sixteen intervals may share endpoints; their interiors cannot overlap.
4. Preview COM Flight. Gravity Influence blends from the retained input candidate, so repeated previews do not accumulate correction. Scene gravity (or zero when disabled), FPS and FPS Base determine the target. Display unit scale does not rescale internal physics.
5. Inspect and edit the candidate. Escape cancels a running preview. Restore Before Flight returns to the retained input. Keep/Discard and Restore Source Animation retain the existing recovery workflow.
6. Apply contact correction after flight. Held/blended contact influence cannot overlap a flight interior. Restore Before Contacts before changing flight settings or regenerating its preview.

## Algorithm and integrity

For normalized interval time u, duration T and constant world-space gravity g, the target is `(1-u)*C0 + u*C1 + 0.5*g*T*T*(u*u-u)`. Intermediate priority poses must already agree with the requested arc within acceptance tolerance; incompatible requests are rejected instead of moving those poses.

The adapter translates a captured master root, preserving the input's relative pose. Every mapped joint and deform bone is checked on the actual rig. Dedicated bound-mesh tests cover hand, foot, trunk and facial deformation on generated default Rigify. Default BoneForge and basic/default Rigify metarigs/generated rigs have transformed-scene fixtures; this does not establish arbitrary production-rig compatibility.

Editable cubic Bezier root-location curves interpolate measured root samples at segment times 0, 1/3, 2/3 and 1. Initial segments are half a frame and include existing curve knots. Actual-rig quarter-segment validation triggers bounded refinement to quarter, eighth and sixteenth frames. Failed passes restore the input and remove their temporary actions. A fast torso-motion fixture requires eighth-frame refinement.

Only master-root location curves change. All other candidate curves retain their copied data. External root handle geometry is preserved; automatic handles may be converted to Free when necessary to freeze the original outside geometry. Shared flight endpoints retain both fitted inward handles. Reports count outside handle freezes.

COM/position acceptance is 0.0002 evaluated trunk lengths. Basis acceptance is 0.0002 relative column error, independent of object scale. The Rigify facial precision probe found small floating-point changes under rigid translation; a raw matrix-entry threshold incorrectly scaled that error with the object. Tests verify bound mesh positions as well as bone transforms.

Jobs reject changed anchors, settings, object transforms, playhead, input curves (including modifiers), missing input actions and conflicting contacts. Cancellation, failed validation, save, load, undo/redo and unregister share recovery handlers. Source animation and its rig modes remain recoverable. Unsupported master-root dependencies fail actual-rig acceptance rather than receiving a guessed adapter.

## Measurements and limitations

Development results: five rig families passed COM and acceleration checks; measured correction time ranged approximately 0.9-6.0 seconds on the existing CPU/host fixture. Default generated Rigify used about 68 ms p95 / 145 ms maximum steps in that run. These are individual runs, not guaranteed hardware budgets. The real modal UI development test passed Escape, Undo/Redo, Keep and source recovery in 7.75 seconds, with 50 ms p95 / 124 ms maximum steps. Final package measurements are recorded separately.

Acceleration is independently measured at quarter-frame spacing (about 10.4 ms at 24 FPS). The five-fixture development p95 error was below 0.025 internal world units/squared second. Earlier two-millisecond differences amplified host float-evaluation noise; that earlier failing evidence is retained. Neither sampling interval certifies arbitrary high-frequency motion or continuous derivative bounds.

Takeoff and landing reports estimate one-sided input and corrected velocities. A ballistic arc generally introduces velocity jumps against adjacent motion. The UI displays the largest estimated jump, not a momentum-continuity promise. Strength below one is a stylistic blend and does not guarantee constant-gravity acceleration. Support masses are artist-authored approximations, not measured anatomy.

No force, torque, angular-momentum, collision, ground-penetration, moving-support or secondary-motion solution is claimed. Joint limits constrain posing, not every temporal sample. Native IK output, arbitrary constraints/space switches, imported production characters, quadrupeds and natural learned inbetweening remain unfinished.

## Evidence

- `tests/test_b4artists_ml_flight_math.py`: five independent numerical contracts.
- `tests/test_b4artists_ml_flight.py`: actual rig/mesh results, acceleration, adaptive fast motion, source/curve preservation, stale edits, contact composition, adjacent intervals, gravity/timing/unit settings, cancellation and saved preview recovery; separate real-window UI entry.
- Development receipts: `training/b4artists_ml/results/flight-host-v6.json`, `flight-adaptive-v1.json`, `flight-rigify-precision.json`, and `docs/b4artists_ml/flight-ui-development.json`.
- Final package: 15 host suites / 180 assertions and 17 numerical checks passed. Twelve host tests exercise flight; the other 168 retain prior regression coverage. The final packaged real-window UI also passed; `checkpoint-flight-v1.json` records artifact hashes, entry scope and host exit limitations.

The installed Bforartists 5.1.0 distribution uses a Blender 5.2.0 Alpha core and exhibits the previously isolated ucrtbase.dll shutdown access violation. Successful test assertions are reported separately from process exit; this is not clean host lifecycle acceptance or human/independent usability approval.


## Final package measurements

The 0.13.0 package is 231,064 bytes (32 files), SHA-256 `7d042f113b77d14f1e40b0e44830dc40c0a5f09900b1bce283af3999ad9e841d`. Every packaged file matches source. The five ordinary flight fixtures measured 0.88-5.40 seconds. Default generated Rigify measured 52.0 ms p95 / 148.8 ms maximum steps. The fast torso fixture required eighth-frame refinement and measured 6.66 seconds with maximum normalized COM error 0.0000886.

The final packaged real-window workflow measured 10.64 seconds, with 70.6 ms p95 / 182.3 ms maximum steps. It ran concurrently with separate regression work; those timings are not an isolated performance comparison. The builder inspected the final screenshot and corrected clipped takeoff/landing labels. This is deterministic UI evidence plus builder inspection, not independent human usability acceptance.


## 0.13.1 maintenance

The 0.13.0 evidence above is historical. FLIGHT-OPTIMIZATION.md records indexed lookup, bulk curve fingerprints, owned preview cleanup, additional regression coverage and fresh package measurements. Source and numerical acceptance thresholds are preserved. The later long-clip baseline found that default Rigify 60/240-frame flight intervals can fail the facial-bone basis check; passing short fixtures do not establish that longer coverage.
