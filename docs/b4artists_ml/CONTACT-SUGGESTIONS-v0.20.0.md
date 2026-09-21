# Scene-aware contact suggestions - experimental 0.20.0

## Animator workflow

Animation Contacts can now scan the selected interpolation candidate for provisional foot holds. The animator chooses an optional static planar mesh or uses the explicitly authored support plane, adjusts character-relative surface-distance and foot-speed thresholds, and clicks **Suggest Foot Contacts**. Matching grounded priority poses can identify an intended hold even when the interpolated foot slides between them.

Every result is labelled **Proposed** with confidence, surface provenance and measured reasons. Proposed and rejected rows are excluded from contact correction. The animator must accept a suggestion before **Preview Contact Correction** can use it, and can edit its interval, blend, strength, point, offset and rotation first. Scanning never changes the action. Existing manual hand/foot capture remains accepted immediately.

The first surface adapter accepts an unparented, static planar mesh without modifiers or constraints and checks its actual face boundaries. With no object selected, the saved support plane is infinite. Moving surfaces, nonplanar collision meshes, hands against props and general collision response remain separate work.

## Evidence

- Source regression: 45 suites and 428 tests pass with one consistent runtime hash, including host-independent interval tests and four scene workflow tests.
- Actual-window default Rigify journey: two proposals, explicit accept/reject, one-contact correction, Keep and Restore Source all pass. The qualified run measured 619.0 ms total for 11 sampled frames, 48.5 ms p95 and 48.5 ms maximum per cooperative suggestion step. Accepted contact error after correction was 1.46e-05 evaluated leg lengths.
- Reload: provisional confidence, provenance, reason and review state survive a `.blend` roundtrip without becoming accepted.
- Exact archive: 13 established offline workflows and 4 packaged suggestion tests pass from the extracted 0.20.0 ZIP. The established run includes 9,813 dense contact checks and blocks outbound Python networking and process launch from the add-on runtime.
- Archive: `releases/b4artists_ml_v0.20.0.zip`, SHA-256 `6b237955204d79a40b0515eca37b23d7368bba940e3cf663ed25a3113ac24648`.

All Bforartists test children still return the known `ucrtbase.dll` access violation after writing passing reports. Clean host shutdown remains unqualified. The contact-correction stage in the UI journey took 17.0 seconds on default Rigify, so complete-workflow responsiveness remains partial even though suggestion ticks pass the 50 ms target. Independent animator usability, broad walk/run/landing evaluation, learned temporal quality and Cascadeur comparison remain unverified.
