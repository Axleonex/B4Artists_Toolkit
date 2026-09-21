# Secondary World-Location Chain Momentum v1

## Status

Complete as a bounded procedural development slice through 2026-09-18, including explicit force/mass and force-at-offset torque, the bounded local rotational-chain angular-momentum path, selected-control self-collision, static planar, single static/directly animated sphere, bounded sets of static spheres, static/directly animated capsule, one bounded static support-plane plus sphere-set plus capsule compound, the v0.37.44 static support-plane plus sphere-set plus closed-mesh compound, the v0.37.46 support-plane plus one directly animated sphere compound, the v0.37.47 support-plane plus static sphere-set plus one directly animated capsule compound, the v0.37.48 support-plane plus static sphere-set plus one directly animated sphere compound, the v0.37.49 support-plane plus exactly two directly animated spheres compound, the v0.37.50 support-plane plus exactly two directly animated spheres plus static sphere-set compound, the v0.37.51 support-plane plus exactly three directly animated spheres with optional static sphere set compound, static triangle-mesh surface, static continuous closed-mesh, and exact static swept-volume collision extensions. This is not a claim of a general rigid-body solver, collision impulse transfer, learned temporal motion, independent animator acceptance, unrestricted production-character generalization, or Cascadeur parity.

## Behavior

The selected-control secondary solver now supports an explicit contiguous parent-to-child chain in world-space location mode. It follows authored world location targets with the existing bounded implicit follower, applies authored force/mass acceleration, and transfers pairwise internal momentum with equal-and-opposite impulses. An optional authored static planar, single static or directly animated spherical, finite static or directly animated capsule, or one static evaluated triangle-mesh surface collider applies bounded external restitution/friction response after that internal transfer and reports raw and resolved penetration. A directly animated sphere may also follow guarded uniform radius animation; response velocity is relative to both sampled center motion and radial surface motion. A directly animated capsule uses guarded endpoint Actions with optional matching uniform scale; response is relative to midpoint translation and radial surface velocity. A closed static mesh can additionally use the existing bounded segment/triangle sweep to catch crossings between solver samples; a closed static mesh can also provide an exact swept-sphere finite-volume test when a positive volume radius and continuous sweep are explicitly requested. A bounded compound may explicitly add one static endpoint capsule and/or one static closed triangle mesh after the support plane and static sphere set; endpoint animation, mesh deformation, mesh motion, continuous sweep, and finite-volume options are rejected in the static compound form. A separate moving-capsule compound may instead add exactly one directly animated, optionally uniformly scaled capsule after the support plane and static sphere set. A separate mixed-sphere compound may add exactly one directly animated, optionally uniformly scaled sphere after the support plane and static sphere set. A separate two-moving-sphere compound may add exactly two directly animated, optionally uniformly scaled spheres after one authored support plane, optionally composed with the bounded static sphere set. It samples each moving sphere center/radius trajectory, detects bounded relative-motion crossings against the support plane, the static sphere set, and the other moving sphere, applies deterministic alternating support/sphere projection, and responds relative to center and radial surface velocity. Hierarchy-aware world-to-local conversion keeps the resulting editable Action consistent with parent-child transforms. Local rotation chain behavior remains a separate `LOCAL_ROTATION` path.

The mode is fail-closed unless the request is explicitly supported. World-location chain mode requires Location output and explicit force/mass assignments. Supported bounded forms include static planar/spherical/sphere-set/capsule/closed-mesh collision; a support plane with exactly one, two, or three directly animated spheres (optional uniform radius scaling), optionally followed by the bounded static sphere set; one moving capsule plus support and a static sphere set; and the separately qualified static mesh/volume paths. Three-moving-sphere support (schemas 39/40) is exact-package qualified by v0.37.51-dev for the declared forms only; its nine-profile probe does not qualify arbitrary production rigs or animation quality. Continuous relative-motion sweep and radial surface velocity apply only to the declared moving spheres. Moving-capsule compounds do not combine with moving spheres or meshes. More than three moving spheres, animated sphere sets, unsupported moving/static mixtures, moving/deforming mesh or volume compounds, finite-volume compound meshes, non-continuous volumes, open continuous meshes, self-collision, wind, and frame-authored impulse combinations remain rejected. The implementation is deterministic and procedural (`learned: false`).

