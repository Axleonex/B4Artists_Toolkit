# B4Artists Machine Learning 0.3 validation

All 58 packaged host tests passed with zero skips: 31 foundation tests, 18 posing tests and nine rig-state tests. Full Rigify generation was enabled. Plain Python separately passed 11 tests and skipped 47 host-dependent tests. Source parsing, whitespace, ZIP integrity and packaged source equality passed.

## New evidence

- Default BoneForge, basic Rigify and full Rigify IK inputs matched to FK with evaluated joint error no greater than 1.91e-7 local rig units in the recorded neutral fixtures.
- Moved IK input conversion checks positions, orientation and scale; a moved Rigify hand can then be posed through the geometric solver and cancelled back to its original channels.
- Full deform-bone weighted point samples retained their evaluated positions through conversion: BoneForge 100 samples (maximum error 1.69e-7), basic Rigify 70 (4.31e-7), full Rigify 320 (5.98e-7) local rig units. These are synthetic probes covering the generated deform bones, not visual acceptance of production character meshes.
- Animated input IK/FK mode curves remain byte-for-value unchanged in the original action, including keys, handles and interpolation metadata. Normalized candidates use constant FK mode keys, and discard/source restoration returns the original modes.
- Partial conversion failure restores original modes and FK transforms. Pending IK sessions resume after reopening; the source action may re-evaluate its original modes, and explicit Solve re-enters the recorded FK working state.
- Kept candidates retain a persistent source recovery record; the UI Restore Source Animation operation was tested after reopening a saved file.

The existing posing and interpolation suites also passed against this package. See checkpoint-v0.3.0.json for result counts and deform measurements; posing-benchmark-v0.3.0.json for scenario samples. The older 0.2 rejection test was replaced with acceptance/cancellation coverage for default IK input. Tests label IK inputs as FK solves.

## Performance and limits

The 15 recorded posing scenarios measured approximately 38.8 to 131.5 ms per solve including host scene evaluation. This excludes initial IK-to-FK conversion and rig creation. Several generated rigs coexist in the benchmark scene. These are individual samples, not cold/warm latency distributions or a responsiveness guarantee. Manual visual quality, peak memory, production characters and direct Cascadeur comparisons remain unverified.

Native IK constraints are not changed. Output is FK. Other animated rig properties, arbitrary space changes, nonuniform/reflected object scale, anatomical joint limits, head/whole-body compensation, temporal contacts, physics and real ML remain unfinished. Generated candidate mode keys include one-frame boundary samples; adjacent subframe behavior can differ in the copied candidate. The source action stays untouched.

## Runtime and package

Host: X:/5.1.0/bforartists.exe, core 5.2.0 Alpha, build dd23ab17120d; CPU identifier AMD64 Family 25 Model 33 Stepping 2, AuthenticAMD. The installed host still exits with its previously isolated shutdown access violation after passing assertions. Every process returned 3221225477; the test markers establish assertion success, not a clean host exit.

ZIP: b4artists_ml_v0.3.0.zip, 13 files, 31,315 bytes. SHA-256: `58701e025e30f7733b126f7bb16475d5a5330cfc000d52858aea669ca5a9fa4d`. No weights, training assets, external inference runtime or network dependency are bundled. No commits, pushes, installed-addon changes or paid services.

The router preflight again reported OMP READY but the remote executor could not access the local X: workspace. It emitted no execution lanes or patch. Native continuation followed the canonical infrastructure-recovery policy. The previous turn and this checkpoint are concrete progress; the full goal remains active and incomplete.
