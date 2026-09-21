# Experimental 0.9.0 - directional bend limits

The full product goal remains active and incomplete. This milestone adds artist-defined signed forward bend bounds, sideways allowances and pose-based forward-axis calibration to whole-body previews. Models, training data, Ghost Tool and Anim Assist are unchanged. This is geometric constraint fitting, not new machine learning, a clinical anatomical model or evidence of Cascadeur parity.

## Coordinate and request contract

Each enabled limit retains its total swing cone and signed twist interval. An optional bend request supplies axis, minimum, maximum and sideways in radians. Absent bend requests retain the earlier two-component residual and saved-request signatures. Control Rotation measures the rest-local animator control. Skeletal Joint uses the already supported evaluated child/parent rest-corrected frame.

For a unit quaternion (w,x,y,z), remove longitudinal Y twist and take the swing logarithm. Its X/Z vector is (x*w+z*y, z*w-x*y) multiplied by swing_angle / (hypot(w,y)*hypot(x,z)). Rotate that vector into the authored forward/perpendicular basis. The forward component is constrained to the signed interval; the perpendicular component is constrained symmetrically by the sideways allowance. These are swing-log components, not Euler angles or clinical flexion/abduction measurements. Quaternion signs are equivalent; reversing the bend direction is not.

Directional requests require total Swing below 180 degrees. An exactly reversed longitudinal axis has no unique twist/swing split: calibration rejects it, and residual evaluation supplies a finite rejection penalty above the acceptance tolerance. This also closes a narrow-cone acceptance hole for restricted twist at the singularity. Mixed ordinary/directional residuals now retain the correct control owner in failure diagnostics.

## Animator workflow and persistence

The optional Limit Bend Direction settings are shown for the selected limit control. Use Current Bend as Forward reads a pose bent by at least 5 degrees in the selected measurement space and writes only the Forward Axis setting. It does not pose the rig, change the rest reference, infer safe ranges or enable a limit. Running solves and ambiguous straight/reversed poses reject calibration. Calibrate each relevant side/control deliberately.

The initial forward range of 0 to 160 degrees and sideways allowance of 5 degrees are editing defaults, not validated anatomical presets. The total swing cone also applies; incompatible bounds are rejected when fitting fails, restoring the preceding preview. Target Strength does not weaken limits. A collapsed Pose Targets section gives the selected limit more sidebar space.

Settings survive new previews and .blend reload. The immutable solve request includes enabled bend settings; changed requests cannot be kept without solving again. An authentic saved 0.8 skeletal-limit preview remains keepable with the new direction option disabled. Existing action/source restoration and FK-only control writes remain in effect.

## Solver changes and retained failures

Coupled pins, orientations, poles and directional inequalities exposed unstable forward derivative estimates in the host's evaluated rig graph. Directional requests now use central differences at normalized step 1e-3, with the final 24 iterations reserved for explicit priorities. Ordinary skeletal requests retain forward step 1e-4; ordinary control requests retain forward step 1e-3 and the existing 12-iteration priority phase. Derivative reuse remains enabled.

Central differences require twice as many probe evaluations per derivative refresh. Progress yields occur after four columns instead of eight, preserving at most eight probe evaluations between those checkpoints. This does not guarantee a fixed millisecond latency: host evaluation and other solver stages still contribute. Every yield restores an accepted pose, and original-rig validation remains authoritative.

No accuracy gate was loosened: maximum pinned-position error 2e-4 body-reference units, relative bone-length error .002, orientation and limit error .001 radians, and pole-direction error .01 radians. Infeasible or unconverged requests restore the previous preview.

Retained development reports under training/b4artists_ml/results:

- bend-limits-v1.json: eight tests, two coupled fitting errors with forward 1e-4 and 12 priority iterations.
- bend-limits-v2.json: eight tests, one fitting error after extending the priority phase to 24 iterations.
- bend-limits-v3.json: nine tests, two fitting errors; reducing the forward step to 1e-5 worsened convergence.
- bend-limits-v4.json: nine tests passed with central 1e-3 derivatives and the original acceptance gates.
- bend-control-space-v5.json: the added default Control Rotation preview/calibration test passed on BoneForge and default generated Rigify.

These failures remain available. They are not evidence that all feasible requests converge or that a general performance improvement was achieved.

## Package verification

All 138 background assertions passed with zero skips: ten new directional tests and 128 established tests. There are 128 package-entry tests and ten source-adapter tests against runtime bytes identical to the ZIP. Twelve unchanged contextual training/data tests were not rerun. The ten new tests cover active directional limits and simultaneous pins/orientations/poles on all five actual humanoid fixtures, both control/skeletal calibration, cancellation, reload, changed-limit rejection, source preservation, singularities and an authentic 0.8 saved preview.

The exact ZIP passed the real event-loop workflow on default generated Rigify with four skeletal bend planes, six requested orientations and four poles. Timer-driven completion, simulated Escape restoring the preceding preview, undo, redo and Keep/source-mode restoration passed. The native screenshot was inspected: the selected directional settings and Skeletal Joint mode are visible with Pose Targets collapsed. At the recorded narrow sidebar width, the calibration label is truncated and lower actions still require scrolling; this is not complete UX acceptance.

The UI fit took 17.98 seconds over 63 iterations and 2491 evaluations. Pin error was 3.354108e-06 body-reference units; limit violation 5.611858e-06 radians; orientation error 3.517308e-07 radians. The 350 cooperative steps had median 36.21 ms, p95 39.72 ms and maximum 162.62 ms. Complete event-loop scenario time was 19.53 seconds, excluding fixture/startup/exit. The host process took 28.89 seconds including those costs. These are single-scenario CPU measurements, not a cold/warm distribution, general performance improvement or continuous live-posing acceptance.

Directional background fits in the recorded fixtures took 3.37-10.14 seconds. They are configured differently from the UI scenario, so the numbers do not establish a UI overhead ratio. Hardware: AMD Ryzen 7 5800XT, Windows host, Bforartists executable X:/5.1.0/bforartists.exe, core 5.2.0 Alpha, build dd23ab17120d.

All eleven background processes and the UI passed their assertion markers and then exited with the known shutdown access violation: unsigned 3221225477 / signed -1073741819. The ucrtbase.dll shutdown problem was previously isolated without the add-on; it remains unresolved. These are not clean host exits.

Package: releases/b4artists_ml_v0.9.0.zip, 24 files, 203,431 bytes. SHA-256: 24dc1501aa0a16b16f89947c9e158c261a086226783d6d60b4fb5db56b4a9839. ZIP integrity, source-byte equality and Python syntax pass. The retained 0.8 ZIP and both bundled models are unchanged. Per-suite hashes, UI/step timing, legacy-fixture provenance, host exits and execution scope are recorded in checkpoint-bend-limits-v1.json.

The canonical router was attempted for implementation and again on resumed completion; both stopped before host application because the remote /mnt/x workspace is unavailable. No lane, policy fingerprint or patch was emitted. Native continuation used the canonical recoverable-infrastructure policy within the declared project scope. No commit, push, installed-addon update, preference change, Ghost Tool edit or Anim Assist edit occurred; tracked and staged Git diffs remain empty.

## Remaining full-goal work

Anatomical range/neutral-reference calibration, further distributed torso/neck adapters, temporal limits, explicit contacts and balance/COM remain incomplete. Learned inbetweening, style, gravity, momentum, secondary motion, continuous interactive latency, imported rigs/proportions/production meshes, quadrupeds and the separate optional Cascadeur connector remain mandatory. No equivalent direct Cascadeur comparison or animator quality study has established parity or superiority.