The bounded `LOCAL_ROTATION` extension is separate from the world-location
chain. It requires a contiguous direct parent-to-child selection, complete
editable rotation curves, a nonzero force offset on every chain control, and
Rotation without Location. It samples evaluated world orientations, converts
the authored world torque to local angular acceleration, and exchanges bounded
equal-and-opposite weighted control-local angular impulses. Its conservation
receipt is for control-local angular momentum, not world rigid-body angular
momentum; the linear force component remains the `WORLD_LOCATION` path.

## Evidence

- Host-independent math suite: 21/21 tests, 0 failures, 0 errors, 0 skips, including static planar, static-sphere, static-capsule, static-mesh, static continuous closed-mesh, exact static swept-volume chain paths plus fail-closed collider validation.
- Historical current-worktree Bforartists baseline: 14/14 tests, 0 failures, 0 errors, 0 skips; `B4ML_SECONDARY_RESULT: PASS`. The world-location/momentum case passes on BoneForge, generated Rigify Default, and generated Rigify Basic; the planar-collision extension passes on BoneForge.
- New targeted BoneForge static-sphere integration: 1/1 test, `B4ML_SECONDARY_RESULT: PASS`; the host emits the passing marker before its known alpha-host shutdown/unregister fault.
- New targeted BoneForge static-capsule integration: 1/1 test, `B4ML_SECONDARY_RESULT: PASS`; the host emits the passing marker before its known alpha-host shutdown/unregister fault.
- New targeted BoneForge static-mesh integration: 1/1 test, `B4ML_SECONDARY_RESULT: PASS`; the closed mesh contains 12 evaluated triangles, records 4 collision samples, raw penetration `0.028661982271749764`, resolved penetration `0.0`, momentum residual `1.7763568394002505e-15`, and preserves priority poses before the known alpha-host shutdown/unregister fault.
- New targeted BoneForge static continuous-mesh integration: 1/1 test, `B4ML_SECONDARY_RESULT: PASS`; the closed mesh contains 12 evaluated triangles, records 4 continuous sweep samples, zero sampled raw penetration, zero resolved penetration, momentum residual `1.7763568394002505e-15`, and preserves priority poses before the known alpha-host shutdown/unregister fault.
- New targeted BoneForge exact static swept-volume integration: 1/1 test, `B4ML_SECONDARY_RESULT: PASS`; the closed mesh contains 12 evaluated triangles, uses a `0.0010000000474974513` swept radius and clearance, records 4 continuous sweep samples, zero sampled raw penetration, zero resolved penetration, momentum residual `2.220446049250313e-16`, and preserves priority poses before the known alpha-host shutdown/unregister fault.
- Final current-source host recheck: 19 tests ran; the 14 BoneForge/non-Rigify cases passed, while 5 Rigify cases errored before fixture creation or during addon unregister on the installed alpha host (`rigify_colors` / `RigifyParameters` incompatibility). No sphere, capsule, mesh, continuous-mesh, exact-volume, plane, or BoneForge chain assertion failed in that recheck.
- Fresh isolated current-worktree recheck on 2026-09-14 is recorded separately in `secondary-world-chain-momentum-recheck-v2.json`: the affected harness ran 164 tests with 164 passed, zero failures/errors/skips, including the Rigify paths. The older five-error observation did not reproduce; the run used an isolated user-resource directory and ended only with the known post-marker `ucrtbase.dll` shutdown fault. This receipt is current-worktree evidence and does not replace exact-package evidence.
- Moving-sphere chain extension on 2026-09-14: host-independent secondary math passes 22/22. The complete current Bforartists `SecondaryMotionTests` class passes 20/20 with zero failures, errors, or skips across BoneForge and generated Rigify fixtures, and emits `B4ML_SECONDARY_RESULT: PASS` before the known post-marker alpha-host `ucrtbase.dll` shutdown fault. The new path reports schema 26 and backend `implicit_selected_control_chain_location_moving_sphere_v1`; static chain cases retain schema 25 and backend `implicit_selected_control_chain_location_v1`. Machine-readable hashes and non-claims are in `training/b4artists_ml/results/secondary-world-chain-moving-sphere-v1.json`.
- Four read-only independent reviewer invocations converged after finding and repairing final-output clearance at partial influence, the near-zero threshold, and minimum-positive floating-point underflow. The final reviewer reports PASS: exact zero and endpoints remain unchanged, while every positive finite strength with a positive envelope receives final clearance projection. This is advisory code review, not full-goal completion authority.
- Exact-package foreground lifecycle on 2026-09-14 passes against immutable `b4artists_ml_v0.37.31-dev.zip` (`4f65d618537c17b97bc450b2117d350b0ae518652ba32fe5e025c2d05f6132c0`). Separate screenshots capture the configured World/Location/Coupled Chain/propagation region and animated/scaling sphere region for later manual semantic review; screenshots are not counted as automated UI-content or human-usability proof. The BoneForge journey generates schema 26, independently samples 22 evaluated control/sphere clearances (minimum `0.020776392002273436`), completes native Undo/Redo and Restore Input with curve-token checks, Keep, save/reload binding recovery, and Restore Source while preserving the source Action, collider Action, armature structure, and rig modes. The parent process observes the exact known post-assertion `EXCEPTION_ACCESS_VIOLATION` / `ucrtbase.dll` shutdown signature rather than inferring it. Receipt: `training/b4artists_ml/results/secondary-world-chain-moving-sphere-foreground-v1.json`.
- A separate read-only foreground-harness reviewer initially blocked weak fail-closed, screenshot, shutdown, provenance, and independent-clearance evidence. After three review invocations and two repair rounds, its final verdict is PASS with no remaining blocker. This remains advisory review, not independent animator acceptance or full-goal completion authority.
- Moving-capsule chain extension on 2026-09-14: schema 27 / `implicit_selected_control_chain_location_moving_capsule_v1` supports one directly animated capsule with optional matching uniform endpoint scale. It samples guarded endpoint/radius trajectories, responds relative to midpoint translation and radial velocity, preserves exact priority keys, and treats exact zero strength as a true no-op with zero collision/coupling counts and no momentum-transfer claim. Scaling-only and continuous moving-capsule chain modes fail closed. Endpoint rotation remains a documented bounded midpoint approximation rather than a continuous moving-surface claim.
- Multiple static spheres on 2026-09-15: the exact v0.37.38 archive passes the dedicated `SecondaryMultiSphereCollisionTests` suite 8/8 on BoneForge and generated Rigify Default. The bounded set supports up to eight static, distinct, unparented, unanimated sphere centers with deterministic order-independent projection, persistence, rollback, and priority-conflict rejection. Receipt: `training/b4artists_ml/results/exact-package-v0.37.38-test_b4artists_ml_secondary_multi_sphere_collision_v1.json`.
- Independent review required and verified fixes for exact-zero host behavior, extreme finite-coordinate overflow, isolated midpoint/radius velocity history, exact priority comparisons, and zero-strength reporting. The final verdict is PASS with no remaining actionable finding. Current-source and exact-package host-independent math pass 36/36; exact-package Bforartists secondary motion passes 24/24, while the legacy capsule binding passes 3/3 before the known post-marker alpha-host shutdown fault.
- The first immutable capsule-chain archive v0.37.32 (`996e6043483055a1c68f2c12e05a9167456cddb2db5ad3aa78e722386dd510af`) is retained but rejected/superseded because it predated the final zero-strength reporting correction. The final immutable v0.37.33 archive (`6c49cd6544c68019dbd28b5708fbccad00c8a3da4e92d4dd75004a0b048da192`) has 54 source-identical members. Its exact-package BoneForge foreground lifecycle passes schema 27, native Undo/Redo, Restore Input, Keep, save/reload, Restore Source, and 22 independently sampled finite capsule clearances with minimum `0.020970401875100908`. Screenshot semantics remain manual-review-only. Receipts: `training/b4artists_ml/results/secondary-world-chain-moving-capsule-v1.json` and `secondary-world-chain-moving-capsule-foreground-v1.json`.
- BoneForge world-chain record: schema 25, backend `implicit_selected_control_chain_location_v1`, 2 loaded controls, 9 coupled samples, 6 editable curves / 66 keys.
- Momentum conservation residual: `3.1401849173675503e-16`.
- Maximum internal impulse: `0.5985296339543954`.
- Maximum world-location error: `3.5762786865234375e-7`.
- Maximum location correction: `0.1458168834832868`.
- BoneForge planar-collision record: schema 25, authored static plane, 2 collision samples, raw penetration `0.02413573339805919`, resolved penetration `0.0`, and maximum location correction `0.1655902820225716`.
- The planar-collision chain retains momentum residual `3.1401849173675503e-16`; its maximum world-location error is `1.6858739404357614e-7`.
- BoneForge static-sphere record: schema 25, one static sphere of radius `1.0`, 2 collision samples, raw penetration `0.030880139527631356`, resolved penetration `0.0`, and momentum residual `2.220446049250313e-16`.
- BoneForge static-capsule record: schema 25, one finite capsule of radius `1.0`, 2 collision samples, raw penetration `0.030880139527631356`, resolved penetration `0.0`, and momentum residual `2.220446049250313e-16`.
- BoneForge static-mesh record: schema 25, one closed static surface mesh with 12 triangles, 4 collision samples, raw penetration `0.028661982271749764`, resolved penetration `0.0`, momentum residual `1.7763568394002505e-15`, and priority poses preserved.
- BoneForge static continuous-mesh record: schema 25, one closed static surface mesh with 12 triangles, 4 collision samples / 4 continuous sweep samples, raw penetration `0.0`, resolved penetration `0.0`, momentum residual `1.7763568394002505e-15`, and priority poses preserved.
- BoneForge exact static swept-volume record: schema 25, one closed static mesh with 12 triangles, continuous exact swept radius/clearance `0.0010000000474974513`, 4 collision samples / 4 continuous sweep samples, raw penetration `0.0`, resolved penetration `0.0`, momentum residual `2.220446049250313e-16`, maximum internal impulse `0.854037010012979`, and priority poses preserved.
- The host again exits with the known shutdown-only `ucrtbase.dll` access violation after the passing harness marker; this is not counted as a test failure.
- Static compound-capsule extension on 2026-09-16: source math passes 35/35 and the complete current-worktree Bforartists secondary-motion class passes 29/29. The exact v0.37.43-dev ZIP independently passes the new four-collider fixture 1/1, reporting schema 31, four colliders, two collision samples, raw penetration `0.030880139527631356`, resolved penetration `0.0`, momentum residual `2.220446049250313e-16`, and maximum world-location error `1.6858739404357614e-7`. The exact v0.37.43 archive also passes the established 85-test pole, 12-test direct-import, and three-character production checks. Receipt: `training/b4artists_ml/results/exact-package-v0.37.43-compound-capsule.json`. This remains one static bounded compound, not broad multi-collider dynamics or general rigid-body collision coupling.
- Static compound-mesh extension on 2026-09-16: source math passes 36/36 and the exact v0.37.44-dev ZIP passes the complete 30-test Bforartists secondary-motion class. Its dedicated four-collider fixture passes 1/1, reporting schema 32, two static spheres plus the authored support plane and one closed 12-triangle mesh, four collision samples, raw penetration `0.019999980926513672`, resolved penetration `0.0`, momentum residual `2.220446049250313e-16`, and maximum world-location error `1.6858739404357614e-7`. The exact archive also passes the established 85-test pole, 12-test direct-import, and three-character production checks. Receipt: `training/b4artists_ml/results/exact-package-v0.37.44-compound-mesh.json`. This remains one static bounded compound, not broad multi-collider dynamics or general rigid-body collision coupling.
- Combined static compound extension on 2026-09-16: the exact v0.37.44-dev ZIP passes the capsule-plus-mesh fixture 1/1, reporting schema 32, two static spheres plus the authored support plane, one static capsule, and one closed 12-triangle mesh, five collision colliders, four collision samples, raw penetration `0.019999980926513672`, resolved penetration `0.0`, momentum residual `2.220446049250313e-16`, and maximum world-location error `1.6858739404357614e-7`. Receipt: `training/b4artists_ml/results/exact-package-v0.37.44-compound-capsule-mesh.json`. This remains one static bounded compound, not broad multi-collider dynamics or general rigid-body collision coupling.

