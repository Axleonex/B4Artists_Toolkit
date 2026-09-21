# Center of mass and support ? experimental 0.11.0

This release adds a current-pose COM/support diagnostic on the five verified humanoid adapters. It changes saved analysis settings and a report only. It does not solve balance, change root motion, infer a sole or floor, or add a new learned model. The full product goal remains active.

## Animator workflow

1. Select the rig or a bound mesh and open **Center of Mass / Support** in the B4Artists ML panel. Click **Initialize Mass Model** once. This preserves already initialized weights when invoked again.
2. Expand **Mass Model**. Choose a segment and edit **Relative Mass** and **Center Along Segment** for the character. Weights normalize across the whole model; zero excludes a segment and at least one must remain positive. Center fraction zero is the first endpoint, one the second. The midpoint default is an editing starting point.
3. In **Animation Contacts**, choose a foot/hand, author its local sole/palm center offset, and **Capture Contact Here**. Set the hold interval, enable **Use as Support Patch**, and author patch width, length and heading. Capturing does not require an interpolation candidate. Patch settings do not change the contact correction algorithm.
4. Expand **Support Plane / Tolerances**. Set a world-space plane point and normal. Set allowed contact position drift/plane error and rotation change. The defaults are 0.01 internal length units and 5 degrees; these are editing tolerances, not calibrated physical accuracy. Gravity comes from the scene; disabling scene gravity is explicit zero gravity.
5. Click **Analyze Current Pose**. Inspect the saved frame, world COM XYZ, signed support margin and excluded contacts. Reanalyze after changing the frame, pose, gravity, contacts or mass model. This is a labelled snapshot, not a live tracking display. Full structured measurements, segment endpoints/centers and excluded-contact reasons are in the armature's `b4ml.support_report` JSON string.

The compact panel keeps mass and plane settings collapsed until needed. World COM and margin are displayed in internal coordinate units; other distance widgets follow the host's display units. Settings and snapshot survive save/reload. A normal panel-button invocation participates in Undo/Redo. Scripts should manage their own undo boundaries when calling synchronous operators; invoking one from a timer is not equivalent to a user UI event.

## Explicit mass approximation

COM is the normalized weighted sum of segment centers. Each center is interpolated along two evaluated world-space endpoints. The 17 editable segments are lower/middle/upper trunk, neck, head, and paired upper arms, forearms, hands, thighs, shins and feet. Trunk and proximal limb segments span mapped joint heads; terminal head/hand/foot segments use the mapped bone's evaluated head and tail. The full mapping and measured endpoints are inspectable in the report.

Default relative weights sum to 100: trunk 12/12/18, neck 2, head 8, each arm 4/2/1, each leg 10/5/2. These are an original artist-editable distribution, **not measured anthropometry**. Center fractions default to 0.5. No mesh-density integration, tissue masses, body-volume estimation, accessory masses or inertia tensor is implied. An accurate-looking number is only as useful as the supplied mass model.

Native IK poses are read through evaluated skeletal joints without FK conversion. The read-only mapping does not require writable rotation channels; existing solvers retain their original write validation. Known unsupported rig conventions and blended IK/FK inputs remain rejected by the underlying adapters. Testing covers five actual generators, not arbitrary rigs sharing their names.

## Support geometry and limits

Only explicitly enabled support contacts inside their hold interval, at full strength, enter the support estimate. Blend intervals and fractional strength do not establish support. A patch is excluded if its evaluated joint-plus-local-offset drifts beyond tolerance, its orientation changes too far from capture, or its center does not lie on the authored plane. Small allowed plane error is projected onto the plane before constructing the patch.

Each patch is an artist-authored rectangle centered on the captured point. Heading zero aligns its width with world X projected onto the plane; world Y is used when the plane normal is nearly parallel to X. Length is the orthogonal in-plane axis. Heading rotates this basis. Width/length are full world-space dimensions. Patches do not automatically fit a deformed mesh, rotate with a moving foot, follow a platform, or detect collisions. Choose dimensions that represent the intended load-bearing area; passing a contact-position test does not prove real surface contact.

