# Airborne angular-momentum refinement in 0.21.0

Experimental 0.21.0 adds an opt-in **Angular Momentum** control to Native Motion Layer flight intervals. It measures the existing animation with the editable 17-segment mass model, solves a bounded whole-character rotation during free flight, and publishes quaternion plus COM-pivot curves on the native motion instance. Takeoff and landing poses remain unchanged. Gravity-arc translation, C2 COM transitions, the source pose action, and rig channels remain independently recoverable.

## Physical model and claim boundary

The solver treats each segment center as a normalized point mass. It measures orbital angular momentum about the whole-body COM and the corresponding point-mass inertia tensor. A constant world angular-momentum target is solved so the integrated rigid correction returns to the authored landing orientation. The correction is capped at 35 degrees and scaled by the animator's 0-1 control. If a correction would worsen the measured variation, the solver publishes the identity correction.

This is a real angular-momentum refinement for the stated point-mass model. It does not include each segment's axial/spin inertia, joint torques, aerodynamic forces, collision impulses, deforming soft tissue, secondary motion, or dynamic contact balance. Those remain separate requirements. It also does not establish visual quality or Cascadeur parity.

## Workflow

1. Generate an interpolation candidate and initialize the mass model.
2. Add a free-flight interval between authored priority poses and choose **Native Motion Layer**.
3. Set **Angular Momentum** above zero. Transition frames and **Match COM Acceleration** may be used at the same time.
4. Run **Preview COM Flight**, inspect the result, and use Keep, Discard, Restore Before Flight, or Restore Source as usual.

The option is off by default, so existing native and root-curve flight results retain their earlier behavior. Root Curves rejects a nonzero angular setting instead of silently ignoring it. An authored priority pose inside the interval requires splitting the angular interval there. Held or blended contacts remain excluded from the flight interior by the existing contact guard.

## Measured evidence

The source-qualified BoneForge and generated Rigify-default fixtures reduce point-mass angular variation by 88.7% and 87.0% respectively. Their maximum published COM error stays below `9.1e-6` body units, relative basis preservation below `2.2e-7`, and rigid-position error below `9.2e-6`. The combined Rigify-default C2 and angular workflow also passes, with takeoff/landing normalized acceleration jumps below `0.04` and `0.022`.

`angular-momentum-full-v2-regression.json` is the final same-hash regression manifest. It covers 46 suites and 439 Bforartists tests, including five pure angular tests, actual BoneForge/Rigify workflows, rotated helper/contact/support coordinates, native ownership, cancellation, source recovery, and the prior animation stack. The exact-package checks and visible-window lifecycle are summarized in `package-test-v0.21.0.json`.

The visible Rigify-default exact-package journey verifies Escape cancellation, generation, Undo/Redo, Keep, Restore Source, reopen, and Discard with C2 and angular options together. Cooperative checkpoints measure 39.46 ms callback p95 and 47.57 ms maximum on this machine. Universal sub-50 ms responsiveness across other hardware, rigs and clips remains unqualified. The installed Bforartists build continues to exit through its known `ucrtbase.dll` shutdown crash after writing successful reports.

Independent animator review, matched Cascadeur execution, other hardware, production characters, long/high-spin flights, quadrupeds, full rigid-body inertia, forces, collision, and secondary motion remain unverified.