- v0.37.45 local angular-chain extension on 2026-09-16: the exact ZIP passes
  the dedicated Rigify integration within the 32/32 secondary-motion suite;
  host-independent math passes 50/50 across the secondary and capsule math
  contracts. The new schema-33 backend
  `implicit_selected_control_chain_angular_momentum_v1` preserves priority
  rotations and reports bounded control-local angular-momentum transfer. The
  exact archive and all receipts are bound by SHA-256
  `239abcb52bfb21eb661e741f9f5c7d42205e27b8d44ac9487ea90fd06180c791`.

- v0.37.46 support-plus-moving-sphere compound on 2026-09-16: host-independent
  secondary/capsule math passes 51/51, and the exact v0.37.46 ZIP passes the
  full 33/33 `SecondaryMotionTests` class plus the dedicated compound fixture
  1/1. The fixture exercises an authored static support plane and exactly one
  evaluated direct moving sphere with uniform scale animation, relative center
  and radius-rate response, priority preservation, and bounded momentum. It
  reports schema 34 and backend
  `implicit_selected_control_chain_location_moving_sphere_compound_support_v1`.
  Exact ZIP SHA-256:
  `4c6f07ebb32bb2c89d3a1a61107704f67a47d05079bd6377eb241da7ebd13eef`.

