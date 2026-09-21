# Procedural Capture-Point Balance v1

Development source adds an opt-in, bounded dynamic-balance estimate to the existing whole-body balance preview. It remains procedural and is not learned motion, force inference, contact-force solving, or a human-usability qualification.

When `Use Capture-Point Estimate` is enabled, the artist supplies a world-space COM velocity. The solver uses the authored support plane, gravity magnitude, and the current preview COM height to compute the constant-gravity pendulum time constant

`tau = sqrt(height / |gravity|)`

and the planar capture point

`capture = COM_projection + velocity_projection * tau`.

The nearest point in the inset support hull is selected, and the correction moves the current COM toward that point minus the authored velocity displacement. Supporting hand/foot contacts and existing whole-body pins remain governed by the same projection solver. This is a local kinematic estimate; it does not simulate forces, friction, stepping, angular momentum, or future animation frames.

Compatibility and evidence contract:

- Disabled mode retains the existing schema-1 static request and `static_only=true` report path.
- Enabled mode uses schema 2 and reports `schema=2`, `dynamic=true`, `static_only=false`, the capture point/target, time constant, capture height, and capture error.
- Nonfinite velocity, wrong gravity direction, zero gravity, and nonpositive COM height fail before mutation.
- The exact v0.37.22 archive has 54 members; package integrity passes, focused math passes 25 tests plus 6 subtests, and a focused BoneForge Bforartists set passes 6/6 including the enabled dynamic solve. The broader legacy balance suite remains unqualified because the installed alpha host has a separate Rigify teardown/fixture incompatibility. See `DYNAMIC-BALANCE-BFORARTISTS-REGRESSION-v1.json`.
- No learned-temporal, independent-animator, production-character, or Cascadeur claim is made.
