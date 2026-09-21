# Long Rigify flight precision investigation

Diagnostic milestone; runtime and v0.13.1 release unchanged. No parity or product acceptance claim.

## Findings

Controlled tests cover BoneForge, basic Rigify and default Rigify, with synthetic meshes bound to their deform bones. Default Rigify root translation produces relative facial-bone basis error up to 0.001758 at 120 world units against the unchanged 0.0002 gate. Direct local assignment reproduces host conversion results. Temporarily changing same-armature constraint spaces did not resolve it. Armature-only object translation leaves geometry behind; co-moving the mesh avoids separation but still fails bone precision.

A minimal three-bone native fixture reproduces Damped Track and Stretch To errors above 0.0002 without importing the add-on. This establishes a host evaluation contribution; it does not prove every product failure has the same cause.

Applying global movement to an evaluated collection instance preserves the transformed default Rigify fixture: static maximum relative basis error 7.53e-8, head error 1.76e-6 world units and mesh error 5.25e-6 world units. Native editable curves and saved scenes reproduce sampled geometry exactly in a fresh process without the add-on loaded.

The 240-frame instance-flight prototype passes dense COM and geometry checks. Half-frame fitting takes 3.507 seconds; four-frame fitting takes 0.448 seconds (fit phase only). Neither passes the unchanged quarter-frame acceleration gate: p95 errors 0.12595 and 0.12524 world units/s? exceed 0.1. These are synchronous diagnostic timings, not interactive performance certification.

A separate native two-key exact parabola also fails this acceleration metric without the add-on: p95 error 0.52875 world units/s?, despite maximum position error 4.395e-5 world units. Float64 and float32-rounded analytic controls pass. Corrected v2 verifies stored keys and handles; v1 retained stale RNA references in its key metadata and is superseded for that proof. The current gate remains failed; neither sampling nor tolerances were relaxed.

## Limits and next action

Collection instancing is a feasibility prototype. Original and instanced geometry are both visible. Production integration still needs ownership/visibility, effective-world-space posing and contacts, external constraint targets and drivers, editable keep/discard, undo/redo, save/reload and export handling. An evaluated global trajectory layer is the next architecture to assess, contingent on an explicitly extended run. Native curve evaluation and acceleration measurement require further diagnosis before integration is accepted.

Host assertions completed, but the tested alpha host still exits with code 3221225477; clean lifecycle acceptance remains failed. Synthetic geometry and builder inspection do not substitute for production characters or independent animator assessment. This work adds no learned temporal motion; all original requirements remain in force.

No runtime changes, installation, commit or push. Existing v0.13.1 regression evidence remains current by hash verification and source/archive comparison, rather than a claim of newly rerunning every test.