- v0.37.47 support-plus-moving-capsule compound on 2026-09-16: the exact
  archive passes the full 34/34 `SecondaryMotionTests` class, the dedicated
  moving-capsule compound fixture 1/1, the exact pole/posing regression 85/85,
  direct imported-humanoid checks 12/12, the bounded production-character
  generalization probe 3/3, and the focused secondary/capsule math contract
  52/52. The fixture exercises one authored static support plane, a static
  sphere set, and exactly one directly animated capsule with endpoint motion,
  uniform scale, bounded continuous relative-motion sweep, priority
  preservation, deterministic compound projection, and bounded momentum. It
  reports schema 35 and backend
  `implicit_selected_control_chain_location_moving_capsule_compound_support_spheres_v1`.
 Exact ZIP SHA-256:
 `d11aedef5d818ed06465de9d60bc45a812784b6e5af7eedccf823d4c46d18339`.

- v0.37.48 mixed moving/static sphere compound on 2026-09-16: the exact
  archive passes the full 35/35 `SecondaryMotionTests` class and the dedicated
  mixed-sphere fixture 1/1, with the exact pole/posing regression 85/85,
  direct imported-humanoid checks 12/12, the bounded production-character
  generalization probe 3/3, and focused secondary/capsule math 53/53. The
  fixture reports schema 36 and backend
  `implicit_selected_control_chain_location_mixed_moving_sphere_compound_support_spheres_v1`;
  it uses one directly animated, optionally uniformly scaled sphere after an
  authored support plane and static sphere set, records two continuous sweep
  samples, zero final penetration, and momentum residual about `2.22e-16`.
  Receipt: `training/b4artists_ml/results/exact-package-v0.37.48-compound-mixed-spheres.json`.

