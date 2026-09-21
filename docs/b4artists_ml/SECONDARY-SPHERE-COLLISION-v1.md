# Static spherical collision v1

Status: verified development 0.37 source; procedural selected-control collision, not learned motion or a general rigid-body solver.

## Animator workflow

In **Secondary Motion**, choose **World**, enable **Location** and **Collision**, then set **Shape** to **Sphere**. Choose one unparented, unanimated object as the world-space center and enter an explicit radius. The object's geometry and scale do not define the radius. Clearance expands the excluded distance; Bounce reflects inward radial speed and Friction reduces tangential speed.

The solver retains the input Action, generates ordinary editable location curves, preserves every captured priority pose, and reports collision samples, raw penetration and final sampled penetration. **Restore Input**, native Undo/Redo, **Keep Candidate**, and **Restore Source Animation** use the existing Secondary Motion lifecycle.

## Algorithm and safety boundary

The deterministic implicit selected-control follower tests each generated control pivot against one static sphere. A point inside radius plus clearance is projected to the boundary. Radial velocity uses the authored restitution and tangential velocity uses the authored friction. The raw follower resolves an exact-center degeneracy from target direction, then opposite velocity, then world +Z. Final influence projection reuses that solved follower direction, then target direction, then +Z, which makes repeated results deterministic.

Sphere center and radius are validated before mutation. The center object must belong to the active scene, cannot be the animated rig, and must be free of parenting, constraints, Actions, drivers, NLA tracks, and rigid-body simulation. The radius cannot have keys or a driver. The center token is checked at every sampled frame, so ordinary edits and frame handlers that move it cancel and restore the retained input. Rotation and scale do not affect the explicit sphere.

If a captured priority pose is inside the excluded sphere, the solve rejects before publishing an Action. Sphere and planar colliders are mutually exclusive. Planar requests retain their prior schema and backend.

## Verification

- Focused Bforartists 5.2 Alpha qualification: 13/13, zero failures, errors, or skips. It covers host-independent collision math and post-projection correction metrics, deterministic center handling, exact outside-sphere compatibility, hostile validation, BoneForge and generated default Rigify workflows with evaluated published-pivot clearance, atomic priority conflict rejection, rigid-body admission, frame-dependent center mutation, keyed and driven radius rejection, visible property binding, and planar compatibility. Evidence: training/b4artists_ml/results/secondary-sphere-collision-focused-v1.json, SHA-256 7eb201ca266b863f7866b0dbbb2e6a21c044cea172e6ff36e75285d9c0f55412.
- Affected regression: 164/164 across 12 suites on one frozen 44-file runtime set. Evidence: training/b4artists_ml/results/secondary-sphere-collision-affected-v1-regression.json, SHA-256 a8d36f06e67d693d4165e47cf0643fb695c511d455fc9abb90778ee7eca1211b.
- Foreground BoneForge journey: visible sphere controls, modal solve, three collision samples, 0.035118090334440966 maximum raw penetration, 9.71445146547012e-17 desired-array penetration, and 4.548495677325626e-08 evaluated published-pivot penetration under the explicit 1e-6 acceptance tolerance, plus exact priority preservation, native Undo/Redo, restore, keep, and source recovery. Across 86 cooperative callbacks, p95 was 10.70 ms and maximum was 19.22 ms. Evidence: docs/b4artists_ml/secondary-sphere-collision-ui-v1.json, SHA-256 4f2b4201bfcc408133b59629342f0b59e47d5a403bcc73e487b19dab2906d49f.
- Foreground screenshot: training/b4artists_ml/cache/secondary-sphere-collision-ui-v1.png, SHA-256 c7129d7c9c6d1a13feeb37277fb5a623d0f92bad14135e6bf051d04181a6a3fb.

All Bforartists processes completed assertions and wrote fresh bound reports. The known host shutdown access violation remained afterward, so clean shutdown is not claimed.

## Limits

The collider excludes selected control pivots at sampled frames. It does not derive bone or mesh volume, use the center object's geometry, support multiple, moving, parented, constrained, or animated spheres, guarantee continuous-time collision, transfer collision impulses or torque through joints, detect self-collision, handle arbitrary or deforming meshes, infer physical properties, learn motion, establish independent animator quality, or demonstrate Cascadeur parity.
