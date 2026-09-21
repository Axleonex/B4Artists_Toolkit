# Moving rigid spherical colliders v1

Status: verified development 0.37 source; deterministic sampled control-pivot exclusion against directly animated centers, not learned motion or a general rigid-body solver.

## Animator workflow

In **Secondary Motion**, choose **World**, enable **Location** and **Collision**, and set **Shape** to **Sphere**. Choose an unparented center object, set an explicit radius, and enable **Follow Center Animation** when that object has complete direct Location curves. Click **Add Sphere to Set** to retain the choice. Every saved row has its own **Follow Animation** switch, center, radius and Remove action. Static and moving rows can coexist, up to the existing eight-sphere limit.

At each secondary-motion sample, a moving row reads the center object's evaluated world origin. The solver keeps selected control pivots outside radius plus Clearance. Bounce and Friction operate on control velocity relative to the moving center, so a translating collider can transfer normal or tangential motion instead of behaving like a different static sphere on every frame.

The center object's Action remains unchanged. The character input Action is retained, generated location curves remain editable, every captured priority pose stays exact, and Preview, Escape, native Undo/Redo, Restore Input, Keep Candidate and Restore Source retain their existing behavior. The row mode and center Action survive save/reload.

## Supported animation and safety boundary

Moving Sphere v1 accepts direct object animation with complete, unmuted Location X/Y/Z curves. The center must belong to the active scene and remain unparented, unconstrained and free of rigid-body ownership, drivers, NLA tracks, curve modifiers, animated scale and animated delta location. Rotation animation is harmless because an explicit sphere uses only the object origin and authored radius.

The solve binds collider, Action and slot identities; Action, AnimData, layer, strip, channel-bag and FCurve state; static `delta_location`; and radius. It checks that binding throughout cooperative work. After sampling, final verification re-evaluates every live center at every frame, compares it with the frozen trajectory within `1e-8`, and computes published clearance from the live value. Changes to Action influence, Action-layer state, `delta_location`, key data or handler-driven evaluated centers reject and restore the owned character candidate. Radius keys or drivers remain unsupported.

Static-only requests preserve schemas 9/10 and backends v8/v9. Any set containing a moving row uses schema 11 and backend `implicit_selected_control_secondary_v10`, records each moving row, reports relative-velocity response, and names the target space as evaluated direct object location.

## Verification

- Focused Bforartists 5.2 Alpha qualification: 9/9, with zero failures, errors or skips. Coverage includes sampled-center validation, overlapping moving-sphere order independence, relative-velocity transfer, mixed static/moving sets, BoneForge and generated Rigify Default workflows, native Add Undo/Redo, save/reload, incomplete/action-modified/scale/driven rejection, priority conflicts, key mutation, and post-sampling Action influence, `delta_location`, Action-layer and frame-handler interference. Evidence: `training/b4artists_ml/results/secondary-moving-sphere-focused-v1.json`, SHA-256 `1622e99d607dc7e5158129f9f9460eb30771d38b4d8e7deb7ed71c461b006f9f`.
- Affected regression: 181/181 across 14 suites on one frozen 44-file runtime. It includes the unchanged 8-case static set, 13-case single static sphere and all affected force/load, secondary-motion, chain, visible-state and registration/recovery suites. Evidence: `training/b4artists_ml/results/secondary-moving-sphere-affected-v1-regression.json`, SHA-256 `3ef3e9ff8a9ff81b9bae06deb67ec34677924424e72b53d984b61b401fa0cd4c`.
- Foreground BoneForge journey: one moving and one static row are visible and editable. The modal and synchronous solves, native Undo/Redo, Restore Input, Keep and Restore Source pass while both the character source and collider Actions remain unchanged. Across 86 callbacks, p95 was 11.10 ms and maximum was 18.34 ms. Two sampled contacts produced 0.03020020296316618 maximum raw penetration, 2.220446049250313e-16 desired-array penetration and 3.781212593034766e-08 evaluated published-pivot penetration under the `1e-6` tolerance; maximum world-location reproduction error was 2.6656007498500226e-07. Evidence: `docs/b4artists_ml/secondary-moving-sphere-collision-ui-v1.json`, SHA-256 `fffd845c2059269db55b72e3f48456ac29dc8eadb72d67309cc718192e89f23d`.
- Foreground screenshot: `training/b4artists_ml/cache/secondary-moving-sphere-collision-ui-v1.png`, SHA-256 `6686918fc50d78b4924f739fa1fee21a0a868931c6aa316110ad86032e5cae95`.
- Final independent, read-only serial review: PASS after checking the complete evaluation-state binding, live-center postcondition, timing of post-sampling interference tests and every evidence hash.

Every Bforartists process completed its assertions and wrote fresh source-bound evidence. The known host shutdown access violation remained after reporting, so clean shutdown is not claimed. The frozen `releases/b4artists_ml_v0.36.0.zip` remains unchanged at SHA-256 `3a0423b632cdc0b279a43e45c58321d75833927fb4207d8a2b35d213e282e2e5`.

## Limits

Collision still represents each selected control as a sampled point and each collider as an explicit sphere. This slice does not use collider geometry or scale, derive bone or mesh volume, support parented, constrained, NLA, driven, rigid-body-owned or deforming targets, detect between-frame tunneling, transfer torque through a character, detect self-collision, infer physical properties, learn motion, establish independent animator quality, or demonstrate Cascadeur parity.