- v0.37.49 two-moving-sphere compound on 2026-09-16: the exact archive passes
  the full 36/36 `SecondaryMotionTests` class and the dedicated two-moving-
  sphere fixture 1/1, with the exact pole/posing regression 85/85, direct
  imported-humanoid checks 12/12, the bounded production-character
  generalization probe 3/3, and focused secondary/capsule math 54/54. The
  fixture reports schema 37 and backend
  `implicit_selected_control_chain_location_moving_sphere_set_compound_support_v1`;
  it uses one authored support plane and exactly two directly animated,
  optionally uniformly scaled spheres, records bounded relative-motion sweep
  and deterministic projection, zero final penetration, and bounded momentum.
  Receipt: `training/b4artists_ml/results/exact-package-v0.37.49-compound-moving-sphere-set.json`.

- v0.37.50 two-moving-sphere plus static-sphere-set compound on 2026-09-16:
  the exact archive passes the full 37/37 `SecondaryMotionTests` class and the
  dedicated two-moving-plus-static-set fixture 1/1, with the exact pole/posing
  regression 85/85, direct imported-humanoid checks 12/12, the bounded
  production-character generalization probe 3/3, and focused secondary/capsule
  math 55/55. The fixture reports schema 38 and backend
  `implicit_selected_control_chain_location_mixed_moving_sphere_set_compound_support_spheres_v1`;
  it uses one authored support plane, a static sphere set, and exactly two
  directly animated, optionally uniformly scaled spheres, records bounded
  relative-motion sweeps and deterministic projection, zero final penetration,
  and bounded momentum. Receipt:
  `training/b4artists_ml/results/exact-package-v0.37.50-compound-moving-sphere-static-set.json`.

