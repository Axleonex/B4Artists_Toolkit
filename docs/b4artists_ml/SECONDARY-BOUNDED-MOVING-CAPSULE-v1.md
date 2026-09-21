# Secondary Motion: bounded moving/deforming capsule collision

Development 0.37 adds an opt-in moving/deforming extension to the analytic
capsule collider. Two explicit unparented endpoint objects may now expose
complete direct location Actions; an optional matching uniform Scale Action
changes the radius at the sampled solve frames. Parents, constraints, rigid
bodies, drivers, NLA, curve modifiers, muted or locked curves, delta
transforms, incomplete XYZ channels, nonuniform scales, endpoint-scale
disagreement and post-sampling mutation fail closed.

The host samples both endpoint trajectories and the radius at the bounded
solver frames. Continuous mode uses eight interpolated substeps and the
existing analytic static capsule sweep at each interpolated state. It also
uses the endpoint-midpoint and radial-radius rates for the bounded relative
velocity response. This is a bounded moving/deforming approximation; it is
not a globally exact moving-surface distance solver, a rigid-body contact
solver, or a learned model.

Moving endpoint mode reports schema `24` with backend
`implicit_selected_control_secondary_moving_capsule_v1`; enabling continuous
mode reports
`implicit_selected_control_secondary_continuous_moving_capsule_v1`. Static
schema 13 and static continuous schema 23 retain their prior contracts.

The host-independent capsule math slice currently passes 12 tests and the
shared secondary math slice passes 12 tests. The exact extracted `0.37.28-dev`
archive passes the three-test Bforartists binding suite and the
capsule-compatible affected regression passes 156/156 across fourteen suites,
with zero test failures, errors or skips. The exact-package foreground journey
passes the moving endpoint and matching radius-scale controls, schema 24
continuous moving-capsule generation, Restore Input, Keep, save/reload and
Restore Source in 6.426 seconds. Native Undo/Redo is recorded as a Bforartists
alpha factory-startup timer-context limitation. The known post-assertion
`ucrtbase.dll` shutdown fault is recorded separately and is not counted as a
feature failure. The exact development archive is
`releases/b4artists_ml_v0.37.28-dev.zip`; its package check passes with SHA-256
`5ebef6d5ff4f05962de1bbddf2754995d3a126f5e24815e4eacb91cb0674a8bc`. The
permitted evaluator/reviewer route remains blocked before evaluation, while
the deterministic fallback is pass. Independent animator usability, learned
temporal quality and Cascadeur comparison remain unqualified. The binding and
remaining host-gate receipt is
`BOUNDED-MOVING-CAPSULE-BFORARTISTS-REGRESSION-v1.json`.