The convex hull of accepted patch vertices defines the planar support region. The COM projection follows the gravity direction onto that plane. Margin is the shortest distance to the hull boundary, positive inside and negative outside. One-point or collinear support is reported as degenerate. Near-boundary, no-support, zero-gravity, COM-below-plane and gravity-not-into-plane cases have explicit statuses.

This is a geometric static estimate. On an inclined plane, output is explicitly **Inclined Geometry Only**; friction and admissible contact forces have not been solved. Even horizontal **Inside Support** is not a prediction of dynamic balance: acceleration, angular momentum, force/torque limits, impacts and friction can change feasibility. The next physics work must retain this distinction.

Primary background references: [MIT Underactuated Robotics: highly articulated legged robots](https://underactuated.mit.edu/humanoids.html) for contact-force and COM dynamics; [Feasible Region: an Actuation-Aware Extension of the Support Region](https://arxiv.org/abs/1903.07999) for the limits of geometry alone. These references are not sources of anthropometric defaults or copied implementations.

## Validation scope

- Eight standalone numerical tests cover weighted COM, invalid/zero mass, coordinate and length changes, hull ordering/duplicates, signed distance, degenerate support, gravity direction, zero gravity and invalid planes.
- Six Bforartists integration tests cover five actual BoneForge/Rigify builders, native IK motion response, editable mass influence, transformed rigs, locked controls, support exclusions, scene gravity, saved settings, source actions/modes/rest bones/constraints and bound mesh sample preservation.
- The transformed Rigify fixture agrees within 5e-6 internal units; rig/dependency evaluation and mathutils use single precision. Pure numerical tests use tighter double-precision checks.
- A real-window test clicks the actual panel button, inspects the result, undoes and redoes it, and checks that rig values remain unchanged. Python timer calls initially failed the undo test because they did not create the same UI undo boundary; the successful test uses actual mouse events and does not add a synthetic post-operation undo push.
- Integration assertions pass before the existing host `ucrtbase.dll` shutdown access violation. This is not a clean host process exit. Process results are recorded separately from test assertions.

See `checkpoint-support-v1.json`, `support-ui-v0.11.0.json`, `package-test-v0.11.0.json`, and `training/b4artists_ml/results/support-package-v0.11.0.json` for final artifact identities, measurements and verification. Timing is a small current-pose diagnostic, not whole-body optimization, inference, viewport rendering or production motion performance. There is no Cascadeur comparison or quality-parity claim.

## Final package measurements

Package: `releases\b4artists_ml_v0.11.0.zip`, 216,869 bytes, 28 files, SHA256 `2af175b4c9594e7c8627a3ba8e0b07a643dd85eacdb31edc36f0ed6218715065`. Every member matches source bytes.

The full regression pass has 158 tests with passing assertions across 13 host suites (148 package-entry tests and 10 existing source-entry contextual-rig tests). After that pass, only the support panel layout changed. The final exact package passed 8 numerical tests, 6 actual-rig tests, and the real-window button/Undo/Redo check. The checkpoint retains both ZIP hashes and the UI-only delta; it does not claim the full regression was rerun on different bytes.

| Fixture | First analysis ms | Warm p50 ms | Warm p95 ms |
|---|---:|---:|---:|
| boneforge | 2.473 | 2.279 | 2.562 |
| rigify_basic | 2.563 | 2.259 | 2.778 |
| rigify_default | 2.509 | 2.380 | 2.660 |
| metarig_basic | 2.291 | 2.106 | 2.297 |
| metarig_default | 2.997 | 2.367 | 2.874 |

Ten warm samples per fixture, after rig evaluation, on the local Windows host. These are small-sample diagnostic timings, not a general latency guarantee. Native-rig/action/mesh preservation checks pass on all five fixtures.