- 2026-09-17 source-only verification: schema 39 covers one support plane plus exactly
  three directly animated, optionally uniformly scaled spheres; schema 40 adds
  the existing bounded static-sphere set. The focused math test checks all
  three trajectories, collision-order invariance, continuous sweep, priority
  preservation, zero final penetration, momentum residual, and four-sphere
  rejection. The BforArtists host tests separately exercise three moving
  spheres with and without a static sphere and verify four-moving-sphere
  rejection before candidate keys change. The focused math suite passes 44/44
  and the full `SecondaryMotionTests` host suite passes 40/40, with zero
  failures, errors, or skips. Durable reports are
  `training/b4artists_ml/results/three-moving-spheres-source-math-v1-20260917.json`
  and `training/b4artists_ml/results/three-moving-spheres-host-v1-20260917.json`.
  Both ran on Bforartists 5.2.0 Alpha; test assertions passed, but teardown
  retains the known `ucrtbase.dll` access-violation process exit. This evidence
  preceded and is retained alongside the exact-package qualification below.

- v0.37.51 three-moving-sphere compound with optional static sphere set on
  2026-09-18: the immutable archive
  `releases/b4artists_ml_v0.37.51-dev.zip` at SHA-256
  `b388368b0a9ac44f3ff75069c79768e67a1bcf368efed7733145c3a9a87d662d`
  passes the full 40/40 `SecondaryMotionTests` class, the dedicated schema-40
  fixture 1/1, focused secondary/capsule math 56/56, pole/posing regression
  87/87 across eight suites, direct imported-humanoid checks 12/12, and the
  nine-profile production-character probe 3/3 test methods. Schemas 39 and 40
  report backends
  `implicit_selected_control_chain_location_moving_sphere_triple_set_compound_support_v1`
  and
  `implicit_selected_control_chain_location_mixed_moving_sphere_triple_set_compound_support_spheres_v1`.
  Receipts are
  `training/b4artists_ml/results/exact-package-v0.37.51-secondary-motion-all.json`,
  `training/b4artists_ml/results/exact-package-v0.37.51-compound-three-moving-sphere-static-set.json`,
  `training/b4artists_ml/results/exact-package-v0.37.51-focused-secondary-math.json`,
  `training/b4artists_ml/results/exact-package-pole-v0.37.51.json`,
  `training/b4artists_ml/results/current-package-direct-zip-import-v0.37.51.json`,
  and
  `training/b4artists_ml/results/exact-package-v0.37.51-production-character-generalization.json`.
  The archive is not installed or promoted; alpha-host assertion receipts pass
  before the known shutdown-only access violation.

The machine-readable receipt is `secondary-world-chain-momentum-ui-v1.json`.

## Boundaries

This slice does not close coupled general rigid-body dynamics, broad collision-coupled momentum, broader production-character generalization, learned temporal quality, independent animator usability, or Cascadeur comparison. Qualified bounded paths include static planar/spherical/sphere-set/capsule/closed-mesh collision; one-, two-, and three-moving-sphere support compounds, with the declared optional bounded static sphere set; one moving capsule plus support and static spheres; and the listed static mesh/volume paths. More than three moving spheres, animated sphere sets, unsupported moving/static mixtures, moving sphere/capsule/mesh mixtures, moving/deforming mesh or volume compounds, finite-volume compound meshes, non-continuous volumes, open continuous meshes, and other collision paths remain outside this chain mode. General rigid-body dynamics, broader production-character generalization, learned temporal quality, independent animator usability, and Cascadeur comparison remain open goal gates.
